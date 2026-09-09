<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getMetrics, getForecast, getRegression } from '@/api'

const metrics = ref(null)
const forecast = ref([])
const regression = ref([])
const loading = ref(true)
const error = ref('')

let chartReg = null
let chartFc = null

const BLUE = '#0b5fff'
const ORANGE = '#ff8a4c'
const GREEN = '#22c55e'

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
  const rows = modelRows()
  return rows.reduce((a, b) => (b.R2 > a.R2 ? b : a))
}

const featureImportance = () => {
  const fi = metrics.value?.feature_importance
  if (!fi) return []
  return Object.entries(fi)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
}

onMounted(async () => {
  try {
    const [mt, fc, rg] = await Promise.all([getMetrics(), getForecast(), getRegression()])
    metrics.value = mt
    forecast.value = fc
    regression.value = rg
    // 先切换 loading，等 DOM 渲染出图表容器后再初始化
    loading.value = false
    await nextTick()
    renderCharts()
  } catch (e) {
    console.error(e)
    error.value = '无法连接后端服务，请确认已启动 car-sales-backend（python main.py）'
    loading.value = false
  }
})

onBeforeUnmount(() => {
  chartReg?.dispose()
  chartFc?.dispose()
})

function renderCharts() {
  // 图1：模型 R² 对比柱状图
  chartReg = echarts.init(document.getElementById('chart-r2'))
  const rows = modelRows()
  chartReg.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 50, right: 30, top: 40, bottom: 40 },
    xAxis: { type: 'category', data: rows.map((r) => r.name) },
    yAxis: { type: 'value', name: 'R²', min: 0, max: 1 },
    series: [
      {
        type: 'bar',
        barWidth: 42,
        data: rows.map((r) => ({
          value: r.R2,
          itemStyle: { color: r.R2 === bestModel()?.R2 ? ORANGE : BLUE },
        })),
        label: { show: true, position: 'top', formatter: '{c}' },
      },
    ],
  })

  // 图2：回归模型测试集真实 vs 预测
  chartFc = echarts.init(document.getElementById('chart-reg'))
  chartFc.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['真实值', '随机森林预测', '线性回归预测'], top: 0 },
    grid: { left: 60, right: 30, top: 40, bottom: 40 },
    xAxis: {
      type: 'category',
      data: regression.value.map((d) => d.date.slice(0, 7)),
    },
    yAxis: { type: 'value', name: '销量（辆）' },
    series: [
      {
        name: '真实值',
        type: 'line',
        smooth: true,
        data: regression.value.map((d) => d.actual),
        lineStyle: { width: 2.5, color: BLUE },
        itemStyle: { color: BLUE },
      },
      {
        name: '随机森林预测',
        type: 'line',
        smooth: true,
        data: regression.value.map((d) => d.pred_rf),
        lineStyle: { width: 2, color: GREEN, type: 'dashed' },
        itemStyle: { color: GREEN },
      },
      {
        name: '线性回归预测',
        type: 'line',
        smooth: true,
        data: regression.value.map((d) => d.pred_lr),
        lineStyle: { width: 2, color: ORANGE, type: 'dashed' },
        itemStyle: { color: ORANGE },
      },
    ],
  })

  // 图3：未来 12 个月预测折线
  const chartFuture = echarts.init(document.getElementById('chart-future'))
  chartFuture.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 60, right: 30, top: 40, bottom: 40 },
    xAxis: {
      type: 'category',
      data: forecast.value.map((d) => d.date.slice(0, 7)),
    },
    yAxis: { type: 'value', name: '预测销量（辆）' },
    series: [
      {
        name: '未来预测',
        type: 'line',
        smooth: true,
        data: forecast.value.map((d) => d.forecast),
        lineStyle: { width: 3, color: ORANGE },
        itemStyle: { color: ORANGE },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(255,138,76,0.25)' },
            { offset: 1, color: 'rgba(255,138,76,0.02)' },
          ]),
        },
      },
    ],
  })
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
    <h2 class="page-title">模型预测</h2>
    <p class="page-desc">四类模型在同一测试集上对比评估，并输出未来 12 个月销量预测。</p>

    <div v-if="loading" class="loading">正在加载数据...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <template v-else>
      <!-- 关键结论 -->
      <div class="stat-grid stat-grid-4">
        <div class="stat-item">
          <div class="stat-value">{{ bestModel()?.name }}</div>
          <div class="stat-label">最优模型</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ bestModel()?.R2 }}</div>
          <div class="stat-label">最优 R²</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ bestModel()?.MAE }}</div>
          <div class="stat-label">最优 MAE（辆）</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ forecast.length }}</div>
          <div class="stat-label">未来预测月数</div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">图1 · 四类模型 R² 对比<span class="dl-btn" @click.stop="downloadChart('chart-r2','图1-四类模型 R² 对比')">⤓ PNG</span></div>
        <div id="chart-r2" class="chart-box"></div>
      </div>

      <div class="card">
        <div class="card-title">图2 · 回归模型测试集真实值 vs 预测值<span class="dl-btn" @click.stop="downloadChart('chart-reg','图2-回归模型测试集真实值 vs 预测值')">⤓ PNG</span></div>
        <div id="chart-reg" class="chart-box"></div>
      </div>

      <div class="card">
        <div class="card-title">图3 · 未来 12 个月销量预测（SARIMA）<span class="dl-btn" @click.stop="downloadChart('chart-future','图3-未来 12 个月销量预测(SARIMA)')">⤓ PNG</span></div>
        <div id="chart-future" class="chart-box"></div>
      </div>

      <div class="card" v-if="featureImportance().length">
        <div class="card-title">特征重要性（随机森林）</div>
        <table class="data-table">
          <thead>
            <tr>
              <th>特征</th>
              <th>重要性</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="f in featureImportance().slice(0, 8)" :key="f.name">
              <td>{{ f.name }}</td>
              <td>{{ f.value.toFixed(4) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<style scoped>
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
.stat-grid-4 {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
@media (max-width: 960px) {
  .stat-grid-4 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

</style>
