
<template>
  <div class="data-display-container">
    <div class="section search-bar">
      <div class="search-container">
        <input type="text" v-model="searchText" placeholder="输入搜索关键词..." class="search-input">
        <input type="text" v-model="lng" placeholder="经度" class="search-input coord-input">
        <input type="text" v-model="lat" placeholder="纬度" class="search-input coord-input">
        <button class="search-button" @click="executeFirstStageSearch">搜索</button>
        <button class="search-button" disabled>在地图上显示</button>
      </div>
    </div>

    <!-- 访问次数条形图 -->
    <div class="section access-times-chart">
      <h3>块访问次数统计</h3>
      <div class="chart-container">
        <AccessTimesChart 
          dataType="multiple" 
          title="块访问次数统计"
          :start="1"
          :end="1000"
        />
      </div>
    </div>

    
    <div class="section process-node-graph">
      <h3>检索流程节点图</h3>
      <div class="graph-placeholder" @mousemove="onSvgMouseMove" @mouseleave="hideTooltip">
        <svg width="100%" height="320" viewBox="0 0 1200 320">
          <!-- 箭头定义 -->
          <defs>
            <marker id="arrow-end" markerWidth="8" markerHeight="8" refX="0" refY="4" orient="auto">
              <path d="M0,1 L8,4 L0,7 L2,4 Z" fill="#6ec6f7" />
            </marker>
            <marker id="arrow-start" markerWidth="8" markerHeight="8" refX="8" refY="4" orient="auto">
              <path d="M0,1 L8,4 L0,7 L2,4 Z" fill="#6ec6f7" />
            </marker>
          </defs>
          <!-- 主干三次贝塞尔曲线（首尾延伸，双箭头，左右拉伸） -->
          <path d="M75,260 C265,80 945,340 1145,120" stroke="#6ec6f7" stroke-width="1.2" fill="none" marker-end="url(#arrow-end)" marker-start="url(#arrow-start)" />
          <!-- 节点与说明 -->
          <g v-for="(node, idx) in mindmapNodes" :key="node.name">
            <!-- 节点圆点（有边框），y坐标根据曲线计算 -->
            <circle :cx="node.x" :cy="node.y" r="6" :fill="node.color" stroke="#d8d4ac" stroke-width="1.5"
              @mouseenter="showTooltip($event, node)" @mouseleave="hideTooltip" @click="onNodeClick(node)" style="cursor:pointer;"/>
            <!-- 节点名称，上下错开分布 -->
            <text :x="node.x" :y="idx % 2 === 0 ? node.y - 26 : node.y + 36" fill="#333" font-size="15" font-weight="bold" text-anchor="middle">{{ node.name }}</text>
          </g>
        </svg>
        <transition name="fade">
          <div v-if="tooltip.show" class="svg-tooltip" :style="{left: tooltip.x + 'px', top: tooltip.y + 'px'}">
            {{ tooltip.text }}
          </div>
        </transition>
      </div>
    </div>

    <!-- 搜索结果浮窗 -->
    <teleport to="body">
      <div v-if="searchResults.length > 0" class="search-results-popup-mask" @click.self="closeSearchResults">
        <div class="search-results-popup">
          <div class="popup-header">
            <h4>搜索结果</h4>
            <button class="popup-close-btn" @click="closeSearchResults">×</button>
          </div>
          <div class="popup-content">
            <!-- PathORAM搜索统计横条 -->
            <div class="pathoram-stats-bar" @click="goToOBIRTreePage">
              <div class="stats-item">
                <span class="stats-label">节点变化:</span>
                <span class="stats-value">{{ pathORAMStats.nodeChange }}</span>
              </div>
              <div class="stats-item">
                <span class="stats-label">搜索耗时:</span>
                <span class="stats-value">{{ pathORAMStats.searchTime }}ms</span>
              </div>
              <div class="stats-arrow">→</div>
            </div>
            <div class="results-list">
              <div 
                    v-for="(result, index) in searchResults" 
                    :key="result.id" 
                    class="result-item"
                    :class="{ 'searching': isSearching && result.id === 'loading' }"
                  >
                <div class="result-header">
                  <!-- <h4 class="result-title">{{ index + 1 }}. {{ result.title }} [{{ result.id }}]</h4> -->
                  <h4 class="result-title">
                   <template v-if="isSearching && result.id === 'loading'">
                        <span class="searching-indicator"></span>
                        搜索中...
                      </template>
                      <template v-else>
                        {{ index + 1 }}. {{ result.title }} [{{ result.id }}]
                      </template>
                    </h4>
                  <div class="result-meta">
                    <span class="coordinates">({{  result.lng || 'N/A' }}, {{ result.lat || 'N/A' }})</span>
                  </div>
                </div>
                <div class="distance-container">
                   <div class="distance-item">
                     <span class="distance-label">综合距离:</span>
                     <span class="distance-value">{{ result.weighted_dist?.toFixed(5) || 'xxx' }}</span>
                   </div>
                   <div class="distance-separator">|</div>
                   <div class="distance-item">
                     <span class="distance-label">空间距离:</span>
                     <span class="distance-value">{{ result.original_dist?.toFixed(2) || 'xxx' }}</span>
                   </div>
                   <div class="distance-separator">|</div>
                   <div class="distance-item">
                     <span class="distance-label">文本距离:</span>
                     <span class="distance-value">{{ result.lev_distance?.toFixed(2) || 'xxx' }}</span>
                   </div>
                   <div class="distance-separator"></div>
                   <!-- <span style="display:inline-block;width:12em;"></span> -->
                   <button class="path-compare-btn-inline" @click="togglePathComparison(index)">
                     {{ result.showPathComparison ? '隐藏路径对比' : 'PathORAM' }}
                   </button>
                 </div>
                <!-- PathORAM路径对比展开区域 -->
                <div v-if="result.showPathComparison" class="path-comparison-section">
                  <div class="path-comparison-header">
                    <h5>PathORAM路径变化对比</h5>
                  </div>
                  <div class="path-comparison-content">
                    <div class="path-before">
                      <h6>搜索前路径结构</h6>
                      <div v-if="result.path_before" class="path-text-container">
                        <div class="path-text">{{formatSinglePath(result.path_before)}}</div>
                        <div class="path-info">
                          <span>深度: {{ Array.isArray(result.path_before) ? result.path_before.length : (result.path_before ? String(result.path_before).split('->').length : 0) }}</span>
                          <!-- <span>节点数: {{ Array.isArray(result.path_before) ? result.path_before.length : 0 }}</span> -->
                        </div>
                      </div>
                      <div v-else class="path-loading">暂无搜索前路径</div>
                    </div>
                    <div class="path-after">
                      <h6>搜索后路径结构</h6>
                      <div v-if="result.path_after" class="path-text-container">
                        <div class="path-text">{{ formatSinglePath(result.path_after) }}</div>
                        <div class="path-info">
                          <!-- <span>深度: {{ Array.isArray(result.path_after) ? result.path_after.length : (result.path_after ? String(result.path_after).split('->').length : 0) }}</span> -->
                          <!-- <span>节点数: {{ Array.isArray(result.path_after) ? result.path_after.length : 0 }}</span> -->
                        </div>
                      </div>
                      <div v-else class="path-loading">暂无搜索后路径</div>
                    </div>
                  </div>
                  <div class="path-stats">
                    <div class="result-chart">
                      <!-- 显示加载状态 -->
                      <div v-if="result.pathLoading" class="path-loading">
                        路径数据加载中...
                      </div>
                      <PathComparisonChart 
                        v-else-if="result.path_before && result.path_after"
                        :key="'path-chart-' + index"
                        :before-path="Array.isArray(result.path_before) ? result.path_before : result.path_before?.split('->').map(Number) || []" 
                        :after-path="Array.isArray(result.path_after) ? result.path_after : result.path_after?.split('->').map(Number) || []" 
                        :height="300"
                        style="width: 100%"
                      />
                      <!-- 数据无效时显示提示 -->
                      <div v-else class="path-loading">
                        等待路径数据...
                      </div>
                    </div>   

                    <!-- <div class="stat-item">
                      <span class="stat-label">节点访问次数:</span>
                      <span class="stat-value">{{ (result.path_before?.access_count ?? 0) + (result.path_after?.access_count ?? 0) }}</span>
                    </div> -->
                    <!-- <div class="stat-item">
                      <span class="stat-label">路径深度变化:</span>
                      <span class="stat-value">{{ ((result.path_after?.depth ?? 0) - (result.path_before?.depth ?? 0)) }}</span>
                    </div>
                    <div class="stat-item">
                      <span class="stat-label">加密操作次数:</span>
                      <span class="stat-value">{{ 0 }}</span>
                    </div> -->
                  </div>
                </div>
              </div>
              <!-- <AccessTimesChart 
                dataType="single" 
                title="单次访问块统计"
                :start="1"
                :end="1000"
                :manualData="accessTimesSnapshot"  
              /> -->
            </div>
          </div>
        </div>
      </div>
    </teleport>
    
    <!-- 节点点击弹窗 - 移到页面最外层 -->
    <teleport to="body">
      <div v-if="popup.show" class="page-popup-mask" @click.self="closePopup">
        <div class="page-popup">
          <div class="popup-header">
            <h4>{{ popup.node?.name }}</h4>
            <button class="popup-close-btn" @click="closePopup">×</button>
          </div>
          <div class="popup-content">
            <div class="desc">{{ popup.node?.desc }}</div>
            <!-- 根据节点类型显示不同组件 -->
            <div v-if="popup.node?.name === '数据预处理与初始化'" class="component-area">
              <h5>IR-Tree结构</h5>
              <IRTreeECharts :key="irTreeKey" />
            </div>
            <div v-else-if="popup.node?.name === 'SGX密钥管理与索引映射'" class="component-area">
              <h5>IR-OBIR关系图</h5>
              <IR_OBIR_RelationSVG :key="irObirKey" />
            </div>
            <div v-else-if="popup.node?.name === '数据加密存储'" class="component-area">
              <h5>存储状态</h5>
              <StorageStatusDisplay />
            </div>
            <div v-else-if="popup.node?.name === '用户加密查询请求'" class="component-area">
              <h5>查询参数</h5>
              <QueryParamDisplay />
            </div>
            <div v-else-if="popup.node?.name === 'SGX查询处理'" class="component-area">
              <h5>逻辑路径</h5>
              <IRLogicPathSVG :key="irLogicPathKey" />
            </div>
            <div v-else-if="popup.node?.name === 'Oblivious访问与剪枝'" class="component-area">
              <h5>访问与剪枝</h5>
              <ObliviousAccessDisplay />
            </div>
            <div v-else-if="popup.node?.name === 'STASH/桶更新与RDT重置'" class="component-area">
              <h5>STASH与RDT</h5>
              <StashRDTDisplay />
            </div>
            <div v-else-if="popup.node?.name === '结果加密返回'" class="component-area">
              <h5>加密返回</h5>
              <ResultEncryptionDisplay />
            </div>
            <div v-else-if="popup.node?.name === '客户端解密与结果呈现'" class="component-area">
              <h5>解密与呈现</h5>
              <QueryResultDisplay :topK="queryParams.topK" :queryKeyword="queryParams.keyword" />
            </div>
            <div v-else class="component-placeholder">
              <!-- 其他节点的组件区域 -->
            </div>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import * as echarts from 'echarts';
