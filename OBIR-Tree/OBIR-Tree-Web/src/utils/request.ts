import axios, { AxiosResponse, AxiosError } from 'axios';

// 定义响应数据类型
interface ApiResponse<T = any> {
  status?: string;
  error?: string;
  data?: T;
}

// 创建基础请求实例
const request = axios.create({
  baseURL: 'http://localhost:8080', // 后端接口基础地址
  timeout: 10000, // 超时时间
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 可在此添加认证信息等
    return config;
  },
  (error) => {
    console.error('请求拦截器错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    // 针对 /topk 接口做 status 检查，其他接口直接返回
    const url = response.config.url || '';
    if (url.includes('/topk')) {
      const data = response.data as ApiResponse;
      if (data.status !== 'success') {
        console.warn('后端返回非成功状态:', data);
        return Promise.reject(new Error(data.error || '请求处理失败'));
      }
    }
    return response;
  },
  (error: AxiosError) => {
    // 统一处理错误
    let message = '网络请求失败';
    if (error.response) {
      message = `请求错误: ${error.response.status} ${error.response.statusText}`;
    } else if (error.request) {
      message = '请求超时，请检查网络';
    }
    console.error(message, error);
    return Promise.reject(new Error(message));
  }
);

export default request;
