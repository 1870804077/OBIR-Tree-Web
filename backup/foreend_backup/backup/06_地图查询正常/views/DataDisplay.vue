<script setup>
import { RouterLink, useRouter } from 'vue-router';
const router = useRouter();

const goBack = () => {
  console.log('触发返回导航到/map');
  router.push('/map').catch(err => {
    console.error('导航失败:', err);
  });
};
</script>

<template>
  <div class="data-display-container">
    <h2>查询过程展示</h2>

    <!-- OBIR_Tree展示区域 -->
    <div class="section obir-tree-container">
      <h3>OBIR_Tree展示</h3>
      <div class="tree-placeholder">
        <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMDAiIGhlaWdodD0iMjUwIiBmaWxsPSJ3aGl0ZSI+PGNpcmNsZSBjeD0iMTUwIiBjeT0iMTI1IiByPSI4MCIgZmlsbD0iI2Y5ZjlmOSIvPjwvc3ZnPg==" alt="空白图" class="blank-image">
      </div>
    </div>

    <!-- 搜索与返回栏 -->
    <div class="section search-bar">
      <div class="search-container">
        <input type="text" placeholder="输入搜索关键词..." class="search-input">
        <button class="search-button">搜索</button>
        <button @click="goBack" class="back-button">返回</button>
      </div>
    </div>

    <!-- 查询流程节点图 -->
    <div class="section process-node-graph">
      <h3>查询流程节点图</h3>
      <div class="graph-placeholder">
        <p>查询流程节点可视化将在此显示</p>
        <div class="loading-indicator"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.data-display-container {
  padding: 20px 20px 20px 80px; /* 增加左侧内边距 */
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: calc(100vh - 200px);
  overflow-y: auto;
}

h2 {
  color: #333;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.section {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  padding: 25px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.section:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
}

h3 {
  color: #444;
  margin-top: 0;
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

/* OBIR Tree 样式 */
.obir-tree-container {
  min-height: 320px;
}

.tree-placeholder, .graph-placeholder {
  border: 1px dashed #ccc;
  transition: all 0.3s ease;
}

.tree-placeholder:hover, .graph-placeholder:hover {
  border-color: #42b983;
  background-color: #f5fff8;
}

.tree-placeholder {
  height: 250px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.blank-image {
  max-width: 100%;
  max-height: 100%;
  opacity: 0.5;
}

/* 搜索栏样式 */
.search-bar {
  padding: 15px 25px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4eaf5 100%);
}

.search-container {
  display: flex;
  gap: 12px;
  align-items: center;
  max-width: 800px;
  margin: 0 auto;
}

.search-input {
  flex: 1;
  padding: 12px 18px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
}

.search-button, :deep(.back-button) {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s ease;
}

.search-button {
  background-color: #42b983;
  color: white;
}

.back-button {
  background-color: #f0f0f0;
  color: #333;
}

.search-button:hover {
  background-color: #359469;
}

:deep(.back-button:hover) {
  background-color: #e0e0e0;
}

/* 流程节点图样式 */
.process-node-graph {
  min-height: 300px;
}

.graph-placeholder {
  height: 350px;
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