import IR_OBIR_RelationSVG from '@/components/IR_OBIR_RelationSVG.vue';
import StorageStatusDisplay from '@/components/StorageStatusDisplay.vue';
import QueryParamDisplay from '@/components/QueryParamDisplay.vue';
import IRLogicPathSVG from '@/components/IRLogicPathSVG.vue';
import ObliviousAccessDisplay from '@/components/ObliviousAccessDisplay.vue';
import StashRDTDisplay from '@/components/StashRDTDisplay.vue';
import ResultEncryptionDisplay from '@/components/ResultEncryptionDisplay.vue';
import QueryResultDisplay from '@/components/QueryResultDisplay.vue';
import TreeChart from '@/components/TreeChart.vue';
import IRTreeECharts from '@/components/IRTreeECharts.vue';
// import { searchAPI } from '../api';
import { mapBackendResultsToFrontend, calculatePathORAMStats, type BackendQueryResult, type FrontendSearchResult } from '../utils/dataMapper';
import AccessTimesChart from '@/components/AccessTimesChart.vue';
import  PathComparisonChart  from '@/components/PathComparisonChart.vue';

const router = useRouter();

function formatSinglePath(path: any): string {
  // 1. 校验是否为有效数组
  if (!Array.isArray(path)) {
    console.warn("路径子项非数组:", path);
    return "路径格式错误";
  }
  if (path.length === 0) {
    return "空路径";
  }

  // 2. 校验是否为纯数字数组（适配后端返回结构）
  const hasInvalidItem = path.some(item => typeof item !== "number" || isNaN(item));
  if (hasInvalidItem) {
    console.warn("路径包含非数字元素:", path);
    return "路径含无效元素";
  }

  // 3. 核心：数字用 "->" 连接（与你要求的格式完全匹配）
  return path.join("->");
}

