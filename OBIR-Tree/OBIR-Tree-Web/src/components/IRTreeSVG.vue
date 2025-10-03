<template>
  <div class="ir-tree-svg-container">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>正在加载IR-Tree结构图...</p>
    </div>
    <div v-else-if="error" class="error">
      <p>数据暂不可用</p>
      <button @click="loadSVG" class="retry-btn">重试</button>
    </div>
    <div v-else class="svg-wrapper" v-html="svgContent"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

interface Props {
  dataFile?: string; // 可选的数据文件路径
}

const props = withDefaults(defineProps<Props>(), {
  dataFile: 'ir_tree_data.json' // 默认数据文件
});

const loading = ref(true);
const error = ref('');
const svgContent = ref('');

const loadSVG = async () => {
  try {
    loading.value = true;
    error.value = '';
    
    // 调用后端API获取SVG - 使用相对路径，通过Vite代理
    const response = await fetch('/api/ir-tree-svg', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        dataFile: props.dataFile
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    
    if (result.success) {
      svgContent.value = result.svg;
    } else {
      throw new Error(result.error || '生成SVG失败');
    }
  } catch (err) {
    error.value = '加载失败';
    console.error('无法获取后端的返回结果，错误为', err);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadSVG();
});
</script>

<style scoped>
.ir-tree-svg-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #42b983;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  text-align: center;
  color: #e74c3c;
}

.retry-btn {
  margin-top: 12px;
  padding: 8px 16px;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.retry-btn:hover {
  background: #359469;
}

.svg-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  border: 1px solid #ddd;
  background: #f9f9f9;
}

.svg-wrapper :deep(svg) {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  display: block;
  margin: 0 auto;
}
</style>