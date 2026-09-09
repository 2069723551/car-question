<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getSeries, getMultiSeries, getFigures, getChartData } from '@/api'

const series = ref([])
const multiSeries = ref([])
const figures = ref([])
const chartData = ref(null)
const loading = ref(true)
const error = ref('')

const charts = {} // 所有 ECharts 实例

// 统一配色（宝石蓝 + 紫 + 橙）
const C = {
  blue: '#0b5fff',
  lightBlue: '#5ea0ff',
  purple: '#7c3aed',
  orange: '#ff8a4c',
  teal: '#0d9488',
  red: '#ef4444',
  grid: '#e5e7eb',
}

function disposeAll() {
  Object.values(charts).forEach((c) => c?.dispose())
}

// 下载单张 ECharts 图为 PNG
function downloadChart(id, name) {
  const chart = charts[id]
  if (!chart) return
  const url = chart.getDataURL({ pixelRatio: 2, backgroundColor: '#ffffff' })
  const a = document.createElement('a')
  a.href = url
  a.download = name + '.png'
  a.click()
}

// 下载季节分解 PNG（图11）
function downloadImg(url, name) {
  const a = document.createElement('a')
  a.href = url
  a.download = name + '.png'
  a.click()
}

// 一键导出全部图表 PNG（逐个触发下载）
function downloadAllCharts() {
  const map = {
    'chart-trend': '图1-中国乘用车月度销量趋势',
    'chart-multi': '图2-新能源vs燃油月度销量',
    'chart-annual': '图3-年度销量汇总',
    'chart-seasonal': '图4-月度季节模式',
    'chart-ma': '图5-移动平均对比',
    'chart-yoy': '图6-年度同比增速',
    'chart-dist': '图7-车型销量分布直方图',
    'chart-mva': '图8-新能源vs燃油堆叠',
    'chart-mva-sales': '图9-新能源渗透率',
    'chart-share': '图10-厂商销量占比',
    'chart-price-band': '图11-价格带分布',
    'chart-price': '图12-国产vs外资走势',
  }
  Object.entries(map).forEach(([id, name], i) => {
    setTimeout(() => downloadChart(id, name), i * 400)
  })
}

