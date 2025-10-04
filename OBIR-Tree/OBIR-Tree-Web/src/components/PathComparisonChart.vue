<template>
  <div class="path-comparison-chart">
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, defineProps } from 'vue';
import * as echarts from 'echarts';
import { nextTick } from 'vue';

// 定义属性：接收两条路径数据和配置项
const props = defineProps({
  // 搜索前的路径数组
  beforePath: {
    type: [Array, String],
    required: true
  },
  // 搜索后的路径数组
  afterPath: {
    type: [Array, String],
    required: true
  },
  // 图表高度
  height: {
    type: Number,
    default: 400
  },
  // 节点大小
  nodeSize: {
    type: Number,
    default: 3
  },
  // 连线长度（水平距离）
  lineLength: {
    type: Number,
    default: 100
  },
  // 最大垂直偏移量（根节点的子节点的偏移量）
  maxVerticalOffset: {
    type: Number,
    default: 100
  },
  // 偏移衰减因子（值越大衰减越快）
  offsetDecay: {
    type: Number,
    default: 1.5
  },
  // 颜色配置
  colors: {
    type: Object,
    default: () => ({
      before: '#4285f4', // 蓝色 - 搜索前
      after: '#ea4335',  // 红色 - 搜索后
      node: '#ffffff',
      border: '#333333'
    })
  },
  // 图例文本
  legendLabels: {
    type: Object,
    default: () => ({
      before: '搜索前路径',
      after: '搜索后路径'
    })
  }
});

// 图表实例和DOM引用
const chartRef = ref<HTMLDivElement>(null);
let chartInstance: echarts.ECharts | null = null;
// 存储所有节点信息，确保同一棵树共享节点
const allTreeNodes = new Map<string, any>();

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return;
  
  // 检测容器尺寸
  const { clientWidth, clientHeight } = chartRef.value;
  if (clientWidth === 0 || clientHeight === 0) {
    console.warn('图表容器尺寸为0，尝试重试');
    setTimeout(initChart, 100);
    return;
  }

  // 销毁已有实例
  if (chartInstance) {
    chartInstance.dispose();
  }
  
  // 清空节点缓存
  allTreeNodes.clear();
  
  // 创建新实例
  chartInstance = echarts.init(chartRef.value);
  
  // 设置图表配置
  const option = generateChartOption();
  console.log('生成的图例配置:', option.legend);
  chartInstance.setOption(option);
  chartInstance.resize();
};

// 标准化路径数据（支持数组和字符串格式）
const normalizePath = (path: any): number[] => {
  if (Array.isArray(path)) {
    return path.filter(item => typeof item === 'number' && !isNaN(item));
  } else if (typeof path === 'string') {
    return path.split('->')
      .map(item => parseFloat(item))
      .filter(num => !isNaN(num));
  }
  return [];
};