function formatPath(secondRoundData: any, index: number): {
  path_before: string;
  path_after: string;
} {
  // 初始化默认结果（异常场景提示）
  const defaultResult = {
    path_before: "无有效前置路径",
    path_after: "无有效后置路径"
  };

  console.log("formatPath:", secondRoundData, index);

  // 1. 基础校验：确保传入的是第二轮返回的有效数据
  if (!secondRoundData || typeof secondRoundData !== "object") {
    console.warn("第二轮返回数据格式错误:", secondRoundData);
    return defaultResult;
  }
  if (secondRoundData.status !== "success") {
    console.warn("第二轮接口请求失败:", secondRoundData.status);
    return defaultResult;
  }

  // 2. 提取并格式化 path_before（按索引）
  let formattedBefore = defaultResult.path_before;
  if (Array.isArray(secondRoundData.path_before)) {
    // 校验索引合法性（避免越界）
    if (index >= 0 && index < secondRoundData.path_before.length) {
      const targetBeforePath = secondRoundData.path_before[index];
      formattedBefore = formatSinglePath(targetBeforePath);
    } else {
      formattedBefore = `前置路径索引无效（有效范围：0~${secondRoundData.path_before.length - 1}）`;
    }
  }

  // 3. 提取并格式化 path_after（按索引，逻辑与before一致）
  let formattedAfter = defaultResult.path_after;
  if (Array.isArray(secondRoundData.path_after)) {
    if (index >= 0 && index < secondRoundData.path_after.length) {
      const targetAfterPath = secondRoundData.path_after[index];
      formattedAfter = formatSinglePath(targetAfterPath);
    } else {
      formattedAfter = `后置路径索引无效（有效范围：0~${secondRoundData.path_after.length - 1}）`;
    }
  }

  // 4. 返回最终的路径对（键名与需求一致：path_before/path_after）
  return {
    path_before: formattedBefore,
    path_after: formattedAfter
  };
}

