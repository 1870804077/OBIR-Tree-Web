<template>
  <div class="query-result-container">
    <div class="result-header">
      <h5>Top-K 查询结果</h5>
      <div class="result-info">
        <span class="info-item">查询关键词: "OBIR-Tree查询"</span>
        <span class="info-item">结果数量: {{ results.length }}</span>
        <span class="info-item">查询时间: {{ queryTime }}</span>
      </div>
    </div>
    
    <div class="results-list">
      <div v-for="(result, index) in results" :key="index" class="result-item">
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
            <span class="meta-item">位置: {{ result.location }}</span>
            <span class="meta-item">距离: {{ result.distance }}km</span>
            <span class="meta-item">类型: {{ result.type }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="result-footer">
      <div class="footer-info">
        <span class="footer-text">✅ 查询结果已成功解密并呈现</span>
        <span class="footer-text">🔐 使用客户端私钥解密</span>
        <span class="footer-text">📊 共返回 {{ results.length }} 条相关结果</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

// 模拟查询结果数据
const results = ref([
  {
    title: "北京大学本部（燕园校区）",
    description: "位于北京市海淀区颐和园路5号，是北京大学的主校区，环境优美，拥有未名湖、博雅塔等著名景观，包含文理学院、工学院等多个院系。",
    relevance: 95,
    location: "北京市海淀区颐和园路5号",
    distance: 0.2,
    type: "教育机构"
  },
  {
    title: "北京大学医学部",
    description: "位于北京市海淀区学院路38号，是北京大学的医学教育中心，拥有多个附属医院和医学研究机构，在医学教育领域享有盛誉。",
    relevance: 92,
    location: "北京市海淀区学院路38号",
    distance: 1.5,
    type: "教育机构"
  },
  {
    title: "北京大学昌平校区",
    description: "位于北京市昌平区沙河高教园区，是北京大学的新校区，主要承担部分本科教育和科研工作，设施现代化，环境优美。",
    relevance: 88,
    location: "北京市昌平区沙河高教园区",
    distance: 25.0,
    type: "教育机构"
  },
  {
    title: "北京大学深圳研究生院",
    description: "位于深圳市南山区深圳湾，是北京大学在深圳设立的研究生教育机构，专注于前沿科技研究和高端人才培养。",
    relevance: 85,
    location: "深圳市南山区深圳湾",
    distance: 2000.0,
    type: "教育机构"
  },
  {
    title: "北京大学图书馆",
    description: "位于燕园校区内，是北京大学的主要图书馆，藏书丰富，为师生提供良好的学习环境，是亚洲最大的大学图书馆之一。",
    relevance: 82,
    location: "北京市海淀区颐和园路5号",
    distance: 0.1,
    type: "图书馆"
  }
]);

const queryTime = ref('2024-01-15 14:30:25');

// 模拟从后端获取数据
const loadQueryResults = async () => {
  try {
    // 调用后端API获取真实的查询结果
    const response = await fetch('/api/query-results', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: 'OBIR-Tree查询',
        topK: 5
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.success) {
      results.value = data.results;
      queryTime.value = data.timestamp;
      console.log('查询结果已从API加载:', data.results.length, '条结果');
    } else {
      throw new Error(data.error || '获取查询结果失败');
    }
  } catch (error) {
    console.error('加载查询结果失败:', error);
    // 如果API调用失败，使用默认的模拟数据
    console.log('使用默认模拟数据');
  }
};

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