<template>
  <div class="profile-view" :class="theme">
    <AppHeader show-utility-icons />

    <main class="profile-page">
      <div class="profile-page-top-actions">
        <el-button class="u-btn u-btn--ghost" @click="goHome">返回主界面</el-button>
      </div>

      <!-- 模块1：个人信息卡片 -->
      <section class="profile-card">
        <div class="profile-card__body">
          <div class="profile-avatar-wrap">
            <el-avatar :size="96" class="profile-avatar">
              <el-icon :size="48"><UserFilled /></el-icon>
            </el-avatar>
          </div>
          <div class="profile-info">
            <h1 class="profile-name">{{ user.name }}</h1>
            <p class="profile-meta">
              {{ user.university }} · {{ user.major }} · {{ user.grade }}
            </p>
            <div class="profile-cv">
              <span class="profile-cv-label">简历完整度</span>
              <el-progress
                :percentage="user.cvCompletion"
                :stroke-width="12"
                :show-text="true"
                color="#63bfb7"
                class="profile-cv-progress"
              />
            </div>
            <div v-if="hasOngoingPlanProgress" class="profile-plan-progress">
              <div class="profile-plan-progress__head">
                <span class="profile-plan-progress__label">正在进行的计划进度</span>
                <span class="profile-plan-progress__stats">
                  {{ ongoingPlanProgress.completed }}/{{ ongoingPlanProgress.total }}
                </span>
              </div>
              <el-progress
                :percentage="ongoingPlanProgress.percentage"
                :stroke-width="10"
                color="#63bfb7"
                class="profile-plan-progress__bar"
              />
              <p class="profile-plan-progress__desc">
                已完成 {{ ongoingPlanProgress.completed }} 项，还剩 {{ ongoingPlanProgress.remaining }} 项
              </p>
            </div>
          </div>
        </div>
        <div class="profile-card__footer">
          <el-button type="primary" class="profile-btn" @click="onCompleteProfile">
            完善资料
          </el-button>
        </div>
      </section>

      <!-- 模块1.5：AI简历解析实验室 -->
      <section class="profile-card resume-lab">
        <div class="resume-lab__header">
          <h2 class="resume-lab__title">AI 简历解析实验室</h2>
          <p class="resume-lab__desc">上传后将触发透视扫描，并把提取的能力关键词落入统计区。</p>
        </div>

        <div class="resume-lab__actions">
          <el-upload
            action="#"
            accept=".pdf,.doc,.docx,image/*"
            :show-file-list="false"
            :before-upload="handleResumeUpload"
          >
            <el-button type="primary" class="profile-btn">上传简历并解析</el-button>
          </el-upload>
          <span v-if="resumeFileName" class="resume-file-name">当前文件：{{ resumeFileName }}</span>
        </div>

        <div class="resume-lab__content">
          <div class="resume-sheet">
            <img
              v-if="resumePreviewUrl"
              class="resume-sheet__preview"
              :src="resumePreviewUrl"
              alt="简历预览"
            />
            <div v-else class="resume-sheet__placeholder">
              <span class="resume-sheet__placeholder-title">等待简历上传</span>
              <span class="resume-sheet__placeholder-sub">支持 PDF / DOC / DOCX / 图片</span>
            </div>
            <div v-if="isScanning" class="laser-scan-bar" />
          </div>

          <div class="ability-dropzone">
            <p class="ability-dropzone__title">能力统计区（AI 捕获）</p>
            <div class="ability-dropzone__rain-layer">
              <TransitionGroup name="keyword-rain" tag="div">
                <span
                  v-for="particle in keywordParticles"
                  :key="particle.id"
                  class="keyword-particle"
                  :style="particle.style"
                >
                  {{ particle.text }}
                </span>
              </TransitionGroup>
            </div>

            <div class="ability-dropzone__chips">
              <span
                v-for="keyword in capturedKeywords"
                :key="keyword"
                class="ability-keyword-chip"
              >
                {{ keyword }}
              </span>
              <span v-if="!capturedKeywords.length" class="ability-dropzone__empty">
                扫描完成后会在这里显示提取关键词
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- 模块2：能力画像速览 -->
      <section class="profile-card ability-snapshot">
        <h2 class="ability-snapshot__title">能力画像速览</h2>
        <div class="ability-snapshot__grid">
          <div ref="radarRef" class="radar-mini" />
          <div class="ability-snapshot__right">
            <p class="ability-score-line">
              综合能力指数
              <strong class="ability-score-num">{{ abilitySummary.score }}</strong>
              分
            </p>
            <p class="ability-rank-line">
              竞争力排位前 <strong>{{ abilitySummary.rankPercent }}%</strong>
            </p>
            <RouterLink class="ability-link" :to="{ name: 'StudentAbilities', query: { step: 'match' } }">
              查看完整画像 →
            </RouterLink>
          </div>
        </div>
      </section>

      <!-- 模块3：报告历史记录（按职业聚合，折叠内时间线） -->
      <section class="profile-card history-section report-history">
        <h2 class="report-history__title">报告历史记录</h2>
        <p class="history-section__hint">
          按目标岗位聚合你的每一步，展开即可看到从测评到改进的连续进化轨迹。
        </p>
        <el-empty
          v-if="!groupedHistory.length"
          class="history-empty"
          description="暂无报告或培训计划记录"
        />
        <el-collapse
          v-else
          v-model="historyCollapseActive"
          class="history-collapse"
        >
          <el-collapse-item
            v-for="group in groupedHistory"
            :key="group.jobTitle"
            :name="group.jobTitle"
          >
            <template #title>
              <div class="history-collapse-title">
                <span class="history-job-title">{{ group.jobTitle }}</span>
                <span class="history-job-meta">
                  <span class="history-count history-count--report">
                    {{ group.counts.report }} 次测评报告
                  </span>
                  <span class="history-count history-count--plan">
                    {{ group.counts.plan }} 次改进计划
                  </span>
                  <span v-if="group.lastUpdated" class="history-last-updated">
                    最近 {{ group.lastUpdated }}
                  </span>
                </span>
                <div v-if="group.planProgress" class="history-plan-progress">
                  <div class="history-plan-progress__head">
                    <span>计划完成度</span>
                    <span>{{ group.planProgress.completed }}/{{ group.planProgress.total }}</span>
                  </div>
                  <el-progress
                    :percentage="group.planProgress.percentage"
                    :stroke-width="8"
                    color="#63bfb7"
                  />
                </div>
              </div>
            </template>
            <el-timeline class="report-timeline history-timeline">
              <el-timeline-item
                v-for="item in group.items"
                :key="`${item.type}-${item.id}`"
                :timestamp="item.date"
                placement="top"
              >
                <div class="report-item history-record-item">
                  <div class="history-record-main">
                    <span
                      class="history-type-tag"
                      :class="
                        item.type === 'report'
                          ? 'history-type-tag--report'
                          : 'history-type-tag--plan'
                      "
                    >
                      {{ item.type === 'report' ? '发展报告' : '培训计划' }}
                    </span>
                    <p class="report-item__title">{{ item.title }}</p>
                    <p class="history-type-desc">
                      {{ item.evolutionText }}
                    </p>
                  </div>
                  <div class="report-item__actions">
                    <el-button type="primary" link @click="viewHistoryItem(item)">
                      查看
                    </el-button>
                    <el-button type="primary" link @click="downloadHistoryItem(item)">
                      下载
                    </el-button>
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
          </el-collapse-item>
        </el-collapse>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { UserFilled } from '@element-plus/icons-vue'
