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
  if (!Array.isArray(pointsArr) || pointsArr.length === 0) {
    console.warn('addBatchMarkers: 点数据为空或格式错误');
    return;
  }
  
  if (!map.value) {
    console.error('addBatchMarkers: 地图未初始化');
    return;
  }
  
  console.log(`addBatchMarkers: 准备添加 ${pointsArr.length} 个点`);
  clearMarkers();
  
  // 验证并过滤有效坐标
  const validPoints = pointsArr.filter(point => {
    const isValid = point && 
                   typeof point.lng === 'number' && 
                   typeof point.lat === 'number' && 
                   !isNaN(point.lng) && 
                   !isNaN(point.lat) &&
                   point.lng >= -180 && point.lng <= 180 &&
                   point.lat >= -90 && point.lat <= 90;
    if (!isValid) {
      console.warn('无效坐标点:', point);
    }
    return isValid;
  });
  
  if (validPoints.length === 0) {
    console.error('addBatchMarkers: 没有有效的坐标点');
    return;
  }
  
  console.log(`addBatchMarkers: 有效点数量 ${validPoints.length}`);
  
  // 构造百度地图Point数组
  const bPoints = validPoints.map(({lng, lat}) => new BMap.Point(lng, lat));
  
  // 配置样式 - 使用更明显的红色点
  const options = {
    size: 3, // 增大到5像素
    shape: BMap?.POINT_SHAPE_CIRCLE || 0,
    color: '#C0C0C0' // 改为灰色，更容易看到
  };
  
  // 创建海量点覆盖物
  const pointCollection = new BMap.PointCollection(bPoints, options);
  map.value.addOverlay(pointCollection);
  markers.push(pointCollection);
  
  console.log('addBatchMarkers: 点已添加到地图');
  
  // 计算边界并自动缩放到合适的视野
  if (validPoints.length > 0) {
    const bounds = new BMap.Bounds();
    validPoints.forEach(({lng, lat}) => {
      bounds.extend(new BMap.Point(lng, lat));
    });
    
    // 如果只有一个点，使用固定缩放级别
    if (validPoints.length === 1) {
      map.value.centerAndZoom(new BMap.Point(validPoints[0].lng, validPoints[0].lat), 12);
    } else {
      // 多个点时自动适应边界
      map.value.setViewport(bounds, {margins: [50, 50, 50, 50]});
    }
  }
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
    
    // 优先检查sessionStorage中的搜索数据（新增）
    const searchDataStr = sessionStorage.getItem('mapSearchData');
    if (searchDataStr) {
      try {
        const searchData = JSON.parse(searchDataStr);
        console.log('从sessionStorage获取搜索数据:', searchData);
        
        if (Array.isArray(searchData) && searchData.length > 0) {
          clearMarkers();
          
          // 分别处理目标点和结果点
          const targetPoints = searchData.filter(item => item.type === 'target');
          const resultPoints = searchData.filter(item => item.type === 'result');
          
          // 添加目标点（红色大圆点）
          targetPoints.forEach(target => {
            const point = new BMap.Point(target.lng, target.lat);
            // 创建红色目标点图标
            const svgIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20">
              <circle cx="10" cy="10" r="8" fill="#ff1744" stroke="#ffffff" stroke-width="2"/>
              <circle cx="10" cy="10" r="3" fill="#ffffff"/>
            </svg>`;
            const icon = new BMap.Icon(
              'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgIcon),
              new BMap.Size(20, 20),
              { anchor: new BMap.Size(10, 10) }
            );
            const marker = new BMap.Marker(point, { icon });
            
            // 添加信息窗口
            const infoWindow = new BMap.InfoWindow(`
              <div style="padding: 5px;">
                <strong>搜索目标点</strong><br/>
                关键词: ${target.keyword}<br/>
                坐标: (${target.lng}, ${target.lat})
              </div>
            `);
            marker.addEventListener('click', () => {
              map.value.openInfoWindow(infoWindow, point);
            });
            
            map.value.addOverlay(marker);
            markers.push(marker);
          });
          
          // 添加结果点（蓝色小圆点）
          resultPoints.forEach((result, index) => {
            const point = new BMap.Point(result.lng, result.lat);
            // 创建蓝色结果点图标
            const svgIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 14 14">
              <circle cx="7" cy="7" r="5" fill="#2196f3" stroke="#ffffff" stroke-width="1"/>
              <circle cx="7" cy="7" r="2" fill="#ffffff"/>
            </svg>`;
            const icon = new BMap.Icon(
              'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgIcon),
              new BMap.Size(14, 14),
              { anchor: new BMap.Size(7, 7) }
            );
            const marker = new BMap.Marker(point, { icon });
            
            // 添加信息窗口
            const infoWindow = new BMap.InfoWindow(`
              <div style="padding: 5px;">
                <strong>${result.title}</strong><br/>
                ID: ${result.id}<br/>
                坐标: (${result.lng}, ${result.lat})<br/>
                ${result.weighted_dist ? `综合距离: ${result.weighted_dist.toFixed(5)}<br/>` : ''}
                ${result.original_dist ? `空间距离: ${result.original_dist.toFixed(2)}<br/>` : ''}
                ${result.lev_distance ? `文本距离: ${result.lev_distance.toFixed(2)}` : ''}
              </div>
            `);
            marker.addEventListener('click', () => {
              map.value.openInfoWindow(infoWindow, point);
            });
            
            map.value.addOverlay(marker);
            markers.push(marker);
          });
          
          // 自动调整地图视野以包含所有点
          if (searchData.length > 0) {
            const allPoints = searchData.map(item => new BMap.Point(item.lng, item.lat));
            const viewport = map.value.getViewport(allPoints);
            map.value.centerAndZoom(viewport.center, viewport.zoom);
          }
          
          // 清理sessionStorage中的数据
          sessionStorage.removeItem('mapSearchData');
          return;
        }
      } catch (parseError) {
        console.error('解析sessionStorage中的搜索数据失败:', parseError);
        searchError.value = '搜索数据解析失败';
      }
    }
    
    // 检查是否需要显示所有点（从sessionStorage获取数据）
    if (route.query.showAll === 'true') {
      const storedPoints = sessionStorage.getItem('mapPoints');
      if (storedPoints) {
        try {
          const pointsArr = JSON.parse(storedPoints);
          console.log(`从sessionStorage加载了 ${pointsArr.length} 个地理位置点`);
          addBatchMarkers(pointsArr);
          // 清理sessionStorage中的数据
          sessionStorage.removeItem('mapPoints');
          return;
        } catch (parseError) {
          console.error('解析sessionStorage中的地图数据失败:', parseError);
          searchError.value = '地图数据解析失败';
        }
      } else {
        console.warn('未找到sessionStorage中的地图数据');
        searchError.value = '未找到地图数据';
      }
    }
    
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
    
    // 检查路由参数points（批量点）- 保持向后兼容
    if (route.query.points) {
      let pointsArr = [];
      try {
        pointsArr = JSON.parse(route.query.points as string);
        console.log(`从URL参数加载了 ${pointsArr.length} 个地理位置点`);
      } catch (parseError) {
        console.error('解析URL参数中的地图数据失败:', parseError);
        searchError.value = '地图数据解析失败';
      }
      addBatchMarkers(pointsArr);
    }
  } catch (error) {
    searchError.value = '地图加载失败';
    console.error('地图初始化失败:', error);
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