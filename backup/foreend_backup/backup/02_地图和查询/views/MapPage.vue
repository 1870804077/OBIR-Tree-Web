<template>
  <div class="map-container">
    <div id="baidu-map"></div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';

onMounted(() => {
  // 初始化百度地图实例
  const map = new BMap.Map('baidu-map');
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

  // 添加示例标记点
  const marker = new BMap.Marker(point);
  map.addOverlay(marker);
  // 添加信息窗口
  const infoWindow = new BMap.InfoWindow('这里是北京市中心');
  marker.addEventListener('click', () => {
    map.openInfoWindow(infoWindow, point);
  });
});
</script>

<style scoped>
.map-container {
  width: 100vw;
  height: 100vh;
}

#baidu-map {
  width: 100%;
  height: 100%;
}
</style>