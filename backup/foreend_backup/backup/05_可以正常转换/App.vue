<script setup>
</script>

<template>
  <div class="app-container">
    <div class="app-layout">
      <!-- 浮动导航图标 -->
      <div class="floating-nav">
        <router-link to="/map" class="nav-icon" title="地图展示">🗺️</router-link>
        <router-link to="/data" class="nav-icon" title="查询过程展示">📊</router-link>
      </div>

      <!-- 右侧内容区域 -->
      <main class="content-area">
        <header class="app-header">
          <h1>OBIR_tree</h1>
          <p>{{ $route.meta.title || '交互式地图展示与数据可视化' }}</p>
        </header>
        <div class="page-content">
          <router-view :key="$route.path" />
        </div>
        <footer class="app-footer">
          <p>© 2023 地图应用演示 | 使用百度地图API</p>
        </footer>
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-container {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-layout {
  display: block;
  flex: 1;
  overflow: hidden;
}

/* 浮动导航图标样式 */
.floating-nav {
  position: fixed;
  top: 50%;
  left: 20px;
  transform: translateY(-50%);
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.nav-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: #42b983;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  text-decoration: none;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.nav-icon:hover {
  transform: scale(1.1);
  background-color: #35495e;
}

.nav-icon.router-link-exact-active {
  background-color: #2c3e50;
}

/* 右侧内容区域样式 */
.content-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #f5f7fa;
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
  height: 500px;
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

.page-content {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
  margin-bottom: 20px;
  min-height: calc(100% - 180px);
}

.app-footer {
  text-align: center;
  padding: 15px;
  color: #666;
  font-size: 0.9rem;
  border-top: 1px solid #eee;
  margin-top: 20px;
}

/* 响应式布局调整 */
@media (max-width: 992px) {
  .sidebar {
    width: 200px;
  }
}

@media (max-width: 768px) {
  .app-layout {
    flex-direction: column;
  }
  .sidebar {
    width: 100%;
    height: auto;
  }
  .nav-menu {
    display: flex;
    padding: 10px 0;
  }
  .nav-item {
    flex: 1;
    justify-content: center;
    padding: 10px;
  }
  .nav-icon {
    margin-right: 5px;
  }
  .nav-text {
    font-size: 0.85rem;
  }
  .content-area {
    padding: 15px;
  }
  .app-header h1 {
    font-size: 1.8rem;
  }
  .page-content {
    padding: 15px;
  }
}

@media (max-width: 480px) {
  .nav-text {
    display: none;
  }
  .nav-icon {
    margin-right: 0;
    font-size: 1.4rem;
  }
  .app-header {
    padding: 15px;
  }
  .app-header h1 {
    font-size: 1.5rem;
  }
}
</style>
