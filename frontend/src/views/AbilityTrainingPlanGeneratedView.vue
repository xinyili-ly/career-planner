<template>
  <div class="plan-generated-view" :class="theme">
    <AppHeader />

    <main class="page-scroll">
      <section class="panel">
        <header class="top-head">
          <div>
            <h1 class="page-title">能力培训计划（生成结果）</h1>
            <p class="page-intro">
              这里展示三个月（约 12 周）的训练甘特图、短期 To Do List（12 周）与长期 To Do List（三个月）。
            </p>
          </div>
          <div class="top-actions">
            <el-button class="u-btn u-btn--ghost" @click="goGuide">返回指引页</el-button>
            <el-button class="u-btn u-btn--primary" type="primary" @click="copyAll">复制全部（文本）</el-button>
          </div>
        </header>

        <section class="block">
          <div class="block-head">
            <h2 class="section-title">三个月计划甘特图（12 周）</h2>
            <div class="legend">
              <span class="pill mint">基础</span>
              <span class="pill purple">项目</span>
              <span class="pill yellow">求职</span>
              <span class="pill pink">复盘</span>
            </div>
          </div>

          <div class="gantt">
            <div class="gantt-head">
              <div class="corner"></div>
              <div v-for="w in weeks" :key="w" class="week">W{{ w }}</div>
            </div>

            <div v-for="row in ganttRows" :key="row.label" class="gantt-row">
              <div class="row-label">{{ row.label }}</div>
              <div class="row-grid">
                <div
                  v-for="(bar, idx) in row.bars"
                  :key="idx"
                  class="bar"
                  :class="bar.tone"
                  :style="barStyle(bar)"
                >
                  {{ bar.title }}
                </div>
              </div>
            </div>
          </div>
        </section>

        <section class="block">
          <div class="todo-head">
            <div>
              <h2 class="section-title">短期 To Do（12 周）</h2>
              <p class="section-desc">支持添加、删除、编辑、完成勾选；数据自动本地保存。</p>
            </div>
            <div class="todo-metrics">
              <span class="metric">剩余：<b>{{ remainingShort }}</b></span>
              <span class="metric">完成：<b>{{ completedShort }}</b>/<b>{{ totalShort }}</b></span>
              <el-button class="u-btn u-btn--primary u-btn--sm" size="small" @click="addTask('short')">添加任务</el-button>
            </div>
          </div>

          <div class="todo-list">
            <div v-for="t in shortTasks" :key="t.id" class="todo-item" :class="{ done: t.completed }">
              <label class="todo-check">
                <input type="checkbox" v-model="t.completed" @change="handleShortToggle(t)" />
                <span class="check-ui"></span>
              </label>

              <div class="todo-body">
                <div v-if="editingId !== t.id" class="todo-title" @dblclick="startEdit(t)">
                  {{ t.title }}
                </div>
                <div v-else class="todo-edit">
                  <el-input
                    v-model="editingTitle"
                    size="small"
                    @keydown.enter="commitEdit(t)"
                    @keydown.esc="cancelEdit"
                    placeholder="编辑任务内容"
                  />
                  <div class="todo-edit-actions">
                    <el-button class="u-btn u-btn--primary u-btn--sm" size="small" type="primary" @click="commitEdit(t)">保存</el-button>
                    <el-button class="u-btn u-btn--ghost u-btn--sm" size="small" @click="cancelEdit">取消</el-button>
                  </div>
                </div>
                <div class="todo-meta">
                  <span v-if="t.week" class="todo-tag">W{{ t.week }}</span>
                  <span v-if="t.tag" class="todo-dim">{{ t.tag }}</span>
                </div>
              </div>

              <div class="todo-actions">
                <el-button class="u-btn u-btn--text" size="small" text @click="startEdit(t)">编辑</el-button>
                <el-button class="u-btn u-btn--text" size="small" text type="danger" @click="removeTask('short', t.id)">删除</el-button>
              </div>
            </div>
          </div>
        </section>

        <section class="block">
          <div class="todo-head">
            <div>
              <h2 class="section-title">长期 To Do（三个月）</h2>
              <p class="section-desc">按 Month 1-3 组织，支持基础 Todo 功能；数据自动本地保存。</p>
            </div>
            <div class="todo-metrics">
              <span class="metric">剩余：<b>{{ remainingLong }}</b></span>
              <span class="metric">完成：<b>{{ completedLong }}</b>/<b>{{ totalLong }}</b></span>
              <el-button class="u-btn u-btn--primary u-btn--sm" size="small" @click="addTask('long')">添加任务</el-button>
            </div>
          </div>

          <div class="todo-groups">
            <section v-for="g in longGroups" :key="g.key" class="todo-group">
              <header class="todo-group-head">
                <h3 class="todo-group-title">{{ g.title }}</h3>
                <span class="todo-group-count">{{ groupRemaining(g.key) }} 未完成 / {{ groupTotal(g.key) }} 总计</span>
              </header>

              <div class="todo-list">
                <div v-for="t in longTasks[g.key]" :key="t.id" class="todo-item" :class="{ done: t.completed }">
                  <label class="todo-check">
                    <input type="checkbox" v-model="t.completed" @change="handleLongToggle(g.key, t)" />
                    <span class="check-ui"></span>
                  </label>

                  <div class="todo-body">
                    <div v-if="editingId !== t.id" class="todo-title" @dblclick="startEdit(t)">
                      {{ t.title }}
                    </div>
                    <div v-else class="todo-edit">
                      <el-input
                        v-model="editingTitle"
                        size="small"
                        @keydown.enter="commitEdit(t)"
                        @keydown.esc="cancelEdit"
                        placeholder="编辑任务内容"
                      />
                      <div class="todo-edit-actions">
                        <el-button class="u-btn u-btn--primary u-btn--sm" size="small" type="primary" @click="commitEdit(t)">保存</el-button>
                        <el-button class="u-btn u-btn--ghost u-btn--sm" size="small" @click="cancelEdit">取消</el-button>
                      </div>
                    </div>
                    <div class="todo-meta">
                      <span class="todo-tag">{{ g.title }}</span>
                    </div>
                  </div>

                  <div class="todo-actions">
                    <el-button class="u-btn u-btn--text" size="small" text @click="startEdit(t)">编辑</el-button>
                    <el-button class="u-btn u-btn--text" size="small" text type="danger" @click="removeTask(g.key, t.id)">删除</el-button>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </section>

        <footer class="site-footer">
          <span>© {{ new Date().getFullYear() }} 职途智引 · AI职业规划助手</span>
        </footer>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useTheme } from '../composables/useTheme'
