<template>
  <div class="summary-container">
    <h2>总结页面</h2>
    <div class="summary-card">
      <h3>应用概况</h3>
      <p>本应用集成百度地图API，提供地图可视化与数据分析功能。通过三个功能页面，用户可以查看地理信息、浏览统计数据并获取综合分析报告。</p>
    </div>

    <div class="features-list">
      <h3>核心功能</h3>
      <ul>
        <li><span class="feature-icon">🗺️</span> 交互式地图浏览，支持缩放、平移和类型切换</li>
        <li><span class="feature-icon">📍</span> 标记点管理与信息展示</li>
        <li><span class="feature-icon">📊</span> 地理数据统计与可视化图表</li>
        <li><span class="feature-icon">🔍</span> 区域数据筛选与查询</li>
        <li><span class="feature-icon">📋</span> 综合数据分析报告生成</li>
      </ul>
    </div>

    <div class="stats-summary">
      <h3>使用统计</h3>
      <div class="stats-grid">
        <div class="stat-item">
          <p class="stat-value">24</p>
          <p class="stat-label">地图标记点</p>
        </div>
        <div class="stat-item">
          <p class="stat-value">6</p>
          <p class="stat-label">数据类别</p>
        </div>
        <div class="stat-item">
          <p class="stat-value">3</p>
          <p class="stat-label">分析维度</p>
        </div>
        <div class="stat-item">
          <p class="stat-value">100%</p>
          <p class="stat-label">数据完整性</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.summary-container {
  padding: 20px;
}

h2 {
  color: #333;
  margin-bottom: 25px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

h3 {
  color: #444;
  margin-top: 0;
}

.summary-card {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 25px;
  margin-bottom: 30px;
  line-height: 1.6;
  color: #555;
}

.features-list {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 25px;
  margin-bottom: 30px;
}

.features-list ul {
  list-style-type: none;
  padding: 0;
}

.features-list li {
  padding: 12px 0;
  border-bottom: 1px solid #f5f5f5;
  display: flex;
  align-items: center;
}

.features-list li:last-child {
  border-bottom: none;
}

.feature-icon {
  margin-right: 15px;
  font-size: 1.2rem;
  color: #42b983;
  min-width: 24px;
}

.stats-summary {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 25px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
  margin-top: 15px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #42b983;
  margin: 0 0 5px 0;
}

.stat-label {
  color: #666;
  margin: 0;
  font-size: 0.9rem;
}
</style>