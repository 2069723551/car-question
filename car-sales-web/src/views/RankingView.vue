<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getRanking } from '@/api'

const data = ref(null)
const loading = ref(true)
const error = ref('')
const charts = {}

const C = {
  blue: '#0b5fff',
  lightBlue: '#5ea0ff',
  purple: '#7c3aed',
  orange: '#ff8a4c',
  teal: '#0d9488',
  red: '#ef4444',
}

const axisStyle = {
  axisLine: { lineStyle: { color: '#d1d5db' } },
  axisLabel: { color: '#6b7280', fontSize: 11 },
  splitLine: { lineStyle: { color: '#f1f5f9' } },
}

function disposeAll() {
  Object.values(charts).forEach((c) => c?.dispose())
}

onMounted(async () => {
  try {
    const res = await getRanking()
    data.value = res?.data
    loading.value = false
    await nextTick()
    renderCharts()
  } catch (e) {
    console.error(e)
    error.value = '无法连接后端服务，请确认已启动 car-sales-backend（python main.py）'
    loading.value = false
  }
})

onBeforeUnmount(disposeAll)

function init(id, option) {
  const el = document.getElementById(id)
  if (!el) return
  if (charts[id]) charts[id].dispose()
  const chart = echarts.init(el)
  chart.setOption(option)
  charts[id] = chart
}

function renderCharts() {
  const d = data.value
  if (!d) return

  // 图1 累计 TOP10 横向条形（含占比）
  const cum = d.cumulative_top.slice().reverse()
  init('chart-rank-bar', {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: (ps) => `${ps[0].name}<br/>累计销量：${ps[0].value.toLocaleString()} 辆<br/>市占率：${d.cumulative_top.find((x) => x.brand === ps[0].name)?.share ?? 0}%` },
    grid: { left: 100, right: 60, top: 10, bottom: 30 },
    xAxis: { type: 'value', name: '销量（辆）', ...axisStyle },
    yAxis: { type: 'category', data: cum.map((x) => x.brand), ...axisStyle },
    series: [
      {
        name: '累计销量',
        type: 'bar',
        barWidth: '55%',
        data: cum.map((x) => x.total),
        label: { show: true, position: 'right', formatter: (p) => d.cumulative_top[9 - p.dataIndex].share + '%', fontSize: 11, color: '#6b7280' },
        itemStyle: {
          borderRadius: [0, 6, 6, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#a5c8ff' },
            { offset: 1, color: C.blue },
          ]),
        },
      },
    ],
  })

  // 图2 TOP6 品牌年度销量趋势
  const trend = d.trend_series
  const years = trend.map((x) => x.year)
  const brands = d.cumulative_top.slice(0, 6).map((x) => x.brand)
  const palette = [C.blue, C.orange, C.purple, C.teal, C.red, '#0891b2']
  init('chart-rank-trend', {
    tooltip: { trigger: 'axis' },
    legend: { top: 0 },
    grid: { left: 70, right: 24, top: 40, bottom: 40 },
    xAxis: { type: 'category', data: years, ...axisStyle },
    yAxis: { type: 'value', name: '年销量（辆）', ...axisStyle },
    series: brands.map((b, i) => ({
      name: b,
      type: 'line',
      smooth: true,
      showSymbol: false,
      data: trend.map((y) => y.brands[b] ?? 0),
      lineStyle: { width: 2.5, color: palette[i] },
      itemStyle: { color: palette[i] },
    })),
  })

  // 图3 年度销量王座演变
  const ch = d.champions
  init('chart-rank-king', {
    tooltip: {
      trigger: 'axis',
      formatter: (ps) => {
        const p = ps[0]
        const row = ch[p.dataIndex]
        return `${row.year} 年<br/>冠军：${row.brand}（${row.total.toLocaleString()} 辆）<br/>亚军：${row.runner_up ?? '—'}`
      },
    },
    grid: { left: 70, right: 24, top: 30, bottom: 40 },
    xAxis: { type: 'category', data: ch.map((x) => x.year), ...axisStyle },
    yAxis: { type: 'value', name: '冠军销量（辆）', ...axisStyle },
    series: [
      {
        name: '年度冠军销量',
        type: 'bar',
        barWidth: '50%',
        data: ch.map((x) => x.total),
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: C.orange },
            { offset: 1, color: '#fed7aa' },
          ]),
        },
        label: {
          show: true,
          position: 'top',
          formatter: (p) => ch[p.dataIndex].brand,
          fontSize: 10,
          color: '#6b7280',
        },
      },
    ],
  })
}

