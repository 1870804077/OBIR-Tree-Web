<template>
  <div class="stash-rdt-container">
    <div class="section">
      <h5>STASH/桶更新与RDT重置过程</h5>
      <div class="process-box">
        <div class="process-step">
          <div class="step-header">
            <span class="step-icon">📦</span>
            <span class="step-title">目标节点暂存STASH</span>
          </div>
          <div class="step-content">
            <p>• 将查询结果相关的目标节点暂存到STASH</p>
            <p>• 保护目标节点不被重加密操作影响</p>
            <p>• 确保查询结果的完整性和准确性</p>
          </div>
        </div>
        
        <div class="process-step">
          <div class="step-header">
            <span class="step-icon">🔄</span>
            <span class="step-title">非目标节点重加密</span>
          </div>
          <div class="step-content">
            <p>• 对非目标节点进行重新加密</p>
            <p>• 使用新的随机密钥更新加密内容</p>
            <p>• 隐藏访问模式，保护隐私</p>
          </div>
        </div>
        
        <div class="process-step">
          <div class="step-header">
            <span class="step-icon">🎯</span>
            <span class="step-title">虚拟块填充</span>
          </div>
          <div class="step-content">
            <p>• 使用虚拟数据填充空桶</p>
            <p>• 隐藏真实的数据分布模式</p>
            <p>• 防止通过存储模式推断信息</p>
          </div>
        </div>
        
        <div class="process-step">
          <div class="step-header">
            <span class="step-icon">🔄</span>
            <span class="step-title">RDT重置并加密写回</span>
          </div>
          <div class="step-content">
            <p>• 重置RDT结构以反映新的访问模式</p>
            <p>• 使用AES-256加密RDT数据</p>
            <p>• 将加密后的RDT写回EDB存储</p>
          </div>
        </div>
        
        <div class="process-step">
          <div class="step-header">
            <span class="step-icon">✅</span>
            <span class="step-title">操作完成验证</span>
          </div>
          <div class="step-content">
            <p>• 验证所有加密操作成功完成</p>
            <p>• 确认STASH中的目标节点安全</p>
            <p>• 准备返回查询结果给客户端</p>
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
.stash-rdt-container {
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
  gap: 16px;
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