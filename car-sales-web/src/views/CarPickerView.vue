<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getCarMeta, recommendCars, getCarTrend, getCarTop, browseCars } from '@/api'

const activeTab = ref('pick')

// ---------- 元数据（筛选项） ----------
const meta = ref({ makes: [], body_types: [], countries: [], price_min: 0, price_max: 136.6 })

// ---------- Tab1 智能推荐 ----------
const form = reactive({
  budget_min: null,
  budget_max: null,
  energy: 'all',
  body: 'all',
  country: 'all',
  limit: 12,
})
const picks = ref([])
const pickLoading = ref(false)
const pickMsg = ref('')

// 趋势弹窗
const trendVisible = ref(false)
const trendData = ref(null)
let chartTrend = null

// ---------- Tab2 车型排行 ----------
const topPeriod = ref('total')
const topData = ref(null)
let chartTop = null

// ---------- Tab3 数据浏览 ----------
const browseForm = reactive({
  page: 1,
  page_size: 15,
  make: '',
  price_min: null,
  price_max: null,
  energy: 'all',
  body: 'all',
  country: 'all',
  keyword: '',
})
const browseData = ref(null)

const fmt = (n) => (n == null ? '-' : Number(n).toLocaleString('zh-CN'))

const energyLabel = (v) => (v === 'EV' ? '新能源' : '燃油')
const evClass = (v) => (v === 'EV' ? 'tag-ev' : 'tag-fuel')

onMounted(async () => {
  try {
    meta.value = (await getCarMeta()).data || {}
    if (meta.value?.makes?.length) browseForm.make = ''
  } catch (e) {
    pickMsg.value = '无法连接后端服务，请确认后端已启动'
  }
  await loadTop()
})

onBeforeUnmount(() => {
  chartTop?.dispose()
  chartTrend?.dispose()
})

// ---------- 推荐 ----------
const doRecommend = async () => {
  pickLoading.value = true
  pickMsg.value = ''
  try {
    const params = {
      budget_min: form.budget_min || undefined,
      budget_max: form.budget_max || undefined,
      energy: form.energy,
      body: form.body,
      country: form.country,
      limit: form.limit,
    }
    picks.value = (await recommendCars(params)).data || []
    if (!picks.value.length) pickMsg.value = '没有符合条件的车型，试试放宽筛选条件'
  } catch (e) {
    pickMsg.value = '查询失败，请检查后端服务'
  } finally {
    pickLoading.value = false
  }
}

// ---------- 趋势弹窗 ----------
const showTrend = async (model, make) => {
  try {
    trendData.value = (await getCarTrend({ model, make })).data || null
    trendVisible.value = true
    await nextTick()
    renderTrend()
  } catch (e) {
    pickMsg.value = '趋势查询失败'
  }
}
const closeTrend = () => {
  trendVisible.value = false
  trendData.value = null
  chartTrend?.dispose()
  chartTrend = null
}
const renderTrend = () => {
  if (!trendData.value) return
  chartTrend?.dispose()
  chartTrend = echarts.init(document.getElementById('chart-trend'))
  const pts = trendData.value.points || []
  chartTrend.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 70, right: 30, top: 40, bottom: 40 },
    xAxis: { type: 'category', data: pts.map((p) => p.month) },
    yAxis: { type: 'value', name: '销量（辆）' },
    series: [
      {
        type: 'line',
        smooth: true,
        data: pts.map((p) => p.sales),
        areaStyle: { color: 'rgba(11, 95, 255, 0.12)' },
        lineStyle: { color: '#0b5fff', width: 2.5 },
        itemStyle: { color: '#0b5fff' },
      },
    ],
  })
}