import AppHeader from '../components/AppHeader.vue'
import {
  getCurrentActionPlan,
  isCareerAgentApiEnabled,
  readLastMatchResult,
  updateActionPlanItemStatus,
} from '../api/careerAgentApi'

const { theme } = useTheme()
const router = useRouter()

const weeks = Array.from({ length: 12 }, (_, i) => i + 1)

const ganttRows = ref([
  {
    label: '基础能力补齐',
    bars: [
      { title: '算法/计网/OS/数据库梳理', start: 1, end: 4, tone: 'mint' },
      { title: '高频专题强化 + 题单', start: 5, end: 8, tone: 'mint' },
      { title: '面试高频点回炉', start: 9, end: 12, tone: 'pink' },
    ],
  },
  {
    label: '项目与作品集',
    bars: [
      { title: 'MVP 选型与需求拆解', start: 1, end: 2, tone: 'purple' },
      { title: '核心功能开发 + 文档', start: 3, end: 7, tone: 'purple' },
      { title: '上线部署 + 作品集包装', start: 8, end: 12, tone: 'yellow' },
    ],
  },
  {
    label: '求职与表达',
    bars: [
      { title: '项目讲解脚本（STAR）', start: 1, end: 3, tone: 'pink' },
      { title: '模拟面试（技术/项目）', start: 4, end: 9, tone: 'yellow' },
      { title: '投递-复盘-迭代闭环', start: 6, end: 12, tone: 'yellow' },
    ],
  },
])

const STORAGE_KEY = 'career_planner_training_plan_generated_v1'
const PLAN_PROGRESS_STORAGE_KEY = 'career_planner_training_plan_progress_v1'
const STUDENT_ID_KEY = 'career_planner_student_id_v1'
const DEFAULT_PLAN_JOB_TITLE = '职业规划'

const shortTasks = ref([])
const longTasks = ref({
  m1: [],
  m2: [],
  m3: [],
})

const longGroups = [
  { key: 'm1', title: 'Month 1' },
  { key: 'm2', title: 'Month 2' },
  { key: 'm3', title: 'Month 3' },
]

const editingId = ref('')
const editingTitle = ref('')
const activePlanJobTitle = ref(DEFAULT_PLAN_JOB_TITLE)

const uid = () => `${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 9)}`
let taskOrderSeed = 0
const nextTaskOrder = () => {
  taskOrderSeed += 1
  return taskOrderSeed
}

const getStudentId = () => {
  try {
    return sessionStorage.getItem(STUDENT_ID_KEY) || 'student_demo_001'
  } catch {
    return 'student_demo_001'
  }
}

