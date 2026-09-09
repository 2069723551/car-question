<script setup>
import { ref, computed, watch, watchEffect, onMounted, onUnmounted } from 'vue'
import { getCarTop, getCarMeta } from '@/api'

// ================== 数据池 ==================
const pool = ref([]) // TOP100 热门车型（含全字段）
const meta = ref({})
const loading = ref(true)
const errMsg = ref('')

const loadData = async () => {
  try {
    const [t, m] = await Promise.all([
      getCarTop({ period: 'total', limit: 100 }),
      getCarMeta(),
    ])
    pool.value = (t && t.data && t.data.rows) || []
    meta.value = (m && m.data) || {}
    if (!pool.value.length) {
      errMsg.value = '车型数据加载为空'
    } else {
      garageBuild()
      loadCustom()
    }
  } catch (e) {
    errMsg.value = '加载失败：' + (e && e.message ? e.message : String(e))
  } finally {
    loading.value = false
  }
}
loadData()

const fmt = (n) => Number(n || 0).toLocaleString('zh-CN')
const evLabel = (v) => (v === 'EV' ? '新能源' : '燃油')
const rnd = (n) => Math.floor(Math.random() * n)
const pickRnd = (arr, n, exclude = []) => {
  const src = arr.filter((x) => !exclude.includes(x))
  const out = []
  while (out.length < n && src.length) {
    out.push(src.splice(rnd(src.length), 1)[0])
  }
  return out
}

const activeTab = ref('paint')

const ptRedraw = () => {
  requestAnimationFrame(() => {
    try {
      if (ptcv.value) {
        if (!ptctx) ptctx = ptcv.value.getContext('2d')
        paintDraw()
      }
      if (ptTop.value) {
        if (!ptTopCtx) ptTopCtx = ptTop.value.getContext('2d')
        paintDrawTop()
      }
    } catch (e) {
      console.warn('pt redraw error', e)
    }
  })
}

watch(activeTab, (v) => {
  if (v === 'paint') ptRedraw()
  if (v === 'race') raceRepaint()
})

// ================== 游戏1：汽车配色师 =================
const ptcv = ref(null)
const ptTop = ref(null)
const ptBody = ref('#ffffff')
const ptTire = ref(0)       // 0普通 1运动 2越野
const ptRim = ref('#d1d5db')       // 轮毂颜色（hex，可取色）
const ptRimStyle = ref(0)   // 0五辐 1多辐 2封闭
const ptLight = ref('#ffffff')
const ptGlass = ref('#93c5fd')     // 车窗颜色（hex，可取色）
const ptStripes = ref([])   // 可叠加拉花 id 数组
const ptStripeColors = ref({})  // 每个拉花的颜色
const ptStripePos = ref({})     // 每个拉花的位置偏移
const ptDecos = ref([])     // 车顶装饰 [{id,type,color,pos}]
const ptPlate = ref('粤A·88888')
const ptImeOn = ref(false)
const ptSaved = ref([])

const ptColors = ['#ffffff', '#1f2937', '#cbd5e1', '#ef4444', '#3b82f6', '#22c55e', '#eab308', '#f97316', '#a855f7', '#ec4899', '#06b6d4', '#d4af37']
const ptLights = ['#ffffff', '#60a5fa', '#fde047', '#f87171']
const ptGlasses = ['#93c5fd', '#b48c5a', '#1f2937', '#e2e8f0']
const ptRimColors = ['#d1d5db', '#1f2937', '#f59e0b', '#ef4444']
const ptTireNames = ['普通', '运动', '越野']
const ptRimNames = ['银色', '黑色', '金色', '红色']
const ptRimStyleNames = ['五辐', '多辐', '封闭']
const ptLightNames = ['白光', '蓝光', '黄光', '红光']
const ptGlassNames = ['浅蓝', '茶色', '深黑', '反光']
const ptStripeNames = ['双条纹', '火焰', '渐变', '星星', '格纹', '闪电', '爱心', '波浪']
const ptStripeIds = [1, 2, 3, 4, 5, 6, 7, 8]
const ptDecoNames = ['小花', '玩偶', '蝴蝶结', '皇冠']
const ptDecoDefaults = ['#ec4899', '#d97706', '#ef4444', '#f59e0b']

let ptctx = null
let ptTopCtx = null

const hexToRgba = (hex, a) => {
  const n = parseInt(String(hex).replace('#', ''), 16)
  if (isNaN(n)) return 'rgba(0,0,0,' + a + ')'
  return 'rgba(' + ((n >> 16) & 255) + ',' + ((n >> 8) & 255) + ',' + (n & 255) + ',' + a + ')'
}

const ptStripeNameOf = (id) => ptStripeNames[ptStripeIds.indexOf(id)] || ''

const ptPlateInput = (e) => {
  if (!ptImeOn.value) ptPlate.value = e.target.value
}

const ptPlateCommit = (e) => {
  ptImeOn.value = false
  ptPlate.value = e.target.value
}

const ptToggleStripe = (id) => {
  const i = ptStripes.value.indexOf(id)
  if (i >= 0) ptStripes.value.splice(i, 1)
  else ptStripes.value.push(id)
}

const ptAddDeco = (type) => {
  ptDecos.value.push({ id: Date.now() + Math.random(), type, color: ptDecoDefaults[type], pos: 0 })
}

const ptDelDeco = (i) => {
  ptDecos.value.splice(i, 1)
}

const ptRandom = () => {
  ptBody.value = ptColors[Math.floor(Math.random() * ptColors.length)]
  ptTire.value = Math.floor(Math.random() * 3)
  ptRim.value = ptRimColors[Math.floor(Math.random() * ptRimColors.length)]
  ptRimStyle.value = Math.floor(Math.random() * 3)
  ptLight.value = ptLights[Math.floor(Math.random() * ptLights.length)]
  ptGlass.value = ptGlasses[Math.floor(Math.random() * ptGlasses.length)]
  const pool = [1, 2, 3, 4, 5, 6, 7, 8].slice().sort(() => Math.random() - 0.5)
  ptStripes.value = pool.slice(0, 1 + Math.floor(Math.random() * 3))
  ptStripeColors.value = {}
  ptStripePos.value = {}
  const palette = ptColors.slice().sort(() => Math.random() - 0.5)
  ptStripes.value.forEach((id, idx) => {
    ptStripeColors.value[id] = palette[idx % palette.length]
    ptStripePos.value[id] = Math.floor(Math.random() * 81) - 40
  })
  ptDecos.value = []
  const nd = Math.floor(Math.random() * 3)
  for (let i = 0; i < nd; i++) {
    ptDecos.value.push({
      id: Date.now() + Math.random() + i,
      type: Math.floor(Math.random() * 4),
      color: ptDecoDefaults[Math.floor(Math.random() * 4)],
      pos: Math.floor(Math.random() * 121) - 60,
    })
  }
  ptPlate.value = '粤A·' + String(Math.floor(10000 + Math.random() * 90000))
}

const ptReset = () => {
  ptBody.value = '#ffffff'
  ptTire.value = 0
  ptRim.value = '#d1d5db'
  ptRimStyle.value = 0
  ptLight.value = '#ffffff'
  ptGlass.value = '#93c5fd'
  ptStripes.value = []
  ptStripeColors.value = {}
  ptStripePos.value = {}
  ptDecos.value = []
  ptPlate.value = '粤A·88888'
}

const ptSave = () => {
  const name = '我的配色 ' + (ptSaved.value.length + 1)
  ptSaved.value.push({
    name,
    body: ptBody.value, tire: ptTire.value, rim: ptRim.value, rimStyle: ptRimStyle.value,
    light: ptLight.value, glass: ptGlass.value,
    stripes: ptStripes.value.slice(),
    stripeColors: Object.assign({}, ptStripeColors.value),
    stripePos: Object.assign({}, ptStripePos.value),
    decos: ptDecos.value.map(d => ({ type: d.type, color: d.color, pos: d.pos })),
    plate: ptPlate.value,
  })
  localStorage.setItem('car_paint_jobs', JSON.stringify(ptSaved.value))
}

const ptApply = (s) => {
  ptBody.value = s.body || '#ffffff'
  ptTire.value = s.tire || 0
  ptRim.value = typeof s.rim === 'number' ? (ptRimColors[s.rim] || '#d1d5db') : (s.rim || '#d1d5db')
  ptRimStyle.value = s.rimStyle || 0
  ptLight.value = s.light || '#ffffff'
  ptGlass.value = typeof s.glass === 'number' ? (ptGlasses[s.glass] || '#93c5fd') : (s.glass || '#93c5fd')
  ptStripes.value = Array.isArray(s.stripes) ? s.stripes.slice() : (s.stripe > 0 ? [s.stripe] : [])
  ptStripeColors.value = Object.assign({}, s.stripeColors || {})
  ptStripePos.value = {}
  const spSrc = Object.assign({}, s.stripePos || {})
  Object.keys(spSrc).forEach(k => { ptStripePos.value[k] = Number(spSrc[k]) || 0 })
  if (s.pos && !s.stripePos && ptStripes.value.length) {
    ptStripePos.value[ptStripes.value[0]] = Number(s.pos) || 0
  }
  ptDecos.value = Array.isArray(s.decos)
    ? s.decos.map(d => ({ id: Date.now() + Math.random(), type: d.type, color: d.color, pos: Number(d.pos) || 0 }))
    : []
  ptPlate.value = s.plate || '粤A·88888'
}

const ptDel = (i) => {
  ptSaved.value.splice(i, 1)
  localStorage.setItem('car_paint_jobs', JSON.stringify(ptSaved.value))
}

try {
  const savedRaw = localStorage.getItem('car_paint_jobs')
  if (savedRaw) ptSaved.value = JSON.parse(savedRaw)
} catch (e) { /* ignore */ }

const carBodyPath = (c) => {
  c.beginPath()
  c.moveTo(90, 285)
  c.lineTo(88, 242)
  c.bezierCurveTo(88, 196, 120, 181, 170, 176)
  c.bezierCurveTo(220, 170, 300, 146, 345, 142)
  c.bezierCurveTo(400, 138, 420, 134, 470, 144)
  c.bezierCurveTo(520, 154, 570, 174, 610, 194)
  c.bezierCurveTo(640, 206, 645, 224, 640, 246)
  c.lineTo(635, 285)
  c.closePath()
}

const paintWheel = (c, x, y) => {
  if (ptTire.value === 0) c.fillStyle = '#1f2937'
  else if (ptTire.value === 1) c.fillStyle = '#111827'
  else c.fillStyle = '#374151'
  c.beginPath()
  c.arc(x, y, 34, 0, Math.PI * 2)
  c.fill()
  c.strokeStyle = 'rgba(255,255,255,0.28)'
  c.lineWidth = 2
  c.beginPath()
  c.arc(x, y, 30, 0, Math.PI * 2)
  c.stroke()
  if (ptTire.value === 2) {
    c.strokeStyle = 'rgba(0,0,0,0.45)'
    c.lineWidth = 2
    for (let i = 0; i < 8; i++) {
      const a = (i / 8) * Math.PI * 2
      c.beginPath()
      c.moveTo(x + Math.cos(a) * 26, y + Math.sin(a) * 26)
      c.lineTo(x + Math.cos(a) * 33, y + Math.sin(a) * 33)
      c.stroke()
    }
  }
  c.fillStyle = ptRim.value
  c.beginPath()
  c.arc(x, y, 18, 0, Math.PI * 2)
  c.fill()
  c.strokeStyle = 'rgba(15,23,42,0.65)'
  c.lineWidth = 3
  if (ptRimStyle.value === 0) {
    for (let i = 0; i < 5; i++) {
      const a = (i / 5) * Math.PI * 2 + Math.PI / 2
      c.beginPath()
      c.moveTo(x, y)
      c.lineTo(x + Math.cos(a) * 15, y + Math.sin(a) * 15)
      c.stroke()
    }
  } else if (ptRimStyle.value === 1) {
    for (let i = 0; i < 10; i++) {
      const a = (i / 10) * Math.PI * 2
      c.beginPath()
      c.moveTo(x, y)
      c.lineTo(x + Math.cos(a) * 15, y + Math.sin(a) * 15)
      c.stroke()
    }
  } else {
    c.fillStyle = ptRim.value
    c.beginPath()
    c.arc(x, y, 15, 0, Math.PI * 2)
    c.fill()
    c.strokeStyle = 'rgba(15,23,42,0.4)'
    c.lineWidth = 1.5
    c.beginPath()
    c.arc(x, y, 8, 0, Math.PI * 2)
    c.stroke()
  }
  c.fillStyle = '#f8fafc'
  c.beginPath()
  c.arc(x, y, 3.5, 0, Math.PI * 2)
  c.fill()
  if (ptTire.value === 1) {
    c.fillStyle = '#ef4444'
    c.beginPath()
    c.arc(x + 10, y, 9, 0, Math.PI * 2)
    c.fill()
  }
}

const drawFlower = (c, x, y, color) => {
  c.strokeStyle = '#22c55e'
  c.lineWidth = 2
  c.beginPath()
  c.moveTo(x, y)
  c.lineTo(x, y + 16)
  c.stroke()
  c.fillStyle = color
  for (let i = 0; i < 6; i++) {
    const a = (i / 6) * Math.PI * 2
    c.beginPath()
    c.ellipse(x + Math.cos(a) * 6, y + Math.sin(a) * 6, 5, 5, 0, 0, Math.PI * 2)
    c.fill()
  }
  c.fillStyle = '#fde047'
  c.beginPath()
  c.arc(x, y, 4, 0, Math.PI * 2)
  c.fill()
}