// 厂商官网映射（点击厂商名跳转官网）
const brandSites = [
  ['一汽-大众', 'https://www.faw-vw.com'],
  ['一汽大众', 'https://www.faw-vw.com'],
  ['上汽大众', 'https://www.svw-volkswagen.com'],
  ['大众', 'https://www.volkswagen.com.cn'],
  ['上汽通用五菱', 'https://www.sgmw.com.cn'],
  ['五菱', 'https://www.sgmw.com.cn'],
  ['上汽通用别克', 'https://www.buick.com.cn'],
  ['别克', 'https://www.buick.com.cn'],
  ['雪佛兰', 'https://www.chevrolet.com.cn'],
  ['凯迪拉克', 'https://www.cadillac.com.cn'],
  ['广汽丰田', 'https://www.gac-toyota.com'],
  ['一汽丰田', 'https://www.ftms.com.cn'],
  ['丰田', 'https://www.toyota.com.cn'],
  ['东风日产', 'https://www.dongfeng-nissan.com.cn'],
  ['日产', 'https://www.nissan.com.cn'],
  ['广汽本田', 'https://www.ghac.cn'],
  ['东风本田', 'https://www.dongfenghonda.com'],
  ['本田', 'https://www.honda.com.cn'],
  ['比亚迪', 'https://www.byd.com'],
  ['吉利', 'https://www.geely.com'],
  ['长安', 'https://www.changan.com.cn'],
  ['长城', 'https://www.gwm.com.cn'],
  ['奇瑞', 'https://www.chery.cn'],
  ['广汽', 'https://www.gac.com.cn'],
  ['东风', 'https://www.dfmc.com.cn'],
  ['特斯拉', 'https://www.tesla.cn'],
  ['蔚来', 'https://www.nio.cn'],
  ['理想', 'https://www.lixiang.com'],
  ['小鹏', 'https://www.xiaopeng.com'],
  ['小米', 'https://www.xiaomiev.com'],
  ['奔驰', 'https://www.mercedes-benz.com.cn'],
  ['宝马', 'https://www.bmw.com.cn'],
  ['奥迪', 'https://www.audi.cn'],
  ['现代', 'https://www.hyundai.com.cn'],
  ['起亚', 'https://www.kia.com'],
  ['福特', 'https://www.ford.com.cn'],
  ['马自达', 'https://www.mazda.com.cn'],
  ['沃尔沃', 'https://www.volvocars.com'],
  ['保时捷', 'https://www.porsche.cn'],
  ['雷克萨斯', 'https://www.lexus.com.cn'],
  ['斯柯达', 'https://www.skoda.com.cn'],
  ['荣威', 'https://www.roewe.com.cn'],
  ['名爵', 'https://www.mgmotor.com.cn'],
  ['领克', 'https://www.lynkco.com.cn'],
  ['哈弗', 'https://www.haval.com.cn'],
  ['哪吒', 'https://www.neta.com'],
  ['零跑', 'https://www.leapmotor.com.cn'],
  ['极氪', 'https://www.zeekrlife.com'],
  ['埃安', 'https://www.aionlife.com'],
  ['阿维塔', 'https://www.avatr.com'],
  ['岚图', 'https://www.voyah.com.cn'],
  ['智己', 'https://www.im-motors.com.cn'],
  ['极狐', 'https://www.arcfox.com.cn'],
  ['红旗', 'https://www.faw-hongqi.com.cn'],
  ['奔腾', 'https://www.besturn.com.cn'],
  ['江淮', 'https://www.jac.com.cn'],
  ['北汽', 'https://www.baicmotor.com'],
  ['福田', 'https://www.foton.com.cn'],
  ['捷达', 'https://www.jetta.com.cn'],
  ['启辰', 'https://www.venucia.com'],
  ['捷途', 'https://www.jetour.com.cn'],
  ['星途', 'https://www.cheryexeed.com'],
  ['标致', 'https://www.peugeot.com.cn'],
  ['雪铁龙', 'https://www.dongfeng-citroen.com.cn'],
  ['捷豹', 'https://www.jaguar.com.cn'],
  ['路虎', 'https://www.landrover.com.cn'],
  ['smart', 'https://www.smart.com'],
]
const brandSite = (name) => {
  if (!name) return ''
  for (const [k, url] of brandSites) {
    if (name.includes(k) || k.includes(name)) return url
  }
  return ''
}