// ---------- 排行 ----------
const loadTop = async () => {
  try {
    topData.value = (await getCarTop({ period: topPeriod.value, limit: 20 })).data || null
    await nextTick()
    renderTop()
  } catch (e) {
    /* ignore */
  }
}
const renderTop = () => {
  if (!topData.value?.rows?.length) return
  const el = document.getElementById('chart-top')
  if (!el) return
  chartTop?.dispose()
  const rows = topData.value.rows.slice(0, 10).slice().reverse()
  chartTop = echarts.init(el)
  chartTop.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 110, right: 50, top: 20, bottom: 30 },
    xAxis: { type: 'value', name: '销量（辆）' },
    yAxis: { type: 'category', data: rows.map((r) => r.model) },
    series: [
      {
        type: 'bar',
        barWidth: 16,
        data: rows.map((r) => ({
          value: r.total,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#2563eb' },
              { offset: 1, color: '#38bdf8' },
            ]),
          },
        })),
        label: { show: true, position: 'right', formatter: (p) => fmt(p.value) },
      },
    ],
  })
}

// ---------- 浏览 ----------
const doBrowse = async (page) => {
  browseForm.page = page || 1
  const params = { ...browseForm, page: browseForm.page }
  // 清理空参数（axios 会把 null 序列化导致后端 422）
  Object.keys(params).forEach((k) => {
    if (params[k] === null || params[k] === '') delete params[k]
  })
  try {
    browseData.value = (await browseCars(params)).data || null
  } catch (e) {
    browseData.value = null
  }
}
const totalPages = () => {
  if (!browseData.value) return 0
  return Math.max(1, Math.ceil(browseData.value.total / browseForm.page_size))
}
watch(activeTab, async (v) => {
  if (v === 'rank') await loadTop()
  if (v === 'browse' && !browseData.value) await doBrowse(1)
})
</script>