const normalizeJobTitle = (value) => {
  const s = String(value || '').trim()
  return s || DEFAULT_PLAN_JOB_TITLE
}

const resolveActivePlanJobTitle = () => {
  const payload = readLastMatchResult()
  if (!payload || typeof payload !== 'object') return DEFAULT_PLAN_JOB_TITLE
  const title =
    payload?.job_info?.title ||
    payload?.summary?.target_job?.title ||
    payload?.target_position ||
    payload?.job_title ||
    payload?.title ||
    ''
  return normalizeJobTitle(title)
}

const toNumberOrUndefined = (value) => {
  const n = Number(value)
  return Number.isFinite(n) ? n : undefined
}

const inferWeek = (item) => {
  const direct = toNumberOrUndefined(item?.week ?? item?.week_no ?? item?.weekNo)
  if (direct && direct >= 1 && direct <= 12) return direct
  const text = String(item?.period ?? item?.timeline ?? item?.title ?? '')
  const match = text.match(/W\s*(\d{1,2})/i)
  if (!match) return undefined
  const n = Number(match[1])
  return n >= 1 && n <= 12 ? n : undefined
}

const inferMonthKey = (item) => {
  const raw = String(item?.month ?? item?.phase ?? item?.group ?? '').toLowerCase()
  if (raw.includes('m2') || raw.includes('month 2') || raw.includes('month2')) return 'm2'
  if (raw.includes('m3') || raw.includes('month 3') || raw.includes('month3')) return 'm3'
  if (raw.includes('m1') || raw.includes('month 1') || raw.includes('month1')) return 'm1'
  const w = inferWeek(item)
  if (typeof w === 'number') {
    if (w <= 4) return 'm1'
    if (w <= 8) return 'm2'
    return 'm3'
  }
  return 'm1'
}

const mapApiItemToTask = (item) => {
  const title =
    item?.title ||
    item?.task_name ||
    item?.task ||
    item?.name ||
    item?.content ||
    item?.description
  if (!title) return null
  const status = String(item?.status || '').toLowerCase()
  return {
    id: String(item?.id || item?.item_id || uid()),
    title: String(title),
    completed: status === 'completed' || status === 'done',
    week: inferWeek(item),
    tag: item?.tag || item?.dimension || item?.category || item?.type || '',
    order: nextTaskOrder(),
    itemId: String(item?.id || item?.item_id || ''),
  }
}

const extractActionItems = (plan) => {
  if (!plan || typeof plan !== 'object') return []
  if (Array.isArray(plan.items)) return plan.items
  if (Array.isArray(plan.action_items)) return plan.action_items
  if (Array.isArray(plan.todo_items)) return plan.todo_items
  if (Array.isArray(plan.tasks)) return plan.tasks
  if (plan.grouped_items && typeof plan.grouped_items === 'object') {
    return Object.values(plan.grouped_items).flatMap((x) => (Array.isArray(x) ? x : []))
  }
  return []
}

const tryApplyGanttWeeks = (source) => {
  const weeksPayload = Array.isArray(source?.weeks) ? source.weeks : []
  if (!weeksPayload.length) return false
  const mapped = weeksPayload
    .map((row, idx) => {
      const bars = Array.isArray(row?.tasks)
        ? row.tasks
            .map((task) => {
              const start = Number(task?.start_week ?? task?.start ?? task?.week ?? 1)
              const end = Number(task?.end_week ?? task?.end ?? start)
              const title = String(task?.title || task?.task_name || task?.name || '').trim()
              if (!title) return null
              return {
                title,
                start: Number.isFinite(start) ? Math.max(1, Math.min(12, start)) : 1,
                end: Number.isFinite(end) ? Math.max(1, Math.min(12, end)) : 1,
                tone: 'mint',
              }
            })
            .filter(Boolean)
        : []
      return {
        label: String(row?.phase_name || row?.label || `阶段 ${idx + 1}`),
        bars,
      }
    })
    .filter((x) => x.bars.length)
  if (!mapped.length) return false
  ganttRows.value = mapped
  return true
}

const tryApplyPlanFromLastMatch = () => {
  const payload = readLastMatchResult()
  if (!payload || typeof payload !== 'object') return false
  const planSource = payload.action_plan || payload.plan || payload
  const hasPlan = applyPlanFromApi(planSource)
  const hasWeeks = tryApplyGanttWeeks(planSource)
  return hasPlan || hasWeeks
}

