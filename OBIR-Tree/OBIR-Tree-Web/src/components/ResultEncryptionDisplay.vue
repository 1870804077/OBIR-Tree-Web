<template>
  <div class="result-encryption-container">
    <div class="data-section">
      <h5>SGX向外部不安全空间传输的数据</h5>
      <div class="data-box sgx-outbound">
        <div class="data-header">
          <span class="data-icon">🔒</span>
          <span class="data-title">SGX加密输出数据</span>
        </div>
        <div class="data-content">
          <div class="data-item">
            <span class="item-label">查询结果:</span>
            <span class="item-value encrypted">已加密 (AES-256)</span>
          </div>
          <div class="data-item">
            <span class="item-label">结果摘要:</span>
            <span class="item-value encrypted">已加密 (SHA-256)</span>
          </div>
          <div class="data-item">
            <span class="item-label">时间戳:</span>
            <span class="item-value encrypted">已加密 (AES-256)</span>
          </div>
          <div class="data-item">
            <span class="item-label">会话标识:</span>
            <span class="item-value encrypted">已加密 (AES-256)</span>
          </div>
          <div class="data-item">
            <span class="item-label">完整性校验:</span>
            <span class="item-value encrypted">已加密 (HMAC-SHA256)</span>
          </div>
          <div class="data-item">
            <span class="item-label">客户端公钥:</span>
            <span class="item-value">明文 (用于加密)</span>
          </div>
        </div>
        <div class="data-footer">
          <span class="footer-text">🔐 所有敏感数据均使用客户端公钥加密</span>
        </div>
      </div>
    </div>
    
    <div class="data-section">
      <h5>外部不安全数据返回到SGX的数据</h5>
      <div class="data-box external-inbound">
        <div class="data-header">
          <span class="data-icon">📡</span>
          <span class="data-title">外部返回数据</span>
        </div>
        <div class="data-content">
          <div class="data-item">
            <span class="item-label">网络状态:</span>
            <span class="item-value">连接正常</span>
          </div>
          <div class="data-item">
            <span class="item-label">传输确认:</span>
            <span class="item-value">ACK已接收</span>
          </div>
          <div class="data-item">
            <span class="item-label">错误信息:</span>
            <span class="item-value">无错误</span>
          </div>
          <div class="data-item">
            <span class="item-label">重试次数:</span>
            <span class="item-value">0次</span>
          </div>
          <div class="data-item">
            <span class="item-label">传输延迟:</span>
            <span class="item-value">15ms</span>
          </div>
          <div class="data-item">
            <span class="item-label">数据包大小:</span>
            <span class="item-value">2.3KB</span>
          </div>
        </div>
        <div class="data-footer">
          <span class="footer-text">⚠️ 外部环境不安全，仅传输加密数据</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 组件逻辑
</script>

<style scoped>
.result-encryption-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}

.data-section {
  flex: 1;
}

.data-section h5 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.data-box {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  background: #fafafa;
  transition: all 0.3s ease;
}

.data-box:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.sgx-outbound {
  border-left: 4px solid #d32f2f;
}

.external-inbound {
  border-left: 4px solid #1976d2;
}

.data-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e0e0e0;
}

.data-icon {
  font-size: 18px;
}

.data-title {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.data-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.data-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid #f0f0f0;
}

.data-item:last-child {
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

.data-footer {
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid #e0e0e0;
  text-align: center;
}

.footer-text {
  font-size: 12px;
  color: #666;
  font-style: italic;
}
</style> 