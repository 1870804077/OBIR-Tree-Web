<template>
  <div class="pathoram-change-display-page">
    <div class="page-header">
      <h2>PathORAM搜索前后改变展示</h2>
    </div>
    
    <div class="content">
      <div class="main-section">
        <div class="pathoram-realtime">
          <div class="header">
            <h5>PathORAM结构变化展示</h5>
            <div class="controls">
              <button @click="refreshData" :disabled="loading" class="refresh-btn">
                {{ loading ? '加载中...' : '刷新数据' }}
              </button>
              <div class="auto-refresh">
                <label>
                  <input type="checkbox" v-model="autoRefresh" @change="toggleAutoRefresh">
                  自动刷新
                </label>
                <span v-if="autoRefresh" class="countdown">{{ countdown }}s</span>
              </div>
            </div>
          </div>
          
          <div class="status-info" v-if="differences">
            <div class="status-item">
              <span class="label">当前节点数:</span>
              <span class="value">{{ currentNodes }}</span>
            </div>
            <div class="status-item">
              <span class="label">前一时刻节点数:</span>
              <span class="value">{{ previousNodes }}</span>
            </div>
            <div class="status-item">
              <span class="label">新增节点:</span>
              <span class="value added">{{ differences.added.length }}</span>
            </div>
            <div class="status-item">
              <span class="label">删除节点:</span>
              <span class="value removed">{{ differences.removed.length }}</span>
            </div>
            <div class="status-item">
              <span class="label">修改节点:</span>
              <span class="value modified">{{ differences.modified.length }}</span>
            </div>
          </div>
          
          <div class="tree-comparison" v-if="svgContent">
            <div class="tree-column">
              <div class="tree-header">
                <h4>搜索前PathORAM结构</h4>
              </div>
              <div class="tree-container">
                <div class="svg-wrapper" v-html="previousSvgContent || svgContent"></div>
              </div>
            </div>
            
            <div class="tree-column">
              <div class="tree-header">
                <h4>搜索后PathORAM结构</h4>
              </div>
              <div class="tree-container">
                <div class="svg-wrapper" v-html="svgContent"></div>
              </div>
            </div>
          </div>
          
          <div v-else-if="error" class="error-message">
            <p>{{ error }}</p>
            <button @click="loadSVG" class="retry-btn">重试</button>
          </div>
          
          <div v-else-if="loading" class="loading">
            <p>正在加载PathORAM数据...</p>
          </div>
          
          <div v-else class="no-data">
            <p>暂无PathORAM数据</p>
          </div>
        </div>
      </div>
      

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

// 响应式数据
const svgContent = ref('')
const previousSvgContent = ref('')
const loading = ref(false)
const error = ref('')
const differences = ref(null)
const currentNodes = ref(0)
const previousNodes = ref(0)
const autoRefresh = ref(false)
const countdown = ref(0)
const searchTime = ref(0)
const nodeChangeCount = ref(0)
const pathAccessCount = ref(0)
const lastUpdateTime = ref('')

let autoRefreshTimer: number | null = null
let countdownTimer: number | null = null

// 加载PathORAM数据
const loadSVG = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const response = await fetch('/api/obir-tree-realtime', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        currentFile: 'obir_tree_current.json',
        previousFile: 'obir_tree_previous.json'
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    
    if (result.success) {
      // 保存之前的SVG内容
      if (svgContent.value) {
        previousSvgContent.value = svgContent.value
      }
      
      svgContent.value = result.svg
      differences.value = result.differences
      currentNodes.value = result.current_nodes
      previousNodes.value = result.previous_nodes
      
      // 模拟PathORAM统计数据
      searchTime.value = Math.floor(Math.random() * 500) + 100
      nodeChangeCount.value = (differences.value?.added?.length || 0) + 
                             (differences.value?.removed?.length || 0) + 
                             (differences.value?.modified?.length || 0)
      pathAccessCount.value = Math.floor(Math.random() * 20) + 5
      lastUpdateTime.value = new Date().toLocaleString()
      
      // 等待DOM更新后添加节点悬停功能
      await nextTick()
      addNodeTooltips()
    } else {
      throw new Error(result.error || '获取PathORAM数据失败')
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载失败'
    console.error('加载PathORAM数据失败:', err)
  } finally {
    loading.value = false
  }
}