<template>
  <div>
    <h2 class="page-title">选车助手</h2>
    <p class="page-desc">基于 38806 条中国乘用车车型-月度销量数据（2018-2024）：按预算与偏好智能推荐、热门车型排行、全量数据浏览。</p>

    <!-- Tab 切换 -->
    <div class="tabs">
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'pick' }"
        @click="activeTab = 'pick'"
      >🎯 智能推荐</button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'rank' }"
        @click="activeTab = 'rank'"
      >🏆 车型排行</button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'browse' }"
        @click="activeTab = 'browse'"
      >📋 数据浏览</button>
    </div>

    <!-- ============ Tab1 智能推荐 ============ -->
    <div v-show="activeTab === 'pick'">
      <div class="card filter-card">
        <div class="filter-grid">
          <div class="filter-item">
            <label>预算区间（万元）</label>
            <div class="budget-row">
              <input v-model.number="form.budget_min" type="number" min="0" placeholder="最低" class="input" />
              <span class="sep">—</span>
              <input v-model.number="form.budget_max" type="number" min="0" placeholder="最高" class="input" />
            </div>
          </div>
          <div class="filter-item">
            <label>能源类型</label>
            <select v-model="form.energy" class="input">
              <option value="all">全部</option>
              <option value="EV">新能源</option>
              <option value="Gasoline">燃油</option>
            </select>
          </div>
          <div class="filter-item">
            <label>车身类型</label>
            <select v-model="form.body" class="input">
              <option value="all">全部</option>
              <option v-for="b in meta.body_types" :key="b.value" :value="b.value">{{ b.label }}</option>
            </select>
          </div>
          <div class="filter-item">
            <label>品牌国别</label>
            <select v-model="form.country" class="input">
              <option value="all">全部</option>
              <option v-for="c in meta.countries" :key="c.value" :value="c.value">{{ c.label }}</option>
            </select>
          </div>
          <div class="filter-item">
            <label>展示数量</label>
            <select v-model.number="form.limit" class="input">
              <option :value="6">6 款</option>
              <option :value="12">12 款</option>
              <option :value="20">20 款</option>
            </select>
          </div>
          <div class="filter-item filter-action">
            <button class="btn-primary" :disabled="pickLoading" @click="doRecommend">
              {{ pickLoading ? '推荐中…' : '开始推荐' }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="pickMsg" class="error">{{ pickMsg }}</div>

      <div v-if="picks.length" class="pick-grid">
        <div
          v-for="(c, i) in picks"
          :key="c.model + i"
          class="pick-card"
          @click="showTrend(c.model, c.make)"
          title="点击查看月销量趋势"
        >
          <div class="pick-top">
            <span class="pick-name">{{ c.model }}</span>
            <span class="pick-badge" :class="evClass(c.is_ev)">{{ energyLabel(c.is_ev) }}</span>
          </div>
          <div class="pick-make">{{ c.make }} · {{ c.country_label }} · {{ c.body_label }}</div>
          <div class="pick-stats">
            <div class="pick-stat">
              <div class="pick-stat-v">{{ fmt(c.total) }}</div>
              <div class="pick-stat-l">累计销量</div>
            </div>
            <div class="pick-stat">
              <div class="pick-stat-v">{{ fmt(Math.round(c.total / c.months)) }}</div>
              <div class="pick-stat-l">月均销量</div>
            </div>
            <div class="pick-stat">
              <div class="pick-stat-v">{{ c.min_price }}~{{ c.max_price }}万</div>
              <div class="pick-stat-l">价格区间</div>
            </div>
          </div>
          <div class="pick-last">最新月（{{ c.last_ym }}）销量 {{ fmt(c.last_sold) }} 辆</div>
        </div>
      </div>
      <div v-else-if="!pickLoading" class="hint">设置筛选条件后点击「开始推荐」，按真实销量热度排序</div>
    </div>

    <!-- ============ Tab2 车型排行 ============ -->
    <div v-show="activeTab === 'rank'">
      <div class="card filter-card">
        <div class="filter-grid rank-filter">
          <div class="filter-item">
            <label>统计周期</label>
            <select v-model="topPeriod" class="input" @change="loadTop">
              <option value="total">2018-2024 累计</option>
              <option value="latest">最新月份（2024-04）</option>
              <option value="2024">2024 年</option>
              <option value="2023">2023 年</option>
              <option value="2022">2022 年</option>
              <option value="2021">2021 年</option>
              <option value="2020">2020 年</option>
              <option value="2019">2019 年</option>
              <option value="2018">2018 年</option>
            </select>
          </div>
          <div class="filter-item rank-info">
            <span v-if="topData" class="rank-label">{{ topData.period }} · 全市场销量 {{ fmt(topData.total) }} 辆</span>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">TOP10 车型销量（{{ topData?.period || '' }}）</div>
        <div id="chart-top" class="chart-box" style="height: 420px"></div>
      </div>

      <div class="card">
        <div class="card-title">车型销量排行榜（TOP20）</div>
        <table class="data-table">
          <thead>
            <tr>
              <th>排名</th>
              <th>车型</th>
              <th>厂商</th>
              <th>车身</th>
              <th>能源</th>
              <th>累计销量（辆）</th>
              <th>市场占比</th>
              <th>最新月销量</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="r in topData?.rows || []"
              :key="r.rank"
              class="rank-row"
              @click="showTrend(r.model, r.make)"
              title="点击查看月销量趋势"
            >
              <td>
                <span class="rank-no" :class="{ 'rank-top': r.rank <= 3 }">{{ r.rank }}</span>
              </td>
              <td class="cell-model">{{ r.model }}</td>
              <td>{{ r.make }}</td>
              <td>{{ r.body_label }}</td>
              <td><span class="badge-sm" :class="evClass(r.is_ev)">{{ energyLabel(r.is_ev) }}</span></td>
              <td class="cell-num">{{ fmt(r.total) }}</td>
              <td class="cell-num">{{ r.share }}%</td>
              <td class="cell-num">{{ fmt(r.last_sold) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ============ Tab3 数据浏览 ============ -->
    <div v-show="activeTab === 'browse'">
      <div class="card filter-card">
        <div class="filter-grid browse-grid">
          <div class="filter-item">
            <label>厂商</label>
            <select v-model="browseForm.make" class="input">
              <option value="">全部（{{ meta.makes.length }} 家）</option>
              <option v-for="m in meta.makes" :key="m" :value="m">{{ m }}</option>
            </select>
          </div>
          <div class="filter-item">
            <label>价格区间（万元）</label>
            <div class="budget-row">
              <input v-model.number="browseForm.price_min" type="number" min="0" placeholder="最低" class="input" />
              <span class="sep">—</span>
              <input v-model.number="browseForm.price_max" type="number" min="0" placeholder="最高" class="input" />
            </div>
          </div>
          <div class="filter-item">
            <label>能源类型</label>
            <select v-model="browseForm.energy" class="input">
              <option value="all">全部</option>
              <option value="EV">新能源</option>
              <option value="Gasoline">燃油</option>
            </select>
          </div>
          <div class="filter-item">
            <label>车身类型</label>
            <select v-model="browseForm.body" class="input">
              <option value="all">全部</option>
              <option v-for="b in meta.body_types" :key="b.value" :value="b.value">{{ b.label }}</option>
            </select>
          </div>
          <div class="filter-item">
            <label>品牌国别</label>
            <select v-model="browseForm.country" class="input">
              <option value="all">全部</option>
              <option v-for="c in meta.countries" :key="c.value" :value="c.value">{{ c.label }}</option>
            </select>
          </div>
          <div class="filter-item">
            <label>车型 / 厂商关键词</label>
            <input v-model="browseForm.keyword" type="text" placeholder="如：秦 / 比亚迪" class="input" @keyup.enter="doBrowse(1)" />
          </div>
          <div class="filter-item filter-action">
            <button class="btn-primary" @click="doBrowse(1)">查询</button>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">
          车型销量明细（共 {{ fmt(browseData?.total || 0) }} 条）
          <span v-if="browseData" class="rank-label">第 {{ browseData.page }} / {{ totalPages() }} 页</span>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>月份</th>
              <th>车型</th>
              <th>厂商</th>
              <th>销量（辆）</th>
              <th>价格（万元）</th>
              <th>能源</th>
              <th>车身</th>
              <th>国别</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(r, i) in browseData?.rows || []" :key="i">
              <td>{{ r.year_month }}</td>
              <td class="cell-model">{{ r.model }}</td>
              <td>{{ r.make }}</td>
              <td class="cell-num">{{ fmt(r.units_sold) }}</td>
              <td class="cell-num">{{ r.price_wan }}</td>
              <td><span class="badge-sm" :class="evClass(r.is_ev)">{{ energyLabel(r.is_ev) }}</span></td>
              <td>{{ r.body_type }}</td>
              <td>{{ r.brand_country }}</td>
            </tr>
          </tbody>
        </table>
        <div class="pager">
          <button class="btn-plain" :disabled="!browseData || browseData.page <= 1" @click="doBrowse(browseData.page - 1)">← 上一页</button>
          <span class="page-info">{{ browseData ? browseData.page : '-' }} / {{ totalPages() }}</span>
          <button class="btn-plain" :disabled="!browseData || browseData.page >= totalPages()" @click="doBrowse(browseData.page + 1)">下一页 →</button>
        </div>
      </div>
    </div>

    <!-- 趋势弹窗 -->
    <div v-if="trendVisible" class="modal-mask" @click.self="closeTrend">
      <div class="modal">
        <div class="modal-head">
          <span class="modal-title">{{ trendData?.model }} · 月销量趋势（{{ trendData?.make }}）</span>
          <button class="modal-close" @click="closeTrend">✕</button>
        </div>
        <div id="chart-trend" class="chart-box" style="height: 340px"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 18px;
}
.tab-btn {
  padding: 9px 22px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: #fff;
  color: #5b6b7f;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.tab-btn:hover {
  border-color: #0b5fff;
  color: #0b5fff;
}
.tab-btn.active {
  background: linear-gradient(135deg, #0b5fff, #2563eb);
  border-color: transparent;
  color: #fff;
  box-shadow: 0 4px 12px rgba(11, 95, 255, 0.3);
}

.filter-card {
  padding: 18px 20px;
}
.filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 14px;
  align-items: end;
}
.filter-item label {
  display: block;
  font-size: 12.5px;
  color: #6b7280;
  margin-bottom: 6px;
  font-weight: 600;
}
.input {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 13.5px;
  color: #1f2937;
  background: #fbfcfe;
  outline: none;
  transition: border-color 0.15s;
}
.input:focus {
  border-color: #0b5fff;
  background: #fff;
}
.budget-row {
  display: flex;
  align-items: center;
  gap: 6px;
}
.sep {
  color: #9ca3af;
}
.filter-action {
  display: flex;
  justify-content: flex-end;
}
.btn-primary {
  padding: 9px 26px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #0b5fff, #2563eb);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(11, 95, 255, 0.3);
  transition: transform 0.15s, box-shadow 0.15s;
}
.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(11, 95, 255, 0.4);
}
.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.btn-plain {
  padding: 7px 18px;
  border: 1px solid #dbe3ef;
  border-radius: 8px;
  background: #fff;
  color: #334155;
  font-size: 13px;
  cursor: pointer;
}
.btn-plain:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.pager {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
  margin-top: 16px;
}
.page-info {
  font-size: 13.5px;
  color: #475569;
  font-weight: 600;
}
.rank-info {
  display: flex;
  align-items: center;
}
.rank-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 600;
}