const applyPlanFromApi = (plan) => {
  const items = extractActionItems(plan)
  if (!items.length) return false
  const mapped = items.map(mapApiItemToTask).filter(Boolean)
  if (!mapped.length) return false

  const nextShort = []
  const nextLong = { m1: [], m2: [], m3: [] }

  for (const task of mapped) {
    if (typeof task.week === 'number' && task.week >= 1 && task.week <= 12) {
      nextShort.push(task)
    } else {
      nextLong[inferMonthKey(task)].push(task)
    }
  }

  if (!nextShort.length && mapped.length) {
    // 后端未给 week 时，先全部放短期，避免页面空白
    nextShort.push(...mapped)
  }

  shortTasks.value = reorderByCompletionAndTime(nextShort)
  longTasks.value = {
    m1: reorderByCompletionAndTime(nextLong.m1),
    m2: reorderByCompletionAndTime(nextLong.m2),
    m3: reorderByCompletionAndTime(nextLong.m3),
  }
  return true
}

const totalShort = computed(() => shortTasks.value.length)
const completedShort = computed(() => shortTasks.value.filter((x) => x.completed).length)
const remainingShort = computed(() => Math.max(0, totalShort.value - completedShort.value))

const totalLong = computed(() => Object.values(longTasks.value).reduce((s, list) => s + (list?.length || 0), 0))
const completedLong = computed(() =>
  Object.values(longTasks.value).reduce((s, list) => s + (list?.filter((t) => t.completed).length || 0), 0)
)
const remainingLong = computed(() => Math.max(0, totalLong.value - completedLong.value))

const groupTotal = (key) => longTasks.value[key]?.length || 0
const groupRemaining = (key) => (longTasks.value[key]?.filter((t) => !t.completed).length || 0)

const barStyle = (bar) => {
  const start = Math.max(1, Math.min(12, Number(bar.start || 1)))
  const end = Math.max(start, Math.min(12, Number(bar.end || start)))
  return { gridColumn: `${start} / ${end + 1}` }
}

function persist() {
  try {
    const total = totalShort.value + totalLong.value
    const completed = completedShort.value + completedLong.value
    const percentage = total > 0 ? Math.round((completed / total) * 100) : 0
    const currentJobTitle = normalizeJobTitle(activePlanJobTitle.value)
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        shortTasks: shortTasks.value,
        longTasks: longTasks.value,
        savedAt: Date.now(),
      })
    )
    let existingProgress = {}
    try {
      existingProgress = JSON.parse(localStorage.getItem(PLAN_PROGRESS_STORAGE_KEY) || '{}') || {}
    } catch {
      existingProgress = {}
    }
    const byJob = existingProgress && typeof existingProgress.byJob === 'object' ? existingProgress.byJob : {}
    byJob[currentJobTitle] = {
      jobTitle: currentJobTitle,
      total,
      completed,
      percentage,
      remaining: Math.max(0, total - completed),
      savedAt: Date.now(),
    }
    localStorage.setItem(
      PLAN_PROGRESS_STORAGE_KEY,
      JSON.stringify({
        total,
        completed,
        percentage,
        remaining: Math.max(0, total - completed),
        jobTitle: currentJobTitle,
        byJob,
        savedAt: Date.now(),
      })
    )
  } catch {
    // ignore
  }
}

function compareByTime(a, b) {
  const wa = Number.isFinite(Number(a?.week)) ? Number(a.week) : Number.POSITIVE_INFINITY
  const wb = Number.isFinite(Number(b?.week)) ? Number(b.week) : Number.POSITIVE_INFINITY
  if (wa !== wb) return wa - wb
  const oa = Number.isFinite(Number(a?.order)) ? Number(a.order) : Number.POSITIVE_INFINITY
  const ob = Number.isFinite(Number(b?.order)) ? Number(b.order) : Number.POSITIVE_INFINITY
  return oa - ob
}

function reorderByCompletionAndTime(list = []) {
  const pending = list.filter((item) => !item.completed).sort(compareByTime)
  const done = list.filter((item) => item.completed).sort(compareByTime)
  return [...pending, ...done]
}

function ensureTaskOrders() {
  const all = [
    ...shortTasks.value,
    ...longTasks.value.m1,
    ...longTasks.value.m2,
    ...longTasks.value.m3,
  ]
  const maxOrder = all.reduce((max, task) => {
    const val = Number(task?.order)
    return Number.isFinite(val) ? Math.max(max, val) : max
  }, 0)
  taskOrderSeed = maxOrder
  for (const task of all) {
    const val = Number(task?.order)
    if (!Number.isFinite(val)) {
      task.order = nextTaskOrder()
    }
  }
}

function normalizeAllTaskOrders() {
  shortTasks.value = reorderByCompletionAndTime(shortTasks.value)
  for (const group of longGroups) {
    longTasks.value[group.key] = reorderByCompletionAndTime(longTasks.value[group.key] || [])
  }
}