import { useTheme } from '../composables/useTheme'
import AppHeader from '../components/AppHeader.vue'
import {
  getLatestProfileSnapshot,
  getProfileSnapshots,
  isCareerAgentApiEnabled,
  readProfileCacheId,
} from '../api/careerAgentApi'

const { theme } = useTheme()
const router = useRouter()

const user = ref({
  name: '李华',
  university: '某985理工大学',
  major: '软件工程',
  grade: '大四',
  cvCompletion: 95,
  reports: [],
  trainingPlans: [],
})

const abilitySummary = ref({
  score: 78,
  rankPercent: 60
})

const radarDimensions = [
  { name: '专业技能', max: 100 },
  { name: '创新能力', max: 100 },
  { name: '学习能力', max: 100 },
  { name: '抗压能力', max: 100 },
  { name: '沟通能力', max: 100 },
  { name: '实习能力', max: 100 }
]

const radarValues = ref([85, 80, 90, 75, 80, 60])
const PLAN_PROGRESS_STORAGE_KEY = 'career_planner_training_plan_progress_v1'
const ongoingPlanProgress = ref({
  total: 0,
  completed: 0,
  remaining: 0,
  percentage: 0,
})
const planProgressByJob = ref({})
const hasOngoingPlanProgress = computed(() => ongoingPlanProgress.value.total > 0)

const buildDefaultReports = () => [
  {
    job_title: 'Java 开发工程师',
    id: 'R001',
    title: '职业发展分析报告',
    date: '2026-04-10',
  },
  {
    job_title: 'Java 开发工程师',
    id: 'R001-2',
    title: '职业发展分析报告（第二次测评）',
    date: '2026-04-12',
  },
  {
    job_title: '前端开发工程师',
    id: 'R002',
    title: '职业发展分析报告',
    date: '2026-03-05',
  },
  {
    job_title: '软件测试工程师',
    id: 'R003',
    title: '职业发展分析报告',
    date: '2026-02-28',
  },
]

const buildDefaultTrainingPlans = () => [
  {
    job_title: 'Java 开发工程师',
    id: 'P001',
    title: 'Java 进阶培训计划',
    date: '2026-04-11',
  },
  {
    job_title: 'Java 开发工程师',
    id: 'P001-2',
    title: 'Java 实战强化培训计划',
    date: '2026-04-13',
  },
  {
    job_title: '数据分析师',
    id: 'P002',
    title: 'Python 进阶培训计划',
    date: '2026-04-01',
  },
]

