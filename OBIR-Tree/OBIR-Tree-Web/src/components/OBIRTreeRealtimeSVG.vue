<template>
  <div class="obir-tree-realtime">
    <div class="header">
      <h5>OBIR-Tree实时路径展示</h5>
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
    
    <div class="svg-container" v-if="svgContent">
      <div class="svg-wrapper" v-html="svgContent"></div>
    </div>
    
    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="loadSVG" class="retry-btn">重试</button>
    </div>
    
    <div v-else-if="loading" class="loading">
      <p>正在加载OBIR-Tree数据...</p>
    </div>
    
    <div v-else class="no-data">
      <p>暂无OBIR-Tree数据</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

// Props
interface Props {
  currentFile?: string
  previousFile?: string
  autoRefreshInterval?: number
}

const props = withDefaults(defineProps<Props>(), {
  currentFile: 'obir_tree_current.json',
  previousFile: 'obir_tree_previous.json',
  autoRefreshInterval: 5000 // 5秒自动刷新
})

// 响应式数据
const svgContent = ref('')
const loading = ref(false)
const error = ref('')
const differences = ref(null)
const currentNodes = ref(0)
const previousNodes = ref(0)
const autoRefresh = ref(false)
const countdown = ref(0)
let autoRefreshTimer: number | null = null
let countdownTimer: number | null = null

// 加载SVG数据
const loadSVG = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const response = await fetch('/api/obir-tree-realtime', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        currentFile: props.currentFile,
        previousFile: props.previousFile
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    
    if (result.success) {
      svgContent.value = result.svg
      differences.value = result.differences
      currentNodes.value = result.current_nodes
      previousNodes.value = result.previous_nodes
    } else {
      throw new Error(result.error || '获取OBIR-Tree数据失败')
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载失败'
    console.error('加载OBIR-Tree实时数据失败:', err)
  } finally {
    loading.value = false
  }
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
  countdown.value = props.autoRefreshInterval / 1000
  autoRefreshTimer = window.setInterval(() => {
    loadSVG()
  }, props.autoRefreshInterval)
  
  countdownTimer = window.setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      countdown.value = props.autoRefreshInterval / 1000
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
.obir-tree-realtime {
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

.svg-container {
  margin-top: 20px;
}

.svg-wrapper {
  display: flex;
  justify-content: center;
  overflow-x: auto;
  padding: 10px;
  background: #fafafa;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
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
</style> 