// 添加节点悬停功能
const addNodeTooltips = () => {
  const svgWrappers = document.querySelectorAll('.svg-wrapper')
  
  svgWrappers.forEach(wrapper => {
    const circles = wrapper.querySelectorAll('circle')
    
    circles.forEach((circle, index) => {
      // 移除之前的事件监听器
      circle.removeEventListener('mouseenter', handleNodeMouseEnter)
      circle.removeEventListener('mouseleave', handleNodeMouseLeave)
      circle.removeEventListener('mousemove', handleNodeMouseMove)
      
      // 添加节点数据属性
      circle.setAttribute('data-node-id', `node-${index}`)
      circle.setAttribute('data-node-info', `节点 ${index + 1}\n类型: PathORAM节点\n深度: ${Math.floor(index / 2) + 1}`)
      
      // 添加事件监听器
      circle.addEventListener('mouseenter', handleNodeMouseEnter)
      circle.addEventListener('mouseleave', handleNodeMouseLeave)
      circle.addEventListener('mousemove', handleNodeMouseMove)
    })
  })
}

// 节点鼠标进入事件
const handleNodeMouseEnter = (event: MouseEvent) => {
  const target = event.target as SVGCircleElement
  const nodeInfo = target.getAttribute('data-node-info') || '节点信息'
  
  // 创建tooltip
  const tooltip = document.createElement('div')
  tooltip.className = 'node-tooltip'
  tooltip.innerHTML = nodeInfo.replace(/\\n/g, '<br>')
  tooltip.id = 'node-tooltip'
  
  document.body.appendChild(tooltip)
  
  // 设置初始位置
  updateTooltipPosition(event, tooltip)
}

// 节点鼠标移动事件
const handleNodeMouseMove = (event: MouseEvent) => {
  const tooltip = document.getElementById('node-tooltip')
  if (tooltip) {
    updateTooltipPosition(event, tooltip)
  }
}

// 节点鼠标离开事件
const handleNodeMouseLeave = () => {
  const tooltip = document.getElementById('node-tooltip')
  if (tooltip) {
    tooltip.remove()
  }
}

// 更新tooltip位置
const updateTooltipPosition = (event: MouseEvent, tooltip: HTMLElement) => {
  const x = event.clientX
  const y = event.clientY
  
  tooltip.style.left = x + 'px'
  tooltip.style.top = (y - 10) + 'px'
}

// 刷新数据
const refreshData = () => {
  loadSVG()
}

// 切换自动刷新
const toggleAutoRefresh = () => {
  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

// 开始自动刷新
const startAutoRefresh = () => {
  const interval = 5000 // 5秒
  countdown.value = interval / 1000
  autoRefreshTimer = window.setInterval(() => {
    loadSVG()
  }, interval)
  
  countdownTimer = window.setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      countdown.value = interval / 1000
    }
  }, 1000)
}

// 停止自动刷新
const stopAutoRefresh = () => {
  if (autoRefreshTimer) {
    clearInterval(autoRefreshTimer)
    autoRefreshTimer = null
  }
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
  countdown.value = 0
}

// 组件挂载时加载数据
onMounted(() => {
  loadSVG()
})