user.value.reports = buildDefaultReports()
user.value.trainingPlans = buildDefaultTrainingPlans()

const historyCollapseActive = ref([])

const parseHistoryDate = (d) => {
  const t = Date.parse(String(d || ''))
  return Number.isFinite(t) ? t : 0
}

const groupedHistory = computed(() => {
  const reportItems = (user.value.reports || []).map((item) => ({
    type: 'report',
    id: item.id,
    title: item.title || '职业发展分析报告',
    date: item.date || '',
    jobTitle: item.job_title || item.jobTitle || '未指定职业',
  }))
  const trainingPlanItems = (user.value.trainingPlans || []).map((item) => ({
    type: 'plan',
    id: item.id,
    title: item.title || '能力培训计划',
    date: item.date || '',
    jobTitle: item.job_title || item.jobTitle || '未指定职业',
  }))
  const allItems = [...reportItems, ...trainingPlanItems]
  const groups = new Map()
  for (const entry of allItems) {
    const jobTitle = String(entry.jobTitle || '未指定职业').trim() || '未指定职业'
    if (!groups.has(jobTitle)) {
      groups.set(jobTitle, [])
    }
    groups.get(jobTitle).push(entry)
  }
  const rows = []
  for (const [jobTitle, items] of groups) {
    const timeline = [...items].sort((a, b) => parseHistoryDate(a.date) - parseHistoryDate(b.date))
    const lastUpdated = [...items].sort((a, b) => parseHistoryDate(b.date) - parseHistoryDate(a.date))[0]?.date || ''
    const counts = timeline.reduce(
      (acc, x) => {
        if (x.type === 'plan') acc.plan += 1
        else acc.report += 1
        return acc
      },
      { report: 0, plan: 0 },
    )
    const itemsWithEvolution = timeline.map((item, index) => {
      const action = item.type === 'report' ? '完成职业测评报告' : '生成针对性培训计划'
      const evolutionPrefix = index === 0 ? '起点' : `第 ${index + 1} 步`
      return {
        ...item,
        evolutionText: `${evolutionPrefix}：${item.date || '未知日期'} ${action}`,
      }
    })
    const planProgress = planProgressByJob.value[jobTitle] || null
    rows.push({ jobTitle, lastUpdated, items: itemsWithEvolution, counts, planProgress })
  }
  rows.sort((a, b) => parseHistoryDate(b.lastUpdated) - parseHistoryDate(a.lastUpdated))
  return rows
})

const radarRef = ref(null)
let chartInstance = null
let resizeObserver = null
const resumeFileName = ref('')
const resumePreviewUrl = ref('')
const isScanning = ref(false)
const keywordParticles = ref([])
const capturedKeywords = ref([])
let particleTimer = null
let scanEndTimer = null
let particleUid = 0

const keywordPool = [
  'Java',
  'Python',
  '沟通能力',
  '项目管理',
  '团队协作',
  'Spring Boot',
  'Vue3',
  '数据分析',
  '问题解决',
  '创新思维',
  'MySQL',
  '英语表达'
]

const clearScanTimers = () => {
  if (particleTimer) {
    clearInterval(particleTimer)
    particleTimer = null
  }
  if (scanEndTimer) {
    clearTimeout(scanEndTimer)
    scanEndTimer = null
  }
}

const revokeResumePreview = () => {
  if (resumePreviewUrl.value && resumePreviewUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(resumePreviewUrl.value)
  }
}

const buildParticleStyle = () => {
  const left = Math.floor(Math.random() * 72) + 8
  const duration = (Math.random() * 0.9 + 1.5).toFixed(2)
  const drift = Math.floor(Math.random() * 40) - 20
  return {
    left: `${left}%`,
    '--rain-duration': `${duration}s`,
    '--drift-x': `${drift}px`
  }
}

const addParticle = (text) => {
  const id = `particle-${particleUid++}`
  keywordParticles.value.push({
    id,
    text,
    style: buildParticleStyle()
  })

  if (!capturedKeywords.value.includes(text)) {
    capturedKeywords.value.push(text)
  }

  setTimeout(() => {
    keywordParticles.value = keywordParticles.value.filter((item) => item.id !== id)
  }, 2200)
}

const startResumeScan = () => {
  clearScanTimers()
  isScanning.value = true
  capturedKeywords.value = []
  keywordParticles.value = []

  const shuffled = [...keywordPool].sort(() => Math.random() - 0.5)
  let index = 0
  particleTimer = setInterval(() => {
    if (index >= shuffled.length) {
      return
    }
    addParticle(shuffled[index])
    index += 1
  }, 420)

  scanEndTimer = setTimeout(() => {
    clearScanTimers()
    isScanning.value = false
    ElMessage.success('简历解析完成，能力关键词已同步到统计区')
  }, 5600)
}