// 确保路径以根节点0起始，实现统一坐标系与同源起点
const ensureRoot = (path: number[]): number[] => {
  if (!Array.isArray(path) || path.length === 0) return [0];
  return path[0] === 0 ? path : [0, ...path];
};

  // 生成图表配置（共享一棵树 + 灰色虚线参考路径 + 叠加前后路径边）
  const generateChartOption = () => {
    // 标准化路径数据并统一以根节点0起始
    const normalizedBeforePath = ensureRoot(normalizePath(props.beforePath));
    const normalizedAfterPath = ensureRoot(normalizePath(props.afterPath));

    // 预置四条参考路径（灰色虚线）
    const presetPaths: number[][] = [
      [0, 1, 3, 7, 15, 31, 63, 127, 255, 511, 1023, 2047, 4095, 8191, 16383, 32767], // 最左侧路径
      [0, 2, 6, 14, 30, 62, 126, 254, 510, 1022, 2046, 4094, 8190, 16382, 32766, 65534], // 最右侧路径
      [0, 1, 4, 10, 22, 46, 94, 190, 382, 766, 1534, 3068, 6136, 12272, 24540, 49082], // 根的左子节点的最右侧路径
      [0, 2, 5, 11, 23, 47, 95, 191, 383, 767, 1535, 3070, 6138, 12274, 24542, 49084], // 根的右子节点的最左侧路径
    ].map(ensureRoot);

    // 注册所有节点（共享坐标）：先处理前/后路径，再处理参考路径
    processPathData(normalizedBeforePath, props.colors.before);
    processPathData(normalizedAfterPath, props.colors.after);
    presetPaths.forEach((p) => processPathData(p, '#999999'));

    // 基础节点集合（唯一）
    const baseNodes = Array.from(allTreeNodes.values());

    // 路径集合用于着色
    const beforeSet = new Set(normalizedBeforePath.map((v) => v.toString()));
    const afterSet = new Set(normalizedAfterPath.map((v) => v.toString()));

    // 为基础节点着色：前蓝、后红、重合蓝红渐变、其他白底灰框
    baseNodes.forEach((node: any) => {
      const inBefore = beforeSet.has(node.id);
      const inAfter = afterSet.has(node.id);
      if (inBefore && inAfter) {
        node.itemStyle = {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: props.colors.before },
            { offset: 1, color: props.colors.after },
          ]),
          borderColor: '#333333',
          borderWidth: 1,
        };
      } else if (inBefore) {
        node.itemStyle = {
          color: props.colors.before,
          borderColor: props.colors.before,
          borderWidth: 1,
        };
      } else if (inAfter) {
        node.itemStyle = {
          color: props.colors.after,
          borderColor: props.colors.after,
          borderWidth: 1,
        };
      } else {
        node.itemStyle = {
          color: props.colors.node,
          borderColor: '#999999',
          borderWidth: 1,
        };
      }
      node.symbolSize = props.nodeSize;
    });

    // 参考路径灰色虚线连线集合
    const greyLinks: any[] = [];
    const addGreyLinks = (path: number[]) => {
      let parent: any = null;
      path.forEach((value, level) => {
        const id = value.toString();
        if (level === 0) {
          parent = allTreeNodes.get(id);
          return;
        }
        const curr = allTreeNodes.get(id);
        if (parent && curr) {
          greyLinks.push({
            source: parent.id,
            target: curr.id,
            lineStyle: { color: '#999999', width: 1, type: 'dashed' },
          });
          parent = curr;
        }
      });
    };
    presetPaths.forEach(addGreyLinks);

    // 生成指定颜色的连线（连接共享节点，不重复节点）
    const buildColoredLinks = (path: number[], color: string): any[] => {
      const colored: any[] = [];
      let parent: any = null;
      path.forEach((value, level) => {
        const id = value.toString();
        const curr = allTreeNodes.get(id);
        if (!curr) return;
        if (level > 0 && parent) {
          colored.push({
            source: parent.id,
            target: curr.id,
            lineStyle: { color, width: 2, type: 'solid' },
          });
        }
        parent = curr;
      });
      return colored;
    };

    const beforeLinks = buildColoredLinks(normalizedBeforePath, props.colors.before);
    const afterLinks = buildColoredLinks(normalizedAfterPath, props.colors.after);

    return {
      // 图例：显示 前/后/边界路径
      legend: {
        data: [
          { name: props.legendLabels.before, icon: 'line', textStyle: { color: props.colors.before } },
          { name: props.legendLabels.after, icon: 'line', textStyle: { color: props.colors.after } },
          { name: '边界路径', icon: 'line', textStyle: { color: '#999999' } },
        ],
        top: 10,
        right: 10,
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        borderWidth: 1,
        borderColor: '#ddd',
        padding: [5, 10],
      },
      tooltip: {
        formatter: function (params: any) {
          return `层级: ${params.data?.level || 'N/A'}<br>节点值: ${params.data?.value || params.data?.name || 'N/A'}`;
        },
      },
      series: [
        {
          name: props.legendLabels.before, // 与图例名称一致
          type: 'graph',
          layout: 'none',
          symbolSize: props.nodeSize,
          roam: true,
          label: { show: false },
          edgeSymbol: ['none', 'none'],
          edgeLabel: { show: false },
          data: baseNodes,
          links: beforeLinks,
          lineStyle: { width: 2, type: 'solid' },
          z: 3, // 层级高于参考线
        },
        // 搜索后路径系列
        {
          name: props.legendLabels.after, // 与图例名称一致
          type: 'graph',
          layout: 'none',
          symbolSize: props.nodeSize,
          roam: true,
          label: { show: false },
          edgeSymbol: ['none', 'none'],
          edgeLabel: { show: false },
          data: baseNodes,
          links: afterLinks,
          lineStyle: { width: 2, type: 'solid' },
          z: 2, // 层级高于参考线
        },
        // 边界路径系列
        {
          name: '边界路径', // 与图例名称一致
          type: 'graph',
          layout: 'none',
          symbolSize: props.nodeSize,
          roam: true,
          label: { show: false },
          edgeSymbol: ['none', 'none'],
          edgeLabel: { show: false },
          data: baseNodes,
          links: greyLinks,
          lineStyle: { width: 1, type: 'dashed' },
          z: 1, // 层级最低
        }
      ],
    };
  };

