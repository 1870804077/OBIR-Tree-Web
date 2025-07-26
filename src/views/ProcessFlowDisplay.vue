<template>
  <div class="data-display-container">
    <div class="section obir-tree-container">
      <h3>OBIR_Tree展示</h3>
      <div class="tree-placeholder">
        <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMDAiIGhlaWdodD0iMjUwIiBmaWxsPSJ3aGl0ZSI+PGNpcmNsZSBjeD0iMTUwIiBjeT0iMTI1IiByPSI4MCIgZmlsbD0iI2Y5ZjlmOSIvPjwvc3ZnPg==" alt="空白图" class="blank-image">
      </div>
    </div>
    <div class="section search-bar">
      <div class="search-container">
        <input type="text" v-model="searchText" placeholder="输入搜索关键词..." class="search-input">
        <input type="text" v-model="lng" placeholder="经度" class="search-input coord-input">
        <input type="text" v-model="lat" placeholder="纬度" class="search-input coord-input">
        <button class="search-button">搜索</button>
        <button class="search-button" @click="showOnMap">在地图上显示</button>
      </div>
    </div>
    <div class="section process-node-graph">
      <h3>检索流程节点图</h3>
      <div class="graph-placeholder" @mousemove="onSvgMouseMove" @mouseleave="hideTooltip">
        <svg width="100%" height="234" viewBox="0 0 1200 234">
          <!-- 箭头定义 -->
          <defs>
            <marker id="arrow-end" markerWidth="8" markerHeight="8" refX="0" refY="4" orient="auto">
              <path d="M0,1 L8,4 L0,7 L2,4 Z" fill="#6ec6f7" />
            </marker>
            <marker id="arrow-start" markerWidth="8" markerHeight="8" refX="8" refY="4" orient="auto">
              <path d="M0,1 L8,4 L0,7 L2,4 Z" fill="#6ec6f7" />
            </marker>
          </defs>
          <!-- 主干三次贝塞尔曲线（首尾延伸，双箭头，左右拉伸） -->
          <path d="M75,195 C265,13 945,273 1145,39" stroke="#6ec6f7" stroke-width="1.2" fill="none" marker-end="url(#arrow-end)" marker-start="url(#arrow-start)" />
          <!-- 节点与说明 -->
          <g v-for="(node, idx) in mindmapNodes" :key="node.name">
            <!-- 节点圆点（有边框），y坐标根据曲线计算 -->
            <circle :cx="node.x" :cy="node.y" r="6" :fill="node.color" stroke="#d8d4ac" stroke-width="1.5"
              @mouseenter="showTooltip($event, node)" @mouseleave="hideTooltip" @click="onNodeClick(node)" style="cursor:pointer;"/>
            <!-- 节点名称，上下错开分布 -->
            <text :x="node.x" :y="idx % 2 === 0 ? node.y - 26 : node.y + 36" fill="#333" font-size="15" font-weight="bold" text-anchor="middle">{{ node.name }}</text>
          </g>
        </svg>
        <transition name="fade">
          <div v-if="tooltip.show" class="svg-tooltip" :style="{left: tooltip.x + 'px', top: tooltip.y + 'px'}">
            {{ tooltip.text }}
          </div>
        </transition>
      </div>
    </div>
    <!-- 节点点击弹窗 - 移到页面最外层 -->
    <teleport to="body">
      <div v-if="popup.show" class="page-popup-mask" @click.self="closePopup">
        <div class="page-popup">
          <div class="popup-header">
            <h4>{{ popup.node?.name }}</h4>
            <button class="popup-close-btn" @click="closePopup">×</button>
          </div>
          <div class="popup-content">
            <div class="desc">{{ popup.node?.desc }}</div>
            <!-- 这里可以放置小流程图等组件 -->
            <div class="component-placeholder">
              <!-- 未来组件区域 -->
            </div>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
