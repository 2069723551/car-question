<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { getOverview, getMetrics, getNews } from '@/api'
import bg1 from '@/assets/news/bg1.jpg'
import bg2 from '@/assets/news/bg2.jpg'
import bg3 from '@/assets/news/bg3.jpg'
import bg4 from '@/assets/news/bg4.jpg'
import lcXiaomi from '@/assets/launch/xiaomi.jpg'
import lcLixiang from '@/assets/launch/lixiang.jpg'
import lcByd from '@/assets/launch/byd.jpg'
import lcChangan from '@/assets/launch/changan.jpg'
import lcVoyah from '@/assets/launch/voyah.jpg'

const router = useRouter()
const overview = ref(null)
const metrics = ref(null)
const news = ref([])
const loading = ref(true)
const error = ref('')

// 资讯卡片轮换背景图
const newsBg = [bg1, bg2, bg3, bg4]
const cardBg = (i) => newsBg[i % newsBg.length]

// 最新汽车发布会（点击直达官方资讯）
const launches = [
  { brand: '小米汽车', name: '2026秋季发布会 · 澎程四款新车上市', date: '2026-09-07', tag: '新车上市', desc: '澎程 N70 Pro 20.99万起，N70/N90 四款增程 SUV 同步上市，发布会 4 分钟锁单破万', source: '小米汽车官网', url: 'https://www.xiaomiev.com/skynomad/n90', color: '#fa5f1e', bg: lcXiaomi },
  { brand: '理想汽车', name: '新一代理想 MEGA 正式上市', date: '2026-09-02', tag: '新车上市', desc: '科技旗舰 MPV 仅推 Home 版，全国统一零售价 50.98 万元，本周内开启首批交付', source: '理想汽车官网', url: 'https://www.lixiang.com/news/186.html', color: '#e8b30b', bg: lcLixiang },
  { brand: '比亚迪', name: '海洋网旗舰 SUV 海狮08 上市', date: '2026-09-02', tag: '新车上市', desc: '官方指导价 22.99 万-27.99 万元，纯电/插混双动力，全系标配天神之眼 B 智驾', source: '新华网', url: 'http://www.xinhuanet.com/auto/20260903/96dc87120b08490eb3b2f11f5ee4b2db/c.html', color: '#1e90ff', bg: lcByd },
  { brand: '长安启源', name: '启源Q06 正式开启预售', date: '2026-09-04', tag: '开启预售', desc: '首搭"天枢领航"智驾系统，纯电/增程共 9 款车型，预售抢订价 14.79 万元起', source: '新浪·权威报道', url: 'https://www.sina.cn/news/article/comos_niracmk9843276.html', color: '#4f46e5', bg: lcChangan },
  { brand: '岚图汽车', name: '岚图追光S 上市发布会', date: '2026-08-15', tag: '上市发布', desc: '全球首款科技 FUV，四激光雷达全场景感知，限时权益价 22.39 万元起', source: '东风集团官网', url: 'https://www.dfmc.com.cn/news/company/news_20260817_0924.html', color: '#dc2626', bg: lcVoyah },
]

const loadData = async () => {
  try {
    const [ov, mt, ns] = await Promise.all([getOverview(), getMetrics(), getNews()])
    overview.value = ov
    metrics.value = mt
    news.value = ns?.news || []
    error.value = ''
    loading.value = false
    return true
  } catch (e) {
    error.value = '无法连接后端服务，正在自动重试…（请确认已启动 car-sales-backend / python main.py）'
    return false
  }
}

// 自动重连：后端未启动/启动慢时每 5 秒重试，连上后自动恢复并停止轮询
let retryTimer = null
onMounted(async () => {
  const ok = await loadData()
  if (!ok) {
    retryTimer = setInterval(async () => {
      if (await loadData()) clearInterval(retryTimer)
    }, 5000)
  }
})
onBeforeUnmount(() => {
  if (retryTimer) clearInterval(retryTimer)
})

// 板块快速入口（点击跳转到对应页面）
const sections = [
  { path: '/data', icon: '📊', title: '数据可视化', desc: '销量趋势、分布与多数据集对比图表', color: '#2563eb' },
  { path: '/ranking', icon: '🏆', title: '销量排行', desc: '厂商与车型销量 TOP 榜单、年度趋势与市占率', color: '#f59e0b' },
  { path: '/model', icon: '📈', title: '模型预测', desc: '四种模型评估与未来 12 个月销量预测', color: '#7c3aed' },
  { path: '/cars', icon: '🚗', title: '选车助手', desc: '按预算与偏好智能推荐车型、销量排行与全量数据浏览', color: '#0d9488' },
  { path: '/fun', icon: '🎮', title: '趣味乐园', desc: '汽车配色师、造车工坊、我的车库、公路赛车等互动小游戏', color: '#ec4899' },
  { path: '/qa', icon: '💬', title: '智能问答', desc: '汽车知识库与项目数据智能问答助手', color: '#ea580c' },
  { path: '/db', icon: '🗄️', title: '数据管理', desc: 'SQLite 数据库状态与接口查询日志', color: '#4f46e5' },
  { path: '/about', icon: '📖', title: '关于项目', desc: '项目说明、技术架构与课程文档', color: '#64748b' },
]