const drawBear = (c, x, y, color) => {
  c.fillStyle = color
  c.beginPath()
  c.arc(x - 7, y - 9, 5, 0, Math.PI * 2)
  c.fill()
  c.beginPath()
  c.arc(x + 7, y - 9, 5, 0, Math.PI * 2)
  c.fill()
  c.beginPath()
  c.arc(x, y, 11, 0, Math.PI * 2)
  c.fill()
  c.beginPath()
  c.arc(x, y + 17, 9, 0, Math.PI * 2)
  c.fill()
  c.fillStyle = '#1f2937'
  c.beginPath()
  c.arc(x - 4, y - 2, 1.6, 0, Math.PI * 2)
  c.fill()
  c.beginPath()
  c.arc(x + 4, y - 2, 1.6, 0, Math.PI * 2)
  c.fill()
  c.beginPath()
  c.arc(x, y + 3, 1.8, 0, Math.PI * 2)
  c.fill()
}

const drawBow = (c, x, y, color) => {
  c.fillStyle = color
  c.beginPath()
  c.moveTo(x, y)
  c.bezierCurveTo(x - 16, y - 10, x - 16, y + 10, x, y)
  c.fill()
  c.beginPath()
  c.moveTo(x, y)
  c.bezierCurveTo(x + 16, y - 10, x + 16, y + 10, x, y)
  c.fill()
  c.fillStyle = '#fbbf24'
  c.beginPath()
  c.arc(x, y, 4, 0, Math.PI * 2)
  c.fill()
}

const drawCrown = (c, x, y, color) => {
  c.fillStyle = color
  c.beginPath()
  c.moveTo(x - 12, y + 8)
  c.lineTo(x - 12, y - 2)
  c.lineTo(x - 7, y + 3)
  c.lineTo(x - 3, y - 6)
  c.lineTo(x + 1, y + 3)
  c.lineTo(x + 6, y - 4)
  c.lineTo(x + 12, y - 1)
  c.lineTo(x + 12, y + 8)
  c.closePath()
  c.fill()
  c.fillStyle = '#ef4444'
  c.beginPath()
  c.arc(x - 3, y - 6, 2.5, 0, Math.PI * 2)
  c.fill()
}

const drawFlowerTop = (c, x, y, color) => {
  c.fillStyle = color
  for (let i = 0; i < 6; i++) {
    const a = (i / 6) * Math.PI * 2
    c.beginPath()
    c.ellipse(x + Math.cos(a) * 5, y + Math.sin(a) * 5, 4, 4, 0, 0, Math.PI * 2)
    c.fill()
  }
  c.fillStyle = '#fde047'
  c.beginPath()
  c.arc(x, y, 3, 0, Math.PI * 2)
  c.fill()
}

const drawBearTop = (c, x, y, color) => {
  c.fillStyle = color
  c.beginPath()
  c.arc(x - 5, y - 6, 3.5, 0, Math.PI * 2)
  c.fill()
  c.beginPath()
  c.arc(x + 5, y - 6, 3.5, 0, Math.PI * 2)
  c.fill()
  c.beginPath()
  c.arc(x, y, 7, 0, Math.PI * 2)
  c.fill()
  c.fillStyle = '#1f2937'
  c.beginPath()
  c.arc(x - 2.5, y, 1.2, 0, Math.PI * 2)
  c.fill()
  c.beginPath()
  c.arc(x + 2.5, y, 1.2, 0, Math.PI * 2)
  c.fill()
}

const drawBowTop = (c, x, y, color) => {
  c.fillStyle = color
  c.beginPath()
  c.moveTo(x, y)
  c.bezierCurveTo(x - 11, y - 7, x - 11, y + 7, x, y)
  c.fill()
  c.beginPath()
  c.moveTo(x, y)
  c.bezierCurveTo(x + 11, y - 7, x + 11, y + 7, x, y)
  c.fill()
  c.fillStyle = '#fbbf24'
  c.beginPath()
  c.arc(x, y, 3, 0, Math.PI * 2)
  c.fill()
}

const drawCrownTop = (c, x, y, color) => {
  c.fillStyle = color
  c.beginPath()
  c.moveTo(x - 9, y + 6)
  c.lineTo(x - 9, y - 1)
  c.lineTo(x - 5, y + 2)
  c.lineTo(x - 2, y - 5)
  c.lineTo(x + 1, y + 2)
  c.lineTo(x + 5, y - 3)
  c.lineTo(x + 9, y)
  c.lineTo(x + 9, y + 6)
  c.closePath()
  c.fill()
}

const paintDrawTop = () => {
  if (!ptTop.value) return
  if (!ptTopCtx) ptTopCtx = ptTop.value.getContext('2d')
  const c = ptTopCtx
  const W = 480
  const H = 300
  const sc = ptStripeColors.value
  const sp = ptStripePos.value
  c.clearRect(0, 0, W, H)
  c.fillStyle = '#eef2f7'
  c.fillRect(0, 0, W, H)
  c.fillStyle = 'rgba(15,23,42,0.12)'
  c.beginPath()
  c.ellipse(240, 158, 192, 80, 0, 0, Math.PI * 2)
  c.fill()
  const bx = 60
  const by = 85
  const bw = 360
  const bh = 130
  c.fillStyle = ptBody.value
  c.beginPath()
  c.roundRect(bx, by, bw, bh, 34)
  c.fill()
  c.strokeStyle = 'rgba(15,23,42,0.35)'
  c.lineWidth = 2
  c.stroke()

  c.save()
  c.beginPath()
  c.roundRect(bx, by, bw, bh, 34)
  c.clip()

  if (ptStripes.value.includes(3)) {
    const grd = c.createLinearGradient(bx, by, bx + bw, by + bh)
    grd.addColorStop(0, 'rgba(59,130,246,0)')
    grd.addColorStop(0.5, hexToRgba(sc[3] || '#a855f7', 0.5))
    grd.addColorStop(1, hexToRgba(sc[3] || '#a855f7', 0.55))
    c.fillStyle = grd
    c.fillRect(bx, by, bw, bh)
  }

  if (ptStripes.value.includes(1)) {
    const dx = (+sp[1] || 0) * 0.5
    c.fillStyle = hexToRgba(sc[1] || '#111827', 0.45)
    c.fillRect(bx + 12 + dx, by + 28, bw - 24, 14)
    c.fillRect(bx + 12 + dx, by + bh - 42, bw - 24, 14)
  }

  if (ptStripes.value.includes(2)) {
    const dx = (+sp[2] || 0) * 0.5
    c.fillStyle = hexToRgba(sc[2] || '#f97316', 0.9)
    c.beginPath()
    c.moveTo(bx + bw - 30 + dx, by + 22)
    c.bezierCurveTo(bx + bw - 70 + dx, by + 8, bx + bw - 60 + dx, by + 55, bx + bw - 95 + dx, by + 40)
    c.bezierCurveTo(bx + bw - 105 + dx, by + 45, bx + bw - 95 + dx, by + 70, bx + bw - 110 + dx, by + 62)
    c.lineTo(bx + bw - 60 + dx, by + 75)
    c.lineTo(bx + bw - 25 + dx, by + 60)
    c.closePath()
    c.fill()
  }

  if (ptStripes.value.includes(8)) {
    const dx = (+sp[8] || 0) * 0.5
    c.fillStyle = hexToRgba(sc[8] || '#3b82f6', 0.75)
    c.beginPath()
    c.moveTo(bx + 8, by + 62 + dx)
    c.bezierCurveTo(bx + 80, by + 50 + dx, bx + 160, by + 72 + dx, bx + 240, by + 58 + dx)
    c.bezierCurveTo(bx + 320, by + 46 + dx, bx + 360, by + 64 + dx, bx + bw - 8, by + 56 + dx)
    c.lineTo(bx + bw - 8, by + 76 + dx)
    c.bezierCurveTo(bx + 320, by + 82 + dx, bx + 240, by + 70 + dx, bx + 160, by + 84 + dx)
    c.bezierCurveTo(bx + 80, by + 96 + dx, bx + 8, by + 78 + dx, bx + 8, by + 78 + dx)
    c.closePath()
    c.fill()
  }

  if (ptStripes.value.includes(5)) {
    const dx = (+sp[5] || 0) * 0.5
    const cell = 9
    for (let r = 0; r < 4; r++) {
      for (let col = 0; col < 7; col++) {
        c.fillStyle = (r + col) % 2 === 0 ? (sc[5] || '#111827') : '#f8fafc'
        c.fillRect(bx + 30 + dx + col * cell, by + 30 + r * cell, cell, cell)
      }
    }
  }

  if (ptStripes.value.includes(6)) {
    const dx = (+sp[6] || 0) * 0.5
    c.fillStyle = sc[6] || '#facc15'
    c.beginPath()
    c.moveTo(bx + 210 + dx, by + 20)
    c.lineTo(bx + 165 + dx, by + 68)
    c.lineTo(bx + 190 + dx, by + 68)
    c.lineTo(bx + 160 + dx, by + 112)
    c.lineTo(bx + 220 + dx, by + 60)
    c.lineTo(bx + 195 + dx, by + 60)
    c.closePath()
    c.fill()
  }

  if (ptStripes.value.includes(7)) {
    const dx = (+sp[7] || 0) * 0.5
    c.fillStyle = hexToRgba(sc[7] || '#ec4899', 0.9)
    const hearts = [[bx + 110, by + 45], [bx + 200, by + 50], [bx + 290, by + 42]]
    for (const [hx, hy] of hearts) {
      c.beginPath()
      c.moveTo(hx + dx, hy + 8)
      c.bezierCurveTo(hx + dx - 10, hy - 2, hx + dx - 4, hy - 8, hx + dx, hy - 2)
      c.bezierCurveTo(hx + dx + 4, hy - 8, hx + dx + 10, hy - 2, hx + dx, hy + 8)
      c.closePath()
      c.fill()
    }
  }

  if (ptStripes.value.includes(4)) {
    const dx = (+sp[4] || 0) * 0.5
    c.fillStyle = sc[4] || '#ffffff'
    const stars = [[bx + 80, by + 90], [bx + 150, by + 60], [bx + 240, by + 92], [bx + 320, by + 62], [bx + 200, by + 105]]
    for (const [sx, sy] of stars) {
      c.beginPath()
      for (let i = 0; i < 5; i++) {
        const a = (i * 4 * Math.PI) / 5 - Math.PI / 2
        c.lineTo(sx + dx + Math.cos(a) * 5.5, sy + Math.sin(a) * 5.5)
      }
      c.closePath()
      c.fill()
    }
  }

  c.restore()

  // 挡风玻璃（覆盖拉花头尾）
  c.fillStyle = hexToRgba(ptGlass.value, 0.85)
  c.beginPath()
  c.moveTo(bx + bw - 78, by + 8)
  c.lineTo(bx + bw - 52, by + 8)
  c.lineTo(bx + bw - 18, by + bh - 8)
  c.lineTo(bx + bw - 42, by + bh - 8)
  c.closePath()
  c.fill()
  c.beginPath()
  c.moveTo(bx + 52, by + 8)
  c.lineTo(bx + 78, by + 8)
  c.lineTo(bx + 42, by + bh - 8)
  c.lineTo(bx + 18, by + bh - 8)
  c.closePath()
  c.fill()
  // 天窗
  c.fillStyle = hexToRgba(ptGlass.value, 0.7)
  c.fillRect(bx + 140, by + 42, 80, bh - 84)
  // 前灯
  c.fillStyle = ptLight.value
  c.beginPath()
  c.ellipse(bx + bw - 6, by + 30, 4, 12, 0, 0, Math.PI * 2)
  c.fill()
  c.beginPath()
  c.ellipse(bx + bw - 6, by + bh - 30, 4, 12, 0, 0, Math.PI * 2)
  c.fill()
  // 尾灯
  c.fillStyle = '#ef4444'
  c.beginPath()
  c.ellipse(bx + 6, by + 30, 4, 12, 0, 0, Math.PI * 2)
  c.fill()
  c.beginPath()
  c.ellipse(bx + 6, by + bh - 30, 4, 12, 0, 0, Math.PI * 2)
  c.fill()
  // 车顶高光
  c.fillStyle = 'rgba(255,255,255,0.18)'
  c.fillRect(bx + 40, by + 14, bw - 80, 14)
  // 车顶装饰（最上层，不被玻璃覆盖）
  for (const d of ptDecos.value) {
    const x = bx + bw / 2 + ((+d.pos || 0) * 0.6)
    const y = by + bh / 2
    if (d.type === 0) drawFlowerTop(c, x, y, d.color)
    else if (d.type === 1) drawBearTop(c, x, y, d.color)
    else if (d.type === 2) drawBowTop(c, x, y, d.color)
    else drawCrownTop(c, x, y, d.color)
  }
}

