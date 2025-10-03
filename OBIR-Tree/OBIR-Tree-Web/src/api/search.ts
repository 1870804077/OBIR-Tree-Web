import request from '@/utils/request';

// 定义查询参数接口
export interface SearchParams {
  keyword: string;
  x: number;
  y: number;
  k: number;
}

// 定义单个查询结果接口
export interface NearestResult {
  rect_id: number;
  keyword: string;
  center_x: number;
  center_y: number;
  weighted_dist: number;
  original_dist: number;
  lev_distance: number;
  orampath: number[];
  // 为了兼容前端显示，添加计算属性
  get id(): number;
  get x(): number;
  get y(): number;
  get distance(): number;
  get path(): number[];
}

// 定义Top-K查询响应接口
export interface TopKResponse {
  status: string;
  count: number;
  results: NearestResult[];
  error?: string;
}

// 定义路径对比结果接口
export interface PathComparison {
  firstRoundPath: number[];
  secondRoundPath: number[];
  differences: number[]; // 不同位置的索引
  isIdentical: boolean;
}

// 定义两轮查询完整结果接口
export interface TwoRoundSearchResult {
  firstRoundResults: NearestResult[];
  secondRoundResults: NearestResult[];
  pathComparisons: PathComparison[];
  summary: {
    totalQueries: number;
    identicalPaths: number;
    differentPaths: number;
  };
}

// 定义初始化信息接口
export interface InitInfo {
  status: string;
  message: string;
  timestamp?: string;
}

// 定义ORAM信息接口
export interface OramInfo {
  status: string;
  info: {
    totalBlocks?: number;
    accessCount?: number;
    currentHeight?: number;
  };
}

// 数据转换函数：将后端返回的数据转换为前端需要的格式
function transformResult(backendResult: any): NearestResult {
  return {
    rect_id: backendResult.rect_id,
    keyword: backendResult.keyword,
    center_x: backendResult.center_x,
    center_y: backendResult.center_y,
    weighted_dist: backendResult.weighted_dist,
    original_dist: backendResult.original_dist,
    lev_distance: backendResult.lev_distance,
    orampath: backendResult.orampath || [],
    // 兼容属性
    get id() { return this.rect_id; },
    get x() { return this.center_x; },
    get y() { return this.center_y; },
    get distance() { return this.weighted_dist; },
    get path() { return this.orampath; }
  };
}

/**
 * 执行两轮查询逻辑（优化版本）
 * @param params 查询参数
 * @returns 两轮查询的完整结果和路径对比
 */
export async function twoRoundSearch(params: SearchParams): Promise<TwoRoundSearchResult> {
  try {
    console.log('开始执行两轮查询，参数:', params);
    const startTime = Date.now();

    // 第一轮查询：使用原始参数
    console.log('执行第一轮查询...');
    const firstRoundResponse = await request.get<TopKResponse>('/topk', {
      params: {
        keyword: params.keyword,
        x: params.x,
        y: params.y,
        k: params.k
      }
    });

    console.log('第一轮查询响应:', firstRoundResponse.data);

    // 转换第一轮结果
    const firstRoundResults = (firstRoundResponse.data.results || []).map(transformResult);
    console.log('第一轮查询结果数量:', firstRoundResults.length);
    
    const firstRoundTime = Date.now();
    console.log(`第一轮查询耗时: ${firstRoundTime - startTime}ms`);

    // 第二轮查询：批量处理，减少请求次数
    console.log('开始执行第二轮查询...');
    const secondRoundResults: NearestResult[] = [];
    const pathComparisons: PathComparison[] = [];

    // 优化：并行执行第二轮查询，而不是串行
    const secondRoundPromises = firstRoundResults.map(async (firstResult, index) => {
      try {
        console.log(`执行第二轮查询 ${index + 1}/${firstRoundResults.length}...`);
        
        // 使用第一轮结果的坐标和关键词进行单独查询
        const secondRoundResponse = await request.get<TopKResponse>('/topk', {
          params: {
            keyword: firstResult.keyword,
            x: firstResult.center_x,
            y: firstResult.center_y,
            k: 1 // 单个结果查询
          }
        });

        const backendSecondResult = secondRoundResponse.data.results?.[0];
        if (backendSecondResult) {
          const secondResult = transformResult(backendSecondResult);

          // 路径对比
          const firstPath = firstResult.orampath || [];
          const secondPath = secondResult.orampath || [];
          
          const differences: number[] = [];
          const maxLength = Math.max(firstPath.length, secondPath.length);
          
          for (let j = 0; j < maxLength; j++) {
            if (firstPath[j] !== secondPath[j]) {
              differences.push(j);
            }
          }

          return {
            secondResult,
            pathComparison: {
              firstRoundPath: firstPath,
              secondRoundPath: secondPath,
              differences,
              isIdentical: differences.length === 0 && firstPath.length === secondPath.length
            }
          };
        }
      } catch (error) {
        console.error(`第二轮查询第${index + 1}个结果时出错:`, error);
        // 即使单个查询失败，也继续处理其他结果
        return {
          secondResult: {
            ...firstResult,
            orampath: [] // 失败时使用空路径
          },
          pathComparison: {
            firstRoundPath: firstResult.orampath || [],
            secondRoundPath: [],
            differences: [],
            isIdentical: false
          }
        };
      }
    });

    // 等待所有第二轮查询完成
    const secondRoundResultsData = await Promise.all(secondRoundPromises);
    
    // 整理结果
    secondRoundResultsData.forEach(data => {
      if (data) {
        secondRoundResults.push(data.secondResult);
        pathComparisons.push(data.pathComparison);
      }
    });

    const endTime = Date.now();
    console.log(`第二轮查询耗时: ${endTime - firstRoundTime}ms`);
    console.log(`总查询耗时: ${endTime - startTime}ms`);

    // 统计信息
    const identicalPaths = pathComparisons.filter(comp => comp.isIdentical).length;
    const differentPaths = pathComparisons.length - identicalPaths;

    const result = {
      firstRoundResults,
      secondRoundResults,
      pathComparisons,
      summary: {
        totalQueries: firstRoundResults.length + secondRoundResults.length,
        identicalPaths,
        differentPaths
      }
    };

    console.log('两轮查询完成，结果:', result);
    return result;

  } catch (error) {
    console.error('两轮查询执行失败:', error);
    throw error;
  }
}

/**
 * 获取初始化信息
 * @returns 初始化信息
 */
export async function getInitInfo(): Promise<InitInfo> {
  const response = await request.get<InitInfo>('/init-info');
  return response.data;
}

/**
 * 获取ORAM运行时信息
 * @returns ORAM信息
 */
export async function getOramInfo(): Promise<OramInfo> {
  const response = await request.get<OramInfo>('/oram-info');
  return response.data;
}