async function syncItemStatus(task) {
  if (!isCareerAgentApiEnabled()) return
  if (!task?.itemId) return
  try {
    await updateActionPlanItemStatus(task.itemId, {
      student_id: getStudentId(),
      status: task.completed ? 'completed' : 'pending',
    })
  } catch (e) {
    console.warn('[career-agent] action-plan/items/update', e)
  }
}

async function handleShortToggle(task) {
  shortTasks.value = reorderByCompletionAndTime(shortTasks.value)
  await syncItemStatus(task)
  persist()
}

async function handleLongToggle(groupKey, task) {
  longTasks.value[groupKey] = reorderByCompletionAndTime(longTasks.value[groupKey] || [])
  await syncItemStatus(task)
  persist()
}

function seedIfEmpty() {
  if (shortTasks.value.length || totalLong.value) return

  shortTasks.value = [
    { id: uid(), title: '完成能力画像构建并确认目标岗位', completed: false, week: 1, tag: '起步', order: nextTaskOrder() },
    { id: uid(), title: '基础四件套复盘：本周输出 1 份知识图谱', completed: false, week: 1, tag: '基础', order: nextTaskOrder() },
    { id: uid(), title: '确定项目选题与里程碑，输出 MVP 需求清单', completed: false, week: 2, tag: '项目', order: nextTaskOrder() },
    { id: uid(), title: '完成 1 次模拟面试并记录复盘', completed: false, week: 3, tag: '求职', order: nextTaskOrder() },
    { id: uid(), title: '把项目亮点写进简历，补齐 3 条量化成果', completed: false, week: 4, tag: '表达', order: nextTaskOrder() },
    { id: uid(), title: '每周至少 2 次题单训练（算法/SQL/八股）', completed: false, week: 5, tag: '基础', order: nextTaskOrder() },
    { id: uid(), title: '完成核心功能开发并写好 README/接口文档', completed: false, week: 6, tag: '项目', order: nextTaskOrder() },
    { id: uid(), title: '把项目上线部署，能在线演示', completed: false, week: 8, tag: '项目', order: nextTaskOrder() },
    { id: uid(), title: '开始投递并维护投递看板（反馈-原因-改进）', completed: false, week: 9, tag: '求职', order: nextTaskOrder() },
    { id: uid(), title: '整理面试高频问题清单 + 标准回答', completed: false, week: 10, tag: '求职', order: nextTaskOrder() },
    { id: uid(), title: '完成 1 次项目复盘（取舍/权衡/风险）并更新文档', completed: false, week: 11, tag: '复盘', order: nextTaskOrder() },
    { id: uid(), title: '最终迭代简历与作品集，准备终面级讲解', completed: false, week: 12, tag: '收官', order: nextTaskOrder() },
  ]

  longTasks.value = {
    m1: [
      { id: uid(), title: '交付 1 个可演示的 MVP 项目（含文档/部署）', completed: false, order: nextTaskOrder() },
      { id: uid(), title: '形成稳定的自我介绍与项目讲解脚本（STAR）', completed: false, order: nextTaskOrder() },
    ],
    m2: [
      { id: uid(), title: '补齐量化成果与技术证据链，能被追问解释', completed: false, order: nextTaskOrder() },
      { id: uid(), title: '完成 3-5 次模拟面试并迭代简历/表达', completed: false, order: nextTaskOrder() },
    ],
    m3: [
      { id: uid(), title: '建立投递-复盘-迭代闭环，稳定获得面试机会', completed: false, order: nextTaskOrder() },
      { id: uid(), title: '完成作品集打磨与岗位针对性优化，提升通过率', completed: false, order: nextTaskOrder() },
    ],
  }

  normalizeAllTaskOrders()
  persist()
}

function tryLoad() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return false
    const payload = JSON.parse(raw)
    if (!payload) return false
    if (Array.isArray(payload.shortTasks)) {
      shortTasks.value = payload.shortTasks.map((task) => ({
        ...task,
        completed: Boolean(task?.completed),
      }))
    }
    if (payload.longTasks && typeof payload.longTasks === 'object') {
      longTasks.value = {
        m1: Array.isArray(payload.longTasks.m1)
          ? payload.longTasks.m1.map((task) => ({ ...task, completed: Boolean(task?.completed) }))
          : [],
        m2: Array.isArray(payload.longTasks.m2)
          ? payload.longTasks.m2.map((task) => ({ ...task, completed: Boolean(task?.completed) }))
          : [],
        m3: Array.isArray(payload.longTasks.m3)
          ? payload.longTasks.m3.map((task) => ({ ...task, completed: Boolean(task?.completed) }))
          : [],
      }
    }
    return true
  } catch {
    return false
  }
}

