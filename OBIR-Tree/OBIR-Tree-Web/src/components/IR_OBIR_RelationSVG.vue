<template>
  <div class="ir-obir-relation-container">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>正在加载IR-OBIR映射关系图...</p>
    </div>
    <div v-else-if="error" class="error">
      <p>数据暂不可用</p>
      <button @click="loadSVG" class="retry-btn">重试</button>
    </div>
    <div v-else class="relation-content">
      <!-- SVG图区域 -->
      <div class="svg-section">
        <h6>映射关系图</h6>
        <div class="svg-wrapper" v-html="svgContent"></div>
      </div>
      
      <!-- 标注区域 -->
      <div class="annotation-section">
        <h6>映射说明</h6>
        <div class="annotations">
          <div v-for="(annotation, index) in annotations" :key="index" class="annotation-item">
            <div class="annotation-header">
              <span class="annotation-type" :class="annotation.type">{{ annotation.type }}</span>
              <span class="annotation-id">{{ annotation.id }}</span>
            </div>
            <div class="annotation-content">
              <p class="annotation-title">{{ annotation.title }}</p>
              <p class="annotation-desc">{{ annotation.description }}</p>
              <div v-if="annotation.details" class="annotation-details">
                <div v-for="(detail, key) in annotation.details" :key="key" class="detail-item">
                  <span class="detail-label">{{ key }}:</span>
                  <span class="detail-value">{{ detail }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

interface Props {
  mappingFile?: string; // 映射关系文件
  annotationFile?: string; // 标注文件
}

const props = withDefaults(defineProps<Props>(), {
  mappingFile: 'ir_obir_mapping.json',
  annotationFile: 'ir_obir_annotations.json'
});

const loading = ref(true);
const error = ref('');
const svgContent = ref('');
const annotations = ref<any[]>([]);

const loadSVG = async () => {
  try {
    loading.value = true;
    error.value = '';
    
    // 调用后端API获取SVG和标注 - 使用相对路径，通过Vite代理
    const response = await fetch('/api/ir-obir-relation-svg', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        mappingFile: props.mappingFile,
        annotationFile: props.annotationFile
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    
    if (result.success) {
      svgContent.value = result.svg;
      annotations.value = result.annotations || [];
    } else {
      throw new Error(result.error || '生成映射关系图失败');
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
.ir-obir-relation-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 400px;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: #666;
  padding: 40px;
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
  padding: 40px;
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

.relation-content {
  display: flex;
  height: 100%;
  gap: 20px;
}

.svg-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.svg-section h6 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 14px;
  font-weight: 600;
}

.svg-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  overflow: auto;
}

.svg-wrapper :deep(svg) {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
}

.annotation-section {
  width: 300px;
  display: flex;
  flex-direction: column;
}

.annotation-section h6 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 14px;
  font-weight: 600;
}

.annotations {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.annotation-item {
  background: #fff;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.annotation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.annotation-type {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.annotation-type.ir {
  background: #e3f2fd;
  color: #1976d2;
}

.annotation-type.obir {
  background: #f3e5f5;
  color: #7b1fa2;
}

.annotation-type.mapping {
  background: #e8f5e8;
  color: #388e3c;
}

.annotation-id {
  font-size: 12px;
  color: #666;
  font-family: monospace;
}

.annotation-content {
  font-size: 13px;
}

.annotation-title {
  margin: 0 0 4px 0;
  font-weight: 600;
  color: #333;
}

.annotation-desc {
  margin: 0 0 8px 0;
  color: #666;
  line-height: 1.4;
}

.annotation-details {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  font-size: 12px;
}

.detail-label {
  color: #666;
  font-weight: 500;
}

.detail-value {
  color: #333;
  font-family: monospace;
}
</style>