const renderPaint = (c, s) => {
  const W = 720
  const H = 420
  const body = s ? (s.body || '#ffffff') : ptBody.value
  const stripes = s ? (Array.isArray(s.stripes) ? s.stripes.slice() : (s.stripe > 0 ? [s.stripe] : [])) : ptStripes.value
  const sc = s ? Object.assign({}, s.stripeColors || {}) : ptStripeColors.value
  const sp = {}
  if (s) {
    Object.keys(Object.assign({}, s.stripePos || {})).forEach(k => { sp[k] = Number(s.stripePos[k]) || 0 })
    if (s.pos && !s.stripePos && stripes.length) sp[stripes[0]] = Number(s.pos) || 0
  } else {
    Object.keys(ptStripePos.value).forEach(k => { sp[k] = Number(ptStripePos.value[k]) || 0 })
  }
  const decos = s ? (Array.isArray(s.decos) ? s.decos.map(d => ({ type: d.type, color: d.color, pos: Number(d.pos) || 0 })) : []) : ptDecos.value
  const glass = s ? (s.glass || '#93c5fd') : ptGlass.value
  const light = s ? (s.light || '#ffffff') : ptLight.value
  const plate = s ? (s.plate !== undefined ? s.plate : ptPlate.value) : ptPlate.value
  c.clearRect(0, 0, W, H)
  const bg = c.createLinearGradient(0, 0, 0, H)
  bg.addColorStop(0, '#e9eef6')
  bg.addColorStop(1, '#d2dbe8')
  c.fillStyle = bg
  c.fillRect(0, 0, W, H)
  c.fillStyle = '#a9b5c7'
  c.fillRect(0, 330, W, H - 330)
  c.fillStyle = 'rgba(255,255,255,0.55)'
  c.fillRect(0, 330, W, 3)
  c.fillStyle = 'rgba(15,23,42,0.14)'
  c.beginPath()
  c.ellipse(230, 318, 40, 8, 0, 0, Math.PI * 2)
  c.fill()
  c.beginPath()
  c.ellipse(560, 318, 40, 8, 0, 0, Math.PI * 2)
  c.fill()

  // 车身轮廓
  c.save()
  carBodyPath(c)
  c.fillStyle = body
  c.fill()
  c.strokeStyle = 'rgba(15,23,42,0.35)'
  c.lineWidth = 2
  c.stroke()
  c.restore()

  // 渐变拉花
  if (stripes.includes(3)) {
    const dx = +sp[3] || 0
    c.save()
    carBodyPath(c)
    c.clip()
    const grd = c.createLinearGradient(90 + dx, 140, 645 + dx, 290)
    grd.addColorStop(0, 'rgba(59,130,246,0)')
    grd.addColorStop(0.5, hexToRgba(sc[3] || '#a855f7', 0.5))
    grd.addColorStop(1, hexToRgba(sc[3] || '#a855f7', 0.55))
    c.fillStyle = grd
    c.fillRect(85 + dx, 134, 565, 150)
    c.restore()
  }

  // 高光
  c.fillStyle = 'rgba(255,255,255,0.38)'
  c.beginPath()
  c.moveTo(200, 166)
  c.bezierCurveTo(280, 146, 350, 141, 430, 148)
  c.lineTo(430, 158)
  c.bezierCurveTo(350, 152, 280, 158, 200, 176)
  c.closePath()
  c.fill()

  // 侧裙阴影
  c.fillStyle = 'rgba(15,23,42,0.1)'
  c.fillRect(102, 272, 526, 13)

  // 双条纹拉花
  if (stripes.includes(1)) {
    const dx = +sp[1] || 0
    c.save()
    carBodyPath(c)
    c.clip()
    c.fillStyle = hexToRgba(sc[1] || '#111827', 0.45)
    c.beginPath()
    c.moveTo(90 + dx, 192)
    c.lineTo(170 + dx, 186)
    c.bezierCurveTo(260 + dx, 166, 320 + dx, 154, 400 + dx, 151)
    c.lineTo(400 + dx, 166)
    c.bezierCurveTo(320 + dx, 170, 260 + dx, 184, 170 + dx, 201)
    c.lineTo(90 + dx, 206)
    c.closePath()
    c.fill()
    c.beginPath()
    c.moveTo(90 + dx, 216)
    c.lineTo(170 + dx, 210)
    c.bezierCurveTo(260 + dx, 190, 320 + dx, 180, 400 + dx, 177)
    c.lineTo(400 + dx, 192)
    c.bezierCurveTo(320 + dx, 196, 260 + dx, 208, 170 + dx, 226)
    c.lineTo(90 + dx, 231)
    c.closePath()
    c.fill()
    c.restore()
  }

  // 火焰拉花
  if (stripes.includes(2)) {
    const dx = +sp[2] || 0
    c.save()
    carBodyPath(c)
    c.clip()
    c.fillStyle = hexToRgba(sc[2] || '#f97316', 0.9)
    c.beginPath()
    c.moveTo(565 + dx, 218)
    c.bezierCurveTo(520 + dx, 200, 470 + dx, 232, 430 + dx, 206)
    c.bezierCurveTo(410 + dx, 196, 420 + dx, 226, 390 + dx, 216)
    c.bezierCurveTo(360 + dx, 206, 350 + dx, 236, 330 + dx, 226)
    c.lineTo(330 + dx, 252)
    c.bezierCurveTo(380 + dx, 240, 420 + dx, 262, 470 + dx, 250)
    c.bezierCurveTo(520 + dx, 240, 550 + dx, 256, 565 + dx, 250)
    c.closePath()
    c.fill()
    c.restore()
  }

  // 波浪拉花
  if (stripes.includes(8)) {
    const dx = +sp[8] || 0
    c.save()
    carBodyPath(c)
    c.clip()
    c.fillStyle = hexToRgba(sc[8] || '#3b82f6', 0.75)
    c.beginPath()
    c.moveTo(90 + dx, 240)
    c.bezierCurveTo(160 + dx, 225, 220 + dx, 255, 290 + dx, 240)
    c.bezierCurveTo(360 + dx, 225, 430 + dx, 255, 500 + dx, 240)
    c.bezierCurveTo(540 + dx, 232, 580 + dx, 240, 620 + dx, 236)
    c.lineTo(620 + dx, 260)
    c.bezierCurveTo(580 + dx, 262, 540 + dx, 255, 500 + dx, 262)
    c.bezierCurveTo(430 + dx, 275, 360 + dx, 250, 290 + dx, 262)
    c.bezierCurveTo(220 + dx, 275, 160 + dx, 248, 90 + dx, 262)
    c.closePath()
    c.fill()
    c.restore()
  }

  // 格纹拉花
  if (stripes.includes(5)) {
    const dx = +sp[5] || 0
    const gx0 = 300 + dx
    const gy0 = 205
    const cell = 11
    c.save()
    carBodyPath(c)
    c.clip()
    for (let r = 0; r < 4; r++) {
      for (let col = 0; col < 10; col++) {
        c.fillStyle = (r + col) % 2 === 0 ? (sc[5] || '#111827') : '#f8fafc'
        c.fillRect(gx0 + col * cell, gy0 + r * cell, cell, cell)
      }
    }
    c.restore()
  }

  // 闪电拉花
  if (stripes.includes(6)) {
    const dx = +sp[6] || 0
    c.save()
    carBodyPath(c)
    c.clip()
    c.fillStyle = sc[6] || '#facc15'
    c.beginPath()
    c.moveTo(460 + dx, 200)
    c.lineTo(400 + dx, 235)
    c.lineTo(435 + dx, 235)
    c.lineTo(390 + dx, 270)
    c.lineTo(475 + dx, 228)
    c.lineTo(440 + dx, 228)
    c.closePath()
    c.fill()
    c.restore()
  }

  // 爱心拉花
  if (stripes.includes(7)) {
    const dx = +sp[7] || 0
    c.save()
    carBodyPath(c)
    c.clip()
    c.fillStyle = hexToRgba(sc[7] || '#ec4899', 0.9)
    const hearts = [[250, 215], [330, 230], [420, 212]]
    for (const [hx, hy] of hearts) {
      c.beginPath()
      c.moveTo(hx + dx, hy + 10)
      c.bezierCurveTo(hx + dx - 14, hy - 4, hx + dx - 6, hy - 12, hx + dx, hy - 4)
      c.bezierCurveTo(hx + dx + 6, hy - 12, hx + dx + 14, hy - 4, hx + dx, hy + 10)
      c.closePath()
      c.fill()
    }
    c.restore()
  }

  // 星星拉花
  if (stripes.includes(4)) {
    const dx = +sp[4] || 0
    const stars = [[205, 210], [262, 190], [380, 216], [452, 196], [520, 214], [300, 230], [410, 242], [558, 200]]
    c.save()
    carBodyPath(c)
    c.clip()
    c.fillStyle = sc[4] || '#ffffff'
    for (const [sx, sy] of stars) {
      c.beginPath()
      for (let i = 0; i < 5; i++) {
        const a = (i * 4 * Math.PI) / 5 - Math.PI / 2
        c.lineTo(sx + dx + Math.cos(a) * 7, sy + Math.sin(a) * 7)
      }
      c.closePath()
      c.fill()
    }
    c.restore()
  }

  // 车顶装饰
  for (const d of decos) {
    const x = 340 + (+d.pos || 0)
    const y = 140
    if (d.type === 0) drawFlower(c, x, y, d.color)
    else if (d.type === 1) drawBear(c, x, y, d.color)
    else if (d.type === 2) drawBow(c, x, y, d.color)
    else drawCrown(c, x, y, d.color)
  }

  // 车窗
  const glassColor = hexToRgba(glass, 0.85)
  c.fillStyle = glassColor
  c.beginPath()
  c.moveTo(200, 174)
  c.bezierCurveTo(250, 156, 300, 152, 330, 154)
  c.lineTo(330, 186)
  c.bezierCurveTo(290, 184, 250, 184, 215, 192)
  c.closePath()
  c.fill()
  c.strokeStyle = 'rgba(15,23,42,0.4)'
  c.lineWidth = 1.5
  c.stroke()
  c.beginPath()
  c.moveTo(345, 159)
  c.bezierCurveTo(380, 152, 430, 156, 460, 164)
  c.lineTo(455, 189)
  c.bezierCurveTo(420, 184, 380, 184, 355, 190)
  c.closePath()
  c.fill()
  c.stroke()

  // 车门线 + 把手
  c.strokeStyle = 'rgba(15,23,42,0.28)'
  c.lineWidth = 1.5
  c.beginPath()
  c.moveTo(302, 174)
  c.lineTo(302, 274)
  c.stroke()
  c.beginPath()
  c.moveTo(468, 174)
  c.lineTo(468, 274)
  c.stroke()
  c.fillStyle = 'rgba(15,23,42,0.5)'
  c.fillRect(336, 250, 22, 4)
  c.fillRect(472, 250, 22, 4)

  // 尾灯 / 前灯
  c.fillStyle = '#ef4444'
  c.beginPath()
  c.ellipse(96, 220, 10, 7, 0, 0, Math.PI * 2)
  c.fill()
  c.fillStyle = light
  c.beginPath()
  c.ellipse(631, 216, 11, 8, 0, 0, Math.PI * 2)
  c.fill()
  c.fillStyle = 'rgba(255,255,255,0.65)'
  c.beginPath()
  c.ellipse(631, 216, 5, 4, 0, 0, Math.PI * 2)
  c.fill()

  // 轮子
  paintWheel(c, 230, 285)
  paintWheel(c, 560, 285)

  // 车牌
  c.fillStyle = '#f8fafc'
  c.fillRect(104, 262, 66, 20)
  c.strokeStyle = '#334155'
  c.lineWidth = 1
  c.strokeRect(104, 262, 66, 20)
  c.fillStyle = '#334155'
  c.font = 'bold 11px sans-serif'
  c.textAlign = 'center'
  c.textBaseline = 'middle'
  c.fillText(String(plate).slice(0, 8), 137, 273)
}

const paintDraw = () => {
  if (!ptcv.value) return
  if (!ptctx) ptctx = ptcv.value.getContext('2d')
  renderPaint(ptctx, null)
}

watchEffect(() => {
  try {
    if (ptcv.value) {
      if (!ptctx) ptctx = ptcv.value.getContext('2d')
      paintDraw()
    }
    if (ptTop.value) {
      if (!ptTopCtx) ptTopCtx = ptTop.value.getContext('2d')
      paintDrawTop()
    }
  } catch (e) {
    console.warn('paint watch error', e)
  }
})

onMounted(() => {
  try {
    if (ptcv.value) {
      if (!ptctx) ptctx = ptcv.value.getContext('2d')
      paintDraw()
    }
    if (ptTop.value) {
      if (!ptTopCtx) ptTopCtx = ptTop.value.getContext('2d')
      paintDrawTop()
    }
    if (garageCv.value && garage.value.result) {
      if (!garageCtx) garageCtx = garageCv.value.getContext('2d')
      garagePaint(garagePaintSel.value === 'current' ? null : (ptSaved.value[garagePaintSel.value] || null))
    }
  } catch (e) {
    console.warn('mount paint error', e)
  }
})

// ================== 游戏2：造车工坊 ==================
const garage = ref({
  name: '凌云Pro',
  brand: '我的车厂',
  body: 'SUV',
  energy: 'EV',
  price: 18,
  result: null,
})

const garageBodies = ['Sedan', 'SUV', 'MPV', 'Hatchback', 'Sports Car']
const garageEnergies = ['EV', 'Gasoline']

const garageBodyLabel = (v) => ({ Sedan: '轿车', SUV: 'SUV', MPV: 'MPV', Hatchback: '两厢车', 'Sports Car': '跑车' }[v] || v)
const garageEnergyLabel = (v) => (v === 'EV' ? '新能源' : '燃油')

const garageAvgMonthly = (list) => (list.length ? list.reduce((s, c) => s + c.total / c.months, 0) / list.length : 0)

