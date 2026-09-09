<script setup>
import { RouterLink, RouterView } from 'vue-router'

const navItems = [
  { path: '/home', label: '项目概览' },
  { path: '/data', label: '数据可视化' },
  { path: '/ranking', label: '销量排行' },
  { path: '/model', label: '模型预测' },
  { path: '/cars', label: '选车助手' },
  { path: '/qa', label: '智能问答' },
  { path: '/db', label: '数据管理' },
  { path: '/fun', label: '趣味乐园' },
  { path: '/about', label: '关于项目' },
]
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand">
        <span class="brand-dot"></span>
        <span class="brand-name">汽车销量预测系统</span>
      </div>
      <nav class="nav">
        <RouterLink
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-link"
          active-class="active"
        >
          {{ item.label }}
        </RouterLink>
      </nav>
    </header>
    <main class="content">
      <RouterView />
    </main>
    <footer class="footer">
      汽车销量预测系统 © 2026 · FastAPI + Vue3 + ECharts + SQLite · 中国乘用车销量数据（乘联会 CPCA 来源）
    </footer>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
  background: linear-gradient(180deg, #eef3fb 0%, #f7f9fc 30%, #f5f7fa 100%);
  background-attachment: fixed;
  color: #2c3e50;
}

.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 顶部导航 */
.topbar {
  height: 60px;
  background: #ffffff;
  border-bottom: 1px solid #e5e9f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #0b5fff;
}

.brand-name {
  font-size: 18px;
  font-weight: 700;
  color: #0b2e5c;
}

.nav {
  display: flex;
  gap: 8px;
}

.nav-link {
  padding: 8px 18px;
  border-radius: 8px;
  text-decoration: none;
  color: #5b6b7f;
  font-size: 14px;
  transition: all 0.2s;
}

.nav-link:hover {
  background: #eef4ff;
  color: #0b5fff;
}

.nav-link.active {
  background: #0b5fff;
  color: #ffffff;
  font-weight: 600;
}

/* 内容区 */
.content {
  flex: 1;
  padding: 24px 32px;
  max-width: 1280px;
  width: 100%;
  margin: 0 auto;
}

/* 统一页面标题（所有板块共用） */
.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #0b2e5c;
  margin: 0 0 6px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.page-title::before {
  content: '';
  width: 6px;
  height: 22px;
  border-radius: 3px;
  background: linear-gradient(180deg, #0b5fff, #7c3aed);
  display: inline-block;
}
.page-desc,
.page-sub {
  color: #7a8699;
  font-size: 14px;
  margin: 0 0 20px;
}
.page-header {
  margin-bottom: 18px;
}

/* 通用卡片 */
.card {
  background: #ffffff;
  border-radius: 14px;
  padding: 24px;
  border: 1px solid #e8ecf3;
  margin-bottom: 20px;
  box-shadow: 0 2px 10px rgba(11, 46, 92, 0.05);
  transition: box-shadow 0.2s;
}
.card:hover {
  box-shadow: 0 6px 18px rgba(11, 46, 92, 0.08);
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  color: #0b2e5c;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #0b5fff;
  display: inline-block;
}

/* 指标大数字 */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.stat-item {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e8ecf3;
  border-top: 3px solid #0b5fff;
}

.stat-value {
  font-size: 30px;
  font-weight: 700;
  color: #0b2e5c;
  margin-bottom: 6px;
}

.stat-label {
  font-size: 13px;
  color: #7a8699;
}

/* 表格 */
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.data-table th,
.data-table td {
  padding: 10px 12px;
  border-bottom: 1px solid #edf0f5;
  text-align: left;
}

.data-table th {
  background: #f0f5ff;
  color: #0b2e5c;
  font-weight: 600;
}

.data-table tr:hover td {
  background: #f8faff;
}

/* 图表容器 */
.chart-box {
  width: 100%;
  height: 420px;
}

/* 页脚 */
.footer {
  text-align: center;
  padding: 18px;
  color: #9aa7b8;
  font-size: 13px;
  background: linear-gradient(90deg, #0b2e5c, #0b5fff);
  color: #dce7ff;
  border-top: none;
}

.loading {
  color: #7a8699;
  font-size: 14px;
  padding: 20px;
  text-align: center;
}

.error {
  color: #d14343;
  font-size: 14px;
  padding: 20px;
  text-align: center;
  background: #fff1f0;
  border-radius: 8px;
}
</style>
