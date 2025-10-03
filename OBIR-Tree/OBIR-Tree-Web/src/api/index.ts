// API 统一导出文件
export { 
  twoRoundSearch, 
  getInitInfo,
  getOramInfo,
  type SearchParams,
  type NearestResult,
  type TopKResponse,
  type TwoRoundSearchResult,
  type PathComparison,
  type InitInfo,
  type OramInfo
} from './search';

// 为了兼容现有代码，保留searchAPI对象
import request from '@/utils/request';

export const searchAPI = {
  // 兼容现有的basicSearch方法 - 使用新的两步查询流程
  async basicSearch(params: { query: string; top_k: number; lng: number; lat: number }) {
    try {
      console.log('开始执行两阶段查询，参数:', params);
      
      // 第一阶段：获取查询结果和缓存键
      const firstRes = await request.get('/first-stage', {
        params: {
          keyword: params.query,
          x: params.lng,
          y: params.lat,
          k: params.top_k
        }
      });
      
      console.log('第一阶段查询结果:', firstRes);
      
      if (firstRes.status !== 'success') {
        throw new Error(firstRes.error || '第一阶段查询失败');
      }

      const results = firstRes.initialResults || [];
      const cacheKey = firstRes.cacheKey;
      
      // 为每个结果添加路径信息的占位符
      const resultsWithPaths = results.map((result: any) => ({
        ...result,
        path_before: null,
        path_after: null,
        showPathComparison: false
      }));

      // 第二阶段：获取PathORAM路径对比信息（如果有缓存键）
      let pathInfo = null;
      if (cacheKey) {
        try {
          console.log('开始第二阶段查询，cacheKey:', cacheKey);
          const secondRes = await request.get('/second-stage', {
            params: {
              cacheKey: cacheKey
            }
          });
          
          console.log('第二阶段查询结果:', secondRes);
          
          if (secondRes.status === 'success') {
            pathInfo = {
              path_before: secondRes.path_before,
              path_after: secondRes.path_after
            };
            
            // 将路径信息添加到所有结果中（因为是基于同一次查询的路径对比）
            resultsWithPaths.forEach((result: any) => {
              result.path_before = pathInfo.path_before;
              result.path_after = pathInfo.path_after;
            });
          }
        } catch (error) {
          // PathORAM路径对比失败不影响主查询结果
          console.warn('PathORAM路径对比加载失败:', error);
        }
      }
      
      return {
        success: true,
        results: resultsWithPaths,
        cacheKey: cacheKey,
        pathInfo: pathInfo,
        time_cost: firstRes.time_cost,
        summary: {
          totalQueries: results.length,
          hasPathInfo: pathInfo !== null
        }
      };
    } catch (error) {
      console.error('两阶段查询失败:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : '搜索失败'
      };
    }
  },

  // 获取树结构（模拟方法，需要根据实际后端接口调整）
  async getTreeStructure() {
    try {
      const info = await getOramInfo();
      return {
        success: true,
        data: info
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : '获取树结构失败'
      };
    }
  }
};

// 兼容现有代码的导出
export const fetchData = async () => {
  return { message: 'Hello from API!' };
};

export const fetchUserData = async () => {
  return { user: 'John Doe', id: 1 };
};