// OBIR-Tree实时路径相关
const obirTreeSVG = ref('');
const obirTreeLoading = ref(true);

// IR-Tree展示相关
const irTreeSVG = ref('');
const irTreeData = ref(null);
const irTreeLoading = ref(false);

// PathORAM统计数据
const pathORAMStats = ref({
  nodeChange: '+12/-8',
  searchTime: 245
});

// // 加载OBIR-Tree SVG
// const loadOBIRTreeSVG = async () => {
//   try {
//     obirTreeLoading.value = true;
//     const response = await fetch('/api/obir-tree-realtime', {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({
//         currentFile: 'obir_tree_current.json',
//         previousFile: 'obir_tree_previous.json'
//       })
//     });
//     if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
//     const result = await response.json();
//     if (result.success) {
//       obirTreeSVG.value = result.svg;
//     } else {
//       throw new Error(result.error || '获取OBIR-Tree数据失败');
//     }
//   } catch (err) {
//     console.error('加载OBIR-Tree SVG失败:', err);
//     obirTreeSVG.value = '';
//   } finally {
//     obirTreeLoading.value = false;
//   }
// };

// // 组件挂载时加载OBIR-Tree数据
// loadOBIRTreeSVG();

// 搜索相关数据
const searchResults = ref<FrontendSearchResult[]>([]);
const resultsExpanded = ref(true);
const isSearching = ref(false); // 标记是否正在搜索
const accessTimesSnapshot = ref<Array<{ block_id: number; accessed_time: number }> | null>(null);
const accessTimesLock = ref(false); // 确保单次获取的原子性

//一阶段访问次数缓存
const captureFirstStageAccessTimes = async () => {
  if (accessTimesLock.value) return;
  accessTimesLock.value = true;
  
  try {
    const response = await fetch(`http://localhost:8080/single-accessed-times?start=${1}&end=${1000}`, {
      method: 'GET'
    });
    
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const result = await response.json();
    
    if (result.status === 'success' && Array.isArray(result.blocks)) {
      accessTimesSnapshot.value = [...result.blocks]; // 深拷贝存储快照
      console.log('已捕获第一阶段访问次数快照');
    }
  } catch (err) {
    console.error('捕获第一阶段访问次数失败:', err);
  } finally {
    accessTimesLock.value = false;
  }
};

// 查询参数
const queryParams = ref({
  topK: 10,
  keyword: ''
});
const irTreeKey = ref(0);
const refreshIRTreeSVG = () => { irTreeKey.value++; };
const irObirKey = ref(0);
const refreshIRObirRelationSVG = () => { irObirKey.value++; };
const irLogicPathKey = ref(0);
const refreshIRLogicPathSVG = () => { irLogicPathKey.value++; };

