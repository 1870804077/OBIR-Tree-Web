<template>
  <div class="map-container">
  <div id="baidu-map"></div>
  <div class="map-controls">
      <div class="search-box">
        <input type="text" v-model="searchKeyword" placeholder="输入地址搜索...">
        <button @click="searchLocation" :disabled="isSearching">{{ isSearching ? '搜索中...' : '搜索' }}</button>
      </div>
      <div class="周边搜索">
        <select v-model="searchType">
          <option value="餐饮">餐饮</option>
          <option value="酒店">酒店</option>
          <option value="景点">景点</option>
          <option value="银行">银行</option>
        </select>
        <button @click="searchNearby" :disabled="isSearching">{{ isSearching ? '搜索中...' : '周边搜索' }}</button>
      </div>
      <div class="control-buttons">
        <button @click="clearMarkers" class="clear-btn">清除标记</button>
      </div>
    </div>
    <div class="coordinate-info" v-if="selectedPoint">
      坐标: {{ selectedPoint.lng.toFixed(6) }}, {{ selectedPoint.lat.toFixed(6) }}
      <button @click="copyCoordinates" class="copy-btn">复制</button>
    </div>
    <div v-if="searchError" class="error-message">{{ searchError }}</div>
    <div v-if="copySuccess" class="success-message">{{ copySuccess }}</div>
</div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue';

const searchKeyword = ref('');
const searchType = ref('餐饮');
const selectedPoint = ref(null);
const searchError = ref('');
const copySuccess = ref('');
const isSearching = ref(false);
const searchTimer = ref(null);

// 声明全局变量
let map = null;
let markers = [];
let geocoder = null;
let localSearch = null;

onMounted(() => {
  try {
    // 初始化百度地图实例
    map = new BMap.Map('baidu-map');
  // 设置中心点坐标（北京）
  const point = new BMap.Point(116.404, 39.915);
  // 初始化地图，设置中心点坐标和地图级别
  map.centerAndZoom(point, 15);
  // 添加地图类型控件
  map.addControl(new BMap.MapTypeControl({
    mapTypes: [BMAP_NORMAL_MAP, BMAP_SATELLITE_MAP, BMAP_HYBRID_MAP]
  }));
  // 启用滚轮放大缩小
  map.enableScrollWheelZoom(true);
  // 添加缩放控件
  map.addControl(new BMap.NavigationControl());
  // 添加比例尺控件
  map.addControl(new BMap.ScaleControl());
  
  // 创建地理编码器实例
  geocoder = new BMap.Geocoder();
  // 创建本地搜索实例
  localSearch = new BMap.LocalSearch(map, {
    renderOptions: { map: map },
    pageCapacity: 10
  });

  onUnmounted(() => {
    // 清除定时器
    if (searchTimer.value) clearTimeout(searchTimer.value);
    // 清除所有标记
    clearMarkers();
    // 销毁地图实例
    if (map) {
      map.clearOverlays();
      map.dispose();
      map = null;
    }
  });    // 添加定位控件
  map.addControl(new BMap.GeolocationControl({
    anchor: BMAP_ANCHOR_BOTTOM_RIGHT,
    showAddressBar: true,
    enableAutoLocation: true
  }));

  // 添加可拖动的示例标记点
  const marker = new BMap.Marker(point);
  marker.enableDragging(); // 启用标记点拖动
  map.addOverlay(marker);
  markers.push(marker);
  // 添加信息窗口
  const infoWindow = new BMap.InfoWindow('这里是北京市中心');
  marker.addEventListener('click', () => {
    map.openInfoWindow(infoWindow, point);
  });


  
  // 监听标记点拖动事件，更新坐标显示
  marker.addEventListener('dragend', (e) => {
    selectedPoint.value = e.point;
    // 更新信息窗口位置
    map.openInfoWindow(infoWindow, e.point);
  });
  
  markers.push(marker);
  } catch (error) {
    console.error('地图初始化失败:', error);
    searchError.value = '地图加载失败，请检查API密钥或网络连接';
  }
});

