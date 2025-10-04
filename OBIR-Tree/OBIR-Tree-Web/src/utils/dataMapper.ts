/**
 * 数据映射工具
 * 将后端API返回的数据格式转换为前端期望的格式
 */

// 后端API返回的原始数据结构
export interface BackendQueryResult {
  id: number;
  keyword: string;
  title: string;
  description: string;
  relevance: number;
  location: string;
  distance: number;
  text_distance: number;
  spatial_distance: number;
  geo_distance_km: number;
  weighted_distance: number;
  lng: number;
  lat: number;
  type: string;
  pathId: string;
  path_before?: {
    path: any[];
    depth: number;
    access_count: number;
    target_id: number;
  };
  path_after?: {
    path: any[];
    depth: number;
    access_count: number;
    target_id: number;
  };
}

// 前端期望的搜索结果数据结构
export interface FrontendSearchResult {
  id: number;
  title: string;
  description: string;
  relevance: number;
  location: string;
  distance: string | number;
  locationDistance?: string | number;
  textDistance?: string | number;
  lng: number;
  lat: number;
  type: string;
  pathId: string;
  showPathComparison?: boolean;
  path_before?: {
    path: any[];
    depth: number;
    access_count: number;
    accessCount?: number;
    target_id: number;
  };
  path_after?: {
    path: any[];
    depth: number;
    access_count: number;
    accessCount?: number;
    target_id: number;
  };
  pathLoading: boolean; // 新增：标记路径数据是否正在加载
}

/**
 * 将后端API返回的查询结果映射为前端期望的格式
 * @param backendResults 后端API返回的结果数组
 * @returns 前端期望格式的结果数组
 */
export function mapBackendResultsToFrontend(backendResults: BackendQueryResult[]): FrontendSearchResult[] {
  return backendResults.map((result, index) => {
    // 映射基础字段
    const frontendResult: FrontendSearchResult = {
      id: result.id,
      title: result.keyword || result.title || `地点 ${result.id}`,
      description: result.description || `位置: ${result.location}`,
      relevance: result.relevance || 0,
      location: result.location || `坐标点 ID: ${result.id}`,
      distance: result.weighted_distance || result.distance || 0,
      locationDistance: result.geo_distance_km || result.spatial_distance || 0,
      textDistance: result.text_distance || 0,
      lng: result.lng || 0,
      lat: result.lat || 0,
      type: result.type || '地理位置',
      pathId: result.pathId || `path_${result.id}_${index}`,
      showPathComparison: false, // 默认不展开路径对比
      pathLoading: false, // 新增：标记路径数据是否正在加载
    };

    // 映射PathORAM路径信息
    if (result.path_before) {
      frontendResult.path_before = {
        path: result.path_before.path || [],
        depth: result.path_before.depth || 0,
        access_count: result.path_before.access_count || 0,
        accessCount: result.path_before.access_count || 0, // 兼容字段
        target_id: result.path_before.target_id || result.id,
      };
    }

    if (result.path_after) {
      frontendResult.path_after = {
        path: result.path_after.path || [],
        depth: result.path_after.depth || 0,
        access_count: result.path_after.access_count || 0,
        accessCount: result.path_after.access_count || 0, // 兼容字段
        target_id: result.path_after.target_id || result.id,
      };
    }

    return frontendResult;
  });
}

/**
 * 格式化距离显示
 * @param distance 距离值
 * @param unit 单位
 * @returns 格式化后的距离字符串
 */
export function formatDistance(distance: number | string, unit: string = 'km'): string {
  if (typeof distance === 'string') {
    return distance;
  }
  
  if (typeof distance === 'number') {
    if (distance < 0.01) {
      return `${(distance * 1000).toFixed(0)}m`;
    } else if (distance < 1) {
      return `${(distance * 1000).toFixed(0)}m`;
    } else {
      return `${distance.toFixed(2)}${unit}`;
    }
  }
  
  return 'N/A';
}

/**
 * 格式化路径显示
 * @param path 路径数组或字符串
 * @returns 格式化后的路径字符串
 */
export function formatPath(path: any): string {
  if (Array.isArray(path)) {
    if (path.length === 0) {
      return '空路径';
    }
    return 'Root->' + path.join('->');
  }
  
  if (typeof path === 'string') {
    return path || '空路径';
  }
  
  return '空路径';
}

/**
 * 计算PathORAM统计信息
 * @param results 搜索结果数组
 * @returns PathORAM统计信息
 */
export function calculatePathORAMStats(results: FrontendSearchResult[]) {
  let totalNodeChanges = 0;
  let totalAccessCount = 0;
  
  results.forEach(result => {
    if (result.path_before && result.path_after) {
      const beforeDepth = result.path_before.depth || 0;
      const afterDepth = result.path_after.depth || 0;
      const depthChange = Math.abs(afterDepth - beforeDepth);
      totalNodeChanges += depthChange;
      
      const beforeAccess = result.path_before.access_count || 0;
      const afterAccess = result.path_after.access_count || 0;
      totalAccessCount += beforeAccess + afterAccess;
    }
  });
  
  // 模拟搜索耗时（基于结果数量和节点变化）
  const searchTime = Math.max(100, results.length * 50 + totalNodeChanges * 10);
  
  return {
    nodeChange: totalNodeChanges > 0 ? `+${totalNodeChanges}/-${Math.floor(totalNodeChanges * 0.6)}` : '+0/-0',
    searchTime: searchTime,
    totalAccessCount: totalAccessCount,
  };
}