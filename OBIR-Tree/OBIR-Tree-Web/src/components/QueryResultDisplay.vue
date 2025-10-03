<template>
  <div class="query-result-container">
    <div class="result-header">
      <h5>Top-{{ topK }} 查询结果</h5>
      <div class="result-info">
        <span class="info-item">查询关键词: "{{ queryKeyword }}"</span>
        <span class="info-item">结果数量: {{ displayResults.length }}</span>
        <span class="info-item">查询时间: {{ queryTime }}</span>
      </div>
    </div>
    
    <div class="results-list">
      <div v-for="(result, index) in displayResults" :key="index" class="result-item">
        <div class="result-rank">
          <span class="rank-number">{{ index + 1 }}</span>
        </div>
        <div class="result-content">
          <div class="result-title">
            <span class="title-text">{{ result.title }}</span>
            <span class="relevance-score">相关度: {{ result.relevance }}%</span>
          </div>
          <div class="result-description">
            {{ result.description }}
          </div>
          <div class="result-meta">
            <span class="meta-item">坐标: ({{ result.lng }}, {{ result.lat }})</span>
            <span class="meta-item">类型: {{ result.type }}</span>
            <span class="meta-item">距离: {{ result.distance?.toFixed(4) }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="result-footer">
      <div class="footer-info">
        <span class="footer-text">✅ 查询结果已成功解密并呈现</span>
        <span class="footer-text">🔐 使用客户端私钥解密</span>
        <span class="footer-text">📊 共返回 {{ displayResults.length }} 条相关结果</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { searchAPI } from '../api';

// Props定义
const props = defineProps<{
  topK?: number;
  queryKeyword?: string;
}>();

// 响应式数据
const results = ref([]);
const queryTime = ref('');

// 计算属性
const topK = computed(() => props.topK || 10);
const queryKeyword = computed(() => props.queryKeyword || 'OBIR-Tree查询');

// 显示的结果（根据topK限制）
const displayResults = computed(() => {
  return results.value.slice(0, topK.value);
});

// 加载查询结果
const loadQueryResults = async () => {
  try {
    const data = await searchAPI.basicSearch({
      query: queryKeyword.value,
      top_k: topK.value,
      lng: 120.15958,
      lat: 30.28745,
    });

    if (data.success) {
      results.value = data.results || [];
      queryTime.value = data.timestamp || '';
      console.log('查询结果已从API加载:', results.value.length, '条结果');
    } else {
      throw new Error(data.error || '获取查询结果失败');
    }
  } catch (error) {
    console.error('无法获取查询结果，错误为', error);
  }
};

// 监听topK变化，重新加载数据
watch(() => props.topK, () => {
  loadQueryResults();
});

// 监听查询关键词变化，重新加载数据
watch(() => props.queryKeyword, () => {
  loadQueryResults();
});

onMounted(() => {
  loadQueryResults();
});
</script>

<style scoped>
.query-result-container {
  width: 100%;
  padding: 20px;
}

.result-header {
  margin-bottom: 20px;
  text-align: center;
}

.result-header h5 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.result-info {
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

.info-item {
  font-size: 13px;
  color: #666;
  padding: 4px 8px;
  background: #f0f0f0;
  border-radius: 4px;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-item {
  display: flex;
  gap: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  background: white;
  transition: all 0.3s ease;
}

.result-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.result-rank {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 40px;
}

.rank-number {
  width: 30px;
  height: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
}

.result-content {
  flex: 1;
}

.result-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.title-text {
  font-weight: 600;
  color: #333;
  font-size: 16px;
}

.relevance-score {
  font-size: 12px;
  color: #28a745;
  background: #d4edda;
  padding: 2px 6px;
  border-radius: 4px;
}

.result-description {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 8px;
}

.result-meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.meta-item {
  font-size: 12px;
  color: #888;
  background: #f8f9fa;
  padding: 2px 6px;
  border-radius: 4px;
}

.result-footer {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
}

.footer-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: center;
}

.footer-text {
  font-size: 12px;
  color: #666;
  font-style: italic;
}
</style>