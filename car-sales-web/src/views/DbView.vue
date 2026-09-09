<script setup>
import { ref, onMounted } from 'vue'
import { getDbStats, getLogs, getSeries, getForecast } from '@/api'

const loading = ref(true)
const error = ref('')
const stats = ref(null)
const logs = ref([])
const sales = ref([])
const forecast = ref([])

onMounted(async () => {
  try {
    const [st, lg, sr, fc] = await Promise.all([
      getDbStats(),
      getLogs(15),
      getSeries(),
      getForecast(),
    ])
    stats.value = st
    logs.value = lg
    sales.value = sr.slice(0, 8)
    forecast.value = fc.map((x) => ({ ...x, forecast: Number(x.forecast).toFixed(2) }))
  } catch (e) {
    console.error(e)
    error.value = '无法连接后端服务，请确认已启动 car-sales-backend（python main.py）'
  } finally {
    loading.value = false
  }
})

function fmtTime(t) {
  return t ? String(t).replace('T', ' ').slice(0, 19) : ''
}
</script>

<template>
  <div>
    <h1 class="page-title">数据管理</h1>
    <p class="page-desc">SQLite 数据库 · 数据表浏览 · 接口查询日志</p>

    <div v-if="error" class="error">{{ error }}</div>
    <div v-else-if="loading" class="loading">正在读取数据库...</div>

    <template v-else>
      <!-- 数据库状态 -->
      <div class="stat-grid">
        <div class="stat-item">
          <div class="stat-value">{{ stats.sales_records }}</div>
          <div class="stat-label">销量数据表 sales_records（条）</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats.prediction_records }}</div>
          <div class="stat-label">预测结果表 prediction_records（条）</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats.query_logs }}</div>
          <div class="stat-label">查询日志表 query_logs（条）</div>
        </div>
      </div>

      <!-- 数据库说明 -->
      <div class="card">
        <div class="card-title">数据库说明</div>
        <p class="db-info">
          后端使用 <b>SQLite</b> 数据库（文件：car-sales-backend/car_sales.db），
          启动时自动建表并将中国乘用车销量数据集（china_car_sales / china_monthly）与预测结果导入数据库。
          数据可视化、模型预测页面改为从数据库读取，每次接口调用自动写入查询日志。
        </p>
      </div>

      <!-- 查询日志 -->
      <div class="card">
        <div class="card-title">接口查询日志（最新 15 条）</div>
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>接口</th>
              <th>方法</th>
              <th>状态</th>
              <th>调用时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in logs" :key="log.id">
              <td>{{ log.id }}</td>
              <td><code class="endpoint">{{ log.endpoint }}</code></td>
              <td>{{ log.method }}</td>
              <td>
                <span class="badge" :class="log.status === 'success' ? 'badge-ok' : 'badge-err'">
                  {{ log.status }}
                </span>
              </td>
              <td>{{ fmtTime(log.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 销量数据预览 -->
      <div class="card">
        <div class="card-title">销量数据表预览（sales_records，前 8 条）</div>
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>日期</th>
              <th>销量（辆）</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in sales" :key="row.id">
              <td>{{ row.id }}</td>
              <td>{{ row.date }}</td>
              <td>{{ row.sales.toLocaleString() }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 预测结果预览 -->
      <div class="card">
        <div class="card-title">预测结果表预览（prediction_records，未来 12 个月）</div>
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>预测月份</th>
              <th>预测销量（辆）</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in forecast" :key="row.id">
              <td>{{ row.id }}</td>
              <td>{{ row.date }}</td>
              <td>{{ Number(row.forecast).toLocaleString() }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<style scoped>
.page-title {
  font-size: 24px;
  color: #0b2e5c;
  margin-bottom: 6px;
}

.page-sub {
  color: #7a8699;
  font-size: 14px;
  margin-bottom: 20px;
}

.db-info {
  font-size: 14px;
  line-height: 1.8;
  color: #3d4f63;
}

.endpoint {
  background: #f0f5ff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 13px;
  color: #0b5fff;
}

.badge {
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 12px;
}

.badge-ok {
  background: #e6f7ed;
  color: #1a8f4d;
}

.badge-err {
  background: #fff1f0;
  color: #d14343;
}
</style>