const handleResumeUpload = (file) => {
  resumeFileName.value = file.name
  revokeResumePreview()
  if (file.type?.startsWith('image/')) {
    resumePreviewUrl.value = URL.createObjectURL(file)
  } else {
    resumePreviewUrl.value = ''
  }
  startResumeScan()
  return false
}

const initRadar = () => {
  if (!radarRef.value) return
  chartInstance = echarts.init(radarRef.value, null, { renderer: 'canvas' })
  const nextValues = Array.isArray(radarValues.value) ? radarValues.value : []
  chartInstance.setOption({
    radar: {
      indicator: radarDimensions,
      radius: '68%',
      center: ['50%', '52%'],
      splitNumber: 4,
      axisName: {
        color: 'rgba(51, 50, 46, 0.75)',
        fontSize: 11
      },
      splitLine: {
        lineStyle: { color: 'rgba(51, 50, 46, 0.12)' }
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(99, 191, 183, 0.06)', 'rgba(99, 191, 183, 0.02)']
        }
      }
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: nextValues,
            name: '能力',
            areaStyle: {
              color: 'rgba(99, 191, 183, 0.35)'
            },
            lineStyle: {
              color: '#63bfb7',
              width: 2
            },
            itemStyle: {
              color: '#63bfb7'
            }
          }
        ]
      }
    ]
  })
}

const updateRadar = () => {
  if (!chartInstance) return
  chartInstance.setOption({
    series: [
      {
        type: 'radar',
        data: [{ value: radarValues.value, name: '能力' }],
      },
    ],
  })
}

const getStudentId = () => readProfileCacheId() || 'student_demo_001'

const loadOngoingPlanProgress = () => {
  try {
    const raw = localStorage.getItem(PLAN_PROGRESS_STORAGE_KEY)
    if (!raw) {
      ongoingPlanProgress.value = { total: 0, completed: 0, remaining: 0, percentage: 0 }
      planProgressByJob.value = {}
      return
    }
    const parsed = JSON.parse(raw)
    const total = Number(parsed?.total)
    const completed = Number(parsed?.completed)
    const remaining = Number(parsed?.remaining)
    const percentage = Number(parsed?.percentage)
    ongoingPlanProgress.value = {
      total: Number.isFinite(total) ? Math.max(0, total) : 0,
      completed: Number.isFinite(completed) ? Math.max(0, completed) : 0,
      remaining: Number.isFinite(remaining) ? Math.max(0, remaining) : 0,
      percentage: Number.isFinite(percentage) ? Math.max(0, Math.min(100, percentage)) : 0,
    }
    const byJobRaw = parsed?.byJob
    const nextByJob = {}
    if (byJobRaw && typeof byJobRaw === 'object') {
      for (const [jobTitle, progress] of Object.entries(byJobRaw)) {
        const p = progress && typeof progress === 'object' ? progress : {}
        const pTotal = Number(p.total)
        const pCompleted = Number(p.completed)
        const pPercentage = Number(p.percentage)
        if (!Number.isFinite(pTotal) || pTotal <= 0) continue
        nextByJob[String(jobTitle).trim() || '职业规划'] = {
          total: Math.max(0, pTotal),
          completed: Number.isFinite(pCompleted) ? Math.max(0, pCompleted) : 0,
          percentage: Number.isFinite(pPercentage) ? Math.max(0, Math.min(100, pPercentage)) : 0,
        }
      }
    }
    planProgressByJob.value = nextByJob
  } catch {
    ongoingPlanProgress.value = { total: 0, completed: 0, remaining: 0, percentage: 0 }
    planProgressByJob.value = {}
  }
}

const applyLatestSnapshot = (snapshot) => {
  if (!snapshot || typeof snapshot !== 'object') return
  const dims = snapshot.dimensions || {}
  radarValues.value = [
    Number(dims.professional_skills?.score ?? 0),
    Number(dims.innovation_capability?.score ?? 0),
    Number(dims.learning_capability?.score ?? 0),
    Number(dims.stress_resistance?.score ?? 0),
    Number(dims.communication_skills?.score ?? 0),
    Number(dims.internship_experience?.score ?? 0),
  ].map((x) => (Number.isFinite(x) ? Math.max(0, Math.min(100, x)) : 0))
  abilitySummary.value = {
    score: Number(snapshot.match_score ?? abilitySummary.value.score ?? 0),
    rankPercent: Number(snapshot.plan_completion_rate ?? abilitySummary.value.rankPercent ?? 0),
  }
  updateRadar()
}

