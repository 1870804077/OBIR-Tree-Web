<template>
  <div class="query-param-container">
    <div class="param-section">
      <h5>客户端查询参数状态</h5>
      <div class="param-box client-params">
        <div class="param-header">
          <span class="param-icon">🔐</span>
          <span class="param-title">客户端加密参数</span>
        </div>
        <div class="param-content">
          <div class="param-item">
            <span class="item-label">查询关键词:</span>
            <span class="item-value encrypted">已加密 (RSA-2048)</span>
          </div>
          <div class="param-item">
            <span class="item-label">时间戳:</span>
            <span class="item-value encrypted">已加密 (AES-256)</span>
          </div>
          <div class="param-item">
            <span class="item-label">会话ID:</span>
            <span class="item-value encrypted">已加密 (AES-256)</span>
          </div>
          <div class="param-item">
            <span class="item-label">用户标识:</span>
            <span class="item-value encrypted">已加密 (RSA-2048)</span>
          </div>
          <div class="param-item">
            <span class="item-label">查询类型:</span>
            <span class="item-value encrypted">已加密 (AES-256)</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="param-section">
      <h5>SGX解密后参数状态</h5>
      <div class="param-box sgx-params">
        <div class="param-header">
          <span class="param-icon">🔓</span>
          <span class="param-title">SGX解密参数</span>
        </div>
        <div class="param-content">
          <div class="param-item">
            <span class="item-label">查询关键词:</span>
            <span class="item-value decrypted">"OBIR-Tree查询"</span>
          </div>
          <div class="param-item">
            <span class="item-label">时间戳:</span>
            <span class="item-value decrypted">2024-01-15 14:30:25</span>
          </div>
          <div class="param-item">
            <span class="item-label">会话ID:</span>
            <span class="item-value decrypted">sess_20240115_143025</span>
          </div>
          <div class="param-item">
            <span class="item-label">用户标识:</span>
            <span class="item-value decrypted">user_12345</span>
          </div>
          <div class="param-item">
            <span class="item-label">查询类型:</span>
            <span class="item-value decrypted">精确匹配</span>
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
.query-param-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}

.param-section {
  flex: 1;
}

.param-section h5 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.param-box {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  background: #fafafa;
  transition: all 0.3s ease;
}

.param-box:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.client-params {
  border-left: 4px solid #d32f2f;
}

.sgx-params {
  border-left: 4px solid #388e3c;
}

.param-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e0e0e0;
}

.param-icon {
  font-size: 18px;
}

.param-title {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.param-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.param-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid #f0f0f0;
}

.param-item:last-child {
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
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-value.encrypted {
  background: #ffebee;
  color: #c62828;
}

.item-value.encrypted::before {
  content: "🔒 ";
}

.item-value.decrypted {
  background: #e8f5e8;
  color: #2e7d32;
}

.item-value.decrypted::before {
  content: "🔓 ";
}
</style> 