<template>
  <div class="map-container">
    <div class="controls">
      <div class="search-box">
        <input type="text" v-model="lng" placeholder="经度">
        <input type="text" v-model="lat" placeholder="纬度">
        <button @click="searchByCoordinate">按坐标查询</button>
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
import { useRoute } from 'vue-router';

const route = useRoute();

const map = ref<any>(null);
const searchError = ref('');
let markers: any[] = [];
let geocoder: any = null;
// 移除MarkerClusterer相关变量和加载逻辑
const lng = ref('');
const lat = ref('');

const initMap = () => {
  const container = document.getElementById('baidu-map');
  if (!container) return;
  map.value = new BMap.Map(container);
  const point = new BMap.Point(116.404, 39.915);
  map.value.centerAndZoom(point, 15);
  map.value.enableScrollWheelZoom(true);
  map.value.addControl(new BMap.NavigationControl());
  geocoder = new BMap.Geocoder();
  // 设置官方浅色地图样式（使用官方 styleId）
  map.value.setMapStyleV2({
    styleId: 'f2e9f0b6b7e3e7e6e7e6e7e6' // 百度官方浅色风格ID
  });
};

const searchByCoordinate = () => {
  const longitude = parseFloat(lng.value);
  const latitude = parseFloat(lat.value);
  if (isNaN(longitude) || isNaN(latitude)) {
    searchError.value = '请输入有效的经纬度';
    return;
  }
  const point = new BMap.Point(longitude, latitude);
  map.value.centerAndZoom(point, 15);
  clearMarkers();
  const marker = new BMap.Marker(point);
  map.value.addOverlay(marker);
  markers.push(marker);
  searchError.value = '';
};

const clearMarkers = () => {
  markers.forEach(marker => map.value.removeOverlay(marker));
  markers = [];
  // 移除MarkerClusterer相关清理
};

const addBatchMarkers = (pointsArr: Array<{lng: number, lat: number}>) => {
  if (!Array.isArray(pointsArr) || pointsArr.length === 0) return;
  clearMarkers();
  // 构造百度地图Point数组
  const bPoints = pointsArr.map(({lng, lat}) => new BMap.Point(lng, lat));
  // 配置样式
  const options = {
    size: 3, // 3像素
    shape: BMap?.POINT_SHAPE_CIRCLE || 0,
    color: '#cccccc' // 浅灰色
  };
  // 创建海量点覆盖物
  const pointCollection = new BMap.PointCollection(bPoints, options);
  map.value.addOverlay(pointCollection);
  markers.push(pointCollection);
  // 缩放到全国
  map.value.centerAndZoom(new BMap.Point(104.114129, 37.550339), 5);
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

const loadClustererScript = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    // 先加载TextIconOverlay
    if (!(window as any).BMapLib || !(window as any).BMapLib.TextIconOverlay) {
      const textIconScript = document.createElement('script');
      textIconScript.src = 'https://api.map.baidu.com/library/TextIconOverlay/1.2/src/TextIconOverlay_min.js';
      textIconScript.onload = () => {
        // 再加载MarkerClusterer
        const clustererScript = document.createElement('script');
        clustererScript.src = 'https://api.map.baidu.com/library/MarkerClusterer/1.2/src/MarkerClusterer_min.js';
        clustererScript.onload = () => resolve();
        clustererScript.onerror = reject;
        document.head.appendChild(clustererScript);
      };
      textIconScript.onerror = reject;
      document.head.appendChild(textIconScript);
    } else if (!(window as any).BMapLib.MarkerClusterer) {
      // 只需加载MarkerClusterer
      const clustererScript = document.createElement('script');
      clustererScript.src = 'https://api.map.baidu.com/library/MarkerClusterer/1.2/src/MarkerClusterer_min.js';
      clustererScript.onload = () => resolve();
      clustererScript.onerror = reject;
      document.head.appendChild(clustererScript);
    } else {
      resolve();
    }
  });
};

onMounted(async () => {
  try {
    await loadMapScript();
    initMap();
    // 优先检查是否有lng/lat参数（单点高亮）
    const lngParam = Number(route.query.lng);
    const latParam = Number(route.query.lat);
    if (!isNaN(lngParam) && !isNaN(latParam)) {
      clearMarkers();
      const point = new BMap.Point(lngParam, latParam);
      // 自定义更小更亮的红色空心圆点icon
      const icon = new BMap.Icon(
        'data:image/svg+xml;base64,' + btoa('<svg width="10" height="10" xmlns="http://www.w3.org/2000/svg"><circle cx="5" cy="5" r="4" fill="none" stroke="#ff1744" stroke-width="2"/></svg>'),
        new BMap.Size(10, 10)
      );
      const marker = new BMap.Marker(point, { icon });
      map.value.addOverlay(marker);
      markers.push(marker);
      
      // 检查是否为简单查看模式（不显示区域圈）
      const isSimpleView = route.query.simple === 'true';
      if (!isSimpleView) {
        // 添加1.5km半径的圆圈
        const circle = new BMap.Circle(point, 1500, {
          strokeColor: '#ff1744',
          strokeWeight: 2,
          strokeOpacity: 0.7,
          fillColor: '#ff1744',
          fillOpacity: 0.15
        });
        map.value.addOverlay(circle);
        markers.push(circle);
      }
      
      map.value.centerAndZoom(point, 5);
      return;
    }
    // 检查路由参数points（批量点）
    if (route.query.points) {
      let pointsArr = [];
      try {
        pointsArr = JSON.parse(route.query.points as string);
      } catch {}
      addBatchMarkers(pointsArr);
    }
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
  top: 10px;
  left: 10px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 10px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  width: 320px;
}
.controls button {
  padding: 8px 16px;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  min-width: 60px;
}
.search-box {
  display: flex;
  gap: 10px;
  width: 100%;
}
.search-box input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  min-width: 0;
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