<template>
  <div class="search-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>OBIR-Tree 空间关键词搜索</h2>
      <p class="page-description">基于隐私保护的空间关键词查询系统</p>
    </div>

    <!-- 搜索控制面板 -->
    <div class="search-panel">
      <el-card class="search-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>搜索参数设置</span>
            <el-button type="primary" :loading="searching" disabled>
              <el-icon><Search /></el-icon>
              {{ searching ? '搜索中...' : '执行搜索' }}
            </el-button>
          </div>
        </template>
        
        <el-form :model="searchForm" label-width="120px" class="search-form">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="关键词">
                <el-input 
                  v-model="searchForm.keyword" 
                  placeholder="请输入搜索关键词"
                  @keyup.enter=""
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="返回结果数">
                <el-input-number 
                  v-model="searchForm.topK" 
                  :min="1" 
                  :max="20" 
                  controls-position="right"
                />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="查询模式">
                <el-select v-model="searchForm.queryMode" placeholder="选择查询模式">
                  <el-option label="基础查询" value="basic" />
                  <el-option label="扩展查询" value="extended" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="经度">
                <el-input-number 
                  v-model="searchForm.lng" 
                  :precision="6"
                  :step="0.001"
                  controls-position="right"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="纬度">
                <el-input-number 
                  v-model="searchForm.lat" 
                  :precision="6"
                  :step="0.001"
                  controls-position="right"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="快速定位">
                <el-select v-model="selectedLocation" @change="setLocation" placeholder="选择城市">
                  <el-option label="北京" :value="{lng: 116.3074, lat: 39.9042}" />
                  <el-option label="上海" :value="{lng: 121.4737, lat: 31.2304}" />
                  <el-option label="广州" :value="{lng: 113.2644, lat: 23.1291}" />
                  <el-option label="深圳" :value="{lng: 114.0579, lat: 22.5431}" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </el-card>
    </div>

    <!-- 搜索结果展示区域 -->
    <div class="results-section" v-if="searchResults.length > 0 || searchError">
      <!-- 错误信息 -->
      <el-alert 
        v-if="searchError" 
        :title="searchError" 
        type="error" 
        show-icon 
        :closable="false"
        class="error-alert"
      />
      
      <!-- 搜索结果 -->
      <el-card v-if="searchResults.length > 0" class="results-card" shadow="hover">
        <template #header>
          <div class="results-header">
            <span>搜索结果</span>
            <div class="results-info">
              <el-tag type="info">关键词: {{ lastSearchKeyword }}</el-tag>
              <el-tag type="success">{{ searchResults.length }} 条结果</el-tag>
              <el-tag type="warning">{{ searchTime }}</el-tag>
            </div>
          </div>
        </template>
        
        <div class="results-list">
          <div v-for="(result, index) in searchResults" :key="index" class="result-item">
            <!-- 结果文本内容 -->
            <div class="result-content">
              <div class="result-keyword">
                <div class="keyword-label">结果文本</div>
                <div class="keyword-value">{{ result.keyword || lastSearchKeyword || '无' }}</div>
              </div>
            </div>
            
            <!-- 坐标信息 - 移到右上角 -->
            <div class="result-coordinates-corner">
              <div class="coord-value">
                <span class="coord-item">{{ result.x ?? 'N/A' }}, {{ result.y ?? 'N/A' }}</span>
              </div>
            </div>
            
            <!-- 距离信息和PathORAM按钮 - 放在同一行 -->
            <div class="result-distance-and-actions">
              <div class="result-distance">
                <div class="distance-label">距离信息</div>
                <div class="distance-value">
                  <div class="distance-item comprehensive">
                    <span class="label">综合距离:</span>
                    <span class="value">{{ result.distance?.toFixed(4) || 'N/A' }}单位</span>
                  </div>
                  <div class="distance-item spatial">
                    <span class="label">空间距离:</span>
                    <span class="value">{{ result.geo_distance_km || result.spatial_distance || 'N/A' }}km</span>
                  </div>
                  <div class="distance-item textual">
                    <span class="label">文本距离:</span>
                    <span class="value">{{ result.text_distance || 'N/A' }}</span>
                  </div>
                </div>
              </div>
              
              <!-- PathORAM路径对比查看按钮 -->
              <div class="result-actions">
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="showPathORAMInfo(result, index)"
                >
                  PathORAM路径对比查看
                </el-button>
              </div>
            </div>

            <!-- PathORAM路径对比预览 -->
            <div class="path-comparison-preview" v-if="twoRoundResults?.pathComparisons?.[index]">
              <div class="path-preview-header">
                <span class="path-preview-title">PathORAM路径对比预览</span>
                <el-tag 
                  :type="twoRoundResults.pathComparisons[index].isIdentical ? 'success' : 'warning'"
                  size="small"
                >
                  {{ twoRoundResults.pathComparisons[index].isIdentical ? '路径相同' : '路径不同' }}
                </el-tag>
              </div>
              <div class="path-preview-content">
                <div class="path-row">
                  <span class="path-label">第一轮路径:</span>
                  <span class="path-value">
                    [{{ twoRoundResults.pathComparisons[index].firstRoundPath.slice(0, 8).join(', ') }}
                    <span v-if="twoRoundResults.pathComparisons[index].firstRoundPath.length > 8">...</span>]
                  </span>
                  <span class="path-length">(长度: {{ twoRoundResults.pathComparisons[index].firstRoundPath.length }})</span>
                </div>
                <div class="path-row">
                  <span class="path-label">第二轮路径:</span>
                  <span class="path-value">
                    [{{ twoRoundResults.pathComparisons[index].secondRoundPath.slice(0, 8).join(', ') }}
                    <span v-if="twoRoundResults.pathComparisons[index].secondRoundPath.length > 8">...</span>]
                  </span>
                  <span class="path-length">(长度: {{ twoRoundResults.pathComparisons[index].secondRoundPath.length }})</span>
                </div>
                <div class="path-row" v-if="twoRoundResults.pathComparisons[index].differences.length > 0">
                  <span class="path-label">差异位置:</span>
                  <span class="path-differences">
                    {{ twoRoundResults.pathComparisons[index].differences.slice(0, 10).join(', ') }}
                    <span v-if="twoRoundResults.pathComparisons[index].differences.length > 10">...</span>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- IR-Tree结构可视化 -->
    <div class="tree-visualization-section">
      <IRTreeVisualization 
        :auto-load="true" 
        @node-selected="handleNodeSelected" 
        @tree-loaded="handleTreeLoaded"
      />
    </div>

    <!-- PathORAM路径信息弹窗 -->
    <el-dialog 
      v-model="pathDialogVisible" 
      title="PathORAM路径对比详情" 
      width="90%"
      :before-close="closePathDialog"
    >
      <div class="path-dialog-content" v-if="selectedResult && selectedResultIndex !== null">
        <!-- 结果基本信息 -->
        <div class="result-basic-info">
          <h3>查询结果信息</h3>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">关键词:</span>
              <span class="info-value">{{ selectedResult.keyword || lastSearchKeyword || '无' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">坐标:</span>
              <span class="info-value">{{ selectedResult.x ?? 'N/A' }}, {{ selectedResult.y ?? 'N/A' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">综合距离:</span>
              <span class="info-value">{{ selectedResult.distance?.toFixed(4) || 'N/A' }}单位</span>
            </div>
            <div class="info-item">
              <span class="info-label">空间距离:</span>
              <span class="info-value">{{ selectedResult.geo_distance_km || selectedResult.spatial_distance || 'N/A' }}km</span>
            </div>
          </div>
        </div>

        <!-- PathORAM路径对比信息 -->
        <div class="path-comparison-detail" v-if="twoRoundResults?.pathComparisons?.[selectedResultIndex]">
          <h3>PathORAM路径对比分析</h3>
          
          <!-- 路径对比概览 -->
          <div class="path-overview">
            <div class="overview-item">
              <span class="overview-label">路径比较结果:</span>
              <el-tag 
                :type="twoRoundResults.pathComparisons[selectedResultIndex].isIdentical ? 'success' : 'warning'"
                size="large"
              >
                {{ twoRoundResults.pathComparisons[selectedResultIndex].isIdentical ? '路径完全相同' : '路径存在差异' }}
              </el-tag>
            </div>
            <div class="overview-item">
              <span class="overview-label">第一轮路径长度:</span>
              <span class="overview-value">{{ twoRoundResults.pathComparisons[selectedResultIndex].firstRoundPath.length }}</span>
            </div>
            <div class="overview-item">
              <span class="overview-label">第二轮路径长度:</span>
              <span class="overview-value">{{ twoRoundResults.pathComparisons[selectedResultIndex].secondRoundPath.length }}</span>
            </div>
            <div class="overview-item" v-if="!twoRoundResults.pathComparisons[selectedResultIndex].isIdentical">
              <span class="overview-label">差异位置数量:</span>
              <span class="overview-value">{{ twoRoundResults.pathComparisons[selectedResultIndex].differences.length }}</span>
            </div>
          </div>

          <!-- 详细路径信息 -->
          <div class="path-details">
            <div class="path-section">
              <h4>第一轮查询路径</h4>
              <div class="path-content">
                <div class="path-array">
                  [{{ twoRoundResults.pathComparisons[selectedResultIndex].firstRoundPath.join(', ') }}]
                </div>
              </div>
            </div>

            <div class="path-section">
              <h4>第二轮查询路径</h4>
              <div class="path-content">
                <div class="path-array">
                  [{{ twoRoundResults.pathComparisons[selectedResultIndex].secondRoundPath.join(', ') }}]
                </div>
              </div>
            </div>

            <!-- 差异分析 -->
            <div class="path-section" v-if="!twoRoundResults.pathComparisons[selectedResultIndex].isIdentical">
              <h4>路径差异分析</h4>
              <div class="differences-content">
                <div class="differences-list">
                  <div class="difference-label">差异位置索引:</div>
                  <div class="difference-values">
                    {{ twoRoundResults.pathComparisons[selectedResultIndex].differences.join(', ') }}
                  </div>
                </div>
                <div class="differences-explanation">
                  <p>以上位置表示两轮查询在PathORAM访问路径中的不同索引位置。</p>
                  <p>路径差异可能由于查询时间、系统状态或随机化策略的不同而产生。</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 第二轮查询结果 -->
        <div class="second-round-results" v-if="twoRoundResults?.secondRoundResults">
          <h3>第二轮查询结果</h3>
          <div class="second-results-list">
            <div v-for="(result, index) in twoRoundResults.secondRoundResults" :key="index" class="second-result-item">
              <div class="second-result-info">
                <span class="result-index">#{{ index + 1 }}</span>
                <span class="result-keyword">{{ result.keyword || '无' }}</span>
                <span class="result-coords">({{ result.x ?? 'N/A' }}, {{ result.y ?? 'N/A' }})</span>
                <span class="result-distance">距离: {{ result.distance?.toFixed(4) || 'N/A' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closePathDialog">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Search } from '@element-plus/icons-vue';
import PathORAMPathDialog from '../components/PathORAMPathDialog.vue';
import IRTreeVisualization from '../components/IRTreeVisualization.vue';
import { twoRoundSearch, type SearchParams, type TwoRoundSearchResult } from '../api/search';

// 搜索表单数据
const searchForm = reactive({
  keyword: '',
  topK: 10,
  lng: 120.15958,
  lat: 30.28745,
  queryMode: 'basic'
});

// 快速定位选择
const selectedLocation = ref(null);

// 搜索状态
const searching = ref(false);
const searchResults = ref([]);
const searchError = ref('');
const lastSearchKeyword = ref('');
const searchTime = ref('');

// 两轮查询结果数据
const twoRoundResults = ref<TwoRoundSearchResult | null>(null);

// PathORAM路径对话框
const pathDialogVisible = ref(false);
const selectedTargetId = ref('');
const selectedResult = ref(null);
const selectedResultIndex = ref<number | null>(null);

// 设置位置
const setLocation = (location: any) => {
  if (location) {
    searchForm.lng = location.lng;
    searchForm.lat = location.lat;
  }
};

// 执行搜索 - 功能已移除
const executeSearch = async () => {
  // 功能已移除
};

// 显示PathORAM路径信息 - 功能已移除
const showPathORAMInfo = (result: any, index: number) => {
  // 功能已移除
};

// 关闭PathORAM路径对话框
const closePathDialog = () => {
  pathDialogVisible.value = false;
  selectedResult.value = null;
  selectedResultIndex.value = null;
  selectedTargetId.value = '';
};

// 处理IR-Tree节点选择 - 功能已移除
const handleNodeSelected = (node: any) => {
  // 功能已移除
};

// 处理IR-Tree加载完成 - 功能已移除
const handleTreeLoaded = (stats: any) => {
  // 功能已移除
};

// 页面加载时不再执行搜索
onMounted(() => {
  // 搜索功能已移除
});
</script>

<style scoped>
.search-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h2 {
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 28px;
  font-weight: 600;
}

.page-description {
  color: #7f8c8d;
  font-size: 16px;
  margin: 0;
}

.search-panel {
  margin-bottom: 30px;
}

.search-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #2c3e50;
}

.search-form {
  margin-top: 20px;
}

.results-section {
  margin-top: 20px;
}

.tree-visualization-section {
  margin-top: 30px;
  margin-bottom: 20px;
}

.error-alert {
  margin-bottom: 20px;
}

.results-card {
  border-radius: 12px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #2c3e50;
}

.results-info {
  display: flex;
  gap: 10px;
}

.results-list {
  margin-top: 20px;
}

.result-item {
  position: relative;
  display: flex;
  align-items: flex-start;
  padding: 20px;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  margin-bottom: 15px;
  background: #fafbfc;
  transition: all 0.3s ease;
  gap: 20px;
}

.result-item:hover {
  background: #f0f9ff;
  border-color: #3b82f6;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

/* 左侧样式 */
.result-left {
  flex-shrink: 0;
  width: 200px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.result-rank {
  display: flex;
  align-items: center;
  gap: 10px;
}

.rank-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  font-weight: 600;
  font-size: 14px;
}

.rank-label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.result-keyword {
  padding: 8px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #007bff;
}

.keyword-label {
  font-size: 11px;
  color: #666;
  margin-bottom: 4px;
  font-weight: 500;
}

.keyword-value {
  font-size: 13px;
  color: #333;
  font-weight: 600;
}

/* 坐标信息 - 右上角样式 */
.result-coordinates-corner {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 8px;
  background: rgba(21, 87, 36, 0.15);
  border: 1px solid #155724;
  border-radius: 12px;
  font-size: 11px;
  color: #155724;
  font-family: 'Courier New', monospace;
  font-weight: 600;
}

.result-coordinates-corner .coord-value {
  display: flex;
  align-items: center;
}

.result-coordinates-corner .coord-item {
  font-size: 11px;
  color: #155724;
  font-family: 'Courier New', monospace;
  font-weight: 600;
}

.result-coordinates {
  padding: 8px;
  background: #f1f3f4;
  border-radius: 6px;
  border-left: 3px solid #28a745;
}

.coord-label {
  font-size: 11px;
  color: #666;
  margin-bottom: 6px;
  font-weight: 500;
}

.coord-value {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.coord-item {
  font-size: 11px;
  color: #555;
  font-family: 'Courier New', monospace;
}

/* 中间内容样式 */
.result-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-right: 120px; /* 为右上角坐标留出空间 */
}

/* 右侧样式 */
.result-right {
  flex-shrink: 0;
  width: 150px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* 坐标信息样式 - 右上角显示 */
.result-coordinates-corner {
  position: absolute;
  top: 15px;
  right: 15px;
  color: #10b981;
  font-size: 13px;
  font-weight: 600;
  font-family: 'Courier New', monospace;
}

.coord-value {
  display: flex;
  align-items: center;
  gap: 4px;
}

.coord-item {
  font-family: 'Courier New', monospace;
}

/* 距离信息和按钮的容器 */
.result-distance-and-actions {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  margin-top: 10px;
}

.result-distance {
  flex: 1;
  padding: 15px;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-radius: 12px;
  border: 1px solid #cbd5e1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.distance-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 8px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.distance-value {
  font-size: 14px;
  color: #1e293b;
  font-weight: 500;
  line-height: 1.5;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.distance-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  font-size: 13px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.distance-item .label {
  color: #64748b;
  font-weight: 500;
}

.distance-item .value {
  color: #1e293b;
  font-weight: 600;
  font-family: 'Courier New', monospace;
}

.distance-item.comprehensive {
  border-color: #3b82f6;
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
}

.distance-item.spatial {
  border-color: #10b981;
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
}

.distance-item.textual {
  border-color: #f59e0b;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
}

/* Actions样式 */
.result-actions {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100px;
}

.result-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.title-text {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  flex: 1;
}

.relevance-score {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  margin-left: 10px;
}

.result-description {
  color: #6b7280;
  line-height: 1.6;
  margin-bottom: 12px;
  font-size: 14px;
}

.result-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.result-actions {
  margin-left: 15px;
  flex-shrink: 0;
}

/* PathORAM路径对比预览样式 */
.path-comparison-preview {
  margin-top: 15px;
  padding: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.path-preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.path-preview-title {
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.path-preview-content {
  font-size: 12px;
  color: #6b7280;
}

.path-row {
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.path-label {
  font-weight: 500;
  color: #374151;
  min-width: 80px;
}

.path-value {
  font-family: 'Courier New', monospace;
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  flex: 1;
}

.path-length {
  color: #6b7280;
  font-size: 11px;
}

.path-differences {
  font-family: 'Courier New', monospace;
  background: #fef3c7;
  padding: 2px 6px;
  border-radius: 4px;
  color: #92400e;
}

/* PathORAM弹窗样式 */
.path-dialog-content {
  max-height: 70vh;
  overflow-y: auto;
}

.result-basic-info {
  margin-bottom: 25px;
  padding: 15px;
  background: #f8fafc;
  border-radius: 8px;
}

.result-basic-info h3 {
  margin: 0 0 15px 0;
  color: #1f2937;
  font-size: 18px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-label {
  font-weight: 500;
  color: #374151;
  min-width: 80px;
}

.info-value {
  color: #6b7280;
  font-family: 'Courier New', monospace;
}

.path-comparison-detail {
  margin-bottom: 25px;
}

.path-comparison-detail h3 {
  margin: 0 0 15px 0;
  color: #1f2937;
  font-size: 18px;
}

.path-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f0f9ff;
  border-radius: 8px;
}

.overview-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.overview-label {
  font-weight: 500;
  color: #374151;
}

.overview-value {
  font-weight: 600;
  color: #1f2937;
}

.path-details {
  margin-top: 20px;
}

.path-section {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.path-section h4 {
  margin: 0 0 10px 0;
  color: #374151;
  font-size: 16px;
}

.path-content {
  background: #f9fafb;
  padding: 10px;
  border-radius: 6px;
}

.path-array {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: #374151;
  word-break: break-all;
  line-height: 1.5;
}

.differences-content {
  background: #fffbeb;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #fbbf24;
}

.differences-list {
  margin-bottom: 10px;
}

.difference-label {
  font-weight: 500;
  color: #92400e;
  margin-bottom: 5px;
}

.difference-values {
  font-family: 'Courier New', monospace;
  color: #b45309;
  background: #fef3c7;
  padding: 6px;
  border-radius: 4px;
}

.differences-explanation {
  font-size: 13px;
  color: #78716c;
}

.differences-explanation p {
  margin: 5px 0;
}

.second-round-results {
  margin-bottom: 20px;
}

.second-round-results h3 {
  margin: 0 0 15px 0;
  color: #1f2937;
  font-size: 18px;
}

.second-results-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.second-result-item {
  padding: 10px 15px;
  border-bottom: 1px solid #f3f4f6;
}

.second-result-item:last-child {
  border-bottom: none;
}

.second-result-info {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 14px;
}

.result-index {
  font-weight: 600;
  color: #6b7280;
  min-width: 30px;
}

.result-keyword {
  font-weight: 500;
  color: #374151;
  flex: 1;
}

.result-coords {
  font-family: 'Courier New', monospace;
  color: #6b7280;
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
}

.result-distance {
  color: #059669;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-view {
    padding: 10px;
  }
  
  .page-header h2 {
    font-size: 24px;
  }
  
  .result-item {
    flex-direction: column;
    align-items: stretch;
  }
  
  .result-rank {
    margin-right: 0;
    margin-bottom: 10px;
    align-self: flex-start;
  }
  
  .result-actions {
    margin-left: 0;
    margin-top: 10px;
  }
  
  .results-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>