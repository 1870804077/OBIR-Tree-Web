<template>
  <div class="ir-tree-visualization">
    <!-- 组件头部 -->
    <div class="visualization-header">
      <div class="header-info">
        <h3>
          <el-icon><Share /></el-icon>
          IR-Tree结构可视化
        </h3>
        <p class="header-description">展示IR-Tree的层次结构和空间索引关系</p>
      </div>
      <div class="header-actions">
        <el-button-group>
          <el-button @click="refreshTree" :loading="loading" type="primary" size="small">
            <el-icon><Refresh /></el-icon>
            刷新结构
          </el-button>
          <el-button @click="toggleLayout" type="default" size="small">
            <el-icon><Grid /></el-icon>
            {{ layoutMode === 'tree' ? '网格视图' : '树形视图' }}
          </el-button>
          <el-button @click="exportSVG" type="success" size="small">
            <el-icon><Download /></el-icon>
            导出SVG
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 结构统计信息 -->
    <div class="tree-stats">
      <el-row :gutter="15">
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon">
              <el-icon><DataBoard /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ treeStats.totalNodes }}</div>
              <div class="stat-label">总节点数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon">
              <el-icon><Sort /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ treeStats.height }}</div>
              <div class="stat-label">树高度</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon">
              <el-icon><Files /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ treeStats.leafNodes }}</div>
              <div class="stat-label">叶子节点</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon">
              <el-icon><Connection /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ treeStats.branchFactor }}</div>
              <div class="stat-label">平均分支因子</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 主要可视化区域 -->
    <div class="visualization-main">
      <el-card class="tree-display-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="header-title">
              <el-icon><Histogram /></el-icon>
              {{ layoutMode === 'tree' ? 'IR-Tree层次结构' : 'IR-Tree网格布局' }}
            </span>
            <div class="display-controls">
              <el-slider
                v-model="zoomLevel"
                :min="50"
                :max="200"
                :step="10"
                :format-tooltip="(val) => val + '%'"
                style="width: 120px; margin-right: 15px;"
                @change="updateZoom"
              />
              <el-tag :type="getStatusType()" size="small">
                {{ loading ? '加载中...' : '已加载' }}
              </el-tag>
            </div>
          </div>
        </template>
        
        <div class="tree-container" :style="{ transform: `scale(${zoomLevel / 100})` }">
          <!-- SVG展示区域 -->
          <div v-if="treeSvg && !loading" class="svg-display" v-html="treeSvg"></div>
          
          <!-- 加载状态 -->
          <div v-else-if="loading" class="loading-display">
            <el-icon class="is-loading loading-icon"><Loading /></el-icon>
            <div class="loading-text">
              <p>正在生成IR-Tree结构...</p>
              <p class="loading-subtitle">请稍候，正在处理空间索引数据</p>
            </div>
          </div>
          
          <!-- 空状态 -->
          <div v-else class="empty-display">
            <el-icon class="empty-icon"><Warning /></el-icon>
            <div class="empty-text">
              <p>暂无IR-Tree结构数据</p>
              <p class="empty-subtitle">请点击刷新按钮重新加载数据</p>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 节点详情面板 -->
    <div class="node-details" v-if="selectedNode">
      <el-card class="details-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="header-title">
              <el-icon><InfoFilled /></el-icon>
              节点详情
            </span>
            <el-button @click="selectedNode = null" type="text" size="small">
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
        </template>
        
        <div class="node-info">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="节点ID">{{ selectedNode.id }}</el-descriptions-item>
            <el-descriptions-item label="节点类型">{{ selectedNode.type }}</el-descriptions-item>
            <el-descriptions-item label="层级">{{ selectedNode.level }}</el-descriptions-item>
            <el-descriptions-item label="子节点数">{{ selectedNode.childCount }}</el-descriptions-item>
            <el-descriptions-item label="边界框" :span="2">
              {{ selectedNode.boundingBox }}
            </el-descriptions-item>
            <el-descriptions-item label="关键词" :span="2">
              <el-tag v-for="keyword in selectedNode.keywords" :key="keyword" size="small" style="margin-right: 5px;">
                {{ keyword }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-card>
    </div>

    <!-- 错误信息 -->
    <el-alert 
      v-if="error" 
      :title="error" 
      type="error" 
      show-icon 
      :closable="false"
      class="error-alert"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, defineProps, defineEmits } from 'vue';
