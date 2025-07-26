<template>
  <div class="storage-status-container">
    <div class="status-section">
      <h5>OBIR-Tree加密存储状态示例</h5>
      <div class="status-box obir-status">
        <div class="status-header">
          <span class="status-icon">🔒</span>
          <span class="status-title">OBIR-Tree存储状态</span>
        </div>
        <div class="status-content">
          <div class="status-item">
            <span class="item-label">根节点:</span>
            <span class="item-value encrypted">已加密 (AES-256)</span>
          </div>
          <div class="status-item">
            <span class="item-label">内部节点:</span>
            <span class="item-value encrypted">已加密 (AES-256)</span>
          </div>
          <div class="status-item">
            <span class="item-label">叶子节点:</span>
            <span class="item-value encrypted">已加密 (AES-256)</span>
          </div>
          <div class="status-item">
            <span class="item-label">映射关系:</span>
            <span class="item-value encrypted">已加密 (Oblivious映射)</span>
          </div>
          <div class="status-item">
            <span class="item-label">虚拟块:</span>
            <span class="item-value">已填充 (隐藏真实分布)</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="status-section">
      <h5>RDT存储状态示例</h5>
      <div class="status-box rdt-status">
        <div class="status-header">
          <span class="status-icon">📊</span>
          <span class="status-title">RDT存储状态</span>
        </div>
        <div class="status-content">
          <div class="status-item">
            <span class="item-label">RDT结构:</span>
            <span class="item-value encrypted">已加密 (AES-256)</span>
          </div>
          <div class="status-item">
            <span class="item-label">访问模式:</span>
            <span class="item-value">Oblivious访问</span>
          </div>
          <div class="status-item">
            <span class="item-label">重置机制:</span>
            <span class="item-value">定期重置</span>
          </div>
          <div class="status-item">
            <span class="item-label">存储位置:</span>
            <span class="item-value">EDB加密数据库</span>
          </div>
          <div class="status-item">
            <span class="item-label">元数据:</span>
            <span class="item-value">公开可见</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 组件逻辑
</script>

<style scoped>
.storage-status-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}

.status-section {
  flex: 1;
}

.status-section h5 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.status-box {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  background: #fafafa;
  transition: all 0.3s ease;
}

.status-box:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.obir-status {
  border-left: 4px solid #1976d2;
}

.rdt-status {
  border-left: 4px solid #388e3c;
}

.status-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e0e0e0;
}

.status-icon {
  font-size: 18px;
}

.status-title {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.status-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid #f0f0f0;
}

.status-item:last-child {
  border-bottom: none;
}

.item-label {
  font-weight: 500;
  color: #555;
  font-size: 13px;
}

.item-value {
  font-size: 13px;
  padding: 2px 8px;
  border-radius: 4px;
  background: #e8f5e8;
  color: #2e7d32;
}

.item-value.encrypted {
  background: #fff3e0;
  color: #f57c00;
}

.item-value.encrypted::before {
  content: "🔒 ";
}
</style> 