const go = (path) => router.push(path)

// 点击资讯卡查看全文
const goDetail = (id) => router.push('/news/' + id)

// 提取四模型对比数据
const modelOrder = [
  { key: 'linear_regression', name: '线性回归' },
  { key: 'random_forest', name: '随机森林' },
  { key: 'holt_winters', name: 'Holt-Winters' },
  { key: 'sarima', name: 'SARIMA' },
]

const modelRows = () => {
  if (!metrics.value?.model_comparison) return []
  return modelOrder.map((m) => ({
    name: m.name,
    ...metrics.value.model_comparison[m.key],
  }))
}

const bestModel = () => {
  if (!metrics.value?.model_comparison) return null
  const rows = modelRows()
  return rows.reduce((a, b) => (b.R2 > a.R2 ? b : a))
}
</script>

<template>
  <div>
    <!-- 顶部：最新汽车资讯 -->
    <section class="news-section">
      <div class="news-header">
        <span class="news-badge">最新资讯</span>
        <span class="news-title">汽车行业动态</span>
        <span class="news-more">AI 自动整理 · 每日更新</span>
      </div>
      <div class="news-scroll">
        <div
          v-for="(n, i) in news"
          :key="i"
          class="news-card"
          :style="{ backgroundImage: 'url(' + cardBg(i) + ')' }"
          @click="goDetail(n.id)"
          title="点击查看全文"
        >
          <div class="news-overlay"></div>
          <div class="news-body">
            <div class="news-date">{{ n.date }}</div>
            <div class="news-headline">{{ n.title }}</div>
            <div class="news-summary">{{ n.summary }}</div>
            <div class="news-source">{{ n.source }} · <span class="news-readmore">点击查看全文 →</span></div>
          </div>
        </div>
      </div>
    </section>

    <!-- 最新汽车发布会 -->
    <section class="launch-section">
      <div class="news-header">
        <span class="news-badge launch-badge">🚀 发布会</span>
        <span class="news-title">最新汽车发布会</span>
        <span class="news-more">点击卡片直达官方资讯</span>
      </div>
      <div class="launch-grid">
        <a
          v-for="(l, i) in launches"
          :key="i"
          :href="l.url"
          target="_blank"
          rel="noopener noreferrer"
          class="launch-card"
          :style="{ backgroundImage: 'linear-gradient(180deg, rgba(15,23,42,0.08) 0%, rgba(15,23,42,0.55) 45%, rgba(15,23,42,0.92) 100%), url(' + l.bg + ')' }"
        >
          <div class="launch-top">
            <span class="launch-date">📅 {{ l.date }}</span>
            <span class="launch-tag" :style="{ background: l.color }">{{ l.tag }}</span>
          </div>
          <div class="launch-brand">{{ l.brand }}</div>
          <div class="launch-name">{{ l.name }}</div>
          <div class="launch-desc">{{ l.desc }}</div>
          <div class="launch-foot">
            <span class="launch-source">{{ l.source }}</span>
            <span class="launch-go">查看官方资讯 →</span>
          </div>
        </a>
      </div>
    </section>

    <!-- 项目简介 -->
    <section class="hero" :style="{ backgroundImage: 'url(' + bg4 + ')' }">
      <div class="hero-overlay"></div>
      <div class="hero-content">
        <h1>汽车销量预测系统</h1>
        <p class="hero-sub">
          基于公开汽车销量数据集，完成数据采集与预处理、特征工程、回归与时间序列建模，
          输出未来销量预测与可视化分析。
        </p>
        <div class="hero-tags">
          <span>FastAPI 后端</span>
          <span>Vue3 前端</span>
          <span>机器学习</span>
          <span>时间序列预测</span>
          <span>SQLite 数据库</span>
          <span>智能问答</span>
        </div>
      </div>
    </section>

    <!-- 板块快速入口 -->
    <section class="section-title">
      <h3>功能板块</h3>
      <span>点击卡片快速进入对应模块</span>
    </section>
    <div class="section-grid">
      <div
        v-for="(s, i) in sections"
        :key="i"
        class="section-card"
        :style="{ '--card-color': s.color }"
        @click="go(s.path)"
      >
        <div class="section-icon">{{ s.icon }}</div>
        <div class="section-body">
          <div class="section-name">{{ s.title }}</div>
          <div class="section-desc">{{ s.desc }}</div>
        </div>
        <div class="section-arrow">进入 →</div>
      </div>
    </div>

    <div v-if="loading" class="loading">正在加载数据...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <template v-else>
      <!-- 关键指标 -->
      <div class="stat-grid">
        <div class="stat-item">
          <div class="stat-value">{{ overview.main.records }}</div>
          <div class="stat-label">主序列记录数（2018-2024 月度）</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ overview.mva.records }}</div>
          <div class="stat-label">明细数据记录数（车型-月度，38806 条）</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ bestModel()?.R2 ?? '-' }}</div>
          <div class="stat-label">最优模型 R²（{{ bestModel()?.name ?? '' }}）</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ bestModel()?.MAE ?? '-' }}</div>
          <div class="stat-label">最优模型 MAE（辆）</div>
        </div>
      </div>

      <!-- 数据集概览 -->
      <div class="card">
        <div class="card-title">数据集概览</div>
        <table class="data-table">
          <thead>
            <tr>
              <th>数据集</th>
              <th>记录数</th>
              <th>时间范围</th>
              <th>均值</th>
              <th>标准差</th>
              <th>最小值</th>
              <th>最大值</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{{ overview.main.name }}</td>
              <td>{{ overview.main.records }}</td>
              <td>{{ overview.main.start }} ~ {{ overview.main.end }}</td>
              <td>{{ overview.main.mean }}</td>
              <td>{{ overview.main.std }}</td>
              <td>{{ overview.main.min }}</td>
              <td>{{ overview.main.max }}</td>
            </tr>
            <tr>
              <td>{{ overview.mva.name }}</td>
              <td>{{ overview.mva.records }}</td>
              <td>{{ overview.mva.start }} ~ {{ overview.mva.end }}</td>
              <td colspan="4">车型-月度销量明细（含新能源标记、价格、车身类型，用于多维 EDA 展示）</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 模型对比摘要 -->
      <div class="card">
        <div class="card-title">模型评估指标（测试集）</div>
        <table class="data-table">
          <thead>
            <tr>
              <th>模型</th>
              <th>MAE</th>
              <th>RMSE</th>
              <th>R²</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in modelRows()" :key="row.name">
              <td>{{ row.name }}</td>
              <td>{{ row.MAE }}</td>
              <td>{{ row.RMSE }}</td>
              <td>{{ row.R2 }}</td>
            </tr>
          </tbody>
        </table>
        <p class="tip">最优模型为 {{ bestModel()?.name }}，R² = {{ bestModel()?.R2 }}，MAE = {{ bestModel()?.MAE }}</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