// 榜单徽章颜色
function medal(i) {
  const colors = ['#f5b50a', '#94a3b8', '#c98a4b', '#0b5fff', '#7c3aed']
  return colors[i] || '#64748b'
}

const statsCards = () => {
  const s = data.value?.stats
  if (!s) return []
  return [
    { label: '数据覆盖年份', value: s.years, color: C.blue },
    { label: '厂商数量', value: s.brands, unit: '个', color: C.purple },
    { label: '总销量', value: s.total_sales.toLocaleString(), unit: '辆', color: C.teal },
    { label: '销量冠军', value: s.top_brand, sub: s.top_brand_sales.toLocaleString() + ' 辆', color: C.orange },
    { label: '纯电（EV）占比', value: s.ev_share + '%', color: C.red },
  ]
}

// 下载图表 PNG
function downloadChart(id, name) {
  const chart = charts[id]
  if (!chart) return
  const url = chart.getDataURL({ pixelRatio: 2, backgroundColor: '#ffffff' })
  const a = document.createElement('a')
  a.href = url
  a.download = name + '.png'
  a.click()
}
</script>

<template>
  <div>
    <h2 class="page-title">厂商销量排行榜（中国）</h2>
    <p class="page-desc">基于中国乘用车月度销量数据（乘联会 CPCA 登记记录整理，2018-2024），展示厂商累计排名、年度趋势与市场格局。</p>

    <div v-if="loading" class="loading">正在加载数据...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <template v-else>
      <!-- 指标卡 -->
      <div class="stat-grid">
        <div v-for="(s, i) in statsCards()" :key="i" class="stat-item" :style="{ '--accent': s.color }">
          <div class="stat-value">{{ s.value }}</div>
          <div class="stat-label">{{ s.label }}</div>
          <div v-if="s.sub" class="stat-sub">{{ s.sub }}</div>
        </div>
      </div>

      <div class="rank-layout">
        <!-- 左侧：榜单卡片 -->
        <div class="rank-left">
          <div class="card">
            <div class="card-title">累计销量 TOP10 厂商榜单（2018-2024）</div>
            <div v-for="(r, i) in data.cumulative_top" :key="r.brand" class="rank-row">
              <span class="rank-no" :style="{ background: medal(i) }">{{ i + 1 }}</span>
              <span class="rank-brand"><a v-if="brandSite(r.brand)" :href="brandSite(r.brand)" target="_blank" rel="noopener" class="brand-link" title="访问{{ r.brand }}官网">{{ r.brand }}</a><template v-else>{{ r.brand }}</template></span>
              <span class="rank-bar">
                <span class="rank-fill" :style="{ width: r.share_in_top + '%', background: medal(i) }"></span>
              </span>
              <span class="rank-num">{{ r.total.toLocaleString() }}</span>
              <span class="rank-share">{{ r.share }}%</span>
            </div>
          </div>

          <div class="card">
            <div class="card-title">最新完整年度（{{ data.stats.latest_year }}）TOP10 厂商</div>
            <div v-for="(r, i) in data.latest_top" :key="r.brand" class="rank-row">
              <span class="rank-no" :style="{ background: medal(i) }">{{ i + 1 }}</span>
              <span class="rank-brand"><a v-if="brandSite(r.brand)" :href="brandSite(r.brand)" target="_blank" rel="noopener" class="brand-link" title="访问{{ r.brand }}官网">{{ r.brand }}</a><template v-else>{{ r.brand }}</template></span>
              <span class="rank-bar">
                <span class="rank-fill" :style="{ width: (r.total / data.latest_top[0].total * 100) + '%', background: '#0b5fff' }"></span>
              </span>
              <span class="rank-num">{{ r.total.toLocaleString() }}</span>
            </div>
          </div>
        </div>

        <!-- 右侧：图表 -->
        <div class="rank-right">
          <div class="card">
            <div class="card-title">图1 · 累计销量 TOP10 厂商（市占率）<span class="dl-btn" @click.stop="downloadChart('chart-rank-bar','图1-累计销量 TOP10(市占率)')">⤓ PNG</span></div>
        <div id="chart-rank-bar" class="chart-box"></div>
          </div>

          <div class="card">
            <div class="card-title">图2 · TOP6 品牌年度销量趋势<span class="dl-btn" @click.stop="downloadChart('chart-rank-trend','图2-TOP6 品牌年度销量趋势')">⤓ PNG</span></div>
        <div id="chart-rank-trend" class="chart-box"></div>
          </div>

          <div class="card">
            <div class="card-title">图3 · 年度销量王座演变（历年冠军）<span class="dl-btn" @click.stop="downloadChart('chart-rank-king','图3-年度销量王座演变(历年冠军)')">⤓ PNG</span></div>
        <div id="chart-rank-king" class="chart-box"></div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 14px;
  margin-bottom: 22px;
}
.stat-item {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 16px 14px;
  border-top: 3px solid var(--accent);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}