function addTask(scope) {
  const title = window.prompt('请输入新任务')
  const trimmed = (title || '').trim()
  if (!trimmed) return

  if (scope === 'short') {
    const week = Number(window.prompt('该任务属于第几周？(1-12，可留空)') || '')
    shortTasks.value = [
      ...shortTasks.value,
      { id: uid(), title: trimmed, completed: false, week: Number.isFinite(week) && week >= 1 && week <= 12 ? week : undefined, tag: '手动添加', order: nextTaskOrder() },
    ]
    shortTasks.value = reorderByCompletionAndTime(shortTasks.value)
  } else {
    const monthKey = window.prompt('添加到哪个月份？输入 m1 / m2 / m3', 'm1')
    const key = monthKey === 'm2' || monthKey === 'm3' ? monthKey : 'm1'
    longTasks.value[key] = reorderByCompletionAndTime([
      ...(longTasks.value[key] || []),
      { id: uid(), title: trimmed, completed: false, order: nextTaskOrder() },
    ])
  }

  persist()
}

function removeTask(scopeOrGroupKey, id) {
  if (scopeOrGroupKey === 'short') {
    shortTasks.value = shortTasks.value.filter((t) => t.id !== id)
  } else {
    longTasks.value[scopeOrGroupKey] = (longTasks.value[scopeOrGroupKey] || []).filter((t) => t.id !== id)
  }
  if (editingId.value === id) cancelEdit()
  persist()
}

function startEdit(task) {
  editingId.value = task.id
  editingTitle.value = task.title
}

function cancelEdit() {
  editingId.value = ''
  editingTitle.value = ''
}

function commitEdit(task) {
  const next = (editingTitle.value || '').trim()
  if (!next) {
    ElMessage.warning('任务内容不能为空')
    return
  }
  task.title = next
  cancelEdit()
  persist()
}

function goGuide() {
  router.push('/ability-training-plan')
}

async function copyAll() {
  const lines = []
  lines.push('能力培训计划（三个月 / 12 周）')
  lines.push('')
  lines.push('短期 To Do（12 周）：')
  for (const t of shortTasks.value) lines.push(`- [${t.completed ? 'x' : ' '}] ${t.week ? `W${t.week} ` : ''}${t.title}`)
  lines.push('')
  lines.push('长期 To Do（三个月）：')
  for (const g of longGroups) {
    lines.push(`${g.title}：`)
    for (const t of longTasks.value[g.key] || []) lines.push(`- [${t.completed ? 'x' : ' '}] ${t.title}`)
  }

  try {
    await navigator.clipboard.writeText(lines.join('\n'))
    ElMessage.success('已复制全部内容')
  } catch {
    ElMessage.warning('复制失败，请手动复制页面内容')
  }
}

onMounted(async () => {
  activePlanJobTitle.value = resolveActivePlanJobTitle()
  let loadedFromApi = false
  const loadedFromLastMatch = tryApplyPlanFromLastMatch()
  if (isCareerAgentApiEnabled()) {
    try {
      const data = await getCurrentActionPlan(getStudentId())
      loadedFromApi = applyPlanFromApi(data)
    } catch (e) {
      console.warn('[career-agent] action-plan/current', e)
    }
  }

  if (!loadedFromApi && !loadedFromLastMatch) {
    const loaded = tryLoad()
    if (!loaded) seedIfEmpty()
  }
  ensureTaskOrders()
  normalizeAllTaskOrders()
  persist()
})
</script>

<style scoped>
.plan-generated-view {
  --u-border-radius: 12px;
  width: 100vw;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--u-body-bg);
  color: var(--u-black);
  font-family: var(--font-family-sans);
}

.plan-generated-view.dark {
  background: var(--dm-bg);
  color: var(--dm-text);
}

.page-scroll {
  padding: 28px 6vw 56px 64px;
  flex: 1;
  box-sizing: border-box;
}

.panel {
  /* 背景统一为主界面同款纯蓝：不使用波点/渐变 */
  background: var(--u-body-bg);
  border-radius: 18px;
  padding: 22px 22px 24px;
  box-shadow: none;
}

.plan-generated-view.dark .panel {
  background: var(--dm-gradient-card);
  border: 1px solid var(--dm-border);
  box-shadow: none;
}