const router = useRouter();
const lng = ref('');
const lat = ref('');
const searchText = ref('');
const points = [
  { lng: 116.404, lat: 39.915 },
  { lng: 117.200, lat: 39.133 },
  { lng: 118.100, lat: 36.900 }
];
const showOnMap = () => {
  const longitude = parseFloat(lng.value);
  const latitude = parseFloat(lat.value);
  if (isNaN(longitude) || isNaN(latitude)) {
    alert('请输入有效的经纬度');
    return;
  }
  router.push({
    path: '/project-search/map',
    query: {
      lng: longitude,
      lat: latitude
    }
  });
};
// 拉伸后的贝塞尔曲线节点分布
function cubicBezier(t, p0, p1, p2, p3) {
  const x = Math.pow(1-t,3)*p0.x + 3*Math.pow(1-t,2)*t*p1.x + 3*(1-t)*t*t*p2.x + t*t*t*p3.x;
  const y = Math.pow(1-t,3)*p0.y + 3*Math.pow(1-t,2)*t*p1.y + 3*(1-t)*t*t*p2.y + t*t*t*p3.y;
  return {x, y};
}
const bezierPoints = [
  {x: 75, y: 195}, // 起点左移，延长左边线条
  {x: 265, y: 13}, // 控制点1
  {x: 945, y: 273}, // 控制点2
  {x: 1145, y: 39}  // 终点
];
const nodeCount = 9;
// 节点分布在中间，间距自动拉开
const mindmapNodes = Array.from({length: nodeCount}, (_, i) => {
  const t = (i+1)/(nodeCount+1); // 节点分布在(0,1)之间的等分点，避开首尾延伸段
  const {x, y} = cubicBezier(t, bezierPoints[0], bezierPoints[1], bezierPoints[2], bezierPoints[3]);
  const colorList = ['#f8f3d4','#e0f7fa','#ffe0b2','#dcedc8','#f3e5f5','#fff9c4','#b2ebf2','#ffcdd2','#c8e6c9'];
  const names = [
    '数据预处理与初始化',
    'SGX密钥管理与索引映射',
    '数据加密存储',
    '用户加密查询请求',
    'SGX查询处理',
    'Oblivious访问与剪枝',
    'STASH/桶更新与RDT重置',
    '结果加密返回',
    '客户端解密与结果呈现'
  ];
  const descs = [
    '客户端准备空间文本数据，分块加密，构建IR-tree索引，生成映射关系，上传加密数据和密钥。',
    'SGX远程证明，密钥解密，IR-tree映射为OBIR-tree，分配物理路径，虚拟块填充，生成加密RDT。',
    'EDB存储加密数据块、RDT、虚拟块，隐藏真实分布，元数据公开但内容安全。',
    '客户端加密查询参数和目标路径，发送至云端，SGX验证合法性并解密。',
    'SGX解密查询参数，获取目标路径，准备Oblivious访问。',
    'SGX读取加密块，解密RDT，筛选高相关节点，剪枝无关节点。',
    '目标节点暂存STASH，非目标节点重加密写回，虚拟块填充，RDT重置并加密写回EDB。',
    'SGX用客户端公钥加密结果，发送至客户端。',
    '客户端用私钥解密，提取原始数据，展示最终结果。'
  ];
  return {
    name: names[i],
    desc: descs[i],
    x,
    y,
    color: colorList[i]
  };
});
const tooltip = ref({ show: false, x: 0, y: 0, text: '' });
function showTooltip(e, node) {
  tooltip.value = {
    show: true,
    x: e.clientX + 10,
    y: e.clientY + 10,
    text: node.desc
  };
}
function hideTooltip() {
  tooltip.value.show = false;
}
function onSvgMouseMove(e) {
  if (tooltip.value.show) {
    tooltip.value.x = e.clientX + 10;
    tooltip.value.y = e.clientY + 10;
  }
}
const popup = ref({ show: false, node: null });
function onNodeClick(node) {
  popup.value = { show: true, node };
}
function closePopup() {
  popup.value = { show: false, node: null };
}
</script>

<style>
.data-display-container {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 600px;
  width: 100%;
  box-sizing: border-box;
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
.search-bar {
  padding: 15px 25px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4eaf5 100%);
}
.search-container {
  display: flex;
  gap: 12px;
  align-items: center;
  max-width: 1000px;
  width: 100%;
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
.search-button {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  font-size: 1rem;
  background-color: #42b983;
  color: white;
  transition: all 0.2s ease;
}
.search-button:hover {
  background-color: #359469;
}
.process-node-graph {
  min-height: 300px;
}
.graph-placeholder {
  position: relative;
  width: 100%;
  min-height: 220px;
  background: linear-gradient(90deg, #f8f3d4 0%, #e0f7fa 100%);
  border-radius: 16px;
  box-shadow: 0 2px 12px #eee;
  margin-top: 8px;
}
.coord-input {
  width: 180px;
  flex: none;
}
.svg-tooltip {
  position: fixed;
  z-index: 99;
  background: rgba(50,50,50,0.95);
  color: #fff;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 15px;
  pointer-events: none;
  max-width: 320px;
  box-shadow: 0 2px 8px #888;
  white-space: pre-line;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.page-popup-mask {
  position: fixed !important;
  left: 0 !important; 
  top: 0 !important; 
  right: 0 !important; 
  bottom: 0 !important;
  background: rgba(0,0,0,0.25);
  z-index: 999999 !important;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: auto;
  transform-style: preserve-3d;
  backface-visibility: hidden;
}
.page-popup {
  position: relative !important;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  padding: 32px 36px 24px 36px;
  min-width: 500px;
  max-width: 90vw;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 1000000 !important;
  transform: translateZ(0);
  will-change: transform;
}
.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}
.popup-header h4 {
  margin: 0;
  font-size: 22px;
  color: #333;
  font-weight: 600;
}
.popup-content {
  flex: 1;
  overflow-y: auto;
}
.popup-close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}
.popup-close-btn:hover {
  background: #f0f0f0;
  color: #666;
}
.component-placeholder {
  margin-top: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 2px dashed #dee2e6;
  text-align: center;
  color: #6c757d;
  font-size: 14px;
  min-height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style> 