const hydrateSnapshots = async () => {
  if (!isCareerAgentApiEnabled()) return
  const studentId = getStudentId()
  try {
    const latest = await getLatestProfileSnapshot(studentId)
    applyLatestSnapshot(latest)
  } catch (e) {
    console.warn('[career-agent] profile/snapshots/latest', e)
  }
  try {
    const snapshotList = await getProfileSnapshots(studentId, 10)
    if (Array.isArray(snapshotList) && snapshotList.length) {
      const jobTitleFromSnapshot = (item) => {
        const t =
          item.target_position ||
          item.job_title ||
          item.position ||
          item.target_job_title ||
          item.job_name ||
          ''
        const s = String(t || '').trim()
        return s || '职业规划'
      }
      const apiReports = snapshotList.map((item) => ({
        type: 'report',
        jobTitle: jobTitleFromSnapshot(item),
        id: item.snapshot_id || item.report_id || item.snapshot_month,
        title:
          item.report_title ||
          `${item.snapshot_month || '当期'} 职业发展报告`,
        date: item.created_at
          ? String(item.created_at).slice(0, 10)
          : String(item.snapshot_month || ''),
      }))
      user.value.reports = apiReports
    }
  } catch (e) {
    console.warn('[career-agent] profile/snapshots', e)
  }
}

const disposeRadar = () => {
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
}

onMounted(async () => {
  loadOngoingPlanProgress()
  nextTick(() => {
    initRadar()
    if (radarRef.value && chartInstance) {
      resizeObserver = new ResizeObserver(() => {
        chartInstance?.resize()
      })
      resizeObserver.observe(radarRef.value)
    }
  })
  await hydrateSnapshots()
})

onUnmounted(() => {
  disposeRadar()
  clearScanTimers()
  revokeResumePreview()
})

const onCompleteProfile = () => {
  ElMessage.success('已打开完善资料（演示）')
}

const goHome = () => {
  router.push({ name: 'Home' })
}

const viewHistoryItem = (item) => {
  if (item?.type === 'plan') {
    router.push({
      name: 'AbilityTrainingPlanGenerated',
      query: { id: String(item.id) },
    })
    return
  }
  router.push({ name: 'ReportDetail', params: { id: String(item.id) } })
}

const downloadHistoryItem = (item) => {
  const label = item?.type === 'plan' ? '培训计划' : '发展报告'
  ElMessage.info(`下载${label}：${item.title}（演示）`)
}
</script>

<style scoped>
.profile-view {
  min-height: 100vh;
  width: 100%;
  background: var(--u-body-bg);
  color: var(--u-black);
}

.profile-view.dark {
  background: var(--dm-bg);
  color: var(--dm-text);
}

