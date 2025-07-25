<script setup>
import MapPage from './views/MapPage.vue'
</script>

<template>
  <div class="app-container">
    <header class="app-header">
      <h1>地图展示</h1>
      <p>交互式地图展示与数据可视化</p>
    </header>
    <main class="map-container">
      <div class="map-frame">
        <MapPage />
      </div>
    </main>
    <footer class="app-footer">
      <p>© 2023 地图应用演示 | 使用百度地图API</p>
    </footer>
  </div>
</template>

<style scoped>
.app-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.app-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #42b983 0%, #35495e 100%);
  color: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  margin: 0 0 10px 0;
  font-size: 2.2rem;
  font-weight: 700;
}

.app-header p {
  margin: 0;
  font-size: 1.1rem;
  opacity: 0.9;
}

.map-container {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.map-frame {
  width: 100%;
  max-width: 1200px;
  height: 600px;
  border-radius: 12px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  border: 1px solid #e0e0e0;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.map-frame:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 25px rgba(0, 0, 0, 0.2);
}

.app-footer {
  text-align: center;
  padding: 15px;
  color: #666;
  font-size: 0.9rem;
  border-top: 1px solid #eee;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .app-container {
    padding: 10px;
  }
  .map-frame {
    height: 450px;
  }
  .app-header h1 {
    font-size: 1.8rem;
  }
}
</style>