const garageBuild = () => {
  const g = garage.value
  const price = Math.max(Number(g.price) || 15, 3)
  const seg = pool.value.filter((c) => c.body_type === g.body && c.is_ev === g.energy)
  const allAvg = garageAvgMonthly(pool.value)
  const baseMonthly = seg.length ? garageAvgMonthly(seg) : allAvg
  // 主流价格锚点：细分市场车型的价格中位数
  const segPrices = seg.map((c) => c.avg_price).sort((a, b) => a - b)
  const midPrice = segPrices.length ? segPrices[Math.floor(segPrices.length / 2)] : 15
  const ratio = midPrice > 0 ? price / midPrice : 1
  // ① 价格弹性系数（指数衰减）：偏离主流价位越远，需求越差
  let priceFactor
  if (ratio < 0.3) {
    priceFactor = 0.35 // 远低于主流，低价反伤品牌
  } else if (ratio < 0.6) {
    priceFactor = 0.7 // 明显低价走量
  } else if (ratio < 0.85) {
    priceFactor = 1.05 // 微低于主流，性价比
  } else if (ratio <= 1.3) {
    priceFactor = 1.15 // 主流价位，需求最旺
  } else if (ratio <= 2) {
    priceFactor = 1.15 * Math.pow(2 / ratio, 1.6) // 1-2 倍主流价，快速衰减
  } else {
    priceFactor = 1.15 * Math.pow(2 / ratio, 2.2) // 2 倍以上，剧烈衰减
  }
  // ② 绝对价格档位上限（通用豪华车市场逻辑：越贵卖得越少）
  const priceCaps = [
    [5000, 3], // 5000 万+：全球限量定制
    [1500, 15], // 1500 万+
    [800, 40], // 800 万+
    [500, 120], // 500 万+
    [300, 300], // 300 万+
    [200, 600], // 200 万+
    [150, 1200], // 150 万+
    [100, 3000], // 100 万+
    [80, 6000], // 80 万+
    [60, 12000], // 60 万+
    [40, 25000], // 40 万+
    [20, 50000], // 20 万+
  ]
  const cap = (priceCaps.find(([p0]) => price >= p0) || [0, 80000])[1]
  // ③ 预估月销 = 细分基准 × 弹性系数（含市场波动），并与绝对上限取小；不再强制保底
  let estMonthly = Math.round(baseMonthly * priceFactor * (0.92 + Math.random() * 0.16))
  estMonthly = Math.min(estMonthly, cap)
  estMonthly = Math.max(estMonthly, 0)
  const estYearly = estMonthly * 12
  const est36 = estMonthly * 36
  // 参考对手：全池中价格最接近的 4 款
  const rivals = [...pool.value]
    .map((c) => ({ c, d: Math.abs(c.avg_price - price) }))
    .sort((a, b) => a.d - b.d)
    .slice(0, 4)
    .map((x) => x.c)
  // 细分市占估算
  const segMonthly = seg.length ? garageAvgMonthly(seg) * seg.length : allAvg * pool.value.length
  const share = segMonthly > 0 ? ((estMonthly / segMonthly) * 100).toFixed(2) : '0.00'
  garage.value.result = {
    estMonthly,
    estYearly,
    est36,
    tier: tierOf(est36),
    rivals,
    share,
    midPrice,
    segCount: seg.length,
    segLabel: `${garageBodyLabel(g.body)} · ${garageEnergyLabel(g.energy)}`,
  }
  requestAnimationFrame(() => garagePaint(garagePaintSel.value === 'current' ? null : (ptSaved.value[garagePaintSel.value] || null)))
}

const garagePaintSelChange = () => {
  if (!garage.value.result) return
  requestAnimationFrame(() => garagePaint(garagePaintSel.value === 'current' ? null : (ptSaved.value[garagePaintSel.value] || null)))
}

const garageCv = ref(null)
let garageCtx = null
const garagePaintSel = ref('current')
const custPaintSel = ref('current')
const garagePaint = (s) => {
  if (!garageCv.value) return
  if (!garageCtx) garageCtx = garageCv.value.getContext('2d')
  const c = garageCtx
  c.setTransform(1, 0, 0, 1, 0, 0)
  c.clearRect(0, 0, 460, 268)
  c.scale(0.639, 0.639)
  renderPaint(c, s)
}

// ================== 游戏3：我的车库 =================
const CAR_IMGS = {
  '轩逸': '/cars/xuanyi.jpg',
  '朗逸': '/cars/lavida.jpg',
  '哈弗H6': '/cars/h6.jpg',
  '卡罗拉': '/cars/corolla.jpg',
  '速腾': '/cars/sagitar.jpg',
  '宏光MINIEV': '/cars/miniev.jpg',
  '雅阁': '/cars/accord.jpg',
  '凯美瑞': '/cars/camry.jpg',
  '帕萨特': '/cars/passat.jpg',
  '宝来': '/cars/bora.jpg',
  '秦PLUS': '/cars/qinplus.jpg',
  '宋PLUS新能源': '/cars/songplus.jpg',
  'Model Y': '/cars/modely.jpg',
  '元PLUS': '/cars/yuanplus.jpg',
}
const MAX_GARAGE = 5
const ga = ref({ items: [] })

const gaCarImg = (m) => CAR_IMGS[m] || ''
const gaIn = (m) => ga.value.items.some((x) => x.model === m)
const gaToggle = (c) => {
  const i = ga.value.items.findIndex((x) => x.model === c.model)
  if (i >= 0) {
    ga.value.items.splice(i, 1)
    saveCustom()
    return
  }
  if (ga.value.items.length >= MAX_GARAGE) return
  ga.value.items.push({ ...c })
}
const gaClear = () => {
  ga.value.items = []
  saveCustom()
}

const gaStats = computed(() => {
  const items = ga.value.items
  if (!items.length) return null
  const totalSales = items.reduce((s, c) => s + (c.total || 0), 0)
  const value = items.reduce((s, c) => s + (c.avg_price || 0), 0)
  const avgPrice = value / items.length
  const tiers = new Set(items.map((c) => tierOf(c.total)))
  const evCount = items.filter((c) => c.is_ev === 'EV').length
  const makes = items.map((c) => c.make)
  const tags = []
  if (items.length === MAX_GARAGE) tags.push('🏆 全明星阵容')
  if (evCount === items.length) tags.push('⚡ 新能源先锋')
  else if (evCount === 0) tags.push('⛽ 燃油党')
  if (tiers.size >= 3) tags.push('🎖 段位收藏家')
  if (makes.filter((m) => /比亚迪|吉利|长安|长城|奇瑞|五菱|哈弗|荣威|传祺|红旗|理想|蔚来/.test(m)).length >= 2) tags.push('🇨🇳 国产之光')
  if (makes.filter((m) => /大众|奥迪|宝马|奔驰/.test(m)).length >= 2) tags.push('🇩🇪 德系控')
  if (makes.filter((m) => /丰田|本田|日产|马自达|铃木/.test(m)).length >= 2) tags.push('🇯🇵 日系迷')
  if (avgPrice >= 30) tags.push('💎 豪华玩家')
  if (items.some((x) => x.custom)) tags.push('🛠 DIY 改装')
  if (!tags.length) tags.push('🚗 品味车库')
  return { totalSales, value, avgPrice, tiers: tiers.size, tags, evCount }
})
const gaShare = computed(() => {
  const st = gaStats.value
  if (!st) return 0
  const total = pool.value.reduce((s, c) => s + (c.total || 0), 0)
  return total > 0 ? (st.totalSales / total) * 100 : 0
})

// ---- 自定义上传 ----
const cust = ref({ show: false, name: '', make: '', body: 'Sedan', energy: 'EV', price: 15, img: '', msg: '' })
const compressImg = (file) =>
  new Promise((resolve) => {
    const img = new Image()
    const url = URL.createObjectURL(file)
    img.onload = () => {
      const maxW = 500
      const scale = Math.min(1, maxW / img.width)
      const c = document.createElement('canvas')
      c.width = Math.round(img.width * scale)
      c.height = Math.round(img.height * scale)
      c.getContext('2d').drawImage(img, 0, 0, c.width, c.height)
      resolve(c.toDataURL('image/jpeg', 0.72))
      URL.revokeObjectURL(url)
    }
    img.onerror = () => {
      URL.revokeObjectURL(url)
      resolve('')
    }
    img.src = url
  })
const onCustFile = (e) => {
  const f = e.target.files && e.target.files[0]
  if (!f) return
  compressImg(f).then((b64) => {
    cust.value.img = b64
    e.target.value = ''
  })
}
const clearCustImg = () => (cust.value.img = '')
const usePaintAsCust = () => {
  const s = custPaintSel.value === 'current' ? null : (ptSaved.value[custPaintSel.value] || null)
  try {
    const off = document.createElement('canvas')
    off.width = 720
    off.height = 420
    renderPaint(off.getContext('2d'), s)
    cust.value.img = off.toDataURL('image/jpeg', 0.85)
    cust.value.msg = '已使用配色师作品作为照片'
  } catch (e) {
    cust.value.msg = '图片生成失败，请重试'
  }
}
const custAdd = () => {
  if (!cust.value.name.trim()) {
    cust.value.msg = '请先填写车名'
    return
  }
  if (ga.value.items.length >= MAX_GARAGE) {
    cust.value.msg = '车库已满（5 辆），请先移除一辆'
    return
  }
  const c = {
    custom: true,
    model: cust.value.name.trim(),
    make: cust.value.make.trim() || '自定义品牌',
    body_type: cust.value.body,
    is_ev: cust.value.energy,
    avg_price: Math.max(1, Number(cust.value.price) || 10),
    total: 0,
    months: 0,
    img: cust.value.img,
  }
  ga.value.items.push(c)
  saveCustom()
  cust.value = { show: false, name: '', make: '', body: 'Sedan', energy: 'EV', price: 15, img: '', msg: '' }
}
const loadCustom = () => {
  try {
    const raw = localStorage.getItem('garage_custom_cars')
    if (raw) {
      const arr = JSON.parse(raw)
      if (Array.isArray(arr)) ga.value.items = ga.value.items.concat(arr.filter((x) => x && x.custom))
    }
  } catch (e) {}
}
const saveCustom = () => {
  try {
    const arr = ga.value.items.filter((x) => x && x.custom)
    if (arr.length) localStorage.setItem('garage_custom_cars', JSON.stringify(arr))
    else localStorage.removeItem('garage_custom_cars')
  } catch (e) {}
}

// ================== 游戏4：公路赛车 ==================
const tierDefs = [
  { key: 'king', name: '王者段位', emoji: '👑', min: 1500000, desc: '累计销量 ≥ 150 万辆，国民神车' },
  { key: 'diamond', name: '钻石段位', emoji: '💎', min: 1000000, desc: '累计销量 100-150 万辆，市场常青树' },
  { key: 'gold', name: '黄金段位', emoji: '🥇', min: 700000, desc: '累计销量 70-100 万辆，实力选手' },
  { key: 'silver', name: '白银段位', emoji: '🥈', min: 500000, desc: '累计销量 50-70 万辆，潜力股' },
  { key: 'bronze', name: '青铜段位', emoji: '🥉', min: 0, desc: '累计销量 50 万辆以下，细分黑马' },
]
const tierOf = (total) => tierDefs.find((t) => total >= t.min)?.name || '青铜段位'

const rcv = ref(null)
const racePhase = ref('idle')
const raceScore = ref(0)
const raceSpeed = ref(0)
const raceBest = ref(Number(localStorage.getItem('race_best') || 0))
const racePaintSel = ref('current')
const raceNewBest = ref(false)

let rctx = null
let rraf = null
let rlast = 0
let rgame = null

const R_LANES = 3
const R_CAR_W = 56
const R_CAR_H = 96
const R_OB_W = 52
const R_OB_H = 92

const raceReset = () => {
  const c = rcv.value
  rgame = {
    w: c.width,
    h: c.height,
    laneW: (c.width * 0.62) / R_LANES,
    roadLeft: c.width * 0.19,
    player: { lane: 1, w: R_CAR_W, h: R_CAR_H, y: c.height - 150 },
    obstacles: [],
    spawnT: 0,
    speed: 320,
    maxSpeed: 860,
    dist: 0,
    over: false,
    lastSwitch: 0,
    openLane: 1,
  }
  rgame.player.x = rgame.roadLeft + rgame.laneW * rgame.player.lane + (rgame.laneW - R_CAR_W) / 2
}

const raceRepaint = () => {
  if (!rcv.value) return
  rctx = rcv.value.getContext('2d')
  if (!rgame) raceReset()
  raceDraw()
}

const raceStart = () => {
  if (!rctx && rcv.value) {
    rctx = rcv.value.getContext('2d')
    raceReset()
  }
  raceReset()
  racePhase.value = 'running'
  raceNewBest.value = false
  rlast = performance.now()
  if (rraf) cancelAnimationFrame(rraf)
  raceLoop(rlast)
}

const raceLoop = (t) => {
  rraf = requestAnimationFrame(raceLoop)
  const dt = Math.min(0.033, (t - rlast) / 1000)
  rlast = t
  raceUpdate(dt)
  raceDraw()
  if (rgame.over) {
    racePhase.value = 'over'
    raceScore.value = Math.floor(rgame.dist)
    if (raceScore.value > raceBest.value) {
      raceBest.value = raceScore.value
      raceNewBest.value = true
      localStorage.setItem('race_best', String(raceBest.value))
    }
    cancelAnimationFrame(rraf)
    rraf = null
  }
}

