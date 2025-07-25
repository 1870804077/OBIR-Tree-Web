<template>
  <div class="map-container">
    <div class="controls">
      <div class="search-box">
        <input type="text" v-model="searchKeyword" placeholder="搜索地址">
        <button @click="searchLocation">搜索</button>
      </div>
    </div>
    <div id="baidu-map"></div>
    <div v-if="searchError" class="error-message">{{ searchError }}</div>
  </div>
</template>

<script setup lang="ts">
// @ts-ignore
declare const BMap: any;
declare global {
  interface Window { baiduMapCallback?: () => void }
}
import { ref, onMounted, onUnmounted } from 'vue';

const map = ref<any>(null);
const searchKeyword = ref('');
const searchError = ref('');
let markers: any[] = [];
let geocoder: any = null;

const initMap = () => {
  const container = document.getElementById('baidu-map');
  if (!container) return;
  map.value = new BMap.Map(container);
  const point = new BMap.Point(116.404, 39.915);
  map.value.centerAndZoom(point, 15);
  map.value.enableScrollWheelZoom(true);
  map.value.addControl(new BMap.NavigationControl());
  geocoder = new BMap.Geocoder();
};

const searchLocation = () => {
  if (!searchKeyword.value.trim()) return;
  geocoder.getPoint(searchKeyword.value, (point: any) => {
    if (point) {
      map.value.centerAndZoom(point, 15);
      clearMarkers();
      const marker = new BMap.Marker(point);
      map.value.addOverlay(marker);
      markers.push(marker);
      searchError.value = '';
    } else {
      searchError.value = '未找到该地址';
    }
  });
};

const clearMarkers = () => {
  markers.forEach(marker => map.value.removeOverlay(marker));
  markers = [];
};

const loadMapScript = (): Promise<void> => {
  return new Promise<void>((resolve, reject) => {
    if (typeof BMap !== 'undefined') {
      resolve();
      return;
    }
    const script = document.createElement('script');
    script.src = 'https://api.map.baidu.com/api?v=3.0&ak=VcwXPliUc7qLq1R2AmlszV5S64fbRNGV&callback=baiduMapCallback';
    window.baiduMapCallback = () => {
      delete window.baiduMapCallback;
      resolve();
    };
    script.onerror = reject;
    document.head.appendChild(script);
  });
};

onMounted(async () => {
  try {
    await loadMapScript();
    initMap();
  } catch (error) {
    searchError.value = '地图加载失败';
    console.error(error);
  }
});

onUnmounted(() => {
  if (map.value) {
    map.value.clearOverlays();
    map.value = null;
  }
  const container = document.getElementById('baidu-map');
  if (container) {
    container.innerHTML = '';
  }
});
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