// 导出图集聚合数据为 CSV
function downloadCsv() {
  const d = chartData.value
  if (!d) return
  const parts = []
  // 年度销量
  parts.push('year,total_sales')
  d.annual_sales.forEach((x) => parts.push(x.year + ',' + x.total))
  // 季节模式
  parts.push('', 'month,avg_sales')
  d.seasonal_pattern.forEach((x) => parts.push(x.month + ',' + x.avg))
  // 同比增速
  parts.push('', 'year,total_sales,growth_pct')
  d.yoy_growth.forEach((x) => parts.push(x.year + ',' + x.total + ',' + (x.growth ?? '')))
  // 国产 vs 外资（万辆）
  parts.push('', 'year,domestic_wan,foreign_wan')
  d.avg_price_trend.forEach((x) => parts.push(x.year + ',' + x.new + ',' + x.used))
  // 价格带分布
  parts.push('', 'band,total_sales')
  d.price_bands.forEach((x) => parts.push(x.band + ',' + x.count))
  // 占比
  parts.push('', 'category,total')
  d.mva_share.forEach((x) => parts.push(x.name + ',' + x.value))
  const blob = new Blob(['\ufeff' + parts.join('\r\n')], { type: 'text/csv;charset=utf-8' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = '汽车销量图集数据.csv'
  a.click()
  URL.revokeObjectURL(a.href)
}

onMounted(async () => {
  try {
    const [s, ms, fg, cd] = await Promise.all([
      getSeries(),
      getMultiSeries(),
      getFigures(),
      getChartData(),
    ])
    series.value = s
    multiSeries.value = ms
    figures.value = fg
    chartData.value = cd?.data
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

// 通用 grid / 轴样式
const axisStyle = {
  axisLine: { lineStyle: { color: '#d1d5db' } },
  axisLabel: { color: '#6b7280', fontSize: 11 },
  splitLine: { lineStyle: { color: '#f1f5f9' } },
}

function renderCharts() {
  const d = chartData.value
  if (!d) return
  const stats = d.stats || {}

  // 图1（保留）主数据集月度销量趋势
  init('chart-trend', {
    tooltip: { trigger: 'axis' },
    grid: { left: 60, right: 24, top: 40, bottom: 40 },
    xAxis: { type: 'category', data: series.value.map((x) => x.date.slice(0, 7)), axisLabel: { interval: 11 }, ...axisStyle },
    yAxis: { type: 'value', name: '销量（辆）', ...axisStyle },
    series: [
      {
        name: '月度销量',
        type: 'line',
        smooth: true,
        data: series.value.map((x) => x.sales),
        lineStyle: { width: 2.5, color: C.blue },
        itemStyle: { color: C.blue },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(11,95,255,0.28)' },
            { offset: 1, color: 'rgba(11,95,255,0.02)' },
          ]),
        },
      },
    ],
  })

  // 图2 新能源(EV) vs 燃油车 月度销量
  init('chart-multi', {
    tooltip: { trigger: 'axis' },
    legend: { data: ['新能源(EV)', '燃油车'], top: 0 },
    grid: { left: 60, right: 24, top: 40, bottom: 40 },
    xAxis: { type: 'category', data: multiSeries.value.map((x) => x.date.slice(0, 7)), axisLabel: { interval: 11 }, ...axisStyle },
    yAxis: { type: 'value', name: '销量（辆）', ...axisStyle },
    series: [
      { name: '新能源(EV)', type: 'line', smooth: true, showSymbol: false, data: multiSeries.value.map((x) => x.new), lineStyle: { width: 2.5, color: C.blue }, itemStyle: { color: C.blue }, areaStyle: { color: 'rgba(11,95,255,0.08)' } },
      { name: '燃油车', type: 'line', smooth: true, showSymbol: false, data: multiSeries.value.map((x) => x.used), lineStyle: { width: 2, color: C.orange }, itemStyle: { color: C.orange } },
    ],
  })

  // 图3 年度销量柱状图
  init('chart-annual', {
    tooltip: { trigger: 'axis' },
    grid: { left: 60, right: 24, top: 30, bottom: 40 },
    xAxis: { type: 'category', data: d.annual_sales.map((x) => x.year), ...axisStyle },
    yAxis: { type: 'value', name: '销量（辆）', ...axisStyle },
    series: [
      {
        name: '年度销量',
        type: 'bar',
        barWidth: '55%',
        data: d.annual_sales.map((x) => x.total),
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: C.blue },
            { offset: 1, color: C.lightBlue },
          ]),
        },
      },
    ],
  })

  // 图4 月度季节模式
  init('chart-seasonal', {
    tooltip: { trigger: 'axis' },
    grid: { left: 60, right: 24, top: 30, bottom: 40 },
    xAxis: { type: 'category', data: d.seasonal_pattern.map((x) => x.month + '月'), ...axisStyle },
    yAxis: { type: 'value', name: '平均销量（辆）', ...axisStyle },
    series: [
      {
        name: '多年平均',
        type: 'bar',
        barWidth: '50%',
        data: d.seasonal_pattern.map((x) => x.avg),
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: C.purple },
            { offset: 1, color: '#c4b5fd' },
          ]),
        },
      },
    ],
  })

  // 图5 移动平均 vs 原始
  init('chart-ma', {
    tooltip: { trigger: 'axis' },
    legend: { data: ['月度销量', '12 月移动平均'], top: 0 },
    grid: { left: 60, right: 24, top: 40, bottom: 40 },
    xAxis: { type: 'category', data: d.moving_average.map((x) => x.date.slice(0, 7)), axisLabel: { interval: 11 }, ...axisStyle },
    yAxis: { type: 'value', name: '销量（辆）', ...axisStyle },
    series: [
      { name: '月度销量', type: 'line', smooth: true, showSymbol: false, data: d.moving_average.map((x) => x.sales), lineStyle: { width: 1.5, color: '#cbd5e1' }, itemStyle: { color: '#cbd5e1' } },
      { name: '12 月移动平均', type: 'line', smooth: true, showSymbol: false, data: d.moving_average.map((x) => x.ma12), lineStyle: { width: 3, color: C.red }, itemStyle: { color: C.red }, areaStyle: { color: 'rgba(239,68,68,0.06)' } },
    ],
  })

  // 图6 年度同比增速
  init('chart-yoy', {
    tooltip: {
      trigger: 'axis',
      formatter: (ps) => {
        const p = ps[0]
        const row = d.yoy_growth[p.dataIndex]
        return `${row.year} 年<br/>销量：${row.total.toLocaleString()} 辆<br/>同比：${row.growth === null ? '—' : row.growth + '%'}`
      },
    },
    grid: { left: 60, right: 24, top: 30, bottom: 40 },
    xAxis: { type: 'category', data: d.yoy_growth.map((x) => x.year), ...axisStyle },
    yAxis: { type: 'value', name: '销量（辆）', ...axisStyle },
    series: [
      {
        name: '年度销量',
        type: 'bar',
        barWidth: '50%',
        data: d.yoy_growth.map((x) => x.total),
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
          color: (p) => {
            const g = d.yoy_growth[p.dataIndex].growth
            return g !== null && g >= 0 ? C.teal : C.red
          },
        },
        label: {
          show: true,
          position: 'top',
          formatter: (p) => {
            const g = d.yoy_growth[p.dataIndex].growth
            return g === null ? '' : (g >= 0 ? '+' : '') + g + '%'
          },
          fontSize: 10,
          color: '#6b7280',
        },
      },
    ],
  })

  // 图7 销量分布直方图
  init('chart-dist', {
    tooltip: { trigger: 'axis' },
    grid: { left: 60, right: 24, top: 30, bottom: 55 },
    xAxis: { type: 'category', data: d.distribution.map((x) => x.range), axisLabel: { rotate: 35, fontSize: 10 }, ...axisStyle },
    yAxis: { type: 'value', name: '车型-月记录数', ...axisStyle },
    series: [
      {
        name: '分布',
        type: 'bar',
        barWidth: '60%',
        data: d.distribution.map((x) => x.count),
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: C.orange },
            { offset: 1, color: '#fed7aa' },
          ]),
        },
      },
    ],
  })

  // 图8 新能源(EV) vs 燃油车（按年堆叠）
  init('chart-mva', {
    tooltip: { trigger: 'axis' },
    legend: { data: ['新能源(EV)', '燃油车'], top: 0 },
    grid: { left: 70, right: 24, top: 40, bottom: 40 },
    xAxis: { type: 'category', data: d.mva_compare.map((x) => x.year), axisLabel: { interval: 3 }, ...axisStyle },
    yAxis: { type: 'value', name: '销量（辆）', ...axisStyle },
    series: [
      { name: '新能源(EV)', type: 'bar', stack: 't', barWidth: '60%', data: d.mva_compare.map((x) => x.new), itemStyle: { color: C.blue } },
      { name: '燃油车', type: 'bar', stack: 't', barWidth: '60%', data: d.mva_compare.map((x) => x.used), itemStyle: { color: '#a5c8ff' } },
    ],
  })

  // 图9 新能源渗透率年度走势
  init('chart-mva-sales', {
    tooltip: { trigger: 'axis', valueFormatter: (v) => v + '%' },
    legend: { data: ['新能源占比', '燃油占比'], top: 0 },
    grid: { left: 70, right: 24, top: 40, bottom: 40 },
    xAxis: { type: 'category', data: d.mva_sales_trend.map((x) => x.year), axisLabel: { interval: 3 }, ...axisStyle },
    yAxis: { type: 'value', name: '占比（%）', min: 0, max: 100, ...axisStyle },
    series: [
      { name: '新能源占比', type: 'line', smooth: true, showSymbol: false, data: d.mva_sales_trend.map((x) => x.new), lineStyle: { width: 3, color: C.teal }, itemStyle: { color: C.teal }, areaStyle: { color: 'rgba(13,148,136,0.12)' } },
      { name: '燃油占比', type: 'line', smooth: true, showSymbol: false, data: d.mva_sales_trend.map((x) => x.used), lineStyle: { width: 2, color: C.orange }, itemStyle: { color: C.orange } },
    ],
  })

  // 图10 新车/二手销量占比环形图
  init('chart-share', {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0 },
    color: [C.blue, C.orange],
    series: [
      {
        name: '销量占比',
        type: 'pie',
        radius: ['42%', '68%'],
        center: ['50%', '46%'],
        label: { formatter: '{b}\n{d}%', fontSize: 12 },
        data: d.mva_share,
        itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 3 },
      },
    ],
  })

  // 图11 / 图12
  renderPriceBand()
  renderPriceChart()
}