/* 推荐卡片 */
.pick-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 14px;
}
.pick-card {
  background: #fff;
  border: 1px solid #e8ecf3;
  border-radius: 14px;
  padding: 18px;
  cursor: pointer;
  transition: transform 0.18s, box-shadow 0.18s, border-color 0.18s;
}
.pick-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 24px rgba(11, 46, 92, 0.12);
  border-color: #0b5fff;
}
.pick-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}
.pick-name {
  font-size: 16px;
  font-weight: 700;
  color: #0b2e5c;
}
.pick-badge {
  font-size: 11.5px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 20px;
}
.tag-ev {
  background: #e0f2e9;
  color: #0f9d6e;
}
.tag-fuel {
  background: #fff2e8;
  color: #d97706;
}
.pick-make {
  font-size: 12.5px;
  color: #6b7280;
  margin-bottom: 12px;
}
.pick-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  padding: 12px 0;
  border-top: 1px dashed #e5e9f0;
  border-bottom: 1px dashed #e5e9f0;
}
.pick-stat-v {
  font-size: 14.5px;
  font-weight: 700;
  color: #0b2e5c;
}
.pick-stat-l {
  font-size: 11px;
  color: #9ca3af;
  margin-top: 2px;
}
.pick-last {
  margin-top: 10px;
  font-size: 12px;
  color: #64748b;
}
.hint {
  text-align: center;
  color: #9ca3af;
  padding: 40px 0;
  font-size: 14px;
}