const raceUpdate = (dt) => {
  const g = rgame
  g.dist += g.speed * dt * 0.5
  raceSpeed.value = Math.round((g.speed / 320) * 100)
  raceScore.value = Math.floor(g.dist)

  // 随时间推移越来越快：基础加速 + 里程越高加速越猛
  g.speed = Math.min(g.maxSpeed, g.speed + dt * (24 + g.dist * 0.00014))

  g.spawnT -= dt
  if (g.spawnT <= 0) {
    // 本批空道：与上一批相邻（最多隔一条道），保证任何时刻都存在可连续通行的纵向逃生通道
    const lo = Math.max(0, g.openLane - 1)
    const hi = Math.min(R_LANES - 1, g.openLane + 1)
    const free = lo + Math.floor(Math.random() * (hi - lo + 1))
    g.openLane = free
    // 堵其它车道 1~2 条（速度越快越倾向堵 2 条），空道永不封死
    const blockables = [0, 1, 2].filter((l) => l !== free).sort(() => Math.random() - 0.5)
    const blockN = Math.random() < 0.35 + (g.speed / g.maxSpeed) * 0.4 ? 2 : 1
    const blocked = blockables.slice(0, Math.min(blockN, blockables.length))
    const colors = ['#e11d48', '#f59e0b', '#10b981', '#8b5cf6', '#0ea5e9', '#f43f5e']
    const spd = g.speed * 0.62
    // 同批障碍纵向错开：第二条道比第一条晚 0.35~0.55 秒到达（y 更靠上），
    // 避免相邻车道障碍在纵向上齐平形成"横墙"，保证换道后前方有足够缝隙
    let delay = 0
    for (const lane of blocked) {
      const ox = g.roadLeft + g.laneW * lane + (g.laneW - R_OB_W) / 2
      const near = g.obstacles.some((o) => o.lane === lane && o.y < 260)
      if (near) continue
      g.obstacles.push({
        x: ox,
        y: -R_OB_H - delay * spd,
        lane,
        w: R_OB_W,
        h: R_OB_H,
        color: colors[Math.floor(Math.random() * colors.length)],
      })
      delay += 0.35 + Math.random() * 0.2
    }
    // 批次间距：初始约 1.2s，最快不低于 0.8s——低速时缝隙约 240px+，高速时约 400px+，
    // 换道后前方始终有可观空窗，不会出现"刚换过去就顶在车屁股上"
    g.spawnT = Math.max(0.8, 1.5 - (g.speed / g.maxSpeed) * 0.75)
  }

  const spd = g.speed * 0.62
  for (let i = g.obstacles.length - 1; i >= 0; i--) {
    const o = g.obstacles[i]
    o.y += spd * dt
    if (o.y > g.h + 20) g.obstacles.splice(i, 1)
  }

  const p = g.player
  for (const o of g.obstacles) {
    if (o.x < p.x + p.w && o.x + o.w > p.x && o.y < p.y + p.h && o.y + o.h > p.y) {
      g.over = true
      break
    }
  }
}

const raceRR = (x, y, w, h, r) => {
  const c = rctx
  c.beginPath()
  c.moveTo(x + r, y)
  c.arcTo(x + w, y, x + w, y + h, r)
  c.arcTo(x + w, y + h, x, y + h, r)
  c.arcTo(x, y + h, x, y, r)
  c.arcTo(x, y, x + w, y, r)
  c.closePath()
}

const raceCarDrawTop = (c, x, y, w, h, s) => {
  const body = s ? (s.body || '#ffffff') : ptBody.value
  const stripes = s ? (Array.isArray(s.stripes) ? s.stripes.slice() : (s.stripe > 0 ? [s.stripe] : [])) : ptStripes.value
  const sc = s ? Object.assign({}, s.stripeColors || {}) : ptStripeColors.value
  const sp = s ? Object.assign({}, s.stripePos || {}) : ptStripePos.value
  const decos = s ? (Array.isArray(s.decos) ? s.decos : []) : ptDecos.value
  const light = s ? (s.light || '#ffffff') : ptLight.value
  const glass = s ? (s.glass || '#93c5fd') : ptGlass.value

  c.save()
  raceRR(x, y, w, h, 12)
  c.fillStyle = body
  c.fill()
  c.clip()

  if (stripes.includes(3)) {
    const dx = (+sp[3] || 0) * 0.3
    const grd = c.createLinearGradient(x, y + h, x, y)
    grd.addColorStop(0, 'rgba(59,130,246,0)')
    grd.addColorStop(1, hexToRgba(sc[3] || '#a855f7', 0.6))
    c.fillStyle = grd
    c.fillRect(x + dx, y, w, h)
  }

  if (stripes.includes(1)) {
    const dx = (+sp[1] || 0) * 0.3
    c.fillStyle = hexToRgba(sc[1] || '#111827', 0.5)
    c.fillRect(x + 6 + dx, y + 24, w - 12, 7)
    c.fillRect(x + 6 + dx, y + 62, w - 12, 7)
  }

  if (stripes.includes(2)) {
    const dx = (+sp[2] || 0) * 0.3
    c.fillStyle = hexToRgba(sc[2] || '#f97316', 0.9)
    c.beginPath()
    c.moveTo(x + w / 2 + dx, y + 8)
    c.bezierCurveTo(x + w - 8 + dx, y + 18, x + w - 6 + dx, y + 30, x + w / 2 + dx, y + 26)
    c.bezierCurveTo(x + 6 + dx, y + 30, x + 8 + dx, y + 18, x + w / 2 + dx, y + 8)
    c.closePath()
    c.fill()
  }

  if (stripes.includes(8)) {
    const dx = (+sp[8] || 0) * 0.3
    c.fillStyle = hexToRgba(sc[8] || '#3b82f6', 0.75)
    c.beginPath()
    c.moveTo(x + 4, y + 44 + dx)
    c.bezierCurveTo(x + w * 0.3, y + 40 + dx, x + w * 0.5, y + 48 + dx, x + w * 0.7, y + 43 + dx)
    c.lineTo(x + w - 4, y + 46 + dx)
    c.lineTo(x + w - 4, y + 51 + dx)
    c.bezierCurveTo(x + w * 0.6, y + 53 + dx, x + w * 0.4, y + 47 + dx, x + 4, y + 51 + dx)
    c.closePath()
    c.fill()
  }

  if (stripes.includes(5)) {
    const dx = (+sp[5] || 0) * 0.3
    const cell = 6
    for (let r = 0; r < 3; r++) {
      for (let col = 0; col < 5; col++) {
        c.fillStyle = (r + col) % 2 === 0 ? (sc[5] || '#111827') : '#f8fafc'
        c.fillRect(x + 13 + dx + col * cell, y + 68 + r * cell, cell, cell)
      }
    }
  }

  if (stripes.includes(6)) {
    const dx = (+sp[6] || 0) * 0.3
    c.fillStyle = sc[6] || '#facc15'
    c.beginPath()
    c.moveTo(x + w * 0.62 + dx, y + 14)
    c.lineTo(x + w * 0.38 + dx, y + 38)
    c.lineTo(x + w * 0.52 + dx, y + 38)
    c.lineTo(x + w * 0.38 + dx, y + 58)
    c.lineTo(x + w * 0.66 + dx, y + 34)
    c.lineTo(x + w * 0.52 + dx, y + 34)
    c.closePath()
    c.fill()
  }

  if (stripes.includes(7)) {
    const dx = (+sp[7] || 0) * 0.3
    c.fillStyle = hexToRgba(sc[7] || '#ec4899', 0.9)
    c.beginPath()
    c.moveTo(x + w / 2 + dx, y + 52)
    c.bezierCurveTo(x + w * 0.3 + dx, y + 42, x + w * 0.36 + dx, y + 32, x + w / 2 + dx, y + 40)
    c.bezierCurveTo(x + w * 0.64 + dx, y + 32, x + w * 0.7 + dx, y + 42, x + w / 2 + dx, y + 52)
    c.closePath()
    c.fill()
  }

  if (stripes.includes(4)) {
    const dx = (+sp[4] || 0) * 0.3
    c.fillStyle = sc[4] || '#ffffff'
    const stars = [[x + 16, y + 20], [x + w - 16, y + 22], [x + 16, y + 74], [x + w - 16, y + 76]]
    for (const [sx, sy] of stars) {
      c.beginPath()
      for (let i = 0; i < 5; i++) {
        const a = (i * 4 * Math.PI) / 5 - Math.PI / 2
        c.lineTo(sx + dx + Math.cos(a) * 4, sy + Math.sin(a) * 4)
      }
      c.closePath()
      c.fill()
    }
  }
  c.restore()

  // 挡风玻璃（车头上端）
  c.fillStyle = hexToRgba(glass, 0.85)
  c.beginPath()
  c.moveTo(x + 8, y + 4)
  c.lineTo(x + w - 8, y + 4)
  c.lineTo(x + w * 0.6, y + 15)
  c.lineTo(x + w * 0.4, y + 15)
  c.closePath()
  c.fill()
  // 后挡
  c.beginPath()
  c.moveTo(x + 8, y + h - 4)
  c.lineTo(x + w - 8, y + h - 4)
  c.lineTo(x + w * 0.6, y + h - 15)
  c.lineTo(x + w * 0.4, y + h - 15)
  c.closePath()
  c.fill()
  // 天窗
  c.fillStyle = hexToRgba(glass, 0.7)
  c.fillRect(x + w * 0.38, y + 30, w * 0.24, 14)

  // 前灯（上端两角）
  c.fillStyle = light
  c.beginPath()
  c.ellipse(x + 7, y + 7, 3, 2.5, 0, 0, Math.PI * 2)
  c.fill()
  c.beginPath()
  c.ellipse(x + w - 7, y + 7, 3, 2.5, 0, 0, Math.PI * 2)
  c.fill()
  // 尾灯（下端两角）
  c.fillStyle = '#ef4444'
  c.beginPath()
  c.ellipse(x + 7, y + h - 7, 3, 2.5, 0, 0, Math.PI * 2)
  c.fill()
  c.beginPath()
  c.ellipse(x + w - 7, y + h - 7, 3, 2.5, 0, 0, Math.PI * 2)
  c.fill()
  // 轮眉（四角）
  c.fillStyle = 'rgba(15,23,42,0.75)'
  c.fillRect(x - 2, y + 10, 6, 14)
  c.fillRect(x + w - 4, y + 10, 6, 14)
  c.fillRect(x - 2, y + h - 24, 6, 14)
  c.fillRect(x + w - 4, y + h - 24, 6, 14)

  // 装饰（车顶中央）
  for (const d of decos) {
    const dx = x + w / 2 + ((+d.pos || 0) * 0.12)
    if (d.type === 0) drawFlowerTop(c, dx, y + h / 2, d.color)
    else if (d.type === 1) drawBearTop(c, dx, y + h / 2, d.color)
    else if (d.type === 2) drawBowTop(c, dx, y + h / 2, d.color)
    else drawCrownTop(c, dx, y + h / 2, d.color)
  }
}

const raceDraw = () => {
  const c = rctx
  const g = rgame
  c.clearRect(0, 0, g.w, g.h)

  const bg = c.createLinearGradient(0, 0, 0, g.h)
  bg.addColorStop(0, '#0b1026')
  bg.addColorStop(1, '#1b2a5e')
  c.fillStyle = bg
  c.fillRect(0, 0, g.w, g.h)

  c.fillStyle = 'rgba(255,255,255,0.6)'
  for (let i = 0; i < 26; i++) {
    const sx = (i * 137.5) % g.w
    const sy = ((i * 61.3 + Math.floor(g.dist * 0.4)) % g.h)
    const r = (i % 3) + 0.6
    c.globalAlpha = 0.35 + (i % 4) * 0.12
    c.beginPath()
    c.arc(sx, sy, r, 0, Math.PI * 2)
    c.fill()
  }
  c.globalAlpha = 1

  c.fillStyle = '#0c2f1c'
  c.fillRect(0, 0, g.roadLeft - 12, g.h)
  c.fillRect(g.roadLeft + g.laneW * R_LANES + 12, 0, g.w, g.h)

  c.fillStyle = '#3f4b68'
  c.fillRect(g.roadLeft - 12, 0, 12, g.h)
  c.fillRect(g.roadLeft + g.laneW * R_LANES, 0, 12, g.h)

  c.fillStyle = '#232a3e'
  c.fillRect(g.roadLeft, 0, g.laneW * R_LANES, g.h)

  c.strokeStyle = 'rgba(255,255,255,0.85)'
  c.lineWidth = 4
  const dashLen = 44
  const offset = (g.dist * 2.2) % (dashLen * 2)
  for (let i = 1; i < R_LANES; i++) {
    const x = g.roadLeft + g.laneW * i
    c.setLineDash([dashLen, dashLen])
    c.beginPath()
    c.moveTo(x, offset - dashLen * 2)
    c.lineTo(x, g.h + dashLen * 2)
    c.stroke()
  }
  c.setLineDash([])

  c.fillStyle = '#ffd166'
  for (let y = -20; y < g.h; y += 46) {
    const yy = (y + (g.dist * 3.2) % 46)
    c.fillRect(g.roadLeft - 7, yy, 3, 8)
    c.fillRect(g.roadLeft + g.laneW * R_LANES + 4, yy, 3, 8)
  }

  for (const o of g.obstacles) {
    raceRR(o.x, o.y, o.w, o.h, 10)
    c.fillStyle = o.color
    c.fill()
    c.fillStyle = 'rgba(255,255,255,0.9)'
    c.fillRect(o.x + 7, o.y + 6, 9, 9)
    c.fillRect(o.x + o.w - 16, o.y + 6, 9, 9)
    c.fillStyle = '#fff7cc'
    c.fillRect(o.x + 8, o.y + o.h - 8, 10, 4)
    c.fillRect(o.x + o.w - 18, o.y + o.h - 8, 10, 4)
  }

  const p = g.player
  const py = g.h - 150
  raceCarDrawTop(c, p.x, py, p.w, p.h, racePaintSel.value === 'current' ? null : (ptSaved.value[racePaintSel.value] || null))
}

