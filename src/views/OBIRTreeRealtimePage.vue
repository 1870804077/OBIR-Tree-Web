<template>
  <div class="obir-tree-realtime-page">
    <div class="page-header">
      <h2>OBIR-Tree实时路径展示</h2>
      <p class="description">
        实时监控OBIR-Tree结构变化，展示节点的新增、删除和修改情况
      </p>
    </div>
    
    <div class="content">
      <div class="main-section">
        <OBIRTreeRealtimeSVG />
      </div>
      
      <div class="info-section">
        <div class="info-card">
          <h4>功能说明</h4>
          <ul>
            <li><strong>横向布局：</strong>OBIR-Tree采用横向绘制，便于观察层级结构</li>
            <li><strong>实时更新：</strong>支持自动刷新，实时显示树结构变化</li>
            <li><strong>差异标注：</strong>用不同颜色标识新增、删除、修改的节点</li>
            <li><strong>状态监控：</strong>显示当前节点数和变化统计</li>
          </ul>
        </div>
        
        <div class="info-card">
          <h4>数据接口</h4>
          <div class="api-info">
            <p><strong>当前数据文件：</strong>obir_tree_current.json</p>
            <p><strong>前一时刻文件：</strong>obir_tree_previous.json</p>
            <p><strong>API接口：</strong>/api/obir-tree-realtime</p>
            <p><strong>更新频率：</strong>可配置（默认5秒）</p>
          </div>
        </div>
        
        <div class="info-card">
          <h4>C++集成说明</h4>
          <div class="integration-info">
            <p>1. C++代码需要输出JSON格式的树结构数据</p>
            <p>2. 数据格式包含nodes（节点列表）和edges（边列表）</p>
            <p>3. 每个节点包含id、value、level、status等字段</p>
            <p>4. 支持实时文件更新，Python脚本自动读取最新数据</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import OBIRTreeRealtimeSVG from '@/components/OBIRTreeRealtimeSVG.vue'
</script>

<style scoped>
.obir-tree-realtime-page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
}

.page-header h2 {
  margin: 0 0 10px 0;
  font-size: 28px;
  font-weight: 600;
}

.description {
  margin: 0;
  font-size: 16px;
  opacity: 0.9;
}

.content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
}

.main-section {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.info-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-card {
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #4CAF50;
}

.info-card h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.info-card ul {
  margin: 0;
  padding-left: 20px;
}

.info-card li {
  margin-bottom: 8px;
  color: #555;
  line-height: 1.5;
}

.info-card strong {
  color: #333;
}

.api-info p, .integration-info p {
  margin: 0 0 8px 0;
  color: #555;
  line-height: 1.5;
}

.api-info strong, .integration-info strong {
  color: #333;
}

@media (max-width: 1024px) {
  .content {
    grid-template-columns: 1fr;
  }
  
  .info-section {
    order: -1;
  }
}

@media (max-width: 768px) {
  .obir-tree-realtime-page {
    padding: 15px;
  }
  
  .page-header {
    padding: 15px;
  }
  
  .page-header h2 {
    font-size: 24px;
  }
  
  .description {
    font-size: 14px;
  }
}
</style> 