// 图11 价格带分布（万元）
function renderPriceBand() {
  const d = chartData.value
  if (!d?.price_bands?.length) return
  const colors = ['#0b5fff', '#3b82f6', '#7c3aed', '#a855f7', '#ff8a4c']
  init('chart-price-band', {
    tooltip: { trigger: 'axis', formatter: (ps) => {
      const x = ps[0]
      const row = d.price_bands[x.dataIndex]
      return row.band + '<br/>累计销量：' + row.count.toLocaleString() + ' 辆'
    } },
    grid: { left: 70, right: 24, top: 30, bottom: 40 },
    xAxis: { type: 'category', data: d.price_bands.map((x) => x.band), ...axisStyle },
    yAxis: { type: 'value', name: '累计销量（辆）', ...axisStyle },
    series: [
      {
        name: '价格带销量',
        type: 'bar',
        barWidth: '52%',
        data: d.price_bands.map((x) => x.count),
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: (p) => new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: colors[p.dataIndex] },
            { offset: 1, color: colors[p.dataIndex] + '88' },
          ]),
        },
        label: {
          show: true,
          position: 'top',
          formatter: (p) => (p.value / 1e4).toFixed(0) + '万',
          fontSize: 11,
          color: '#6b7280',
        },
      },
    ],
  })
}

