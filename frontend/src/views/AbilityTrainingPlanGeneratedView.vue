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
                <input type="checkbox" v-model="t.completed" @change="persist" />
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
                    <input type="checkbox" v-model="t.completed" @change="persist" />
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

const uid = () => `${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 9)}`

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
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        shortTasks: shortTasks.value,
        longTasks: longTasks.value,
        savedAt: Date.now(),
      })
    )
  } catch {
    // ignore
  }
}

function seedIfEmpty() {
  if (shortTasks.value.length || totalLong.value) return

  shortTasks.value = [
    { id: uid(), title: '完成能力画像构建并确认目标岗位', completed: false, week: 1, tag: '起步' },
    { id: uid(), title: '基础四件套复盘：本周输出 1 份知识图谱', completed: false, week: 1, tag: '基础' },
    { id: uid(), title: '确定项目选题与里程碑，输出 MVP 需求清单', completed: false, week: 2, tag: '项目' },
    { id: uid(), title: '完成 1 次模拟面试并记录复盘', completed: false, week: 3, tag: '求职' },
    { id: uid(), title: '把项目亮点写进简历，补齐 3 条量化成果', completed: false, week: 4, tag: '表达' },
    { id: uid(), title: '每周至少 2 次题单训练（算法/SQL/八股）', completed: false, week: 5, tag: '基础' },
    { id: uid(), title: '完成核心功能开发并写好 README/接口文档', completed: false, week: 6, tag: '项目' },
    { id: uid(), title: '把项目上线部署，能在线演示', completed: false, week: 8, tag: '项目' },
    { id: uid(), title: '开始投递并维护投递看板（反馈-原因-改进）', completed: false, week: 9, tag: '求职' },
    { id: uid(), title: '整理面试高频问题清单 + 标准回答', completed: false, week: 10, tag: '求职' },
    { id: uid(), title: '完成 1 次项目复盘（取舍/权衡/风险）并更新文档', completed: false, week: 11, tag: '复盘' },
    { id: uid(), title: '最终迭代简历与作品集，准备终面级讲解', completed: false, week: 12, tag: '收官' },
  ]

  longTasks.value = {
    m1: [
      { id: uid(), title: '交付 1 个可演示的 MVP 项目（含文档/部署）', completed: false },
      { id: uid(), title: '形成稳定的自我介绍与项目讲解脚本（STAR）', completed: false },
    ],
    m2: [
      { id: uid(), title: '补齐量化成果与技术证据链，能被追问解释', completed: false },
      { id: uid(), title: '完成 3-5 次模拟面试并迭代简历/表达', completed: false },
    ],
    m3: [
      { id: uid(), title: '建立投递-复盘-迭代闭环，稳定获得面试机会', completed: false },
      { id: uid(), title: '完成作品集打磨与岗位针对性优化，提升通过率', completed: false },
    ],
  }

  persist()
}

function tryLoad() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return false
    const payload = JSON.parse(raw)
    if (!payload) return false
    if (Array.isArray(payload.shortTasks)) shortTasks.value = payload.shortTasks
    if (payload.longTasks && typeof payload.longTasks === 'object') {
      longTasks.value = {
        m1: Array.isArray(payload.longTasks.m1) ? payload.longTasks.m1 : [],
        m2: Array.isArray(payload.longTasks.m2) ? payload.longTasks.m2 : [],
        m3: Array.isArray(payload.longTasks.m3) ? payload.longTasks.m3 : [],
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
      { id: uid(), title: trimmed, completed: false, week: Number.isFinite(week) && week >= 1 && week <= 12 ? week : undefined, tag: '手动添加' },
    ]
  } else {
    const monthKey = window.prompt('添加到哪个月份？输入 m1 / m2 / m3', 'm1')
    const key = monthKey === 'm2' || monthKey === 'm3' ? monthKey : 'm1'
    longTasks.value[key] = [...(longTasks.value[key] || []), { id: uid(), title: trimmed, completed: false }]
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

onMounted(() => {
  const loaded = tryLoad()
  if (!loaded) seedIfEmpty()
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
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
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
  background:
    radial-gradient(circle at 12px 12px, rgba(51, 50, 46, 0.08) 1.6px, transparent 2.3px)
      0 0 / 28px 28px,
    linear-gradient(135deg, var(--u-bg-normal), var(--u-gradient-fade));
  border-radius: 18px;
  padding: 22px 22px 24px;
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.08);
}

.plan-generated-view.dark .panel {
  background: var(--dm-gradient-card);
  border: 1px solid var(--dm-border);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
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
  font-size: clamp(20px, 1.4vw, 26px);
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
  border-radius: 16px;
  background: var(--u-panel);
  border: 1px solid var(--u-border);
  overflow: hidden;
}

.plan-generated-view.dark .gantt {
  background: var(--dm-surface-card);
  border-color: var(--dm-border);
}

.gantt-head {
  display: grid;
  grid-template-columns: 160px repeat(12, 1fr);
  align-items: center;
  background: #f8fafc;
  border-bottom: 1px solid rgba(148, 163, 184, 0.25);
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
  min-height: 74px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.22);
}

.gantt-row:last-child {
  border-bottom: none;
}

.row-label {
  padding: 14px 12px;
  font-weight: 700;
  background: #fbfdff;
  color: #334155;
  display: flex;
  align-items: center;
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
  padding: 10px 12px;
  gap: 10px;
}

.bar {
  border-radius: 14px;
  padding: 10px 12px;
  color: var(--u-black);
  font-size: 13px;
  line-height: 1.25;
  box-shadow: 2px 2px 0px var(--u-black);
  border: var(--u-border);
}

.plan-generated-view.dark .bar {
  background: rgba(255, 255, 255, 0.06);
  color: var(--dm-text);
  border-color: var(--dm-border);
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
  background: linear-gradient(90deg, var(--u-bg-normal), var(--u-fade-normal));
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
  background: var(--u-bg-normal);
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
  background: var(--u-bg-completed);
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
  background: var(--u-normal);
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

