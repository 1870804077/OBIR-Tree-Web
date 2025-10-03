import { defineStore } from 'pinia';

interface AccessTimesData {
  blocks: Array<{ block_id: number; accessed_time: number }>;
  timestamp: number;
}

export const useChartStore = defineStore('chart', {
  state: () => ({
    multipleAccessTimesCache: null as AccessTimesData | null,
  }),
  
  actions: {
    // 缓存多组访问次数数据
    setMultipleAccessTimes(data: Array<{ block_id: number; accessed_time: number }>) {
      this.multipleAccessTimesCache = {
        blocks: data,
        timestamp: Date.now()
      };
    },
    
    // 获取缓存的多组访问次数数据
    getMultipleAccessTimes() {
      // 简单的缓存有效期检查（可选）
      if (this.multipleAccessTimesCache) {
        // 例如：缓存10分钟有效
        const tenMinutes = 10 * 60 * 1000;
        if (Date.now() - this.multipleAccessTimesCache.timestamp < tenMinutes) {
          return this.multipleAccessTimesCache.blocks;
        }
      }
      return null;
    }
  }
});