<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getNewsDetail } from '@/api'

const route = useRoute()
const router = useRouter()
const news = ref(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const res = await getNewsDetail(route.params.id)
    news.value = res?.news
  } catch (e) {
    console.error(e)
    error.value = '资讯加载失败，可能已被移除'
  } finally {
    loading.value = false
  }
})

const paragraphs = () => (news.value?.content ?? '').split('\n\n').filter((p) => p.trim())
</script>

<template>
  <div>
    <div v-if="loading" class="loading">正在加载资讯...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <template v-else>
      <button class="back-btn" @click="router.push('/home')">← 返回首页</button>

      <div class="card detail-card">
        <div class="detail-meta">
          <span class="detail-date">{{ news.date }}</span>
          <span class="detail-source">{{ news.source }}</span>
        </div>
        <h2 class="detail-title">{{ news.title }}</h2>
        <p class="detail-summary">{{ news.summary }}</p>
        <div class="detail-body">
          <p v-for="(p, i) in paragraphs()" :key="i" class="detail-para">{{ p }}</p>
        </div>
      </div>

      <div class="card related-card">
        <div class="card-title">继续浏览</div>
        <button class="related-btn" @click="router.push('/home')">返回首页看更多资讯</button>
        <button class="related-btn" @click="router.push('/ranking')">查看品牌销量排行榜</button>
        <button class="related-btn" @click="router.push('/qa')">向智能问答提问</button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.back-btn {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 13px;
  color: #42526b;
  cursor: pointer;
  margin-bottom: 16px;
  transition: all 0.2s;
}
.back-btn:hover {
  border-color: #0b5fff;
  color: #0b5fff;
}

.detail-card {
  max-width: 860px;
  margin: 0 auto 20px;
}
.detail-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}
.detail-date {
  color: #0b5fff;
  font-size: 13px;
  font-weight: 600;
}
.detail-source {
  color: #9ca3af;
  font-size: 13px;
}
.detail-title {
  font-size: 26px;
  color: #0b2e5c;
  line-height: 1.4;
  margin-bottom: 14px;
}
.detail-summary {
  font-size: 15px;
  color: #6b7280;
  line-height: 1.8;
  padding: 14px 16px;
  background: #f0f5ff;
  border-radius: 10px;
  border-left: 4px solid #0b5fff;
  margin-bottom: 20px;
}
.detail-body .detail-para {
  font-size: 15px;
  color: #374151;
  line-height: 2;
  margin-bottom: 14px;
  text-indent: 2em;
}

.related-card {
  max-width: 860px;
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}
.related-card .card-title {
  width: 100%;
}
.related-btn {
  background: #f7f9fc;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  padding: 8px 18px;
  font-size: 13px;
  color: #42526b;
  cursor: pointer;
  transition: all 0.2s;
}
.related-btn:hover {
  background: #eef4ff;
  color: #0b5fff;
  border-color: #0b5fff;
}
</style>