// 执行第一阶段搜索
const executeFirstStageSearch = async () => {
  try {
    //搜索开始前重置上一次快照
    resetAccessTimesSnapshot();
    // 验证输入参数
    if (!searchText.value.trim()) {
      alert('请输入搜索关键词');
      return;
    }
    
    const longitude = parseFloat(lng.value);
    const latitude = parseFloat(lat.value);
    
    if (isNaN(longitude) || isNaN(latitude)) {
      alert('请输入有效的经纬度坐标');
      return;
    }
    
    console.log('开始第一阶段搜索，参数:', {
      keyword: searchText.value,
      x: longitude,
      y: latitude,
      k: queryParams.value.topK,
    });
    
// 2. 先显示浮窗并标记为搜索中
    isSearching.value = true;
    // 确保有至少一个空结果来触发浮窗显示
    if (searchResults.value.length === 0) {
      searchResults.value = [{
        title: '搜索中...',
        description: '正在获取结果，请稍候',
        lng: longitude,
        lat: latitude,
        original_dist: 0,
        weighted_dist: 0,
        lev_distance: 0,
        id: 0,
        showPathComparison: false,
        path_before: null,
        path_after: null
      }];
    }

    // 构建URL参数 - 根据接口文档使用GET方法和URL参数
    const params = new URLSearchParams({
      keyword: searchText.value,
      x: longitude.toString(),
      y: latitude.toString(),
      k: queryParams.value.topK.toString()
    });
    
    // 调用第一阶段查询API - 使用GET方法
    const response = await fetch(`http://localhost:8080/first-stage?${params}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();

    // 第一阶段完成后立即捕获访问次数快照
    await captureFirstStageAccessTimes();

    isSearching.value = false;
    console.log('第一阶段查询结果:', result);
    
    if (result.status === 'success') {
      // 解析第一阶段结果 - 根据接口文档的响应格式
      const { cacheKey, time_cost, initialResults } = result;
      
      // 存储cacheKey用于第二阶段查询
      window.currentCacheKey = cacheKey;
      
      // 处理搜索结果并显示在浮窗中 - 根据接口文档的数据结构
      const processedResults = initialResults.map((item, index) => ({
        title: item.keyword || searchText.value,
        description: `搜索结果 ${index + 1}`,
        lng: item.center_x || longitude,
        lat: item.center_y || latitude,
        x: item.center_x || longitude,
        y: item.center_y || latitude,
        // 根据接口文档，第一阶段返回的是weighted_dist, original_dist, lev_distance
        original_dist: item.original_dist || 0,
        weighted_dist: item.weighted_dist || 0,
        lev_distance: item.lev_distance || 0,
        id: item.rect_id || 'N/A',
        showPathComparison: false,
        path_before: null,
        path_after: null,
        pathLoading: false // 初始化加载状态
      }));
      
      searchResults.value = processedResults;
      
      // 更新PathORAM统计信息
      pathORAMStats.value = {
        nodeChange: '+12/-8',
        searchTime: time_cost || 245
      };
      
      console.log('第一阶段搜索成功！找到', processedResults.length, '个结果');
      console.log('缓存键:', cacheKey);
      
      // 自动执行第二阶段查询
      if (cacheKey) {
        await executeSecondStageSearch(cacheKey);
      }
      
    } else {
      console.error('第一阶段搜索失败:', result.error);
      alert(`搜索失败: ${result.error || '未知错误'}`);
    }
  } catch (err) {
    console.error('第一阶段搜索失败:', err);
    const errorMessage = err instanceof Error ? err.message : '搜索过程中发生未知错误';
    alert(`搜索失败: ${errorMessage}`);
  }
};

//重置快照
const resetAccessTimesSnapshot = () => {
  accessTimesSnapshot.value = null; // 清空快照
};

// 执行第二阶段搜索
const executeSecondStageSearch = async (cacheKey) => {
  try {
    if (!cacheKey || cacheKey.trim() === '') {
      console.error('缓存键为空，无法执行第二阶段搜索');
      return;
    }
    // 确保第一阶段快照已捕获
    if (!accessTimesSnapshot.value) {
      console.warn('等待第一阶段访问次数快照捕获完成');
      await new Promise(resolve => {
        const check = setInterval(() => {
          if (accessTimesSnapshot.value || !accessTimesLock.value) {
            clearInterval(check);
            resolve(true);
          }
        }, 50);
      });
    }
    searchResults.value.forEach(item => {
      item.pathLoading = true;
    });
    const trimmedKey = cacheKey.trim();
    const url = `http://localhost:8080/second-stage?cacheKey=${encodeURIComponent(trimmedKey)}`;
    console.log('第二阶段请求URL:', url);
    // 不加Content-Type头
    const response = await fetch(url, {
      method: 'GET'
    });
    if (!response.ok) {
      const errorText = await response.text();
      console.error('第二阶段API响应错误:', response.status, errorText);
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
    }
    const result = await response.json();
    console.log('第二阶段查询结果:', result);
    if (result.status === 'success') {
      const { path_before, path_after } = result;
      searchResults.value.forEach((item, idx) => {
        item.path_before = Array.isArray(path_before) ? path_before[idx] : null;
        item.path_after = Array.isArray(path_after) ? path_after[idx] : null;
        item.pathLoading = false; // 加载完成
      });
      console.log('第二阶段搜索成功！');
      console.log('搜索前路径:', path_before);
      console.log('搜索后路径:', path_after);
    } else {
      console.error('第二阶段搜索失败:', result.error || result.message || '未知错误');
      searchResults.value.forEach(item => {
        item.pathLoading = false;
      });
    }
  } catch (err) {
    searchResults.value.forEach(item => {
      item.pathLoading = false;
    });
    console.error('第二阶段搜索失败:', err);
    const errorMessage = err instanceof Error ? err.message : '第二阶段搜索过程中发生未知错误';
    console.error('详细错误信息:', errorMessage);
  }
};

// 执行搜索 - 功能已移除
const executeSearch = async () => {
  // 功能已移除
};

// 关闭搜索结果浮窗
const closeSearchResults = () => {
  searchResults.value = [];
};

// 跳转到OBIR-Tree展示页面
const goToOBIRTreePage = () => {
  router.push('/obir-tree-display');
};

// IR-Tree数据加载（改用统一接口，无兜底）
const loadIRTree = async () => {
  // 功能已移除
};

// 切换PathORAM路径对比显示（直接读取结果中的path_before/path_after）
const togglePathComparison = async (index: number) => {
  if (searchResults.value[index]) {
    searchResults.value[index].showPathComparison = !searchResults.value[index].showPathComparison;
  }
};

// 更新OBIR-Tree实时路径
const updateOBIRTreePath = async () => {
  // 功能已移除
};

const lng = ref('');
const lat = ref('');
const searchText = ref('');
const showOnMap = () => {
  const longitude = parseFloat(lng.value);
  const latitude = parseFloat(lat.value);
  if (isNaN(longitude) || isNaN(latitude)) {
    alert('请输入有效的经纬度');
    return;
  }
  router.push({
    path: '/project-search/map',
    query: {
      lng: longitude,
      lat: latitude
    }
  });
};
// 拉伸后的贝塞尔曲线节点分布
function cubicBezier(t, p0, p1, p2, p3) {
  const x = Math.pow(1-t,3)*p0.x + 3*Math.pow(1-t,2)*t*p1.x + 3*(1-t)*t*t*p2.x + t*t*t*p3.x;
  const y = Math.pow(1-t,3)*p0.y + 3*Math.pow(1-t,2)*t*p1.y + 3*(1-t)*t*t*p2.y + t*t*t*p3.y;
  return {x, y};
}
const bezierPoints = [
  {x: 75, y: 260}, // 起点左移，延长左边线条
  {x: 265, y: 80}, // 控制点1
  {x: 945, y: 340}, // 控制点2
  {x: 1145, y: 120}  // 终点
];
const nodeCount = 9;
// 节点分布在中间，间距自动拉开
const mindmapNodes = Array.from({length: nodeCount}, (_, i) => {
  const t = (i+1)/(nodeCount+1); // 节点分布在(0,1)之间的等分点，避开首尾延伸段
  const {x, y} = cubicBezier(t, bezierPoints[0], bezierPoints[1], bezierPoints[2], bezierPoints[3]);
  const colorList = ['#f8f3d4','#e0f7fa','#ffe0b2','#dcedc8','#f3e5f5','#fff9c4','#b2ebf2','#ffcdd2','#c8e6c9'];
  const names = [
    '数据预处理与初始化',
    'SGX密钥管理与索引映射',
    '数据加密存储',
    '用户加密查询请求',
    'SGX查询处理',
    'Oblivious访问与剪枝',
    'STASH/桶更新与RDT重置',
    '结果加密返回',
    '客户端解密与结果呈现'
  ];
  const descs = [
    '客户端准备空间文本数据，分块加密，构建IR-tree索引，生成映射关系，上传加密数据和密钥。',
    'SGX远程证明，密钥解密，IR-tree映射为OBIR-tree，分配物理路径，虚拟块填充，生成加密RDT。',
    'EDB存储加密数据块、RDT、虚拟块，隐藏真实分布，元数据公开但内容安全。',
    '客户端加密查询参数，发送至云端，SGX验证合法性以及解密之后使用IR-Tree元数据得到逻辑路径。',
    'SGX解密查询参数，获取目标路径，准备Oblivious访问。',
    'SGX读取加密块，解密RDT，筛选高相关节点，剪枝无关节点。',
    '目标节点暂存STASH，非目标节点重加密写回，虚拟块填充，RDT重置并加密写回EDB。',
    'SGX用客户端公钥加密结果，发送至客户端。',
    '客户端用私钥解密，提取原始数据，展示最终结果。'
  ];
  return {
    name: names[i],
    desc: descs[i],
    x,
    y,
    color: colorList[i]
  };
});
const tooltip = ref({ show: false, x: 0, y: 0, text: '' });
function showTooltip(e, node) {
  tooltip.value = {
    show: true,
    x: e.clientX + 10,
    y: e.clientY + 10,
    text: node.desc
  };
}
function hideTooltip() {
  tooltip.value.show = false;
}
function onSvgMouseMove(e) {
  if (tooltip.value.show) {
    tooltip.value.x = e.clientX + 10;
    tooltip.value.y = e.clientY + 10;
  }
}
const popup = ref({ show: false, node: null });

function onNodeClick(node) {
  popup.value = { show: true, node };
}

function closePopup() {
  popup.value = { show: false, node: null };
}

</script>

<style>
.data-display-container {
  padding: 10px 15px; /* 减少内边距，使边框更贴近导航栏 */
  display: flex;
  flex-direction: column;
  gap: 15px; /* 减少组件间距 */
  min-height: 600px;
  width: 100%;
  box-sizing: border-box;
}
.section {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  padding: 20px; /* 减少section内边距 */
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.section:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
}
h3 {
  color: #444;
  margin-top: 0;
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}
.obir-tree-container {
  min-height: 320px;
}
.tree-placeholder, .graph-placeholder {
  border: 1px dashed #ccc;
  transition: all 0.3s ease;
}
.tree-placeholder:hover, .graph-placeholder:hover {
  border-color: #42b983;
  background-color: #f5fff8;
}
.tree-placeholder {
  height: 250px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: #f9f9f9;
  border-radius: 8px;
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
}

.tree-placeholder:hover {
  background-color: #f0f8ff;
  border-color: #4CAF50;
}

.obir-tree-svg {
  max-width: 100%;
  max-height: 200px;
  overflow: hidden;
}

.obir-tree-svg svg {
  max-width: 100%;
  max-height: 100%;
}

.obir-tree-loading, .obir-tree-error {
  text-align: center;
  color: #666;
}

.obir-tree-loading p, .obir-tree-error p {
  margin: 0;
  font-size: 16px;
}

.obir-tree-error {
  color: #f44336;
}
.blank-image {
  max-width: 100%;
  max-height: 100%;
  opacity: 0.5;
}
.search-bar {
  padding: 15px 25px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4eaf5 100%);
}
.search-container {
  display: flex;
  gap: 12px;
  align-items: center;
  max-width: 1000px;
  width: 100%;
  margin: 0 auto;
}
.search-input {
  flex: 1;
  padding: 12px 18px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
}
.search-button {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  font-size: 1rem;
  background-color: #42b983;
  color: white;
  transition: all 0.2s ease;
}
.search-button:hover {
  background-color: #359469;
}
.process-node-graph {
  min-height: 300px;
}
.graph-placeholder {
  position: relative;
  width: 100%;
  min-height: 220px;
  background: linear-gradient(90deg, #f8f3d4 0%, #e0f7fa 100%);
  border-radius: 16px;
  box-shadow: 0 2px 12px #eee;
  margin-top: 8px;
}
.coord-input {
  width: 180px;
  flex: none;
}
.svg-tooltip {
  position: fixed;
  z-index: 99;
  background: rgba(50,50,50,0.95);
  color: #fff;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 15px;
  pointer-events: none;
  max-width: 320px;
  box-shadow: 0 2px 8px #888;
  white-space: pre-line;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.page-popup-mask {
  position: fixed !important;
  left: 0 !important; 
  top: 0 !important; 
  right: 0 !important; 
  bottom: 0 !important;
  background: rgba(0,0,0,0.25);
  z-index: 999999 !important;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: auto;
  transform-style: preserve-3d;
  backface-visibility: hidden;
}
.page-popup {
  position: relative !important;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  padding: 32px 36px 24px 36px;
  min-width: 500px;
  max-width: 90vw;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 1000000 !important;
  transform: translateZ(0);
  will-change: transform;
}
.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}
.popup-header h4 {
  margin: 0;
  font-size: 22px;
  color: #333;
  font-weight: 600;
}
.popup-content {
  flex: 1;
  overflow-y: auto;
}
.popup-close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}
.popup-close-btn:hover {
  background: #f0f0f0;
  color: #666;
}
.component-placeholder {
  margin-top: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 2px dashed #dee2e6;
  text-align: center;
  color: #6c757d;
  font-size: 14px;
  min-height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.component-area {
  margin-top: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #dee2e6;
  min-height: 300px;
}

.component-area h5 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

/* 搜索结果浮窗样式 */
.search-results-popup-mask {
  position: fixed !important;
  left: 0 !important;
  top: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999998 !important;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: auto;
}

.search-results-popup {
  position: relative !important;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  padding: 32px 36px 24px 36px;
  min-width: 1000px;
  max-width: 90vw;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 999999 !important;
}

.search-results-popup .popup-content {
  max-height: 70vh;
  overflow-y: auto;
}

.obir-tree-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.obir-tree-section h5 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.obir-tree-section .tree-placeholder {
  height: 200px;
  border: 1px dashed #ccc;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f9f9f9;
  cursor: pointer;
  transition: all 0.3s ease;
}

.obir-tree-section .tree-placeholder:hover {
  background-color: #f0f8ff;
  border-color: #4CAF50;
}

.obir-tree-section .obir-tree-svg {
  max-width: 100%;
  max-height: 180px;
  overflow: hidden;
}

.obir-tree-section .obir-tree-svg svg {
  max-width: 100%;
  max-height: 100%;
}

/* IR-Tree展示区域样式 */
.tree-display-area {
  min-height: 300px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.ir-tree-svg {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ir-tree-svg svg {
  max-width: 100%;
  max-height: 100%;
}

.ir-tree-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 16px;
}

.ir-tree-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.ir-tree-placeholder:hover {
  background-color: #f0f8ff;
  color: #4CAF50;
}

/* PathORAM统计横条样式 */
.pathoram-stats-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  margin-bottom: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.pathoram-stats-bar:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.stats-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stats-label {
  font-size: 12px;
  opacity: 0.9;
  margin-bottom: 2px;
}

.stats-value {
  font-size: 16px;
  font-weight: bold;
}

.stats-arrow {
  font-size: 20px;
  font-weight: bold;
  opacity: 0.8;
}

/* PathORAM路径变化展示样式 */
.pathoram-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.pathoram-section h5 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.section-description {
  margin: 0 0 20px 0;
  color: #666;
  font-size: 14px;
}

.pathoram-comparison {
  display: flex;
  gap: 20px;
  min-height: 300px;
}

.pathoram-before,
.pathoram-after {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.pathoram-before h6,
.pathoram-after h6 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 14px;
  font-weight: 600;
  text-align: center;
}

.pathoram-display {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.pathoram-svg {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pathoram-svg svg {
  max-width: 100%;
  max-height: 100%;
}

.pathoram-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 14px;
}

.pathoram-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pathoram-placeholder:hover {
  background-color: #f0f8ff;
  color: #4CAF50;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.result-item {
  background: linear-gradient(135deg, #ffffff, #f8f9fa);
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  position: relative;
}

.result-item:hover {
  background: linear-gradient(135deg, #ffffff, #f0f8ff);
  border-color: #4CAF50;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.15);
  transform: translateY(-2px);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.result-title {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 700;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.result-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

.relevance {
  color: #4CAF50;
  font-weight: 700;
  font-size: 14px;
  background: rgba(76, 175, 80, 0.1);
  padding: 2px 8px;
  border-radius: 12px;
}

.distance-info {
  color: #1e293b;
  font-size: 13px;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  font-weight: 500;
  line-height: 1.4;
}

.coordinates {
   color: #10b981;
   font-size: 13px;
   font-family: 'Courier New', monospace;
   font-weight: 600;
 }

 .location-info {
   color: #666;
   font-size: 12px;
   font-style: italic;
 }

 /* 距离容器样式 */
 .distance-container {
   display: flex;
   align-items: center;
   justify-content: flex-start;
   gap: 8px;
   margin: 10px 0;
   padding: 12px 16px;
   background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
   border: 1px solid #cbd5e1;
   border-radius: 8px;
   box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
 }

 .distance-item {
   display: flex;
   align-items: center;
   gap: 4px;
 }

 .distance-label {
   font-size: 13px;
   color: #1e293b;
   font-weight: 500;
 }

 .distance-value {
   font-size: 13px;
   color: #0f172a;
   font-weight: 600;
   font-family: 'Courier New', monospace;
 }

 .distance-separator {
   color: #64748b;
   font-weight: bold;
   margin: 0 4px;
 }

 /* PathORAM按钮内联样式 */
 .path-compare-btn-inline {
   background: linear-gradient(135deg, #10b981 0%, #059669 100%);
   color: white;
   border: none;
   padding: 6px 12px;
   border-radius: 6px;
   font-size: 12px;
   font-weight: 500;
   cursor: pointer;
   transition: all 0.2s ease;
   box-shadow: 0 1px 3px rgba(16, 185, 129, 0.3);
   margin-left: auto;
 }

 .path-compare-btn-inline:hover {
   background: linear-gradient(135deg, #059669 0%, #047857 100%);
   transform: translateY(-1px);
   box-shadow: 0 2px 6px rgba(16, 185, 129, 0.4);
   margin-left: auto;
 }
 
 .result-description {
  margin: 0 0 15px 0;
  color: #555;
  line-height: 1.6;
  font-size: 14px;
  background: rgba(0, 0, 0, 0.02);
  padding: 10px;
  border-radius: 6px;
  border-left: 3px solid #4CAF50;
}

.result-footer {
  position: relative;
  min-height: 35px;
}

/* PathORAM按钮右下角样式 */
.path-compare-btn-corner {
  position: absolute;
  bottom: 0;
  right: 0;
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px 0 8px 0;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(76, 175, 80, 0.3);
}

.path-compare-btn-corner:hover {
  background: linear-gradient(135deg, #45a049, #4CAF50);
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(76, 175, 80, 0.4);
}

/* PathORAM路径对比展开区域样式 */
.path-comparison-section {
  margin-top: 15px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.path-comparison-header h5 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
  text-align: center;
}

.path-comparison-content {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.path-before,
.path-after {
  flex: 1;
}

.path-before h6,
.path-after h6 {
  margin: 0 0 10px 0;
  color: #555;
  font-size: 14px;
  font-weight: 600;
  text-align: center;
}

.path-text-container {
  min-height: 100px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background-color: white;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow: visible;
}

.path-text {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  color: #333;
  background-color: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #e9ecef;
  word-break: break-all;
}

.path-info {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #666;
}

.path-info span {
  background-color: #e9ecef;
  padding: 4px 8px;
  border-radius: 3px;
}

.path-loading {
  color: #999;
  font-style: italic;
  text-align: center;
  padding: 20px;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.path-stats {
  display: flex;
  gap: 20px;
  justify-content: space-around;
  padding: 10px;
  background-color: white;
  border-radius: 6px;
  border: 1px solid #ddd;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

@media (max-width: 768px) {
  .path-comparison-content {
    flex-direction: column;
    gap: 15px;
  }
  
  .path-stats {
    flex-direction: column;
    gap: 10px;
  }
}
  .path-text {
    /* 1. 固定宽度 */
    width: 400px;
    
    /* 3. 基础样式优化 */
    padding: 8px 0;
    line-height: 1.6;
    /* font-family: monospace; */
  }

  .access-times-chart-wrapper {
  width: 100%;
  height: 400px; /* 明确指定高度 */
  min-height: 300px;
  }

    /* 搜索中状态样式 */
  .searching-indicator {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 3px solid rgba(76, 175, 80, 0.3);
    border-radius: 50%;
    border-top-color: #4CAF50;
    animation: spin 1s ease-in-out infinite;
    margin-right: 8px;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .result-item.searching {
    background: linear-gradient(135deg, #f0f8ff 0%, #e8f4f8 100%);
  }

.result-chart {
  margin: 12px 0;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #eee;
  width: 100%;
}
</style>