const raceKey = (e) => {
  const down = e.type === 'keydown'
  if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
    e.preventDefault()
    if (!down || !rgame || rgame.over) return
    const now = performance.now()
    if (now - rgame.lastSwitch < 130) return
    rgame.lastSwitch = now
    const dir = e.key === 'ArrowLeft' ? -1 : 1
    const nl = Math.max(0, Math.min(R_LANES - 1, rgame.player.lane + dir))
    if (nl !== rgame.player.lane) {
      rgame.player.lane = nl
      rgame.player.x = rgame.roadLeft + rgame.laneW * nl + (rgame.laneW - R_CAR_W) / 2
    }
  }
  if (e.key === ' ' || e.key === 'Enter') {
    if (racePhase.value === 'idle' || racePhase.value === 'over') {
      e.preventDefault()
      raceStart()
    }
  }
}

onMounted(() => {
  window.addEventListener('keydown', raceKey)
  window.addEventListener('keyup', raceKey)
  if (rcv.value) {
    rctx = rcv.value.getContext('2d')
    raceReset()
    raceDraw()
  }
})
onUnmounted(() => {
  if (rraf) cancelAnimationFrame(rraf)
  window.removeEventListener('keydown', raceKey)
  window.removeEventListener('keyup', raceKey)
})
</script>

<template>
  <div>
    <div class="page-header">
      <h2 class="page-title">趣味乐园</h2>
      <p class="page-desc">
        基于 38806 条中国乘用车真实销量数据打造的互动小游戏：汽车配色师、造车工坊、我的车库、公路赛车。
      </p>
    </div>

    <div v-if="loading" class="loading">数据加载中…</div>
    <div v-else-if="errMsg" class="error">{{ errMsg }}</div>

    <template v-else>
      <!-- 游戏导航 -->
      <div class="game-tabs">
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'paint' }"
          @click="activeTab = 'paint'; ptRedraw()"
        >🎨 汽车配色师</button>
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'garage' }"
          @click="activeTab = 'garage'"
        >🏭 造车工坊</button>
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'garage2' }"
          @click="activeTab = 'garage2'"
        >🏠 我的车库</button>
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'race' }"
          @click="activeTab = 'race'"
        >🏎️ 公路赛车</button>
      </div>

      <!-- ============ 游戏1：汽车配色师 ============ -->
      <section v-show="activeTab === 'paint'" class="game-panel">
        <div class="game-head">
          <h3 class="card-title">🎨 汽车配色师 · 自由改装你的爱车</h3>
          <div class="game-score">已保存 <b>{{ ptSaved.length }}</b> 款配色</div>
        </div>

        <div class="paint-wrap">
          <div class="paint-preview">
            <canvas ref="ptcv" class="paint-canvas" width="720" height="420"></canvas>
            <div class="paint-top-title">⬇ 俯视图预览 · 实时同步</div>
            <canvas ref="ptTop" class="paint-top" width="480" height="300"></canvas>
          </div>

          <div class="paint-panel">
            <div class="paint-sec paint-sec-full">
              <div class="paint-sec-title">🎨 车身颜色</div>
              <div class="paint-swatches">
                <button v-for="c in ptColors" :key="c" class="paint-swatch" :style="{ background: c }" :class="{ on: ptBody === c }" @click="ptBody = c" :title="c"></button>
                <input type="color" v-model="ptBody" class="paint-color-pick" title="自定义取色" />
              </div>
            </div>

            <div class="paint-sec">
              <div class="paint-sec-title">🛞 轮胎</div>
              <div class="paint-opts">
                <button v-for="(o, i) in ptTireNames" :key="o" class="paint-opt" :class="{ on: ptTire === i }" @click="ptTire = i">{{ o }}</button>
              </div>
            </div>

            <div class="paint-sec">
              <div class="paint-sec-title">⚙️ 轮毂颜色</div>
              <div class="paint-opts">
                <button v-for="(o, i) in ptRimNames" :key="o" class="paint-opt" :class="{ on: ptRim === ptRimColors[i] }" @click="ptRim = ptRimColors[i]">{{ o }}</button>
                <input type="color" v-model="ptRim" class="paint-color-pick" title="自定义取色" />
              </div>
            </div>

            <div class="paint-sec">
              <div class="paint-sec-title">🌀 轮毂样式</div>
              <div class="paint-opts">
                <button v-for="(o, i) in ptRimStyleNames" :key="o" class="paint-opt" :class="{ on: ptRimStyle === i }" @click="ptRimStyle = i">{{ o }}</button>
              </div>
            </div>

            <div class="paint-sec">
              <div class="paint-sec-title">💡 车灯</div>
              <div class="paint-opts">
                <button v-for="(o, i) in ptLightNames" :key="o" class="paint-opt" :class="{ on: ptLight === ptLights[i] }" @click="ptLight = ptLights[i]">{{ o }}</button>
                <input type="color" v-model="ptLight" class="paint-color-pick" title="自定义取色" />
              </div>
            </div>

            <div class="paint-sec">
              <div class="paint-sec-title">🪟 车窗</div>
              <div class="paint-opts">
                <button v-for="(o, i) in ptGlassNames" :key="o" class="paint-opt" :class="{ on: ptGlass === ptGlasses[i] }" @click="ptGlass = ptGlasses[i]">{{ o }}</button>
                <input type="color" v-model="ptGlass" class="paint-color-pick" title="自定义取色" />
              </div>
            </div>

            <div class="paint-sec paint-sec-full">
              <div class="paint-sec-title">🎀 拉花涂装 · 可叠加
                <button class="paint-clear" @click="ptStripes = []; ptStripeColors = {}; ptStripePos = {}">清除全部</button>
              </div>
              <div class="paint-opts">
                <button v-for="(o, i) in ptStripeNames" :key="o" class="paint-opt" :class="{ on: ptStripes.includes(ptStripeIds[i]) }" @click="ptToggleStripe(ptStripeIds[i])">{{ o }}</button>
              </div>
              <div v-if="ptStripes.length" class="paint-configs">
                <div v-for="id in ptStripes" :key="id" class="paint-config-row">
                  <span class="paint-config-name">{{ ptStripeNameOf(id) }}</span>
                  <input type="color" v-model="ptStripeColors[id]" class="paint-color-pick" title="拉花颜色" />
                  <input type="range" min="-60" max="60" v-model.number="ptStripePos[id]" class="paint-range" title="位置" />
                  <button class="paint-del" @click="ptToggleStripe(id)">✕</button>
                </div>
              </div>
            </div>

            <div class="paint-sec paint-sec-full">
              <div class="paint-sec-title">🧸 车顶装饰 · 可叠加</div>
              <div class="paint-opts">
                <button v-for="(o, i) in ptDecoNames" :key="o" class="paint-opt" @click="ptAddDeco(i)">＋{{ o }}</button>
              </div>
              <div v-if="ptDecos.length" class="paint-configs">
                <div v-for="(d, i) in ptDecos" :key="d.id" class="paint-config-row">
                  <span class="paint-config-name">{{ ptDecoNames[d.type] }}</span>
                  <input type="color" v-model="d.color" class="paint-color-pick" title="装饰颜色" />
                  <input type="range" min="-100" max="100" v-model.number="d.pos" class="paint-range" title="位置" />
                  <button class="paint-del" @click="ptDelDeco(i)">✕</button>
                </div>
              </div>
            </div>

            <div class="paint-sec paint-sec-full">
              <div class="paint-sec-title">🔖 车牌</div>
              <input :value="ptPlate" @input="ptPlateInput" @compositionstart="ptImeOn = true" @compositionend="ptPlateCommit" maxlength="8" class="paint-plate-input" placeholder="输入车牌，如 粤A·88888" />
            </div>
          </div>
        </div>

        <div class="paint-actions">
          <button class="btn btn-primary paint-btn" @click="ptRandom">🎲 随机灵感</button>
          <button class="btn paint-btn" @click="ptReset">↺ 重置原厂</button>
          <button class="btn paint-btn" @click="ptSave">💾 保存配色</button>
        </div>

        <div v-if="ptSaved.length" class="paint-saved">
          <div v-for="(s, i) in ptSaved" :key="i" class="paint-saved-item" @click="ptApply(s)" title="点击应用此配色">
            <span class="paint-saved-color" :style="{ background: s.body }"></span>
            <span>{{ s.name }}</span>
            <button class="paint-del" @click.stop="ptDel(i)">✕</button>
          </div>
        </div>

        <div class="race-key-hint">点击色板或取色盘换色 · 每个拉花与装饰可单独调色和调位置 · 支持保存多套配色</div>
      </section>

<!-- ============ 游戏2：造车工坊 ============ -->
      <section v-show="activeTab === 'garage'" class="game-panel">
        <div class="game-head">
          <h3 class="card-title">造车工坊 · 设计你的专属车型</h3>
          <div class="game-score">基于真实销量数据估算 · 一键造车</div>
        </div>
        <div class="garage-layout">
          <div class="clue-card garage-form">
            <div class="clue-title">🛠️ 车型配置</div>
            <div class="garage-grid">
              <label class="garage-field">
                <span>车名</span>
                <input v-model="garage.name" class="input" placeholder="如：凌云Pro" />
              </label>
              <label class="garage-field">
                <span>品牌</span>
                <input v-model="garage.brand" class="input" placeholder="如：我的车厂" />
              </label>
              <label class="garage-field">
                <span>车身类型</span>
                <select v-model="garage.body" class="input">
                  <option v-for="b in garageBodies" :key="b" :value="b">{{ garageBodyLabel(b) }}</option>
                </select>
              </label>
              <label class="garage-field">
                <span>能源类型</span>
                <select v-model="garage.energy" class="input">
                  <option value="EV">新能源</option>
                  <option value="Gasoline">燃油</option>
                </select>
              </label>
              <label class="garage-field garage-wide">
                <span>定价（万元）：<b>{{ garage.price }}</b></span>
                <input v-model.number="garage.price" class="input" type="number" min="3" max="10000" />
              </label>
            </div>
            <button class="btn-primary garage-build" @click="garageBuild">🏭 造车！</button>
          </div>

          <div v-if="garage.result" class="garage-card">
            <div class="garage-paint-tip">
              <span>🎨 配色预览</span>
              <select v-model="garagePaintSel" class="input garage-paint-sel" @change="garagePaintSelChange">
                <option value="current">当前配色</option>
                <option v-for="(jb, i) in ptSaved" :key="i" :value="i">我的配色 {{ i + 1 }}</option>
              </select>
            </div>
            <canvas ref="garageCv" class="garage-car" width="460" height="268"></canvas>
            <div class="garage-name">{{ garage.name }} <span class="garage-brand">{{ garage.brand }}</span></div>
            <div class="garage-sub">{{ garage.result.segLabel }} · 定价 {{ Number(garage.price).toLocaleString('zh-CN') }} 万元</div>
            <div class="garage-stats">
              <div class="garage-stat">
                <div class="garage-stat-value">{{ garage.result.estMonthly.toLocaleString('zh-CN') }}</div>
                <div class="garage-stat-label">预估月销（辆）</div>
              </div>
              <div class="garage-stat">
                <div class="garage-stat-value">{{ garage.result.estYearly.toLocaleString('zh-CN') }}</div>
                <div class="garage-stat-label">预估年销（辆）</div>
              </div>
              <div class="garage-stat">
                <div class="garage-stat-value">{{ garage.result.share }}%</div>
                <div class="garage-stat-label">细分市占率</div>
              </div>
              <div class="garage-stat">
                <div class="garage-stat-value tier-badge">{{ garage.result.tier }}</div>
                <div class="garage-stat-label">预计段位</div>
              </div>
            </div>
            <div class="garage-rival-title">同价位参考对手（真实车型）</div>
            <div class="garage-rivals">
              <div v-for="r in garage.result.rivals" :key="r.model" class="garage-rival">
                <span class="garage-rival-name">{{ r.model }}</span>
                <span class="garage-rival-meta">{{ r.make }} · {{ garageEnergyLabel(r.is_ev) }} · {{ r.avg_price }} 万</span>
                <span class="garage-rival-sold">{{ (r.total / 10000).toFixed(1) }}万</span>
              </div>
            </div>
            <div class="garage-note">
              <template v-if="Number(garage.price) >= 500">
                定价已进入超豪华/限量区间，市场极小，按高端定制逻辑估算。
              </template>
              <template v-else>
                本估算基于 {{ garage.result.segCount || '全部' }} 款同类真实车型的平均月销与价格弹性推算，仅作趣味参考。
              </template>
            </div>
            <button class="btn-primary garage-build" @click="garageBuild">🎲 重新造一辆</button>
          </div>
          <div v-else class="garage-empty">
            <div class="garage-empty-icon">🏭</div>
            <div>配置好车名、车身、能源和定价，点击「造车！」<br />系统将基于 38806 条真实销量数据估算你的新车表现</div>
          </div>
        </div>
      </section>