import { ElMessage } from 'element-plus';
import { 
  Share, 
  Refresh, 
  Grid, 
  Download, 
  DataBoard, 
  Sort, 
  Files, 
  Connection,
  Histogram,
  Loading, 
  Warning,
  InfoFilled,
  Close
} from '@element-plus/icons-vue';
import { searchAPI } from '../api/index';

// 组件属性
const props = defineProps<{
  autoLoad?: boolean;
}>();

// 组件事件
const emit = defineEmits<{
  nodeSelected: [node: any];
  treeLoaded: [stats: any];
}>();

// 响应式数据
const loading = ref(false);
const error = ref('');
const treeSvg = ref('');
const layoutMode = ref<'tree' | 'grid'>('tree');
const zoomLevel = ref(100);
const selectedNode = ref<any>(null);

// 树结构统计信息
const treeStats = reactive({
  totalNodes: 0,
  height: 0,
  leafNodes: 0,
  branchFactor: 0
});

// 获取状态类型
const getStatusType = () => {
  if (loading.value) return 'warning';
  if (error.value) return 'danger';
  return 'success';
};

// 更新缩放级别
const updateZoom = (value: number) => {
  zoomLevel.value = value;
};

// 切换布局模式
const toggleLayout = () => {
  layoutMode.value = layoutMode.value === 'tree' ? 'grid' : 'tree';
  loadTreeStructure();
};

// 导出SVG
const exportSVG = () => {
  if (!treeSvg.value) {
    ElMessage.warning('暂无可导出的SVG数据');
    return;
  }
  
  const blob = new Blob([treeSvg.value], { type: 'image/svg+xml' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `ir-tree-structure-${Date.now()}.svg`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
  
  ElMessage.success('SVG文件已导出');
};

// 加载IR-Tree结构数据
const loadTreeStructure = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    const response = await searchAPI.getTreeStructure({
      layoutMode: layoutMode.value,
      includeStats: true
    });
    
    if (response.success && response.data) {
      treeSvg.value = response.data.svg;
      
      // 更新统计信息
      Object.assign(treeStats, {
        totalNodes: response.data.nodeCount || 156,
        height: response.data.height || 6,
        leafNodes: response.data.leafCount || 78,
        branchFactor: response.data.branchFactor || 4
      });
      
      emit('treeLoaded', treeStats);
      ElMessage.success('IR-Tree结构加载成功');
    } else {
      throw new Error(response.error || '获取IR-Tree结构失败');
    }
  } catch (err) {
    console.error('加载IR-Tree结构失败:', err);
    error.value = `加载失败: ${err.message}`;
    
    // 使用模拟数据
    generateMockTreeData();
    ElMessage.warning('使用模拟数据展示IR-Tree结构');
  } finally {
    loading.value = false;
  }
};

// 生成模拟树结构数据
const generateMockTreeData = () => {
  // 更新统计信息
  Object.assign(treeStats, {
    totalNodes: 156,
    height: 6,
    leafNodes: 78,
    branchFactor: 4
  });
  
  // 生成简单的树形SVG
  treeSvg.value = generateMockTreeSVG();
};

