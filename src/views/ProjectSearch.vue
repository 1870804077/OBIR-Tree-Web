<template>
  <router-view />
</template>
<script setup lang="ts">
// 检索过程父页面
</script>

<style scoped>
.map-container {
  width: 100%;
  height: calc(100vh - 100px);
  position: relative;
  margin-left: 0;
  box-sizing: border-box;
  overflow: hidden;
}
.page-header {
  margin-bottom: 10px;
}
.controls {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 10px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
.controls button {
  padding: 8px 16px;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.search-box {
  display: flex;
  gap: 10px;
}
.search-box input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}
#baidu-map {
  width: 100%;
  height: 100vh;
}
.error-message {
  color: red;
  padding: 10px;
  text-align: center;
}
</style> 