<!-- ================== 游戏3：我的车库 ============ -->
      <section v-show="activeTab === 'garage2'" class="game-panel">
        <div class="game-head">
          <h3 class="card-title">🏠 我的车库 · 收藏你的 Dream Car</h3>
          <div class="game-score">已收藏 <b>{{ ga.items.length }}</b> / {{ MAX_GARAGE }} 辆</div>
        </div>

        <button class="btn btn-ghost ga-custom-btn" @click="cust.show = !cust.show">
          {{ cust.show ? '收起自定义面板' : '📷 上传自定义车型' }}
        </button>

        <div v-if="cust.show" class="ga-custom">
          <div class="ga-cust-title">自定义车型 · 上传你的爱车</div>
          <div class="ga-cust-main">
            <label class="ga-upload">
              <input type="file" accept="image/*" @change="onCustFile" />
              <img v-if="cust.img" :src="cust.img" alt="预览" />
              <div v-else class="ga-upload-ph">📷<br />点击上传照片</div>
            </label>
            <div class="ga-cust-form">
              <div class="ga-cust-field">
                <span>车名</span>
                <input v-model="cust.name" class="input" placeholder="如：我的DreamCar" />
              </div>
              <div class="ga-cust-field">
                <span>品牌</span>
                <input v-model="cust.make" class="input" placeholder="选填" />
              </div>
              <div class="ga-cust-field">
                <span>车身类型</span>
                <select v-model="cust.body" class="input">
                  <option value="Sedan">轿车</option>
                  <option value="SUV">SUV</option>
                  <option value="MPV">MPV</option>
                  <option value="Hatchback">两厢车</option>
                  <option value="Sports Car">跑车</option>
                </select>
              </div>
              <div class="ga-cust-field">
                <span>能源类型</span>
                <select v-model="cust.energy" class="input">
                  <option value="EV">新能源</option>
                  <option value="Gasoline">燃油</option>
                </select>
              </div>
              <div class="ga-cust-field">
                <span>定价（万元）</span>
                <input v-model.number="cust.price" class="input" type="number" min="1" />
              </div>
            </div>
          </div>
          <div class="ga-upload-btns">
            <select v-model="custPaintSel" class="input garage-paint-sel">
              <option value="current">当前配色</option>
              <option v-for="(jb, i) in ptSaved" :key="i" :value="i">我的配色 {{ i + 1 }}</option>
            </select>
            <button class="btn btn-ghost ga-upload-rm" @click="usePaintAsCust">🎨 用配色师作品当照片</button>
            <button v-if="cust.img" class="btn btn-ghost ga-upload-rm" @click="clearCustImg">移除照片</button>
          </div>
          <div v-if="cust.msg" class="ga-cust-msg">{{ cust.msg }}</div>
          <div class="ga-cust-actions">
            <button class="btn btn-primary" @click="custAdd">加入车库</button>
            <button class="btn btn-ghost" @click="cust.show = false">取消</button>
          </div>
        </div>

        <div v-if="!ga.items.length" class="garage-empty2">
          <div class="garage-empty-icon">🏠</div>
          <div>从下方 TOP30 热门车型中挑选，或点击上方「上传自定义车型」</div>
          <div class="garage-empty-sub">带 📷 的车型可直接看到实拍图</div>
        </div>

        <template v-else>
          <div class="ga-stats">
            <div class="ga-stat">
              <div class="ga-stat-v">¥{{ gaStats.value.toFixed(1) }}万</div>
              <div class="ga-stat-l">车库总价值</div>
            </div>
            <div class="ga-stat">
              <div class="ga-stat-v">{{ (gaStats.totalSales / 10000).toFixed(1) }}万辆</div>
              <div class="ga-stat-l">累计总销量</div>
            </div>
            <div class="ga-stat">
              <div class="ga-stat-v">{{ gaStats.tiers }} 档</div>
              <div class="ga-stat-l">覆盖段位</div>
            </div>
            <div class="ga-stat">
              <div class="ga-stat-v">{{ gaShare.toFixed(2) }}%</div>
              <div class="ga-stat-l">TOP100份额</div>
            </div>
          </div>
          <div class="ga-tags">
            <span v-for="tg in gaStats.tags" :key="tg" class="ga-tag">{{ tg }}</span>
          </div>
          <div class="ga-list">
            <div v-for="c in ga.items" :key="c.model" class="ga-card">
              <div class="ga-pic">
                <img v-if="c.img || gaCarImg(c.model)" :src="c.img || gaCarImg(c.model)" :alt="c.model" />
                <div v-else class="ga-pic-ph">🚗</div>
                <span v-if="c.custom" class="ga-custom-badge">自定义</span>
              </div>
              <div class="ga-info">
                <div class="ga-name">{{ c.model }}</div>
                <div class="ga-sub">{{ c.make }} · {{ evLabel(c.is_ev) }} · {{ c.body_label ? c.body_label : c.body_type }}</div>
                <div class="ga-sub2">
                  <template v-if="c.custom">¥{{ c.avg_price }}万 · 自定义收藏</template>
                  <template v-else>¥{{ c.avg_price }}万 · 累计 {{ (c.total / 10000).toFixed(1) }}万辆 · {{ tierOf(c.total) }}</template>
                </div>
              </div>
              <button class="ga-remove" @click="gaToggle(c)">移除</button>
            </div>
          </div>
          <button class="btn btn-ghost ga-clear" @click="gaClear">清空车库</button>
        </template>

        <div class="ga-pool-head">
          <div class="card-title" style="margin: 0">热门车型精选 TOP30</div>
          <div class="ga-pool-note">点击车型卡片加入 / 移出车库</div>
        </div>
        <div class="ga-pool">
          <div
            v-for="c in pool.slice(0, 30)"
            :key="c.model"
            :class="['ga-pool-item', { 'ga-pool-sel': gaIn(c.model) }]"
            @click="gaToggle(c)"
          >
            <div class="ga-pool-pic">
              <img v-if="gaCarImg(c.model)" :src="gaCarImg(c.model)" :alt="c.model" />
              <div v-else class="ga-pool-ph">{{ c.model.slice(0, 1) }}</div>
            </div>
            <div class="ga-pool-info">
              <div class="ga-pool-name">
                {{ c.model }}
                <span v-if="gaCarImg(c.model)" class="ga-cam">📷</span>
              </div>
              <div class="ga-pool-sub">{{ c.make }} · ¥{{ c.avg_price }}万 · {{ (c.total / 10000).toFixed(1) }}万辆</div>
            </div>
            <div class="ga-pool-plus">{{ gaIn(c.model) ? '✓' : '+' }}</div>
          </div>
        </div>
      </section>

<!-- ============ 游戏4：公路赛车 ============ -->
      <section v-show="activeTab === 'race'" class="game-panel race-panel">
        <div class="game-head">
          <h3 class="card-title">🏎️ 公路赛车 · 躲避车流跑得越远分越高</h3>
          <div class="game-score">最高纪录 <b>{{ raceBest }}</b> m</div>
        </div>

        <div class="race-paint-sel-row">
          <span>🎨 车辆配色</span>
          <select v-model="racePaintSel" @change="raceRepaint" class="input garage-paint-sel">
            <option value="current">当前配色</option>
            <option v-for="(jb, i) in ptSaved" :key="i" :value="i">我的配色 {{ i + 1 }}</option>
          </select>
        </div>

        <div class="race-wrap">
          <canvas ref="rcv" class="race-canvas" width="900" height="600"></canvas>

          <div v-if="racePhase === 'idle'" class="race-overlay">
            <div class="race-logo">🏎️</div>
            <div class="race-title">公路赛车</div>
            <div class="race-tip">← → 切换车道 · 躲避障碍车流</div>
            <button class="btn btn-primary race-btn" @click="raceStart">开始游戏</button>
            <div v-if="raceBest" class="race-best">🏆 最高纪录：{{ raceBest }} 米</div>
          </div>

          <div v-else-if="racePhase === 'over'" class="race-overlay">
            <div class="race-title">💥 撞车了！</div>
            <div class="race-score">本次行驶 <b>{{ raceScore }}</b> 米</div>
            <div v-if="raceNewBest" class="race-newbest">🎉 打破纪录，太强了！</div>
            <div v-else class="race-best">🏆 最高纪录：{{ raceBest }} 米</div>
            <button class="btn btn-primary race-btn" @click="raceStart">再跑一次</button>
          </div>

          <div v-if="racePhase === 'running'" class="race-hud">
            <div class="race-hud-item">🏁 {{ raceScore }} m</div>
            <div class="race-hud-item">⚡ {{ raceSpeed }} km/h</div>
          </div>
        </div>
        <div class="race-key-hint">键盘 ← / → 切换车道 · 空格 / 回车开始或重开</div>
      </section>


    </template>
  </div>
</template>

<style scoped>
/* 游戏 Tab 导航 */
.game-tabs {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}
.tab-btn {
  padding: 10px 22px;
  border-radius: 10px;
  border: 1px solid #e2e8f2;
  background: #ffffff;
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
  background: linear-gradient(135deg, #0b5fff, #7c3aed);
  color: #ffffff;
  border-color: transparent;
}

/* 游戏面板 */
.game-panel {
  background: #ffffff;
  border-radius: 14px;
  padding: 24px;
  border: 1px solid #e8ecf3;
  box-shadow: 0 2px 10px rgba(11, 46, 92, 0.05);
}
.race-panel {
  padding: 16px;
}
.race-panel .game-head {
  margin-bottom: 10px;
}
.game-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 18px;
}
.game-score {
  color: #7a8699;
  font-size: 14px;
}
.game-score b {
  color: #0b5fff;
  font-size: 18px;
}

/* 线索卡 */
.clue-card {
  background: linear-gradient(135deg, #f0f5ff, #faf6ff);
  border: 1px solid #dbe6ff;
  border-radius: 12px;
  padding: 18px;
  margin-bottom: 18px;
}
.clue-title {
  font-size: 16px;
  font-weight: 700;
  color: #0b2e5c;
  margin-bottom: 14px;
}
.clue-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}
.clue-item {
  background: #ffffff;
  border-radius: 10px;
  padding: 10px 12px;
  border: 1px solid #e8ecf3;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.clue-item.clue-wide {
  grid-column: span 1;
}
.clue-label {
  font-size: 12px;
  color: #9aa7b8;
}
.clue-item b {
  font-size: 14px;
  color: #0b2e5c;
}

/* 选项 */
.opt-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}
.opt-btn {
  padding: 14px;
  border-radius: 10px;
  border: 2px solid #e2e8f2;
  background: #ffffff;
  font-size: 15px;
  font-weight: 600;
  color: #2c3e50;
  cursor: pointer;
  transition: all 0.2s;
}
.opt-btn:hover:not(:disabled) {
  border-color: #0b5fff;
  color: #0b5fff;
  background: #f0f5ff;
}
.opt-btn.right {
  border-color: #16a34a;
  background: #f0fdf4;
  color: #16a34a;
}
.opt-btn.wrong {
  border-color: #dc2626;
  background: #fef2f2;
  color: #dc2626;
}
.opt-btn.dim {
  opacity: 0.45;
}

/* 反馈与结果 */
.feedback {
  background: #f8faff;
  border-radius: 10px;
  padding: 14px 16px;
  font-size: 14px;
  color: #2c3e50;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.next-btn {
  margin-left: auto;
}
.result-card {
  text-align: center;
  padding: 30px 20px;
}
.result-score {
  font-size: 56px;
  font-weight: 800;
  color: #0b5fff;
  line-height: 1;
}
.result-unit {
  font-size: 22px;
  color: #7a8699;
  margin-left: 6px;
}
.result-verdict {
  font-size: 18px;
  font-weight: 700;
  color: #0b2e5c;
  margin: 14px 0 6px;
}
.result-sub {
  color: #7a8699;
  font-size: 14px;
  margin-bottom: 18px;
}

/* 销量大猜想 */
.paint-wrap {
  display: grid;
  grid-template-columns: 1fr;
  gap: 18px;
  align-items: start;
}

.paint-preview {
  position: sticky;
  top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.paint-canvas {
  display: block;
  width: 100%;
  max-width: 500px;
  height: auto;
  border-radius: 12px;
  background: #e9eef6;
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.16);
  border: 1px solid rgba(15, 23, 42, 0.08);
}

.paint-top-title {
  font-size: 12px;
  color: #64748b;
  font-weight: 700;
  margin-top: 2px;
}

.paint-top {
  display: block;
  width: 100%;
  max-width: 500px;
  height: auto;
  border-radius: 12px;
  background: #eef2f7;
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.16);
  border: 1px solid rgba(15, 23, 42, 0.08);
}

.paint-panel {
  min-width: 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  align-content: start;
}

.paint-sec-full {
  grid-column: 1 / -1;
}

.paint-sec-title {
  font-size: 13px;
  font-weight: 700;
  color: #334155;
  margin-bottom: 6px;
}