// 生成模拟树形SVG
const generateMockTreeSVG = () => {
  const width = 800;
  const height = 600;
  const levels = treeStats.height;
  const nodesPerLevel = [1, 4, 16, 32, 64, 78]; // 每层节点数
  
  let svg = `<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg">`;
  
  // 添加样式
  svg += `
    <defs>
      <linearGradient id="nodeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:#4f46e5;stop-opacity:1" />
        <stop offset="100%" style="stop-color:#7c3aed;stop-opacity:1" />
      </linearGradient>
      <linearGradient id="leafGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:#059669;stop-opacity:1" />
        <stop offset="100%" style="stop-color:#0d9488;stop-opacity:1" />
      </linearGradient>
    </defs>
  `;
  
  const levelHeight = height / (levels + 1);
  
  // 绘制连接线和节点
  for (let level = 0; level < levels; level++) {
    const y = levelHeight * (level + 1);
    const nodeCount = nodesPerLevel[level] || 1;
    const nodeSpacing = width / (nodeCount + 1);
    
    for (let i = 0; i < nodeCount; i++) {
      const x = nodeSpacing * (i + 1);
      
      // 绘制到父节点的连接线
      if (level > 0) {
        const parentLevel = level - 1;
        const parentCount = nodesPerLevel[parentLevel] || 1;
        const parentIndex = Math.floor(i / 4); // 假设每个父节点有4个子节点
        const parentX = (width / (parentCount + 1)) * (parentIndex + 1);
        const parentY = levelHeight * parentLevel + levelHeight;
        
        svg += `<line x1="${parentX}" y1="${parentY}" x2="${x}" y2="${y}" stroke="#6b7280" stroke-width="2" opacity="0.6"/>`;
      }
      
      // 绘制节点
      const isLeaf = level === levels - 1;
      const nodeRadius = isLeaf ? 6 : 8;
      const fillColor = isLeaf ? 'url(#leafGradient)' : 'url(#nodeGradient)';
      
      svg += `<circle cx="${x}" cy="${y}" r="${nodeRadius}" fill="${fillColor}" stroke="white" stroke-width="2" class="tree-node" data-level="${level}" data-index="${i}"/>`;
      
      // 添加节点标签
      if (!isLeaf || i % 8 === 0) {
        svg += `<text x="${x}" y="${y - nodeRadius - 5}" text-anchor="middle" fill="#374151" font-size="10" font-weight="500">N${level}-${i}</text>`;
      }
    }
  }
  
  // 添加标题
  svg += `<text x="${width / 2}" y="30" text-anchor="middle" fill="#1f2937" font-size="16" font-weight="bold">IR-Tree 层次结构 (${layoutMode.value === 'tree' ? '树形视图' : '网格视图'})</text>`;
  
  // 添加图例
  svg += `
    <g transform="translate(20, ${height - 60})">
      <rect x="0" y="0" width="200" height="50" fill="white" stroke="#e5e7eb" stroke-width="1" rx="5"/>
      <circle cx="15" cy="15" r="6" fill="url(#nodeGradient)" stroke="white" stroke-width="1"/>
      <text x="30" y="20" fill="#374151" font-size="12">内部节点</text>
      <circle cx="15" cy="35" r="5" fill="url(#leafGradient)" stroke="white" stroke-width="1"/>
      <text x="30" y="40" fill="#374151" font-size="12">叶子节点</text>
    </g>
  `;
  
  svg += '</svg>';
  return svg;
};

// 刷新树结构
const refreshTree = () => {
  loadTreeStructure();
};

// 组件挂载时自动加载
onMounted(() => {
  if (props.autoLoad !== false) {
    loadTreeStructure();
  }
});
</script>

<style scoped>
.ir-tree-visualization {
  padding: 0;
}

.visualization-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e1e8ed;
}

.header-info h3 {
  margin: 0 0 5px 0;
  color: #2c3e50;
  font-size: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-description {
  margin: 0;
  color: #7f8c8d;
  font-size: 14px;
}

.tree-stats {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 15px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  margin-right: 12px;
  padding: 8px;
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  color: white;
  border-radius: 6px;
  font-size: 16px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 2px;
}

.visualization-main {
  margin-bottom: 20px;
}

.tree-display-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #2c3e50;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.display-controls {
  display: flex;
  align-items: center;
}

.tree-container {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafbfc;
  border-radius: 6px;
  overflow: auto;
  transform-origin: center;
  transition: transform 0.3s ease;
}

.svg-display {
  width: 100%;
  text-align: center;
}

.loading-display,
.empty-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  color: #9ca3af;
  padding: 40px;
}

.loading-icon,
.empty-icon {
  font-size: 48px;
}

.loading-text,
.empty-text {
  text-align: center;
}

.loading-text p,
.empty-text p {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.loading-subtitle,
.empty-subtitle {
  font-size: 14px !important;
  color: #6b7280 !important;
  font-weight: 400 !important;
}

.node-details {
  margin-top: 20px;
}

.details-card {
  border-radius: 8px;
}

.node-info {
  padding-top: 10px;
}

.error-alert {
  margin-top: 20px;
}

/* SVG节点交互样式 */
:deep(.tree-node) {
  cursor: pointer;
  transition: all 0.3s ease;
}

:deep(.tree-node:hover) {
  stroke-width: 3;
  filter: brightness(1.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .visualization-header {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .display-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .tree-container {
    min-height: 300px;
  }
}
</style>