.top-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.top-actions {
  display: inline-flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.page-title {
  font-size: clamp(28px, 2.2vw, 38px);
  margin: 0 0 10px;
}

.page-intro {
  font-size: clamp(16px, 1.05vw, 18px);
  line-height: 1.65;
  color: #444;
  max-width: 920px;
  margin: 0;
}

.plan-generated-view.dark .page-intro {
  color: var(--dm-text-secondary);
}

.block {
  margin-top: 16px;
}

.section-title {
  margin: 0;
  font-size: clamp(16px, 1.05vw, 18px);
  font-weight: 600;
  line-height: 1.35;
}

.section-desc {
  margin: 6px 0 0;
  font-size: clamp(14px, 0.95vw, 16px);
  color: #555;
  line-height: 1.5;
}

.plan-generated-view.dark .section-desc {
  color: var(--dm-text-secondary);
}

.block-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.legend {
  display: inline-flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.pill {
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  border: 1px solid rgba(15, 23, 42, 0.06);
  background: rgba(255, 255, 255, 0.9);
}

.plan-generated-view.dark .pill {
  background: rgba(255, 255, 255, 0.06);
  border-color: var(--dm-border);
}

/* 参考 Uiineed Todo List 的柔和配色（近似） */
.mint {
  color: var(--u-mint);
}
.purple {
  color: var(--u-purple);
}
.yellow {
  color: var(--u-yellow);
}
.pink {
  color: var(--u-pink);
}

.gantt {
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(249, 243, 229, 0.82), rgba(232, 246, 255, 0.62));
  border: 1px solid rgba(51, 50, 46, 0.16);
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
  overflow: hidden;
}

.plan-generated-view.dark .gantt {
  background: rgba(255, 255, 255, 0.04);
  border-color: var(--dm-border);
  box-shadow: none;
}

.gantt-head {
  display: grid;
  grid-template-columns: 160px repeat(12, 1fr);
  align-items: center;
  background: rgba(232, 246, 255, 0.58);
  border-bottom: 1px solid rgba(148, 163, 184, 0.18);
}

.plan-generated-view.dark .gantt-head {
  background: var(--dm-surface-elevated);
  border-bottom-color: var(--dm-border);
}

.corner {
  height: 52px;
}

.week {
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  color: #1f2937;
  font-size: 12px;
}

.plan-generated-view.dark .week {
  color: var(--dm-text);
}

.gantt-row {
  display: grid;
  grid-template-columns: 160px 1fr;
  min-height: 78px;
  border-bottom: 1px dashed rgba(148, 163, 184, 0.2);
}

.gantt-row:last-child {
  border-bottom: none;
}

.row-label {
  padding: 14px 12px;
  font-weight: 700;
  background: rgba(249, 243, 229, 0.7);
  color: #334155;
  display: flex;
  align-items: center;
  border-right: 1px solid rgba(148, 163, 184, 0.18);
}

.plan-generated-view.dark .row-label {
  background: var(--dm-surface);
  color: var(--dm-text);
}

.row-grid {
  position: relative;
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  align-items: center;
  padding: 12px 14px;
  gap: 10px;
}

.bar {
  border-radius: 12px;
  padding: 10px 12px;
  color: var(--u-black);
  font-size: 13px;
  line-height: 1.25;
  box-shadow: 0 3px 8px rgba(15, 23, 42, 0.08);
  border: 1px solid rgba(51, 50, 46, 0.16);
}

.plan-generated-view.dark .bar {
  background: rgba(255, 255, 255, 0.06);
  color: var(--dm-text);
  border-color: rgba(255, 255, 255, 0.16);
  box-shadow: none;
}

.bar.mint {
  /* 绿色系：完成态薄荷绿 */
  background: linear-gradient(90deg, var(--u-bg-completed), var(--u-fade-completed));
}
.bar.purple {
  /* 蓝色系：使用 Uiineed 的 body-bg 蓝 */
  background: linear-gradient(90deg, var(--u-body-bg), var(--u-fade-body));
}
.bar.yellow {
  /* 黄色系：normal 纸张黄 */
  /* 移除偏黄底色：改用更中性的“页面底”柔和渐变 */
  background: linear-gradient(90deg, var(--u-body-bg), var(--u-fade-body));
}
.bar.pink {
  /* 粉色系：submit 粉 */
  background: linear-gradient(90deg, var(--u-bg-submit), var(--u-fade-submit));
}

.todo-head {
  margin-top: 6px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.todo-metrics {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px;
  border-radius: 999px;
  background: var(--u-bg-submit);
  border: var(--u-border);
  box-shadow: var(--u-box-shadow);
  flex-wrap: wrap;
  justify-content: flex-end;
}

.plan-generated-view.dark .todo-metrics {
  background: rgba(255, 255, 255, 0.06);
}

.metric {
  font-size: 13px;
  color: #475569;
}

.plan-generated-view.dark .metric {
  color: var(--dm-text-secondary);
}

.todo-groups {
  margin-top: 12px;
  display: grid;
  gap: 12px;
}

.todo-group {
  border-radius: var(--u-border-radius);
  padding: 14px 14px 12px;
  background: rgba(255, 255, 255, 0.7);
  border: var(--u-border);
  box-shadow: var(--u-box-shadow);
}

.plan-generated-view.dark .todo-group {
  background: var(--dm-surface-elevated);
  border-color: var(--dm-border);
}

.todo-group-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.todo-group-title {
  margin: 0;
  font-size: 18px;
}

.todo-group-count {
  font-size: 13px;
  color: #64748b;
}

.plan-generated-view.dark .todo-group-count {
  color: var(--dm-text-muted);
}

.todo-list {
  margin-top: 12px;
  display: grid;
  gap: 8px;
}

.todo-item {
  display: grid;
  grid-template-columns: 28px 1fr auto;
  gap: 10px;
  align-items: start;
  padding: 10px 10px;
  border-radius: var(--u-border-radius);
  /* 移除偏黄默认底色：改用更中性的页面底 */
  background: var(--u-body-bg);
  border: var(--u-border);
  box-shadow: var(--u-box-shadow);
}

/* Uiineed 风格混搭：未完成任务交替使用不同底色，避免“全黄”单调 */
.todo-list .todo-item:not(.done):nth-child(4n + 2) {
  background: var(--u-bg-edit);
}

.todo-list .todo-item:not(.done):nth-child(4n + 3) {
  background: var(--u-bg-submit);
}

.todo-list .todo-item:not(.done):nth-child(4n) {
  background: var(--u-bg-discard);
}

/* 加一点 Uiineed 的淡蓝（body-bg）参与混搭 */
.todo-list .todo-item:not(.done):nth-child(6n + 1) {
  background: var(--u-body-bg);
}

.plan-generated-view.dark .todo-item {
  background: var(--dm-surface-card);
  border-color: var(--dm-border);
}

.todo-item.done {
  background: color-mix(in srgb, var(--u-bg-completed) 78%, #8aa8a2);
}

.plan-generated-view.dark .todo-item.done {
  background: color-mix(in srgb, var(--u-bg-completed) 52%, var(--dm-bg));
}

.todo-check {
  position: relative;
  width: 22px;
  height: 22px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.todo-check input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.check-ui {
  width: 18px;
  height: 18px;
  border-radius: 6px;
  border: var(--u-border);
  display: inline-block;
  box-sizing: border-box;
  background: #fff;
}

.todo-check input:checked + .check-ui {
  background: var(--u-completed);
}

.todo-body {
  min-width: 0;
}

.todo-title {
  font-size: 16px;
  line-height: 1.5;
  word-break: break-word;
}

.todo-item.done .todo-title {
  text-decoration: line-through;
  color: var(--u-placeholder);
}

.plan-generated-view.dark .todo-item.done .todo-title {
  color: var(--dm-text-muted);
}

.todo-meta {
  margin-top: 6px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.todo-tag,
.todo-dim {
  font-size: 13px;
  padding: 2px 8px;
  border-radius: 999px;
  border: var(--u-border);
}

.todo-tag {
  /* 移除偏黄标签底色（短期 W 标签） */
  background: var(--u-bg-muted);
  color: var(--u-black);
}

.todo-dim {
  background: var(--u-body-bg);
  color: var(--u-black);
}

/* 长期计划的 Month 标签用完成态薄荷绿，短期周标签保持 normal 黄 */
.todo-group .todo-tag {
  background: var(--u-bg-completed);
}

.plan-generated-view.dark .todo-tag,
.plan-generated-view.dark .todo-dim {
  background: rgba(255, 255, 255, 0.06);
  color: var(--dm-text);
  border-color: var(--dm-border);
}

.todo-actions {
  display: inline-flex;
  gap: 6px;
  align-items: center;
}

.todo-edit-actions {
  margin-top: 8px;
  display: flex;
  gap: 8px;
}

.site-footer {
  margin-top: 16px;
  padding-top: 24px;
  border-top: 1px solid rgba(148, 163, 184, 0.35);
  font-size: clamp(14px, 0.9vw, 16px);
  color: #94a3b8;
  text-align: center;
  width: 100%;
}

.plan-generated-view.dark .site-footer {
  border-top-color: var(--dm-border);
  color: var(--dm-text-muted);
}

@media (max-width: 900px) {
  .page-scroll {
    padding-inline: 16px;
  }
  .gantt-head {
    grid-template-columns: 120px repeat(12, 1fr);
  }
  .gantt-row {
    grid-template-columns: 120px 1fr;
  }
}
</style>