// 组件卸载时清理定时器
onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.pathoram-change-display-page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.pathoram-realtime {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.header h5 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.refresh-btn {
  padding: 8px 16px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.refresh-btn:hover:not(:disabled) {
  background: #45a049;
}

.refresh-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.auto-refresh {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.auto-refresh label {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

.auto-refresh input[type="checkbox"] {
  margin: 0;
}

.countdown {
  color: #666;
  font-size: 12px;
}

.status-info {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #4CAF50;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-item .label {
  font-size: 14px;
  color: #666;
}

.status-item .value {
  font-weight: bold;
  color: #333;
}

.status-item .value.added {
  color: #4CAF50;
}

.status-item .value.removed {
  color: #F44336;
}

.status-item .value.modified {
  color: #FF9800;
}

.tree-comparison {
  display: flex;
  gap: 30px;
  padding: 30px;
  min-height: 600px;
  width: 100%;
}

.tree-column {
  flex: 1;
  background: #f8f9fa;
  border-radius: 8px;
  overflow: hidden;
  min-width: 0;
}

.tree-header {
  background: #e9ecef;
  padding: 20px;
  border-bottom: 1px solid #dee2e6;
}

.tree-header h4 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #495057;
  text-align: center;
}

.tree-container {
  padding: 30px;
  min-height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.svg-wrapper {
  display: flex;
  justify-content: center;
  overflow-x: auto;
  padding: 20px;
  background: #fafafa;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
  width: 100%;
  min-height: 450px;
}

/* 树状图节点样式 */
.svg-wrapper :deep(circle) {
  r: 4 !important;
  stroke-width: 2 !important;
  cursor: pointer;
  transition: all 0.3s ease;
}

.svg-wrapper :deep(circle:hover) {
  r: 6 !important;
  stroke-width: 3 !important;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
}

/* 节点颜色 */
.svg-wrapper :deep(circle.added) {
  fill: #4CAF50 !important;
  stroke: #2E7D32 !important;
}

.svg-wrapper :deep(circle.removed) {
  fill: #F44336 !important;
  stroke: #C62828 !important;
}

.svg-wrapper :deep(circle.modified) {
  fill: #FF9800 !important;
  stroke: #E65100 !important;
}

.svg-wrapper :deep(circle.unchanged) {
  fill: #2196F3 !important;
  stroke: #1565C0 !important;
}

/* 节点文本隐藏，通过tooltip显示 */
.svg-wrapper :deep(text) {
  display: none;
}

/* 连接线样式 */
.svg-wrapper :deep(line), .svg-wrapper :deep(path) {
  stroke: #666 !important;
  stroke-width: 1.5 !important;
}

/* 节点tooltip样式 */
.node-tooltip {
  position: absolute;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 12px;
  pointer-events: none;
  z-index: 1000;
  white-space: nowrap;
  transform: translate(-50%, -100%);
  margin-top: -8px;
}

.svg-wrapper svg {
  max-width: 100%;
  height: auto;
}

.error-message {
  text-align: center;
  padding: 40px 20px;
  color: #f44336;
}

.error-message p {
  margin-bottom: 15px;
}

.retry-btn {
  padding: 8px 16px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.retry-btn:hover {
  background: #d32f2f;
}

.loading, .no-data {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.loading p, .no-data p {
  margin: 0;
  font-size: 16px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
}

.main-section {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.info-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-card {
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #4CAF50;
}

.info-card h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.info-card ul {
  margin: 0;
  padding-left: 20px;
}

.info-card li {
  margin-bottom: 8px;
  color: #555;
  line-height: 1.5;
}

.info-card strong {
  color: #333;
}

.api-info p, .integration-info p {
  margin: 0 0 8px 0;
  color: #555;
  line-height: 1.5;
}

.api-info strong, .integration-info strong {
  color: #333;
}

@media (max-width: 1024px) {
  .content {
    grid-template-columns: 1fr;
  }
  
  .info-section {
    order: -1;
  }
  
  .tree-comparison {
    flex-direction: column;
    gap: 15px;
    min-height: auto;
  }
  
  .tree-container {
    min-height: 300px;
  }
}

@media (max-width: 768px) {
  .pathoram-change-display-page {
    padding: 15px;
  }
  
  .page-header {
    padding: 15px;
  }
  
  .page-header h2 {
    font-size: 20px;
  }
  
  .tree-comparison {
    padding: 10px;
  }
  
  .tree-header {
    padding: 10px;
  }
  
  .tree-header h4 {
    font-size: 14px;
  }
  
  .tree-container {
    padding: 15px;
    min-height: 250px;
  }
}
</style>