<template>
  <div class="tree-chart-container">
    <v-chart 
      ref="chartRef" 
      class="tree-chart" 
      :option="chartOption" 
      @click="onNodeClick"
      autoresize
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { use } from 'echarts/core'
import { TreeChart } from 'echarts/charts'
import {
  TooltipComponent,
  LegendComponent,
  TitleComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'

// 注册ECharts组件
use([
  CanvasRenderer,
  TreeChart,
  TooltipComponent,
  LegendComponent,
  TitleComponent
])

interface TreeNode {
  id: string
  label: string
  type: string
  level: number
  children?: TreeNode[]
}

interface TreeEdge {
  from: string
  to: string
}

interface TreeData {
  nodes: TreeNode[]
  edges: TreeEdge[]
}

const props = defineProps<{
  data: TreeData
  title?: string
  layout?: 'orthogonal' | 'radial'
  orient?: 'LR' | 'RL' | 'TB' | 'BT'
  symbolSize?: number
  lineStyle?: {
    color?: string
    width?: number
    type?: 'solid' | 'dashed' | 'dotted'
  }
}>()

const emit = defineEmits<{
  nodeClick: [node: TreeNode]
}>()

const chartRef = ref()

// 转换数据为ECharts树形结构
const convertToTreeData = (data: TreeData) => {
  if (!data || !data.nodes || !data.edges) return null
  
  // 创建节点映射
  const nodeMap = new Map()
  data.nodes.forEach(node => {
    nodeMap.set(node.id, {
      id: node.id,
      name: node.label,
      type: node.type,
      level: node.level,
      children: [],
      // 设置初始展开状态：前5层默认展开
      collapsed: node.level >= 5,
      itemStyle: {
        color: getNodeColor(node.type),
        borderColor: getNodeBorderColor(node.type),
        borderWidth: 2
      },
      label: {
        show: true,
        color: '#333',
        fontWeight: 'bold'
      }
    })
  })
  
  // 构建父子关系
  data.edges.forEach(edge => {
    const parent = nodeMap.get(edge.from)
    const child = nodeMap.get(edge.to)
    if (parent && child) {
      parent.children.push(child)
    }
  })
  
  // 找到根节点
  const rootNode = data.nodes.find(node => node.type === 'root')
  return rootNode ? nodeMap.get(rootNode.id) : null
}

// 根据节点类型获取颜色
const getNodeColor = (type: string) => {
  const colorMap: Record<string, string> = {
    root: '#ff6b6b',
    node: '#4ecdc4',
    leaf: '#45b7d1',
    default: '#95a5a6'
  }
  return colorMap[type] || colorMap.default
}

// 根据节点类型获取边框颜色
const getNodeBorderColor = (type: string) => {
  const colorMap: Record<string, string> = {
    root: '#e74c3c',
    node: '#26a69a',
    leaf: '#3498db',
    default: '#7f8c8d'
  }
  return colorMap[type] || colorMap.default
}

// ECharts配置
const chartOption = computed(() => {
  const treeData = convertToTreeData(props.data)
  if (!treeData) return {}
  
  return {
    title: {
      text: props.title || '',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#333'
      }
    },
    tooltip: {
      trigger: 'item',
      triggerOn: 'mousemove',
      formatter: (params: any) => {
        const data = params.data
        return `
          <div style="padding: 8px;">
            <div><strong>节点ID:</strong> ${data.id}</div>
            <div><strong>标签:</strong> ${data.name}</div>
            <div><strong>类型:</strong> ${data.type}</div>
            <div><strong>层级:</strong> ${data.level}</div>
          </div>
        `
      }
    },
    series: [
      {
        type: 'tree',
        data: [treeData],
        top: '10%',
        left: '10%',
        bottom: '10%',
        right: '10%',
        symbolSize: props.symbolSize || 12,
        layout: props.layout || 'orthogonal',
        orient: props.orient || 'TB',
        label: {
          position: 'bottom',
          verticalAlign: 'middle',
          align: 'center',
          fontSize: 12,
          fontWeight: 'bold',
          color: '#333'
        },
        leaves: {
          label: {
            position: 'bottom',
            verticalAlign: 'middle',
            align: 'center'
          }
        },
        emphasis: {
          focus: 'descendant'
        },
        expandAndCollapse: true,
        animationDuration: 550,
        animationDurationUpdate: 750,
        lineStyle: {
          color: props.lineStyle?.color || '#ccc',
          width: props.lineStyle?.width || 2,
          type: props.lineStyle?.type || 'solid',
          curveness: 0.3
        }
      }
    ]
  }
})

// 节点点击事件
const onNodeClick = (params: any) => {
  if (params.componentType === 'series' && params.seriesType === 'tree') {
    const nodeData = params.data
    const node: TreeNode = {
      id: nodeData.id,
      label: nodeData.name,
      type: nodeData.type,
      level: nodeData.level
    }
    emit('nodeClick', node)
  }
}

// 监听数据变化
watch(() => props.data, () => {
  if (chartRef.value) {
    chartRef.value.setOption(chartOption.value, true)
  }
}, { deep: true })

// 组件挂载后调整图表大小
onMounted(() => {
  setTimeout(() => {
    if (chartRef.value) {
      chartRef.value.resize()
    }
  }, 100)
})

// 暴露方法给父组件
defineExpose({
  resize: () => {
    if (chartRef.value) {
      chartRef.value.resize()
    }
  }
})
</script>

<style scoped>
.tree-chart-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.tree-chart {
  width: 100%;
  height: 100%;
  min-height: 400px;
}
</style>