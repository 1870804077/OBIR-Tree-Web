<template>
  <div class="pathoram-dialog">
    <!-- 对话框头部信息 -->
    <div class="dialog-header">
      <div class="target-info">
        <h3>{{ resultInfo?.title || '搜索目标' }}</h3>
        <p class="target-description">{{ resultInfo?.description || '查看PathORAM路径变化' }}</p>
      </div>
      <div class="dialog-actions">
        <el-button @click="refreshPaths" :loading="loading" type="primary" size="small">
          <el-icon><Refresh /></el-icon>
          刷新路径
        </el-button>
      </div>
    </div>

    <!-- 路径对比展示区域 -->
    <div class="path-comparison">
      <el-row :gutter="20">
        <!-- 搜索前路径 -->
        <el-col :span="12">
          <el-card class="path-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="header-title">
                  <el-icon><DocumentRemove /></el-icon>
                  搜索前路径
                </span>
                <el-tag type="info" size="small">{{ beforePathData.nodeCount }} 节点</el-tag>
              </div>
            </template>
            
            <div class="path-content">
              <div v-if="beforePathSvg" class="svg-container" v-html="beforePathSvg"></div>
              <div v-else-if="loading" class="loading-placeholder">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>加载路径数据中...</span>
              </div>
              <div v-else class="empty-placeholder">
                <el-icon><Warning /></el-icon>
                <span>暂无路径数据</span>
              </div>
            </div>
            
            <div class="path-stats">
              <div class="stat-item">
                <span class="stat-label">访问节点:</span>
                <span class="stat-value">{{ beforePathData.nodeCount }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">路径深度:</span>
                <span class="stat-value">{{ beforePathData.depth }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">访问次数:</span>
                <span class="stat-value">{{ beforePathData.accessCount }}</span>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 搜索后路径 -->
        <el-col :span="12">
          <el-card class="path-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="header-title">
                  <el-icon><DocumentAdd /></el-icon>
                  搜索后路径
                </span>
                <el-tag type="success" size="small">{{ afterPathData.nodeCount }} 节点</el-tag>
              </div>
            </template>
            
            <div class="path-content">
              <div v-if="afterPathSvg" class="svg-container" v-html="afterPathSvg"></div>
              <div v-else-if="loading" class="loading-placeholder">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>加载路径数据中...</span>
              </div>
              <div v-else class="empty-placeholder">
                <el-icon><Warning /></el-icon>
                <span>暂无路径数据</span>
              </div>
            </div>
            
            <div class="path-stats">
              <div class="stat-item">
                <span class="stat-label">访问节点:</span>
                <span class="stat-value">{{ afterPathData.nodeCount }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">路径深度:</span>
                <span class="stat-value">{{ afterPathData.depth }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">访问次数:</span>
                <span class="stat-value">{{ afterPathData.accessCount }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 路径变化分析 -->
    <div class="path-analysis">
      <el-card class="analysis-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="header-title">
              <el-icon><TrendCharts /></el-icon>
              路径变化分析
            </span>
          </div>
        </template>
        
        <div class="analysis-content">
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="analysis-item">
                <div class="analysis-label">节点变化</div>
                <div class="analysis-value" :class="getChangeClass(nodeChange)">
                  {{ nodeChange > 0 ? '+' : '' }}{{ nodeChange }}
                  <el-icon v-if="nodeChange > 0"><ArrowUp /></el-icon>
                  <el-icon v-else-if="nodeChange < 0"><ArrowDown /></el-icon>
                  <el-icon v-else><Minus /></el-icon>
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="analysis-item">
                <div class="analysis-label">深度变化</div>
                <div class="analysis-value" :class="getChangeClass(depthChange)">
                  {{ depthChange > 0 ? '+' : '' }}{{ depthChange }}
                  <el-icon v-if="depthChange > 0"><ArrowUp /></el-icon>
                  <el-icon v-else-if="depthChange < 0"><ArrowDown /></el-icon>
                  <el-icon v-else><Minus /></el-icon>
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="analysis-item">
                <div class="analysis-label">访问变化</div>
                <div class="analysis-value" :class="getChangeClass(accessChange)">
                  {{ accessChange > 0 ? '+' : '' }}{{ accessChange }}
                  <el-icon v-if="accessChange > 0"><ArrowUp /></el-icon>
                  <el-icon v-else-if="accessChange < 0"><ArrowDown /></el-icon>
                  <el-icon v-else><Minus /></el-icon>
                </div>
              </div>
            </el-col>
          </el-row>
          
          <div class="analysis-summary">
            <el-alert 
              :title="getAnalysisSummary()" 
              :type="getAnalysisType()" 
              show-icon 
              :closable="false"
            />
          </div>
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
import { ref, reactive, computed, onMounted, defineProps, defineEmits } from 'vue';
import { 
  Refresh, 
  DocumentRemove, 
  DocumentAdd, 
  TrendCharts, 
  Loading, 
  Warning,
  ArrowUp,
  ArrowDown,
  Minus
} from '@element-plus/icons-vue';

// 组件属性
const props = defineProps<{
  targetId: string;
  resultInfo?: any;
}>();

// 组件事件
const emit = defineEmits<{
  close: [];
}>();

// 响应式数据
const loading = ref(false);
const error = ref('');
const beforePathSvg = ref('');
const afterPathSvg = ref('');

// 路径数据
const beforePathData = reactive({
  nodeCount: 0,
  depth: 0,
  accessCount: 0
});

const afterPathData = reactive({
  nodeCount: 0,
  depth: 0,
  accessCount: 0
});

// 计算属性 - 路径变化
const nodeChange = computed(() => afterPathData.nodeCount - beforePathData.nodeCount);
const depthChange = computed(() => afterPathData.depth - beforePathData.depth);
const accessChange = computed(() => afterPathData.accessCount - beforePathData.accessCount);

// 获取变化样式类
const getChangeClass = (change: number) => {
  if (change > 0) return 'change-increase';
  if (change < 0) return 'change-decrease';
  return 'change-neutral';
};

// 获取分析类型
const getAnalysisType = () => {
  const totalChange = Math.abs(nodeChange.value) + Math.abs(depthChange.value) + Math.abs(accessChange.value);
  if (totalChange === 0) return 'info';
  if (accessChange.value < 0) return 'success';
  if (accessChange.value > 2) return 'warning';
  return 'info';
};

// 获取分析摘要
const getAnalysisSummary = () => {
  if (nodeChange.value === 0 && depthChange.value === 0 && accessChange.value === 0) {
    return 'PathORAM路径结构保持稳定，未发生显著变化';
  }
  
  let summary = 'PathORAM路径变化分析: ';
  const changes: string[] = [];
  
  if (nodeChange.value !== 0) {
    changes.push(`访问节点${nodeChange.value > 0 ? '增加' : '减少'}${Math.abs(nodeChange.value)}个`);
  }
  
  if (depthChange.value !== 0) {
    changes.push(`路径深度${depthChange.value > 0 ? '增加' : '减少'}${Math.abs(depthChange.value)}层`);
  }
  
  if (accessChange.value !== 0) {
    changes.push(`访问次数${accessChange.value > 0 ? '增加' : '减少'}${Math.abs(accessChange.value)}次`);
  }
  
  return summary + changes.join('，');
};

// 将 path 数组渲染为简单的水平链式 SVG
function buildPathSvg(title: string, seq: number[], color: string) {
  const spacing = 60;
  const width = Math.max(120, seq.length * spacing + 40);
  const height = 120;
  let x = 20;
  const y = height / 2;
  let svg = `<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg">`;
  svg += `<text x="${width/2}" y="18" text-anchor="middle" fill="${color}" font-size="14" font-weight="bold">${title}</text>`;
  for (let i = 0; i < seq.length; i++) {
    const node = seq[i];
    svg += `<circle cx="${x}" cy="${y}" r="12" fill="${color}" opacity="0.85" />`;
    svg += `<text x="${x}" y="${y+5}" text-anchor="middle" fill="#fff" font-size="12">${node}</text>`;
    if (i < seq.length - 1) {
      svg += `<line x1="${x+12}" y1="${y}" x2="${x+spacing-12}" y2="${y}" stroke="${color}" stroke-width="2" marker-end="url(#arrow)" />`;
    }
    x += spacing;
  }
  // 箭头定义
  svg += `<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="6" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="${color}" /></marker></defs>`;
  svg += '</svg>';
  return svg;
}

// 从 resultInfo 解析后端提供的路径信息
function applyPathsFromResult() {
  try {
    const before = props.resultInfo?.path_before;
    const after = props.resultInfo?.path_after;
    const beforeSeq: number[] = Array.isArray(before?.path) ? before.path : (before?.path ? String(before.path).replace(/^Root->?/, '').split('->').filter(Boolean).map(Number) : []);
    const afterSeq: number[] = Array.isArray(after?.path) ? after.path : (after?.path ? String(after.path).replace(/^Root->?/, '').split('->').filter(Boolean).map(Number) : []);

    beforePathData.depth = before?.depth ?? beforeSeq.length;
    afterPathData.depth = after?.depth ?? afterSeq.length;

    beforePathData.accessCount = before?.access_count ?? before?.accessCount ?? 0;
    afterPathData.accessCount = after?.access_count ?? after?.accessCount ?? 0;

    // 访问节点数量用序列长度近似
    beforePathData.nodeCount = beforeSeq.length;
    afterPathData.nodeCount = afterSeq.length;

    beforePathSvg.value = beforeSeq.length ? buildPathSvg('搜索前路径', beforeSeq, '#3b82f6') : '';
    afterPathSvg.value = afterSeq.length ? buildPathSvg('搜索后路径', afterSeq, '#10b981') : '';
  } catch (e: any) {
    console.error(`无法解析后端路径数据，错误为${e.message}`);
    error.value = '无法解析路径数据';
  }
}

// 刷新路径（重新从当前 resultInfo 应用）
const refreshPaths = () => {
  loading.value = true;
  try {
    applyPathsFromResult();
  } finally {
    loading.value = false;
  }
};

// 组件挂载时加载数据
onMounted(() => {
  applyPathsFromResult();
});
</script>

<style scoped>
/* 保持原样式不变，仅少量字段名调整 */
.pathoram-dialog { padding: 0; }
.dialog-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #e1e8ed; }
.target-info h3 { margin: 0 0 5px 0; color: #2c3e50; font-size: 18px; font-weight: 600; }
.target-description { margin: 0; color: #7f8c8d; font-size: 14px; }
.path-comparison { margin-bottom: 20px; }
.path-card { height: 100%; border-radius: 8px; }
.card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; color: #2c3e50; }
.header-title { display: flex; align-items: center; gap: 8px; }
.path-content { min-height: 200px; display: flex; align-items: center; justify-content: center; background: #f8fafc; border-radius: 6px; margin-bottom: 15px; }
.svg-container { width: 100%; text-align: center; }
.loading-placeholder, .empty-placeholder { display: flex; flex-direction: column; align-items: center; gap: 10px; color: #9ca3af; font-size: 14px; }
.path-stats { display: flex; justify-content: space-between; padding: 10px; background: #f1f5f9; border-radius: 6px; }
.stat-item { text-align: center; }
.stat-label { display: block; font-size: 12px; color: #64748b; margin-bottom: 4px; }
.stat-value { display: block; font-size: 16px; font-weight: 600; color: #1e293b; }
.analysis-card { border-radius: 8px; }
.analysis-content { padding-top: 10px; }
.analysis-item { text-align: center; padding: 15px; background: #f8fafc; border-radius: 6px; border: 1px solid #e2e8f0; }
.analysis-label { font-size: 14px; color: #64748b; margin-bottom: 8px; }
.analysis-value { display: flex; align-items: center; justify-content: center; gap: 4px; font-size: 18px; font-weight: 600; }
.change-increase { color: #dc2626; }
.change-decrease { color: #16a34a; }
.change-neutral { color: #6b7280; }
.analysis-summary { margin-top: 20px; }
.error-alert { margin-top: 20px; }
@media (max-width: 768px) { .dialog-header { flex-direction: column; align-items: stretch; gap: 15px; } .path-stats { flex-direction: column; gap: 10px; } .analysis-item { margin-bottom: 10px; } }
</style>