/* 排行表格 */
.rank-row {
  cursor: pointer;
}
.rank-row:hover td {
  background: #f6f9ff;
}
.rank-no {
  display: inline-flex;
  width: 24px;
  height: 24px;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  background: #f1f5f9;
  color: #475569;
  font-size: 12.5px;
  font-weight: 700;
}
.rank-top {
  background: linear-gradient(135deg, #0b5fff, #38bdf8);
  color: #fff;
}
.cell-model {
  font-weight: 600;
  color: #0b2e5c;
}
.cell-num {
  text-align: right;
  font-variant-numeric: tabular-nums;
}
.badge-sm {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 12px;
}

/* 弹窗 */
.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(8, 20, 40, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  backdrop-filter: blur(3px);
}
.modal {
  background: #fff;
  border-radius: 16px;
  width: min(720px, 92vw);
  padding: 20px 20px 12px;
  box-shadow: 0 20px 60px rgba(2, 10, 30, 0.35);
}
.modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}
.modal-title {
  font-size: 16px;
  font-weight: 700;
  color: #0b2e5c;
}
.modal-close {
  border: none;
  background: #f1f5f9;
  width: 30px;
  height: 30px;
  border-radius: 8px;
  color: #475569;
  font-size: 14px;
  cursor: pointer;
}
.modal-close:hover {
  background: #e2e8f0;
}
</style>