/* ---- 发布会区 ---- */
.launch-section {
  margin-bottom: 24px;
}
.launch-badge {
  background: linear-gradient(135deg, #7c3aed, #a855f7);
  box-shadow: 0 2px 8px rgba(124, 58, 237, 0.3);
}
.launch-grid {
  display: flex;
  gap: 14px;
  overflow-x: auto;
  padding-bottom: 8px;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
}
.launch-grid::-webkit-scrollbar {
  height: 6px;
}
.launch-grid::-webkit-scrollbar-track {
  background: #edf1f8;
  border-radius: 3px;
}
.launch-grid::-webkit-scrollbar-thumb {
  background: #c3cede;
  border-radius: 3px;
}
.launch-card {
  flex: 0 0 320px;
  scroll-snap-align: start;
  border-radius: 14px;
  padding: 16px 16px 14px;
  min-height: 180px;
  color: #fff;
  background-size: cover;
  background-position: center;
  display: flex;
  flex-direction: column;
  gap: 6px;
  text-decoration: none;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.14);
  transition: transform 0.2s, box-shadow 0.2s;
}
.launch-card:hover {
  transform: translateY(-4px) scale(1.01);
  box-shadow: 0 10px 26px rgba(0, 0, 0, 0.22);
}
.launch-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.launch-date {
  font-size: 12px;
  opacity: 0.92;
}
.launch-tag {
  background: rgba(255, 255, 255, 0.22);
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 999px;
}
.launch-brand {
  font-size: 15px;
  font-weight: 800;
  letter-spacing: 0.5px;
}
.launch-name {
  font-size: 15.5px;
  font-weight: 700;
  line-height: 1.35;
}
.launch-desc {
  font-size: 12.5px;
  line-height: 1.5;
  opacity: 0.9;
  flex: 1;
}
.launch-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
}
.launch-source {
  opacity: 0.85;
}
.launch-go {
  font-weight: 700;
  color: #fde68a;
}

