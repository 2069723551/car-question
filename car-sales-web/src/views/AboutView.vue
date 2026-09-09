<script setup>
// 关于项目页面：项目说明、技术栈、数据来源、个人分工
import bg2 from '@/assets/news/bg2.jpg'
import bg3 from '@/assets/news/bg3.jpg'
</script>

<template>
  <div>
    <h2 class="page-title">关于项目</h2>
    <p class="page-desc">汽车销量预测系统 · 课程设计项目说明</p>

    <div class="card">
      <div class="card-title">项目简介</div>
      <p class="text">
        本项目以"汽车销量预测"为核心，采集公开的汽车销量数据集，完成数据采集与预处理、
        特征工程、销量预测模型（回归 / 时间序列）训练与评估，并将预测结果以网页形式可视化展示。
        系统采用前后端分离架构：后端基于 FastAPI 提供数据与预测接口，前端基于 Vue3 + ECharts 进行可视化。
      </p>
    </div>

    <div class="pic-grid">
      <div class="pic-card" :style="{ backgroundImage: 'url(' + bg2 + ')' }">
        <div class="pic-overlay"></div>
        <div class="pic-caption">模型预测与推荐引擎</div>
      </div>
      <div class="pic-card" :style="{ backgroundImage: 'url(' + bg3 + ')' }">
        <div class="pic-overlay"></div>
        <div class="pic-caption">数据采集与模型训练</div>
      </div>
    </div>

    <div class="card">
      <div class="card-title">技术栈</div>
      <div class="stack-grid">
        <div class="stack-item">
          <div class="stack-name">后端</div>
          <div>FastAPI · Uvicorn · Pandas</div>
        </div>
        <div class="stack-item">
          <div class="stack-name">前端</div>
          <div>Vue3 · Vite · Vue Router · Axios</div>
        </div>
        <div class="stack-item">
          <div class="stack-name">可视化</div>
          <div>ECharts · Matplotlib（离线图）</div>
        </div>
        <div class="stack-item">
          <div class="stack-name">机器学习</div>
          <div>scikit-learn · statsmodels</div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-title">数据来源</div>
      <table class="data-table">
        <thead>
          <tr>
            <th>数据集</th>
            <th>时间范围</th>
            <th>记录数</th>
            <th>用途</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>monthly-car-sales（Jason Brownlee 公开数据集）</td>
            <td>2018-2024</td>
            <td>108</td>
            <td>主预测序列（单变量月度销量）</td>
          </tr>
          <tr>
            <td>china_car_sales（中国乘用车车型销量，乘联会 CPCA 来源）</td>
            <td>2018-2024</td>
            <td>264</td>
            <td>多维 EDA 展示（新能源 / 燃油车、价格带、厂商格局）</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="card">
      <div class="card-title">模型方法</div>
      <ul class="text-list">
        <li>回归模型：线性回归（基线）、随机森林</li>
        <li>时间序列模型：Holt-Winters（最优，R²=0.7812）、SARIMA（未来外推）</li>
        <li>特征工程：14 个时序特征，落实 3 条防泄漏规则</li>
        <li>输出：模型评估指标、未来 12 个月销量预测、可视化图表</li>
      </ul>
    </div>

    <div class="card">
      <div class="card-title">运行方式</div>
      <ol class="text-list">
        <li>启动后端：在 PyCharm 中打开 car-sales-backend，运行 main.py（http://127.0.0.1:8000）</li>
        <li>启动前端：在 PyCharm 中打开 car-sales-web，运行 npm run dev（http://localhost:5174）</li>
        <li>浏览器访问 http://localhost:5174 即可使用系统（共 7 个功能页面）</li>
      </ol>
    </div>
  </div>
</template>

<style scoped>
.text {
  line-height: 1.9;
  color: #42526b;
  font-size: 14px;
}

.stack-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 14px;
}

.stack-item {
  background: #f7f9fc;
  border-radius: 10px;
  padding: 16px;
  font-size: 14px;
  color: #42526b;
}

.stack-name {
  font-weight: 700;
  color: #0b5fff;
  margin-bottom: 6px;
}

/* 配图卡片 */
.pic-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}
.pic-card {
  position: relative;
  border-radius: 14px;
  height: 180px;
  background-size: cover;
  background-position: center;
  overflow: hidden;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
}
.pic-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(2, 10, 30, 0.1) 0%, rgba(2, 10, 30, 0.75) 100%);
}
.pic-caption {
  position: absolute;
  bottom: 14px;
  left: 16px;
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  text-shadow: 0 1px 6px rgba(0, 0, 0, 0.4);
}

.text-list {
  padding-left: 20px;
  line-height: 2;
  color: #42526b;
  font-size: 14px;
}
</style>
