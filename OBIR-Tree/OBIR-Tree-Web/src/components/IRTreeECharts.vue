<template>
  <div class="ir-tree-echarts-container">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>加载IR-Tree数据中...</p>
    </div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="loadData" class="retry-btn">重试</button>
    </div>
    <div v-else ref="chartContainer" style="width: 100%; height: 100%;"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { searchAPI } from '../api'

interface TreeNode {
  id: string
  name: string
  type: string
  level: number
  children?: TreeNode[]
  collapsed?: boolean
  x?: number
  y?: number
}

interface EChartsNode {
  id: string
  name: string
  x: number
  y: number
  symbolSize: number
  itemStyle: {
    color: string
  }
  label: {
    show: boolean
    position: string
  }
}

interface EChartsLink {
  source: string
  target: string
}

const loading = ref(true)
const error = ref('')
const chartContainer = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null
const treeData = ref<TreeNode | null>(null)
const expandedNodes = ref<Set<string>>(new Set())

const loadData = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await searchAPI.getTreeStructure()
    if (!response.success) {
      throw new Error(response.error || '获取IR-Tree数据失败')
    }
    const data = response.data || response.results
    if (!data || !(data as any).tree) {
      throw new Error('返回数据格式不正确')
    }
    treeData.value = processTreeData((data as any).tree as TreeNode)
    await nextTick()
    renderChart()
  } catch (err: unknown) {
    console.error('获取IR-Tree数据失败:', err)
    error.value = err instanceof Error ? err.message : '加载失败'
  } finally {
    loading.value = false
  }
}

const processTreeData = (root: any): TreeNode => {
  function traverse(node: any, level: number): TreeNode {
    const nodeId = String(node.id ?? node.nodeId ?? `${level}-${Math.random()}`)
    const processedNode: TreeNode = {
      id: nodeId,
      name: `${node.keyword || node.name || 'Node'} (ID: ${node.id ?? node.nodeId ?? '?'})`,
      type: level === 0 ? 'root' : (node.children && node.children.length > 0) ? 'node' : 'leaf',
      level,
      collapsed: level >= 5, // 第5层及以后默认折叠
      children: []
    }

    if (Array.isArray(node.children)) {
      processedNode.children = node.children.map((child: any) => traverse(child, level + 1))
    }

    return processedNode
  }

  return traverse(root, 0)
}

const getVisibleNodes = (root: TreeNode): { nodes: EChartsNode[], links: EChartsLink[] } => {
  const nodes: EChartsNode[] = []
  const links: EChartsLink[] = []
  const levelCounts: { [key: number]: number } = {}

  function traverse(node: TreeNode, parentId?: string) {
    // 计算节点位置
    if (!levelCounts[node.level]) {
      levelCounts[node.level] = 0
    }
    const x = levelCounts[node.level] * 150 + 100
    const y = node.level * 100 + 50
    levelCounts[node.level]++

    // 创建ECharts节点
    const echartsNode: EChartsNode = {
      id: node.id,
      name: node.name,
      x,
      y,
      symbolSize: node.type === 'root' ? 30 : node.type === 'leaf' ? 15 : 20,
      itemStyle: {
        color: node.type === 'root' ? '#ff6b6b' : node.type === 'leaf' ? '#4ecdc4' : '#45b7d1'
      },
      label: {
        show: true,
        position: 'bottom'
      }
    }
    nodes.push(echartsNode)

    // 创建连接线
    if (parentId) {
      links.push({
        source: parentId,
        target: node.id
      })
    }

    // 递归处理子节点（只处理前5层或已展开的节点）
    if (node.children && (node.level < 4 || expandedNodes.value.has(node.id))) {
      node.children.forEach(child => traverse(child, node.id))
    }
  }

  traverse(root)
  return { nodes, links }
}

const findNodeById = (root: TreeNode, id: string): TreeNode | null => {
  if (root.id === id) return root
  if (root.children) {
    for (const child of root.children) {
      const found = findNodeById(child, id)
      if (found) return found
    }
  }
  return null
}

const renderChart = () => {
  if (!chartContainer.value || !treeData.value) return

  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = echarts.init(chartContainer.value)
  
  const { nodes, links } = getVisibleNodes(treeData.value)

  const option = {
    title: {
      text: 'IR-Tree 结构图',
      left: 'center',
      top: 10
    },
    tooltip: {
       trigger: 'item',
       formatter: (params: any) => {
         if (params.dataType === 'node') {
           const node = treeData.value ? findNodeById(treeData.value, params.data.id) : null
           return `节点: ${params.data.name}<br/>层级: ${node?.level || '未知'}`
         }
         return ''
       }
     } as any,
    series: [{
      type: 'graph',
      layout: 'none',
      symbolSize: 20,
      roam: true,
      label: {
        show: true,
        position: 'bottom',
        fontSize: 10
      },
      edgeSymbol: ['none', 'arrow'],
      edgeSymbolSize: [0, 8],
      data: nodes,
      links: links,
      lineStyle: {
        opacity: 0.9,
        width: 2,
        curveness: 0
      },
      emphasis: {
        focus: 'adjacency',
        lineStyle: {
          width: 4
        }
      }
    }]
  }

  chartInstance.setOption(option)

  // 添加点击事件处理节点展开/折叠
  chartInstance.on('click', (params: any) => {
    if (params.dataType === 'node') {
      const nodeId = params.data.id
      if (expandedNodes.value.has(nodeId)) {
        expandedNodes.value.delete(nodeId)
      } else {
        expandedNodes.value.add(nodeId)
      }
      renderChart() // 重新渲染图表
    }
  })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.ir-tree-echarts-container {
  width: 100%;
  height: 400px;
  position: relative;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4CAF50;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #f56565;
}

.retry-btn {
  margin-top: 10px;
  padding: 8px 16px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.retry-btn:hover {
  background: #45a049;
}
</style>