// 处理路径数据，生成节点和连线信息（共享同一棵树）
const processPathData = (path: number[], color: string) => {
  if (!Array.isArray(path) || path.length === 0) {
    console.warn('无效的路径数据，使用默认路径', path);
    path = [0]; // 默认根节点
  }

  const nodes: any[] = [];
  const links: any[] = [];
  let parentNode: any = null;
  
  // 为每个节点生成坐标
  path.forEach((value, level) => {
    if (typeof value !== 'number' || isNaN(value)) {
      console.warn(`路径中存在无效节点值: ${value} 在层级 ${level}`);
      return;
    }

    const nodeId = value.toString();
    
    // 如果节点已存在，直接使用（共享坐标与唯一节点）
    if (allTreeNodes.has(nodeId)) {
      const existingNode = allTreeNodes.get(nodeId);
      nodes.push(existingNode);

      // 添加连线（跳过根节点）
      if (level > 0 && parentNode) {
        links.push({
          source: parentNode.id,
          target: existingNode.id,
          lineStyle: {
            color: color,
            arrow: false,
            width: 1,
          },
        });
      }

      parentNode = existingNode;
      return;
    }
    
    // 计算节点坐标
    let x = level * props.lineLength;
    let y = 0;
    
    // 根节点（level 0）
    if (level === 0) {
      x = 0;
      y = 0;
    } 
    // 子节点
    else if (parentNode) {
      // 计算偏移量：随层级增加而减小（衰减）
      const offset = props.maxVerticalOffset / Math.pow(level, props.offsetDecay);
      
      // 偶数：右子节点，向上偏移
      // 奇数：左子节点，向下偏移
      y = value % 2 === 0 
        ? parentNode.y - offset 
        : parentNode.y + offset;
    }
    
    // 创建新节点
    const newNode = {
      id: nodeId,
      name: value.toString(),
      value: value,
      level: level,
      x: x,
      y: y,
      itemStyle: {
        color: color, // 实心节点
        borderColor: color,
        borderWidth: 1
      },
      symbolSize: props.nodeSize
    };
    
    // 缓存节点
    allTreeNodes.set(nodeId, newNode);
    nodes.push(newNode);
    
    // 添加连线（跳过根节点）
    if (level > 0 && parentNode) {
      links.push({
        source: parentNode.id,
        target: newNode.id,
        lineStyle: {
          color: color
        }
      });
    }
    
    parentNode = newNode;
  });
  
  return { nodes, links };
};

// 监听容器大小变化，重绘图表
const handleResize = () => {
  chartInstance?.resize();
};

// 监听属性变化，更新图表
watch(
  () => [props.beforePath, props.afterPath, props.height, props.nodeSize, props.lineLength, props.maxVerticalOffset, props.offsetDecay, props.colors, props.legendLabels],
  async () => {
    if (chartRef.value && props.height) {
      chartRef.value.style.height = `${props.height}px`;
    }

    if (!chartInstance) {
      await nextTick();
      initChart();
    } else {
      allTreeNodes.clear(); // 清除节点缓存
      chartInstance.setOption(generateChartOption());
      chartInstance.resize();
    }
  },
  { deep: true }
);

// 生命周期钩子
onMounted(() => {
  nextTick(() => {
    if (chartRef.value && props.height) {
      chartRef.value.style.height = `${props.height}px`;
    }
    initChart();
    window.addEventListener('resize', handleResize);
  });
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (chartInstance) {
    chartInstance.dispose();
    chartInstance = null;
  }
});
</script>

<style scoped>
.path-comparison-chart {
  width: 100%;
  height: 100%;
  min-height: 400px;
  padding: 10px;
  box-sizing: border-box;
}

.chart-container {
  width: 100%;
  height: 100%;
  min-height: 400px;
  overflow: visible;
}
</style>