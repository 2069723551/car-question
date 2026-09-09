import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/HomeView.vue'
import DataView from '@/views/DataView.vue'
import ModelView from '@/views/ModelView.vue'
import QaView from '@/views/QaView.vue'
import AboutView from '@/views/AboutView.vue'
import DbView from '@/views/DbView.vue'
import RankingView from '@/views/RankingView.vue'
import CarPickerView from '@/views/CarPickerView.vue'
import FunView from '@/views/FunView.vue'
import NewsDetailView from '@/views/NewsDetailView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/home',
    },
    {
      path: '/prediction',
      redirect: '/home',
    },
    {
      path: '/home',
      name: 'home',
      component: HomeView,
      meta: { title: '项目概览 · 汽车销量预测系统' },
    },
    {
      path: '/data',
      name: 'data',
      component: DataView,
      meta: { title: '数据可视化 · 汽车销量预测系统' },
    },
    {
      path: '/model',
      name: 'model',
      component: ModelView,
      meta: { title: '模型预测 · 汽车销量预测系统' },
    },
    {
      path: '/qa',
      name: 'qa',
      component: QaView,
      meta: { title: '智能问答 · 汽车销量预测系统' },
    },
    {
      path: '/about',
      name: 'about',
      component: AboutView,
      meta: { title: '关于项目 · 汽车销量预测系统' },
    },
    {
      path: '/db',
      name: 'db',
      component: DbView,
      meta: { title: '数据管理 · 汽车销量预测系统' },
    },
    {
      path: '/ranking',
      name: 'ranking',
      component: RankingView,
      meta: { title: '销量排行 · 汽车销量预测系统' },
    },
    {
      path: '/cars',
      name: 'cars',
      component: CarPickerView,
      meta: { title: '选车助手 · 汽车销量预测系统' },
    },
    {
      path: '/fun',
      name: 'fun',
      component: FunView,
      meta: { title: '趣味乐园 · 汽车销量预测系统' },
    },
    {
      path: '/news/:id',
      name: 'news-detail',
      component: NewsDetailView,
      meta: { title: '资讯详情 · 汽车销量预测系统' },
    },
  ],
})

// 路由守卫 - 更新页面标题
router.beforeEach((to, from, next) => {
  if (to.meta?.title) {
    document.title = to.meta.title
  }
  next()
})

export default router