.paint-swatches {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.paint-swatch {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: 2px solid #d5dbe6;
  cursor: pointer;
  transition: all 0.15s;
}

.paint-swatch.on {
  border-color: #0b5fff;
  box-shadow: 0 0 0 2px rgba(11, 95, 255, 0.28);
  transform: scale(1.12);
}

.paint-opts {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.paint-opt {
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  color: #475569;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.paint-opt.on {
  background: linear-gradient(135deg, #0b5fff, #7c3aed);
  color: #ffffff;
  border-color: transparent;
}

.paint-pos-title {
  margin-top: 4px;
}

.paint-clear {
  border: none;
  background: #fee2e2;
  color: #dc2626;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 6px;
  cursor: pointer;
  margin-left: 8px;
  vertical-align: middle;
}

.paint-clear:hover {
  background: #fecaca;
}

.paint-color-pick {
  width: 34px;
  height: 30px;
  border: 2px solid #d5dbe6;
  border-radius: 8px;
  padding: 0 2px;
  cursor: pointer;
  background: #ffffff;
}

.paint-color-pick::-webkit-color-swatch-wrapper {
  padding: 2px;
}

.paint-color-pick::-webkit-color-swatch {
  border: none;
  border-radius: 4px;
}

@media (min-width: 1100px) {
  .paint-wrap {
    grid-template-columns: 420px 1fr;
  }
}

.paint-configs {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 8px;
}

.paint-config-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 8px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 12px;
  color: #334155;
}

.paint-config-name {
  width: 40px;
  font-weight: 700;
  flex-shrink: 0;
}

.paint-range {
  flex: 1;
  accent-color: #0b5fff;
  height: 4px;
  min-width: 60px;
}

.paint-actions {
  display: flex;
  gap: 10px;
  margin-top: 16px;
  flex-wrap: wrap;
}

.paint-btn {
  padding: 8px 18px;
  font-size: 13px;
}

.paint-saved {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.paint-saved-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #ffffff;
  cursor: pointer;
  font-size: 12px;
  color: #334155;
  transition: all 0.15s;
}

.paint-saved-item:hover {
  border-color: #0b5fff;
}

.paint-saved-color {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 1px solid #d5dbe6;
}

.paint-del {
  border: none;
  background: none;
  color: #94a3b8;
  cursor: pointer;
  font-size: 13px;
  line-height: 1;
}

.paint-plate-input {
  width: 100%;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  font-size: 13px;
  color: #334155;
  outline: none;
  box-sizing: border-box;
}

.paint-plate-input:focus {
  border-color: #0b5fff;
}
.input {
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid #dbe3ee;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}
.input:focus {
  border-color: #0b5fff;
}
.btn-primary {
  padding: 10px 24px;
  border-radius: 10px;
  border: none;
  background: linear-gradient(135deg, #0b5fff, #7c3aed);
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}
.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.quiz-history {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.quiz-msg {
  background: #f0f5ff;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 13px;
  color: #0b2e5c;
}

/* 段位榜 */
.tier-search {
  display: flex;
  gap: 10px;
  margin-bottom: 14px;
}
.tier-result {
  background: #f0f5ff;
  border-radius: 10px;
  padding: 12px 16px;
  margin-bottom: 16px;
  font-size: 14px;
  color: #0b2e5c;
}
.tier-result.dim {
  color: #7a8699;
}
.tier-badge {
  color: #0b5fff;
  font-weight: 700;
}
.tier-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.tier-block {
  border-radius: 12px;
  border: 1px solid #e8ecf3;
  overflow: hidden;
}
.tier-head {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: linear-gradient(90deg, #f0f5ff, #faf6ff);
  border-bottom: 1px solid #e8ecf3;
}
.tier-emoji {
  font-size: 24px;
}
.tier-name {
  font-weight: 700;
  color: #0b2e5c;
  font-size: 15px;
}
.tier-desc {
  font-size: 12px;
  color: #9aa7b8;
}
.tier-count {
  margin-left: auto;
  font-size: 13px;
  color: #0b5fff;
  font-weight: 600;
  background: #ffffff;
  border-radius: 20px;
  padding: 4px 12px;
  border: 1px solid #dbe6ff;
}
.tier-cars {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1px;
  background: #eef1f6;
}
.tier-car {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #ffffff;
  padding: 10px 14px;
  font-size: 13px;
}
.tier-car-name {
  font-weight: 700;
  color: #0b2e5c;
  min-width: 84px;
}
.tier-car-meta {
  color: #9aa7b8;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.tier-car-sold {
  color: #0b5fff;
  font-weight: 700;
}
.tier-empty {
  grid-column: 1 / -1;
  padding: 16px;
  text-align: center;
  color: #9aa7b8;
  font-size: 13px;
  background: #ffffff;
}


/* 造车工坊 */
.garage-layout {
  display: grid;
  grid-template-columns: minmax(260px, 340px) 1fr;
  gap: 18px;
  align-items: start;
}
.garage-form {
  margin-bottom: 0;
}
.garage-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}
.garage-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.garage-field span {
  font-size: 12px;
  color: #7a8699;
}
.garage-field b {
  color: #0b5fff;
}
.garage-field.garage-wide {
  grid-column: 1 / -1;
}
.garage-build {
  width: 100%;
  padding: 12px;
  font-size: 15px;
}
.garage-car {
  display: block;
  width: 100%;
  max-width: 460px;
  height: auto;
  border-radius: 10px;
  margin-bottom: 10px;
  border: 1px solid rgba(15, 23, 42, 0.08);
}

.garage-paint-tip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-size: 12px;
  color: #64748b;
  font-weight: 700;
  margin-bottom: 6px;
}

.garage-paint-sel {
  max-width: 150px;
  padding: 4px 8px;
  font-size: 12px;
}

.ga-upload-btns {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.garage-card {
  background: linear-gradient(135deg, #0b2e5c, #0b5fff);
  border-radius: 14px;
  padding: 22px;
  color: #ffffff;
}
.garage-name {
  font-size: 22px;
  font-weight: 800;
  letter-spacing: 1px;
}
.garage-brand {
  font-size: 13px;
  font-weight: 400;
  color: #bcd2ff;
  margin-left: 8px;
}
.garage-sub {
  font-size: 13px;
  color: #bcd2ff;
  margin: 6px 0 16px;
}
.garage-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 16px;
}
.garage-stat {
  background: rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  padding: 12px 8px;
  text-align: center;
}
.garage-stat-value {
  font-size: 18px;
  font-weight: 800;
}
.garage-stat-label {
  font-size: 11px;
  color: #bcd2ff;
  margin-top: 4px;
}
.tier-badge {
  color: #ffd76a;
}
.garage-rival-title {
  font-size: 13px;
  color: #bcd2ff;
  margin-bottom: 8px;
}
.garage-rivals {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 12px;
}
.garage-rival {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 12px;
  font-size: 13px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}
.garage-rival:last-child {
  border-bottom: none;
}
.garage-rival-name {
  font-weight: 700;
  min-width: 80px;
}
.garage-rival-meta {
  color: #bcd2ff;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.garage-rival-sold {
  color: #ffd76a;
  font-weight: 700;
}
.garage-note {
  font-size: 11px;
  color: #bcd2ff;
  margin-bottom: 12px;
  line-height: 1.5;
}
.garage-empty {
  border: 2px dashed #dbe3ee;
  border-radius: 14px;
  padding: 50px 20px;
  text-align: center;
  color: #7a8699;
  font-size: 14px;
  line-height: 1.8;
}
.garage-empty-icon {
  font-size: 44px;
  margin-bottom: 10px;
}

@media (max-width: 720px) {
  .garage-layout {
    grid-template-columns: 1fr;
  }
  .garage-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 720px) {
  .clue-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .opt-list {
    grid-template-columns: 1fr;
  }
  .tier-cars {
    grid-template-columns: 1fr;
  }
}

/* ============ 我的车库 ============ */
.garage-empty2 {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 36px 16px;
  background: linear-gradient(135deg, #f6f9ff, #eef4ff);
  border: 2px dashed #b8cdf0;
  border-radius: 14px;
  color: #5b7290;
  font-size: 14px;
  text-align: center;
}
.garage-empty-icon {
  font-size: 40px;
}
.garage-empty-sub {
  font-size: 12px;
  color: #93a7c2;
}
.ga-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 12px;
}
.ga-stat {
  background: linear-gradient(135deg, #3a7afe, #5b8cff);
  color: #fff;
  border-radius: 12px;
  padding: 12px 8px;
  text-align: center;
}
.ga-stat-v {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 2px;
}
.ga-stat-l {
  font-size: 12px;
  opacity: 0.85;
}
.ga-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 14px;
}
.ga-tag {
  background: #eef3ff;
  border: 1px solid #c9d8f8;
  color: #2f5bd0;
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 13px;
  font-weight: 600;
}
.ga-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 12px;
}
.ga-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fff;
  border: 1px solid #e3ecfb;
  border-radius: 12px;
  padding: 10px;
}
.ga-pic {
  width: 84px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  background: #eef3fb;
}
.ga-pic img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.ga-pic-ph {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  background: linear-gradient(135deg, #dfe9fa, #eef4fd);
}
.ga-info {
  flex: 1;
  min-width: 0;
}
.ga-name {
  font-weight: 700;
  font-size: 15px;
  color: #1b2a4a;
}
.ga-sub {
  font-size: 12px;
  color: #7185a5;
  margin-top: 2px;
}
.ga-sub2 {
  font-size: 12px;
  color: #4a6bb8;
  margin-top: 3px;
  font-weight: 600;
}
.ga-remove {
  flex-shrink: 0;
  border: 1px solid #f0c8c8;
  background: #fff5f5;
  color: #d05050;
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
}
.ga-remove:hover {
  background: #ffe2e2;
}
.ga-clear {
  margin-bottom: 16px;
}
.ga-pool-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 14px 0 10px;
  flex-wrap: wrap;
  gap: 6px;
}
.ga-pool-note {
  font-size: 12px;
  color: #93a7c2;
}
.ga-pool {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 10px;
}
.ga-pool-item {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff;
  border: 1px solid #e3ecfb;
  border-radius: 10px;
  padding: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.ga-pool-item:hover {
  border-color: #8fb0f0;
  box-shadow: 0 4px 12px rgba(58, 122, 254, 0.12);
}
.ga-pool-sel {
  border-color: #3a7afe;
  background: #f0f5ff;
}
.ga-pool-pic {
  width: 62px;
  height: 44px;
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
  background: #eef3fb;
}
.ga-pool-pic img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.ga-pool-ph {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
  color: #5b7bbf;
  background: linear-gradient(135deg, #dfe9fa, #eef4fd);
}
.ga-pool-info {
  flex: 1;
  min-width: 0;
}
.ga-pool-name {
  font-size: 13px;
  font-weight: 700;
  color: #1b2a4a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.ga-cam {
  font-size: 11px;
}
.ga-pool-sub {
  font-size: 11px;
  color: #8296b5;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.ga-pool-plus {
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #e8f0ff;
  color: #3a7afe;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
}
.ga-pool-sel .ga-pool-plus {
  background: #3a7afe;
  color: #fff;
}

/* ============ 自定义上传 ============ */
.ga-custom-btn {
  margin-bottom: 12px;
  border-style: dashed;
}
.ga-custom {
  background: linear-gradient(135deg, #f6f9ff, #eef4ff);
  border: 1px solid #c9d8f8;
  border-radius: 14px;
  padding: 14px;
  margin-bottom: 14px;
}
.ga-cust-title {
  font-weight: 700;
  color: #1b2a4a;
  font-size: 14px;
  margin-bottom: 10px;
}
.ga-cust-main {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  flex-wrap: wrap;
}
.ga-upload {
  width: 120px;
  height: 90px;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  display: block;
  flex-shrink: 0;
  background: #fff;
  border: 2px dashed #b8cdf0;
}
.ga-upload input {
  display: none;
}
.ga-upload img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.ga-upload-ph {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  font-size: 12px;
  color: #5b7bbf;
  gap: 4px;
  text-align: center;
}
.ga-upload-rm {
  margin: 6px 0 0 132px;
  padding: 4px 10px;
  font-size: 12px;
}
.ga-cust-form {
  flex: 1;
  min-width: 240px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}
.ga-cust-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.ga-cust-field > span {
  font-size: 12px;
  color: #5b7290;
}
.ga-cust-field .input {
  padding: 6px 8px;
  font-size: 13px;
}
.ga-cust-msg {
  margin-top: 8px;
  color: #d05050;
  font-size: 12px;
}
.ga-cust-actions {
  margin-top: 10px;
  display: flex;
  gap: 10px;
}
.ga-custom-badge {
  position: absolute;
  left: 4px;
  top: 4px;
  background: rgba(58, 122, 254, 0.92);
  color: #fff;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 6px;
}
.ga-pic {
  position: relative;
}

/* ============ 公路赛车 ============ */
.race-panel .race-wrap {
  position: relative;
  max-width: 520px;
  margin: 0 auto;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.race-paint-sel-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #475569;
  font-weight: 700;
  margin-bottom: 10px;
}

.race-canvas {
  display: block;
  width: 100%;
  height: auto;
  background: #0b1026;
}
.race-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: rgba(8, 12, 30, 0.82);
  backdrop-filter: blur(4px);
  color: #fff;
  text-align: center;
  padding: 20px;
}
.race-logo {
  font-size: 34px;
}
.race-title {
  font-size: 21px;
  font-weight: 800;
  background: linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.race-tip {
  font-size: 12px;
  color: #a8b7d8;
}
.race-btn {
  margin-top: 4px;
  padding: 8px 26px;
  font-size: 14px;
}
.race-best {
  font-size: 13px;
  color: #ffd166;
}
.race-newbest {
  font-size: 14px;
  color: #4ade80;
  font-weight: 700;
}
.race-score {
  font-size: 18px;
  color: #e2e8f0;
}
.race-score b {
  font-size: 26px;
  color: #60a5fa;
}
.race-hud {
  position: absolute;
  top: 12px;
  left: 12px;
  right: 12px;
  display: flex;
  justify-content: space-between;
  pointer-events: none;
}
.race-hud-item {
  background: rgba(10, 15, 40, 0.72);
  border: 1px solid rgba(96, 165, 250, 0.4);
  color: #dbeafe;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 700;
  backdrop-filter: blur(3px);
}
.race-key-hint {
  text-align: center;
  margin-top: 6px;
  color: #8296b5;
  font-size: 12px;
}
</style>
