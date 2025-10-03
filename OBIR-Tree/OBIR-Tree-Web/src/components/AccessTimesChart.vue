<template>
  <div class="access-times-chart-container">
    <div ref="chartRef" class="access-times-chart-wrapper"></div>
    <div v-if="isLoading" class="chart-loading">加载中...</div>
    <div v-if="isError" class="chart-error">数据加载失败，请刷新重试</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, defineProps, watch } from 'vue';
import * as echarts from 'echarts';
import { useChartStore } from '@/store/chartStores';

// 定义组件属性
const props = defineProps({
  // 数据类型：single 或 multiple
  dataType: {
    type: String,
    required: true,
    validator: (value: string) => ['single', 'multiple'].includes(value)
  },
  // 数据范围起始值
  start: {
    type: Number,
    default: 1
  },
  // 数据范围结束值
  end: {
    type: Number,
    default: 1000
  },
  // 图表标题
  title: {
    type: String,
    default: '块访问次数统计'
  },
  manualData: {
    type: Array as () => Array<{ block_id: number; accessed_time: number }>,
    default: null
  }
});

// 状态管理
const chartRef = ref<HTMLDivElement | null>(null);
let chartInstance: echarts.ECharts | null = null;
const accessTimesData = ref<Array<{ block_id: number; accessed_time: number }>>([]);
const isLoading = ref<boolean>(false);
const isError = ref<boolean>(false);

// 数据请求方法
const fetchData = async () => {
  try {
    // 防抖/并发保护：如果正在加载中，直接返回，避免并发二次请求
    if (isLoading.value) return;

    isLoading.value = true;
    isError.value = false;
    

    // 如果手动传入数据，直接使用
    if (props.manualData) {
      accessTimesData.value = props.manualData;
      initChart();
      isLoading.value = false;
      return;
    }

  // 对于multiple类型，先检查缓存
    if (props.dataType === 'multiple') {
      const chartStore = useChartStore();
      const cachedData = chartStore.getMultipleAccessTimes();
      if (cachedData) {
        accessTimesData.value = cachedData;
        initChart();
        isLoading.value = false;
        return; // 直接使用缓存数据，不发起请求
      }
    }

    // 根据数据类型选择不同接口
    const url = props.dataType === 'single' 
      ? `http://localhost:8080/single-accessed-times?start=${props.start}&end=${props.end}`
      : `http://localhost:8080/accessed-times?start=${props.start}&end=${props.end}`;
      
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    console.log('访问次数数据:', result);
    if (result.status === 'success' && Array.isArray(result.access_times)) {
    // 转换字段名以匹配前端期望的结构
    accessTimesData.value = result.access_times.map(item => ({
      block_id: item.block_id,
      accessed_time: item.accessed_count  // 将 accessed_count 映射为 accessed_time
    }));

    // 对于multiple类型，存入缓存（同样需要转换字段名）
    if (props.dataType === 'multiple') {
      const chartStore = useChartStore();
      chartStore.setMultipleAccessTimes(accessTimesData.value);
    }

    initChart();
  } else {
    console.error('访问次数数据格式错误:', result);
      isError.value = true;
  }
  } catch (error) {
    console.error('获取访问次数数据失败:', error);
    isError.value = true;
  } finally {
    isLoading.value = false;
  }
};

// 图表初始化方法
const initChart = () => {
  if (!chartRef.value) {
    console.warn('图表容器 DOM 未找到');
    return;
  }

  // 检查容器宽高
  const dom = chartRef.value;
  const clientWidth = dom.clientWidth;
  const clientHeight = dom.clientHeight;
  
  if (clientWidth === 0 || clientHeight === 0) {
    console.warn('图表容器宽高为 0，100ms 后重试初始化');
    setTimeout(initChart, 100);
    return;
  }

  // 销毁已有实例
  if (chartInstance) {
    chartInstance.dispose();
  }

  // 创建新实例
  chartInstance = echarts.init(dom);

  // 图表配置项
  const chartOption: echarts.EChartsOption = {
    title: {
      text: `${props.title} (${props.start}-${props.end})`,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#333'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any[]) => {
        const target = params[0];
        return `块ID: ${target.name}<br/>访问次数: ${target.value}`;
      },
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: '#eee',
      borderWidth: 1
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: accessTimesData.value.map(item => item.block_id),
      axisLabel: {
        interval: 49,
        rotate: 0,
        fontSize: 12,
        color: '#666'
      },
      axisLine: { lineStyle: { color: '#eee' } },
      name: 'Block ID',
      nameTextStyle: { fontSize: 13, color: '#999' },
      nameLocation: 'middle',
      nameGap: 30
    },
    yAxis: {
      type: 'value',
      min: 0,
      axisLabel: {
        fontSize: 12,
        color: '#666',
        formatter: '{value} '
      },
      axisLine: { lineStyle: { color: '#eee' } },
      splitLine: { lineStyle: { color: '#f5f5f5' } },
      name: 'TIMES',
      nameTextStyle: { fontSize: 13, color: '#999' },
      nameLocation: 'middle',
      nameGap: 50
    },
    dataZoom: [
      {
        type: 'slider',
        show: true,
        xAxisIndex: [0],
        start: 0,
        end: 10,
        height: 16,
        bottom: 5,
        borderColor: '#eee',
        fillerColor: 'rgba(84, 112, 198, 0.2)',
        handleColor: '#5470c6'
      },
      {
        type: 'inside',
        xAxisIndex: [0],
        start: 0,
        end: 10
      }
    ],
    series: [
      {
        name: '访问次数',
        type: 'bar',
        data: accessTimesData.value.map(item => item.accessed_time),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#5470c6' },
            { offset: 1, color: '#91cc75' }
          ]),
          borderRadius: 4
        },
        barWidth: '60%',
        emphasis: {
          itemStyle: { color: '#5470c6' }
        }
      }
    ]
  };

  chartInstance.setOption(chartOption);

  // 窗口大小变化响应
  const handleResize = () => {
    chartInstance?.resize();
  };
  window.addEventListener('resize', handleResize);

  // 组件卸载时清理
  onUnmounted(() => {
    window.removeEventListener('resize', handleResize);
    chartInstance?.dispose();
    chartInstance = null;
  });
};

// 监听数据类型变化重新加载数据
watch(
  () => [props.dataType, props.start, props.end],
  () => {
    fetchData();
  },
  { immediate: true }
);
// 移除 onMounted 中的重复调用，避免与 watch({ immediate: true }) 造成的双请求
// onMounted(async () => {
//   await nextTick();
//   fetchData();
// });
</script>

<style scoped>
.access-times-chart-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 300px;
}

.access-times-chart-wrapper {
  width: 100%;
  height: 100%;
  min-height: 300px;
}

.chart-loading, .chart-error {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.8);
  color: #666;
  font-size: 16px;
}

.chart-error {
  color: #f44336;
}
</style>