// 图12 国产 vs 外资品牌销量走势（万辆）
function renderPriceChart() {
  const d = chartData.value
  if (!d?.avg_price_trend?.length) return
  init('chart-price', {
    tooltip: { trigger: 'axis' },
    legend: { data: ['国产车', '外资车'], top: 0 },
    grid: { left: 70, right: 24, top: 40, bottom: 40 },
    xAxis: { type: 'category', data: d.avg_price_trend.map((x) => x.year), axisLabel: { interval: 3 }, ...axisStyle },
    yAxis: { type: 'value', name: '销量（万辆）', min: (v) => Math.floor(v.min * 0.85), max: (v) => Math.ceil(v.max * 1.05), ...axisStyle },
    series: [
      { name: '国产车', type: 'line', smooth: true, showSymbol: false, data: d.avg_price_trend.map((x) => x.new), lineStyle: { width: 3, color: C.blue }, itemStyle: { color: C.blue }, areaStyle: { color: 'rgba(11,95,255,0.1)' } },
      { name: '外资车', type: 'line', smooth: true, showSymbol: false, data: d.avg_price_trend.map((x) => x.used), lineStyle: { width: 2.5, color: C.orange }, itemStyle: { color: C.orange }, areaStyle: { color: 'rgba(255,138,76,0.1)' } },
    ],
  })
}


// 指标卡
const statCards = () => {
  const s = chartData.value?.stats
  if (!s) return []
  return [
    { label: '历史累计销量', value: s.main_total.toLocaleString(), unit: '辆', color: C.blue },
    { label: '月均销量', value: s.main_avg.toLocaleString(), unit: '辆', color: C.purple },
    { label: '销量峰值', value: s.main_peak.sales.toLocaleString(), sub: s.main_peak.date, color: C.teal },
    { label: '销量低谷', value: s.main_trough.sales.toLocaleString(), sub: s.main_trough.date, color: C.orange },
    { label: '新能源(EV)总销量', value: s.mva_new_total.toLocaleString(), unit: '辆', color: C.red },
    { label: '燃油车总销量', value: s.mva_used_total.toLocaleString(), unit: '辆', color: '#64748b' },
  ]
}
</script>

