<template>
  <div class="qa-page">
    <div class="page-header">
      <h2 class="page-title">智能问答</h2>
      <p class="page-desc">基于汽车行业知识库与项目销量数据的智能问答助手，输入问题即可获得回答</p>
    </div>

    <!-- 聊天区 -->
    <div class="chat-panel">
      <div class="chat-messages" ref="msgBox">
        <div v-if="messages.length === 0" class="welcome">
          <div class="welcome-icon">AI</div>
          <p class="welcome-title">你好，我是汽车智能助手</p>
          <p class="welcome-desc">
            我可以回答汽车选购、新能源、保养、市场行情等汽车知识问题，<br />
            也能查询本系统的销量统计、趋势与预测数据。
          </p>
        </div>

        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          class="msg-row"
          :class="msg.role"
        >
          <div class="msg-avatar" :class="msg.role">{{ msg.role === 'user' ? '我' : 'AI' }}</div>
          <div class="msg-bubble">
            <div v-if="msg.topic" class="msg-topic">{{ msg.topic }}</div>
            <div class="msg-text">{{ msg.answer }}</div>
          </div>
        </div>

        <div v-if="loading" class="msg-row assistant">
          <div class="msg-avatar assistant">AI</div>
          <div class="msg-bubble typing">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <!-- 推荐问题 -->
      <div v-if="messages.length === 0" class="suggest-grid">
        <button
          v-for="(q, i) in suggested"
          :key="i"
          class="suggest-chip"
          @click="quickAsk(q)"
        >
          {{ q }}
        </button>
      </div>

      <!-- 输入区 -->
      <div class="chat-input-bar">
        <input
          v-model="question"
          class="chat-input"
          placeholder="输入你想了解的汽车问题，回车发送…"
          @keyup.enter="send"
        />
        <button class="btn btn-primary" :disabled="loading || !question.trim()" @click="send">
          {{ loading ? '思考中…' : '发送' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { askQuestion } from '@/api'

const question = ref('')
const loading = ref(false)
const messages = ref([])
const msgBox = ref(null)
const suggested = ref([
  '新能源车和燃油车怎么选？',
  '10 万预算买什么车好？',
  '历史销量最高的月份是哪个？',
  '未来销量预测趋势如何？',
  '汽车多久保养一次？',
  '本系统数据库有多少条记录？',
])

async function scrollBottom() {
  await nextTick()
  if (msgBox.value) {
    msgBox.value.scrollTop = msgBox.value.scrollHeight
  }
}

async function send() {
  const q = question.value.trim()
  if (!q || loading.value) return
  messages.value.push({ role: 'user', answer: q })
  question.value = ''
  loading.value = true
  await scrollBottom()

  try {
    const data = await askQuestion(q)
    messages.value.push({
      role: 'assistant',
      answer: data.answer || '抱歉，暂时无法回答，请换一种问法。',
      topic: data.topic,
    })
  } catch (e) {
    messages.value.push({
      role: 'assistant',
      answer: '请求失败：' + (e.message || '网络异常') + '，请确认后端服务已启动（8000 端口）。',
      topic: '错误',
    })
  } finally {
    loading.value = false
    await scrollBottom()
  }
}

function quickAsk(q) {
  question.value = q
  send()
}
</script>

<style scoped>
.qa-page {
  max-width: 860px;
  margin: 0 auto;
  padding: 8px 0 24px;
}

.chat-panel {
  background: #fff;
  border-radius: 14px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 2px 10px rgba(30, 58, 138, 0.06);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.chat-messages {
  min-height: 380px;
  max-height: 460px;
  overflow-y: auto;
  padding: 20px;
  background: #f8fafc;
}
.chat-messages::-webkit-scrollbar {
  width: 6px;
}
.chat-messages::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.welcome {
  text-align: center;
  padding: 36px 20px 24px;
}
.welcome-icon {
  width: 56px;
  height: 56px;
  margin: 0 auto 12px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}
.welcome-title {
  font-size: 17px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px;
}
.welcome-desc {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.8;
  margin: 0;
}

.msg-row {
  display: flex;
  gap: 10px;
  margin-bottom: 14px;
}
.msg-row.user {
  flex-direction: row-reverse;
}
.msg-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
}
.msg-avatar.assistant {
  background: linear-gradient(135deg, #2563eb, #7c3aed);
}
.msg-avatar.user {
  background: #9ca3af;
}
.msg-bubble {
  max-width: 78%;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 10px 14px;
}
.msg-row.user .msg-bubble {
  background: #2563eb;
  border-color: #2563eb;
  color: #fff;
}
.msg-topic {
  font-size: 11px;
  color: #7c3aed;
  background: #f3e8ff;
  display: inline-block;
  padding: 1px 8px;
  border-radius: 8px;
  margin-bottom: 6px;
}
.msg-row.user .msg-topic {
  display: none;
}
.msg-text {
  font-size: 14px;
  line-height: 1.75;
  white-space: pre-line;
  word-break: break-word;
}

.typing {
  display: flex;
  gap: 5px;
  padding: 12px 16px;
}
.typing span {
  width: 7px;
  height: 7px;
  background: #9ca3af;
  border-radius: 50%;
  animation: blink 1.2s infinite;
}
.typing span:nth-child(2) {
  animation-delay: 0.2s;
}
.typing span:nth-child(3) {
  animation-delay: 0.4s;
}
@keyframes blink {
  0%, 80%, 100% {
    opacity: 0.25;
    transform: scale(0.8);
  }
  40% {
    opacity: 1;
    transform: scale(1);
  }
}

.suggest-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px 20px;
  border-top: 1px solid #f1f5f9;
}
.suggest-chip {
  background: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
  border-radius: 14px;
  padding: 6px 12px;
  font-size: 12.5px;
  cursor: pointer;
  transition: all 0.15s;
}
.suggest-chip:hover {
  background: #dbeafe;
  border-color: #93c5fd;
}

.chat-input-bar {
  display: flex;
  gap: 10px;
  padding: 14px 16px;
  border-top: 1px solid #e5e7eb;
  background: #fff;
}
.chat-input {
  flex: 1;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.15s;
}
.chat-input:focus {
  border-color: #2563eb;
}
.btn {
  border: none;
  border-radius: 10px;
  padding: 10px 22px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
}
.btn-primary {
  background: #2563eb;
  color: #fff;
}
.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