// 复制坐标到剪贴板
const copyCoordinates = () => {
  if (!selectedPoint.value) return;
  const coordinates = `${selectedPoint.value.lng.toFixed(6)}, ${selectedPoint.value.lat.toFixed(6)}`;
  navigator.clipboard.writeText(coordinates).then(() => {
    copySuccess.value = '坐标已复制到剪贴板';
    setTimeout(() => { copySuccess.value = ''; }, 2000);
  }).catch(err => {
    console.error('复制失败:', err);
  });
};

// 地址搜索功能
const searchLocation = () => {
  if (!searchKeyword.value) return;
  if (searchTimer.value) clearTimeout(searchTimer.value);
  searchTimer.value = setTimeout(() => {
    isSearching.value = true;
    searchError.value = '';
    // 清除之前的标记
    clearMarkers();
    // 使用地理编码搜索地址
    geocoder.getPoint(searchKeyword.value, (point) => {
      if (point) {
        map.centerAndZoom(point, 15);
        const marker = new BMap.Marker(point);
        map.addOverlay(marker);
        markers.push(marker);
        // 获取地址详情
        geocoder.getLocation(point, (rs) => {
          const address = rs.address;
          const infoWindow = new BMap.InfoWindow(`地址: ${address}`);
          marker.addEventListener('click', () => {
            map.openInfoWindow(infoWindow, point);
          });
        });
      } else {
        searchError.value = '未找到该地址';
      }
      isSearching.value = false;
    });
  }, 300);
}; 

// 周边搜索功能
const searchNearby = () => {
  if (!map.getCenter()) return;
  if (searchTimer.value) clearTimeout(searchTimer.value);
  searchTimer.value = setTimeout(() => {
    isSearching.value = true;
    searchError.value = '';
    // 清除之前的标记
    clearMarkers();
    // 搜索当前中心点周边的设施
    localSearch.searchNearby(searchType.value, map.getCenter(), 1000);
    // 监听搜索完成事件
    localSearch.setSearchCompleteCallback(() => {
      isSearching.value = false;
      if (localSearch.getResults()?.getPoiCount() === 0) {
        searchError.value = '未找到相关结果';
      }
    });
  }, 300);
};

// 清除所有标记
const clearMarkers = () => {
  if (!map) return;
  markers.forEach(marker => {
    map.removeOverlay(marker);
  });
  markers = [];
  selectedPoint.value = null;
  searchError.value = '';
  copySuccess.value = '';
};
</script>

<style scoped>
.map-container {
  width: 100vw;
  height: 100vh;
  position: relative;
}

.map-controls {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 1000;
  display: flex;
  gap: 15px;
  padding: 10px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.search-box input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-right: 8px;
}

.search-box button,
.周边搜索 button {
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.search-box button:hover,
.周边搜索 button:hover {
  background: #0056b3;
}

.周边搜索 select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-right: 8px;
}

.control-buttons {
  display: flex;
  gap: 8px;
}

.clear-btn {
  padding: 8px 16px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.clear-btn:hover {
  background: #5a6268;
}

#baidu-map {
  width: 100%;
  height: 100%;
}

.error-message {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 1000;
  padding: 8px 16px;
  background: #dc3545;
  color: white;
  border-radius: 4px;
  font-size: 14px;
  animation: fadeOut 3s forwards;
}

.success-message {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 1000;
  padding: 8px 16px;
  background: #28a745;
  color: white;
  border-radius: 4px;
  font-size: 14px;
  animation: fadeOut 2s forwards;
}

.周边搜索 select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-right: 8px;
}

.control-buttons {
  display: flex;
  gap: 8px;
}

.clear-btn {
  padding: 8px 16px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.clear-btn:hover {
  background: #5a6268;
}
</style>