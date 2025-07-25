<template>
  <div class="data-display-container">
    <h2>数据展示页面</h2>
    <div class="data-card">
      <h3>地图数据统计</h3>
      <div class="data-grid">
        <div class="data-item">
          <p class="data-label">标记点数量</p>
          <p class="data-value">24</p>
        </div>
        <div class="data-item">
          <p class="data-label">覆盖区域</p>
          <p class="data-value">128 km²</p>
        </div>
        <div class="data-item">
          <p class="data-label">数据更新时间</p>
          <p class="data-value">2023-11-15</p>
        </div>
        <div class="data-item">
          <p class="data-label">活跃区域</p>
          <p class="data-value">6个</p>
        </div>
      </div>
    </div>

    <div class="chart-container">
      <h3>区域分布图表</h3>
      <div class="chart-placeholder">
        <p>图表将在此显示</p>
        <div class="loading-indicator"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.data-display-container {
  padding: 20px;
}

h2 {
  color: #333;
  margin-bottom: 25px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.data-card {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
  margin-bottom: 30px;
}

.data-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 15px;
}

.data-item {
  text-align: center;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.data-label {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.data-value {
  color: #333;
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
}

.chart-container {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
}

.chart-placeholder {
  height: 300px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: #f9f9f9;
  border-radius: 8px;
  color: #999;
}

.loading-indicator {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(66, 185, 131, 0.2);
  border-radius: 50%;
  border-top-color: #42b983;
  animation: spin 1s ease-in-out infinite;
  margin-top: 15px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>