.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 4px;
}
.stat-label {
  font-size: 12px;
  color: #6b7280;
}
.stat-sub {
  font-size: 11px;
  color: #9ca3af;
  margin-top: 2px;
}

.rank-layout {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 18px;
  align-items: start;
}
@media (max-width: 1000px) {
  .rank-layout {
    grid-template-columns: 1fr;
  }
}
.rank-left {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.rank-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 0;
  font-size: 13px;
}
.rank-no {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  color: #fff;
  font-weight: 700;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.rank-brand {
  width: 92px;
  font-weight: 600;
  color: #1f2937;
  flex-shrink: 0;
}
.brand-link {
  color: #1f2937;
  text-decoration: none;
  border-bottom: 1px dashed #94a3b8;
  transition: color 0.15s, border-color 0.15s;
}
.brand-link:hover {
  color: #0b5fff;
  border-bottom-color: #0b5fff;
}
.rank-bar {
  flex: 1;
  height: 12px;
  background: #eef2f7;
  border-radius: 6px;
  overflow: hidden;
}
.rank-fill {
  display: block;
  height: 100%;
  border-radius: 6px;
}
.rank-num {
  width: 76px;
  text-align: right;
  color: #111827;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
}
.rank-share {
  width: 42px;
  text-align: right;
  color: #6b7280;
  flex-shrink: 0;
}
.rank-right {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.card-title {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 12px;
  padding-left: 10px;
  border-left: 4px solid #0b5fff;
}
.chart-box {
  width: 100%;
  height: 300px;
}
.dl-btn {
  float: right;
  font-size: 11px;
  font-weight: 400;
  color: #0b5fff;
  background: #eef4ff;
  border-radius: 6px;
  padding: 2px 8px;
  cursor: pointer;
  opacity: 0.75;
  transition: opacity 0.2s;
}
.dl-btn:hover {
  opacity: 1;
  background: #dbe8ff;
}
</style>