/* ---- 资讯区 ---- */
.news-section {
  margin-bottom: 24px;
}
.news-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}
.news-badge {
  background: linear-gradient(135deg, #dc2626, #ef4444);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 8px;
  letter-spacing: 1px;
  box-shadow: 0 2px 8px rgba(220, 38, 38, 0.3);
}
.news-title {
  font-size: 17px;
  font-weight: 700;
  color: #1f2937;
}
.news-more {
  margin-left: auto;
  font-size: 12px;
  color: #9ca3af;
}
.news-scroll {
  display: flex;
  gap: 14px;
  overflow-x: auto;
  padding-bottom: 8px;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
}
.news-scroll::-webkit-scrollbar {
  height: 6px;
}
.news-scroll::-webkit-scrollbar-track {
  background: #edf1f8;
  border-radius: 3px;
}
.news-scroll::-webkit-scrollbar-thumb {
  background: #c3cede;
  border-radius: 3px;
}
.news-card {
  position: relative;
  flex: 0 0 400px;
  scroll-snap-align: start;
  background-size: cover;
  background-position: center;
  border-radius: 14px;
  min-height: 250px;
  overflow: hidden;
  display: flex;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12);
  transition: transform 0.2s, box-shadow 0.2s;
}
.news-card {
  cursor: pointer;
}
.news-card:hover {
  transform: translateY(-4px) scale(1.01);
  box-shadow: 0 10px 26px rgba(0, 0, 0, 0.2);
}
.news-card:hover .news-readmore {
  opacity: 1;
}
.news-readmore {
  margin-top: 6px;
  font-size: 11.5px;
  color: #fbbf24;
  font-weight: 600;
  opacity: 0;
  transition: opacity 0.2s;
}
.news-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(2, 10, 30, 0.25) 0%, rgba(2, 10, 30, 0.55) 55%, rgba(2, 10, 30, 0.92) 100%);
}
.news-body {
  position: relative;
  z-index: 1;
  padding: 16px 16px 14px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  width: 100%;
}
.news-date {
  font-size: 12px;
  color: #fbbf24;
  font-weight: 600;
  margin-bottom: 6px;
}
.news-headline {
  font-size: 15px;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.5;
  margin-bottom: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.news-summary {
  font-size: 12.5px;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.news-source {
  margin-top: 8px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.55);
}

/* ---- hero ---- */
.hero {
  position: relative;
  background-size: cover;
  background-position: center;
  border-radius: 16px;
  padding: 34px 38px;
  color: #ffffff;
  margin-bottom: 22px;
  overflow: hidden;
  box-shadow: 0 6px 22px rgba(2, 10, 30, 0.25);
}
.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(100deg, rgba(2, 20, 60, 0.88) 0%, rgba(2, 20, 60, 0.55) 55%, rgba(2, 20, 60, 0.15) 100%);
}
.hero-content {
  position: relative;
  z-index: 1;
}
.hero h1 {
  font-size: 32px;
  margin-bottom: 12px;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.35);
}
.hero-sub {
  font-size: 15px;
  line-height: 1.8;
  color: #e6eeff;
  margin-bottom: 18px;
  max-width: 640px;
}
.hero-tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.hero-tags span {
  background: rgba(255, 255, 255, 0.16);
  border: 1px solid rgba(255, 255, 255, 0.32);
  border-radius: 20px;
  padding: 4px 14px;
  font-size: 13px;
  backdrop-filter: blur(4px);
}

/* ---- 板块入口 ---- */
.section-title {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 14px;
}
.section-title h3 {
  font-size: 18px;
  color: #1f2937;
  margin: 0;
}
.section-title span {
  font-size: 13px;
  color: #9ca3af;
}
.section-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 14px;
  margin-bottom: 28px;
}
.section-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 16px;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
}
.section-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
  border-color: var(--card-color);
}
.section-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: color-mix(in srgb, var(--card-color) 12%, #fff);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}
.section-body {
  flex: 1;
  min-width: 0;
}
.section-name {
  font-size: 15px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 3px;
}
.section-desc {
  font-size: 12.5px;
  color: #6b7280;
  line-height: 1.5;
}
.section-arrow {
  font-size: 13px;
  color: var(--card-color);
  font-weight: 600;
  white-space: nowrap;
}

/* ---- 原有数据区 ---- */
.tip {
  margin-top: 12px;
  font-size: 14px;
  color: #0b5fff;
  font-weight: 600;
}
</style>