<template>
  <div>
    <h2 class="page-title">数据可视化 · 汽车数据图集</h2>
    <p class="page-desc">基于中国乘用车销量数据（乘联会 CPCA 来源，2018-2024，38806 条车型-月度记录），展示市场趋势、新能源渗透、价格带与厂商格局（共 12 张图）。</p>
    <div class="export-bar">
      <button class="export-btn" @click="downloadAllCharts">⤓ 一键导出全部图表</button>
      <button class="export-btn" @click="downloadCsv">⤓ 导出聚合数据 CSV</button>
    </div>

    <div v-if="loading" class="loading">正在加载数据...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <template v-else>
      <!-- 指标卡 -->
      <div class="stat-grid">
        <div v-for="(s, i) in statCards()" :key="i" class="stat-item" :style="{ '--accent': s.color }">
          <div class="stat-value">{{ s.value }}</div>
          <div class="stat-label">{{ s.label }}</div>
          <div v-if="s.sub" class="stat-sub">{{ s.sub }}</div>
        </div>
      </div>

      <!-- 图集网格 -->
      <div class="gallery-grid">
        <div class="card">
          <div class="card-title">图1 · 中国乘用车月度销量趋势（2018-2024）<span class="dl-btn" @click.stop="downloadChart('chart-trend','图1-中国乘用车月度销量趋势')">⤓ PNG</span></div>
          <div id="chart-trend" class="chart-box"></div>
        </div>

        <div class="card">
          <div class="card-title">图2 · 新能源(EV) vs 燃油车月度销量<span class="dl-btn" @click.stop="downloadChart('chart-multi','图2-新能源vs燃油月度销量')">⤓ PNG</span></div>
          <div id="chart-multi" class="chart-box"></div>
        </div>

        <div class="card">
          <div class="card-title">图3 · 年度销量汇总（万辆）<span class="dl-btn" @click.stop="downloadChart('chart-annual','图3-年度销量汇总')">⤓ PNG</span></div>
          <div id="chart-annual" class="chart-box"></div>
        </div>

        <div class="card">
          <div class="card-title">图4 · 月度季节模式（多年平均）<span class="dl-btn" @click.stop="downloadChart('chart-seasonal','图4-月度季节模式(多年平均)')">⤓ PNG</span></div>
          <div id="chart-seasonal" class="chart-box"></div>
        </div>

        <div class="card">
          <div class="card-title">图5 · 12 个月移动平均 vs 原始序列<span class="dl-btn" @click.stop="downloadChart('chart-ma','图5-12 个月移动平均 vs 原始序列')">⤓ PNG</span></div>
          <div id="chart-ma" class="chart-box"></div>
        </div>

        <div class="card">
          <div class="card-title">图6 · 年度销量与同比增速<span class="dl-btn" @click.stop="downloadChart('chart-yoy','图6-年度销量与同比增速')">⤓ PNG</span></div>
          <div id="chart-yoy" class="chart-box"></div>
        </div>

        <div class="card">
          <div class="card-title">图7 · 车型月销量分布直方图<span class="dl-btn" @click.stop="downloadChart('chart-dist','图7-月度销量分布直方图')">⤓ PNG</span></div>
          <div id="chart-dist" class="chart-box"></div>
        </div>

        <div class="card">
          <div class="card-title">图8 · 新能源(EV) vs 燃油车（按年堆叠）<span class="dl-btn" @click.stop="downloadChart('chart-mva','图8-新能源vs燃油堆叠')">⤓ PNG</span></div>
          <div id="chart-mva" class="chart-box"></div>
        </div>

        <div class="card">
          <div class="card-title">图9 · 新能源渗透率年度走势（%）<span class="dl-btn" @click.stop="downloadChart('chart-mva-sales','图9-新能源渗透率')">⤓ PNG</span></div>
          <div id="chart-mva-sales" class="chart-box"></div>
        </div>

        <div class="card">
          <div class="card-title">图10 · 厂商销量占比（TOP6 + 其他）<span class="dl-btn" @click.stop="downloadChart('chart-share','图10-厂商销量占比')">⤓ PNG</span></div>
          <div id="chart-share" class="chart-box"></div>
        </div>

        <div class="card">
          <div class="card-title">图11 · 价格带分布（2018-2024）<span class="dl-btn" @click.stop="downloadChart('chart-price-band','图11-价格带分布')">⤓ PNG</span></div>
          <div id="chart-price-band" class="chart-box"></div>
        </div>

        <div class="card">
          <div class="card-title">图12 · 国产 vs 外资品牌销量走势（万辆）<span class="dl-btn" @click.stop="downloadChart('chart-price','图12-国产vs外资走势')">⤓ PNG</span></div>
          <div id="chart-price" class="chart-box"></div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
/* 指标卡 */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
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

/* 图集网格 */
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 18px;
}
.card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 16px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}
.export-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}
.export-btn {
  background: #fff;
  border: 1px solid #c7d6f0;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 13px;
  color: #0b5fff;
  cursor: pointer;
  transition: all 0.2s;
}
.export-btn:hover {
  background: #eef4ff;
  border-color: #0b5fff;
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
.full-img {
  display: block;
  width: 100%;
  height: 300px;
  object-fit: contain;
  background: #fafbfc;
  border-radius: 8px;
}

@media (max-width: 900px) {
  .gallery-grid {
    grid-template-columns: 1fr;
  }
}
</style>