.profile-page {
  max-width: 920px;
  margin: 0 auto;
  padding: 24px 20px 48px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.profile-page-top-actions {
  display: flex;
  justify-content: flex-start;
}

.profile-card {
  background: color-mix(in srgb, var(--u-bg-normal) 78%, var(--u-panel));
  border-radius: 16px;
  border: var(--u-border);
  box-shadow: var(--u-box-shadow);
  padding: 24px;
  box-sizing: border-box;
}

.profile-page .profile-card:nth-of-type(1) {
  background: color-mix(in srgb, var(--u-bg-normal) 78%, var(--u-panel));
}

.profile-page .profile-card:nth-of-type(2) {
  background: color-mix(in srgb, var(--u-bg-normal) 78%, var(--u-panel));
}

.profile-page .profile-card:nth-of-type(3) {
  background: color-mix(in srgb, var(--u-bg-normal) 78%, var(--u-panel));
}

.profile-view.dark .profile-card {
  background: linear-gradient(160deg, #1f2937 0%, #111827 100%);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35);
  border: 1px solid var(--dm-border);
}

.profile-view.dark .profile-page .profile-card:nth-of-type(1) {
  background: linear-gradient(160deg, #1f2937 0%, #111827 100%);
}

.profile-view.dark .profile-page .profile-card:nth-of-type(2) {
  background: linear-gradient(160deg, #1f2937 0%, #111827 100%);
}

.profile-view.dark .profile-page .profile-card:nth-of-type(3) {
  background: linear-gradient(160deg, #1f2937 0%, #111827 100%);
}

.profile-card__body {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  flex-wrap: wrap;
}

.profile-avatar-wrap {
  flex-shrink: 0;
}

.profile-avatar {
  border: 2px solid rgba(51, 50, 46, 0.12);
  background: linear-gradient(
    145deg,
    color-mix(in srgb, var(--u-body-bg) 88%, #ffffff),
    color-mix(in srgb, var(--u-bg-normal) 82%, var(--u-panel))
  );
  color: rgba(51, 50, 46, 0.65);
}

.profile-info {
  flex: 1;
  min-width: 200px;
}

.profile-name {
  margin: 0 0 8px;
  font-size: clamp(22px, 2vw, 28px);
  font-weight: 700;
  color: var(--u-black);
}

.profile-meta {
  margin: 0 0 16px;
  font-size: clamp(14px, 1vw, 16px);
  color: rgba(51, 50, 46, 0.72);
  line-height: 1.5;
}

.profile-view.dark .profile-meta {
  color: #94a3b8;
}

.profile-cv-label {
  display: block;
  font-size: 14px;
  margin-bottom: 8px;
  color: color-mix(in srgb, var(--u-black) 78%, var(--u-placeholder));
}

.profile-cv-progress {
  max-width: 100%;
}

.profile-plan-progress {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px dashed rgba(51, 50, 46, 0.16);
}

.profile-plan-progress__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.profile-plan-progress__label {
  font-size: 14px;
  color: color-mix(in srgb, var(--u-black) 82%, var(--u-placeholder));
}

.profile-plan-progress__stats {
  font-size: 13px;
  font-weight: 600;
  color: color-mix(in srgb, var(--u-completed) 78%, #0f766e);
}

.profile-plan-progress__bar {
  margin-top: 8px;
}

.profile-plan-progress__desc {
  margin: 6px 0 0;
  font-size: 12px;
  line-height: 1.4;
  color: rgba(51, 50, 46, 0.58);
}

:deep(.profile-cv-progress .el-progress-bar__outer) {
  background-color: rgba(51, 50, 46, 0.1);
}

.profile-card__footer {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(51, 50, 46, 0.08);
}

.profile-view.dark .profile-card__footer {
  border-top-color: var(--dm-border);
}

.profile-btn {
  border-radius: 999px;
  background: var(--u-bg-submit);
  border-color: rgba(51, 50, 46, 0.2);
  color: var(--u-black);
}

.profile-btn:hover {
  background: color-mix(in srgb, var(--u-bg-submit) 76%, var(--u-panel));
  border-color: rgba(51, 50, 46, 0.3);
}

.ability-snapshot__title {
  margin: 0 0 16px;
  font-size: clamp(18px, 1.3vw, 20px);
  font-weight: 600;
}

.ability-snapshot__grid {
  display: grid;
  grid-template-columns: minmax(200px, 260px) 1fr;
  gap: 20px;
  align-items: center;
}

.radar-mini {
  width: 100%;
  height: 220px;
  min-height: 200px;
}

.ability-snapshot__right {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ability-score-line,
.ability-rank-line {
  margin: 0;
  font-size: clamp(15px, 1.05vw, 17px);
  line-height: 1.5;
}

.ability-score-num {
  font-size: clamp(26px, 2vw, 32px);
  margin: 0 4px;
  color: var(--u-completed);
}

.ability-link {
  margin-top: 4px;
  font-size: 15px;
  color: color-mix(in srgb, var(--u-completed) 72%, #2563eb);
  text-decoration: none;
  align-self: flex-start;
}

.ability-link:hover {
  text-decoration: underline;
}

.report-history__title {
  margin: 0 0 16px;
  font-size: clamp(18px, 1.3vw, 20px);
  font-weight: 600;
}

.history-section__hint {
  margin: -8px 0 16px;
  font-size: 13px;
  line-height: 1.5;
  color: rgba(51, 50, 46, 0.62);
}

.history-empty {
  padding: 12px 0 8px;
}

.history-collapse {
  border: none;
  --history-collapse-pad: 4px 0 0;
}

:deep(.history-collapse.el-collapse) {
  border-top: none;
  border-bottom: none;
}

:deep(.history-collapse .el-collapse-item__header) {
  height: auto;
  min-height: 48px;
  line-height: 1.35;
  padding: 10px 12px;
  border-radius: 12px;
  background: color-mix(in srgb, var(--u-bg-normal) 88%, var(--u-panel));
  border: 1px solid rgba(51, 50, 46, 0.08);
}

:deep(.history-collapse .el-collapse-item__wrap) {
  border-bottom: none;
}

:deep(.history-collapse .el-collapse-item__content) {
  padding: 12px 4px 8px 8px;
}

.history-collapse-title {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  width: 100%;
  padding-right: 8px;
  box-sizing: border-box;
}

.history-plan-progress {
  width: 100%;
  margin-top: 2px;
}

.history-plan-progress__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: rgba(51, 50, 46, 0.6);
  margin-bottom: 4px;
}

.history-job-title {
  font-size: clamp(15px, 1.05vw, 17px);
  font-weight: 600;
  color: var(--u-black);
}

.history-job-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 12px;
  font-size: 12px;
}

.history-count--report {
  color: color-mix(in srgb, #2563eb 82%, var(--u-black));
  font-weight: 500;
}

.history-count--plan {
  color: color-mix(in srgb, var(--u-completed) 78%, #0f766e);
  font-weight: 500;
}

.history-count--muted {
  color: rgba(51, 50, 46, 0.45);
}

.history-last-updated {
  color: rgba(51, 50, 46, 0.5);
}

.history-timeline {
  margin-top: 4px;
}

.history-record-item {
  align-items: flex-start;
}

.history-record-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-type-tag {
  display: inline-flex;
  align-self: flex-start;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  line-height: 1.4;
}

.history-type-tag--report {
  background: rgba(37, 99, 235, 0.12);
  color: #1d4ed8;
}

.history-type-tag--plan {
  background: color-mix(in srgb, var(--u-completed) 22%, transparent);
  color: color-mix(in srgb, var(--u-completed) 55%, #0f766e);
}

.history-type-desc {
  margin: 0;
  font-size: 12px;
  line-height: 1.45;
  color: rgba(51, 50, 46, 0.55);
}

.profile-view.dark .history-section__hint {
  color: var(--dm-text-muted);
}

.profile-view.dark .history-job-title {
  color: var(--dm-text);
}

.profile-view.dark .history-count--report {
  color: color-mix(in srgb, #93c5fd 70%, var(--dm-text));
}

.profile-view.dark .history-count--plan {
  color: color-mix(in srgb, var(--u-completed) 65%, var(--dm-text));
}

.profile-view.dark .history-count--muted,
.profile-view.dark .history-last-updated {
  color: var(--dm-text-muted);
}

.profile-view.dark .history-plan-progress__head {
  color: var(--dm-text-secondary);
}

.profile-view.dark .history-type-tag--report {
  background: rgba(59, 130, 246, 0.2);
  color: #93c5fd;
}

.profile-view.dark .history-type-tag--plan {
  background: color-mix(in srgb, var(--u-completed) 18%, transparent);
  color: color-mix(in srgb, var(--u-completed) 72%, #5eead4);
}

.profile-view.dark .history-type-desc {
  color: var(--dm-text-muted);
}

.profile-view.dark :deep(.history-collapse .el-collapse-item__header) {
  background: color-mix(in srgb, var(--dm-surface-elevated) 88%, var(--dm-bg));
  border-color: var(--dm-border);
}

.report-item {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.report-item__title {
  margin: 0;
  font-size: clamp(15px, 1vw, 16px);
  font-weight: 500;
  flex: 1;
  min-width: 0;
}

.report-item__actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

:deep(.report-timeline .el-timeline-item__timestamp) {
  color: rgba(51, 50, 46, 0.55);
  font-size: 13px;
}

:deep(.report-timeline .el-timeline-item__node--primary) {
  background-color: var(--u-completed);
}

:deep(.report-timeline .el-timeline-item__tail) {
  border-left-color: color-mix(in srgb, var(--u-completed) 35%, #cbd5e1);
}

.profile-view.dark :deep(.report-timeline .el-timeline-item__timestamp) {
  color: var(--dm-text-muted);
}

.profile-view.dark .profile-name {
  color: #f8fafc;
}

.profile-view.dark :deep(.el-progress-bar__outer) {
  background-color: rgba(148, 163, 184, 0.22) !important;
}

.profile-view.dark .profile-btn {
  background: color-mix(in srgb, var(--u-bg-submit) 68%, var(--dm-surface-elevated));
  color: var(--dm-text);
  border-color: var(--dm-border);
}

.profile-view.dark .profile-btn:hover {
  background: color-mix(in srgb, var(--u-bg-submit) 56%, var(--dm-surface-elevated));
}

.resume-lab__header {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 14px;
}

.resume-lab__title {
  margin: 0;
  font-size: clamp(18px, 1.35vw, 21px);
}

.resume-lab__desc {
  margin: 0;
  color: rgba(51, 50, 46, 0.68);
  font-size: 14px;
  line-height: 1.55;
}

.resume-lab__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.resume-file-name {
  font-size: 13px;
  color: rgba(51, 50, 46, 0.62);
}

.resume-lab__content {
  display: grid;
  grid-template-columns: minmax(220px, 300px) 1fr;
  gap: 14px;
}

.resume-sheet {
  position: relative;
  min-height: 270px;
  border-radius: 12px;
  border: 1px solid rgba(51, 50, 46, 0.12);
  background:
    linear-gradient(120deg, rgba(99, 191, 183, 0.06), rgba(99, 191, 183, 0.01)),
    color-mix(in srgb, var(--u-bg-normal) 86%, #ffffff);
  overflow: hidden;
}

.resume-sheet__preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.resume-sheet__placeholder {
  height: 100%;
  min-height: 270px;
  display: grid;
  place-content: center;
  text-align: center;
  gap: 6px;
}

.resume-sheet__placeholder-title {
  font-size: 15px;
  font-weight: 600;
}

.resume-sheet__placeholder-sub {
  font-size: 12px;
  color: rgba(51, 50, 46, 0.56);
}

.laser-scan-bar {
  position: absolute;
  left: 6px;
  right: 6px;
  top: 0;
  height: 24px;
  border-radius: 9px;
  background: linear-gradient(
    180deg,
    rgba(78, 245, 218, 0.06) 0%,
    rgba(78, 245, 218, 0.65) 50%,
    rgba(78, 245, 218, 0.08) 100%
  );
  box-shadow:
    0 0 10px rgba(78, 245, 218, 0.45),
    0 0 26px rgba(78, 245, 218, 0.2);
  animation: laserScan 1.9s ease-in-out infinite alternate;
}

.ability-dropzone {
  position: relative;
  min-height: 270px;
  border-radius: 12px;
  border: 1px dashed rgba(99, 191, 183, 0.45);
  background: linear-gradient(160deg, rgba(99, 191, 183, 0.08), rgba(99, 191, 183, 0.02));
  padding: 14px 12px;
  overflow: hidden;
}

.ability-dropzone__title {
  margin: 0 0 10px;
  font-size: 14px;
  font-weight: 600;
  color: color-mix(in srgb, var(--u-completed) 70%, var(--u-black));
}

.ability-dropzone__rain-layer {
  position: absolute;
  inset: 38px 0 54px;
  pointer-events: none;
}

.keyword-particle {
  position: absolute;
  top: -20px;
  display: inline-flex;
  align-items: center;
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 12px;
  color: #0f766e;
  background: rgba(240, 253, 250, 0.95);
  border: 1px solid rgba(15, 118, 110, 0.2);
  animation: keywordRain var(--rain-duration, 1.8s) ease-in forwards;
}

.ability-dropzone__chips {
  position: absolute;
  left: 12px;
  right: 12px;
  bottom: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.ability-keyword-chip {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  border: 1px solid rgba(15, 118, 110, 0.2);
  background: rgba(255, 255, 255, 0.82);
  color: #0f766e;
  font-size: 12px;
  line-height: 1;
  padding: 6px 10px;
}

.ability-dropzone__empty {
  font-size: 12px;
  color: rgba(51, 50, 46, 0.56);
}

.keyword-rain-enter-active,
.keyword-rain-leave-active {
  transition: opacity 0.35s ease;
}

.keyword-rain-enter-from,
.keyword-rain-leave-to {
  opacity: 0;
}

@keyframes laserScan {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(238px);
  }
}

@keyframes keywordRain {
  0% {
    transform: translate3d(0, -14px, 0) scale(0.92);
    opacity: 0;
  }
  12% {
    opacity: 1;
  }
  100% {
    transform: translate3d(var(--drift-x, 0), 180px, 0) scale(0.9);
    opacity: 0.1;
  }
}

.profile-view.dark .ability-score-num {
  color: color-mix(in srgb, var(--u-completed) 74%, #c4f1ea);
}

.profile-view.dark .ability-link {
  color: color-mix(in srgb, var(--u-completed) 60%, #9ec5ff);
}

.profile-view.dark :deep(.report-timeline .el-timeline-item__node--primary) {
  background-color: color-mix(in srgb, var(--u-completed) 72%, #d6fff8);
}

.profile-view.dark :deep(.report-timeline .el-timeline-item__tail) {
  border-left-color: color-mix(in srgb, var(--u-completed) 38%, var(--dm-border));
}

.profile-view.dark .resume-lab__desc,
.profile-view.dark .resume-file-name,
.profile-view.dark .ability-dropzone__empty,
.profile-view.dark .resume-sheet__placeholder-sub {
  color: var(--dm-text-secondary);
}

.profile-view.dark .resume-sheet {
  border-color: var(--dm-border);
  background: linear-gradient(
    130deg,
    rgba(37, 99, 235, 0.14),
    color-mix(in srgb, var(--dm-surface-card) 88%, var(--u-bg-normal))
  );
}

.profile-view.dark .ability-dropzone {
  border-color: color-mix(in srgb, var(--u-completed) 36%, var(--dm-border));
  background: linear-gradient(160deg, rgba(15, 118, 110, 0.22), rgba(15, 118, 110, 0.06));
}

.profile-view.dark .keyword-particle,
.profile-view.dark .ability-keyword-chip {
  background: color-mix(in srgb, var(--dm-surface-elevated) 92%, rgba(15, 118, 110, 0.35));
  border-color: color-mix(in srgb, var(--u-completed) 34%, var(--dm-border));
  color: color-mix(in srgb, #d5fff7 75%, var(--dm-text));
}

.profile-view.dark .profile-plan-progress {
  border-top-color: var(--dm-border);
}

.profile-view.dark .profile-plan-progress__label,
.profile-view.dark .profile-plan-progress__desc {
  color: var(--dm-text-secondary);
}

.profile-view.dark .profile-plan-progress__stats {
  color: color-mix(in srgb, var(--u-completed) 68%, var(--dm-text));
}

@media (max-width: 640px) {
  .profile-page {
    padding: 16px 12px 40px;
  }

  .profile-card {
    padding: 16px;
  }

  .ability-snapshot__grid {
    grid-template-columns: 1fr;
  }

  .radar-mini {
    height: 200px;
  }

  .resume-lab__content {
    grid-template-columns: 1fr;
  }

  .resume-sheet,
  .ability-dropzone {
    min-height: 230px;
  }

  .laser-scan-bar {
    animation-duration: 1.7s;
  }

  @keyframes laserScan {
    0% {
      transform: translateY(0);
    }
    100% {
      transform: translateY(194px);
    }
  }
}
</style>
