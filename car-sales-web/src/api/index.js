import axios from 'axios'

// 创建 axios 实例
// 所有 /api 请求走相对路径，由 Vite 代理转发到后端 127.0.0.1:8000。
// 这样无论用 localhost / 127.0.0.1 / 局域网IP 访问前端，都能正确连到后端。
const apiClient = axios.create({
  baseURL: '',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    console.log('发送请求：', config.method.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('请求错误：', error)
    return Promise.reject(error)
  },
)

// 响应拦截器：直接返回后端封装的 data
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('响应错误：', error.response?.status, error.message)
    return Promise.reject(error)
  },
)

// ============ 汽车销量预测系统 API ============

// 数据集概览
export const getOverview = () => apiClient.get('/api/overview')

// 主数据集月度销量序列
export const getSeries = () => apiClient.get('/api/series')

// 辅助数据集新车/二手车登记序列
export const getMultiSeries = () => apiClient.get('/api/multi-series')

// 四类模型评估指标
export const getMetrics = () => apiClient.get('/api/metrics')

// 未来 12 个月销量预测
export const getForecast = () => apiClient.get('/api/forecast')

// 回归模型测试集真实值 vs 预测值
export const getRegression = () => apiClient.get('/api/regression')

// 可视化图表文件列表
export const getFigures = () => apiClient.get('/api/figures')

// 数据库状态（三张表记录数）
export const getDbStats = () => apiClient.get('/api/db-stats')

// 最近接口查询日志
export const getLogs = (limit = 20) => apiClient.get('/api/logs', { params: { limit } })

// 智能问答：提问
export const askQuestion = (question) => apiClient.post('/api/qa/ask', { question })

// 智能问答：推荐问题
export const getSuggestedQuestions = () => apiClient.get('/api/qa/suggest')

// 最新汽车资讯（首页顶部）
export const getNews = () => apiClient.get('/api/news')

// 资讯详情（单条全文）
export const getNewsDetail = (id) => apiClient.get('/api/news/' + id)

// 数据图集（数据可视化大屏全部图表数据）
export const getChartData = () => apiClient.get('/api/charts/all')

// 品牌销量排行榜（榜单 + 趋势 + 占比）
export const getRanking = () => apiClient.get('/api/ranking/all')

export default apiClient

// 选车助手：筛选项元数据
export const getCarMeta = () => apiClient.get('/api/cars/meta')

// 选车助手：智能推荐（预算/能源/车身/国别筛选）
export const recommendCars = (params) => apiClient.get('/api/cars/recommend', { params })

// 选车助手：车型月销量趋势
export const getCarTrend = (params) => apiClient.get('/api/cars/trend', { params })

// 选车助手：车型销量 TOP 榜
export const getCarTop = (params) => apiClient.get('/api/cars/top', { params })

// 选车助手：车型数据浏览（分页筛选）
export const browseCars = (params) => apiClient.get('/api/cars/browse', { params })
