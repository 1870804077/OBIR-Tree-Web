<template>
  <div class="oblivious-access-container">
    <div class="section">
      <h5>Oblivious访问与剪枝过程</h5>
      <div class="process-box">
        <div class="process-step">
          <div class="step-header">
            <span class="step-icon">🔍</span>
            <span class="step-title">SGX解密查询参数</span>
          </div>
          <div class="step-content">
            <p>• 使用SGX密钥解密客户端发送的查询参数</p>
            <p>• 验证查询参数的合法性和完整性</p>
            <p>• 提取查询关键词和目标路径信息</p>
          </div>
        </div>
        
        <div class="process-step">
          <div class="step-header">
            <span class="step-icon">📊</span>
            <span class="step-title">获取目标路径</span>
          </div>
          <div class="step-content">
            <p>• 根据IR-Tree元数据计算逻辑路径</p>
            <p>• 确定需要访问的物理存储位置</p>
            <p>• 准备Oblivious访问操作</p>
          </div>
        </div>
        
        <div class="process-step">
          <div class="step-header">
            <span class="step-icon">🔐</span>
            <span class="step-title">读取加密块</span>
          </div>
          <div class="step-content">
            <p>• 从EDB中读取加密的数据块</p>
            <p>• 解密RDT结构获取访问模式</p>
            <p>• 执行Oblivious内存访问</p>
          </div>
        </div>
        
        <div class="process-step">
          <div class="step-header">
            <span class="step-icon">✂️</span>
            <span class="step-title">筛选与剪枝</span>
          </div>
          <div class="step-content">
            <p>• 筛选高相关性的节点</p>
            <p>• 剪枝无关的节点分支</p>
            <p>• 优化查询性能</p>
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
.oblivious-access-container {
  width: 100%;
  padding: 20px;
}

.section h5 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
  text-align: center;
}

.process-box {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.process-step {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  background: #fafafa;
  transition: all 0.3s ease;
}

.process-step:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.step-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e0e0e0;
}

.step-icon {
  font-size: 20px;
}

.step-title {
  font-weight: 600;
  color: #333;
  font-size: 16px;
}

.step-content {
  color: #555;
  font-size: 14px;
  line-height: 1.6;
}

.step-content p {
  margin: 6px 0;
  padding-left: 10px;
}

.step-content p:first-child {
  margin-top: 0;
}

.step-content p:last-child {
  margin-bottom: 0;
}
</style> 