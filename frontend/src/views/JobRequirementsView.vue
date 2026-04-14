<template>
  <div class="jobs-view" :class="theme">
    <AppHeader />

    <!-- 内容 -->
    <main class="page-scroll">
      <!-- 标题与说明 -->
      <section class="hero-title-area">
        <h1 class="page-title">核心岗位画像库</h1>
        <p class="page-intro">
          依托 AI 大模型深度解构超 10,000 条行业实时招聘数据，结构化沉淀出涵盖计算机信息化核心领域的专业岗位画像。从专业硬实力到职场软素质，全方位解析 AI 时代高影响力职业的胜任力底座。系统不仅精准对标技能鸿沟，更前瞻性地构建了垂直晋升与跨行迁徙的血缘图谱，将碎片化需求转化为清晰的职业进化坐标，助你精准锚定成长路径，实现高质量的职业跃迁。
        </p>
        <div class="icon-row">
          <span
            v-for="n in 30"
            :key="n"
            class="small-icon"
          >
            ⚙
          </span>
        </div>
      </section>

      <section v-if="(loadingJobs && !hasRenderableJobs) || jobsError || isUsingMockFallback" class="status-panel">
        <p v-if="loadingJobs && !hasRenderableJobs" class="status-text">正在从后端加载岗位列表...</p>
        <p v-else-if="jobsError" class="status-text status-error">
          岗位接口加载失败：{{ jobsError }}，当前已自动使用本地兜底数据。
        </p>
        <p v-else-if="isUsingMockFallback" class="status-text">
          当前展示的是本地兜底岗位数据。
        </p>
      </section>

      <!-- 岗位卡片网格：统一尺寸 + 悬停/点击交互 -->
      <section class="jobs-grid">
        <div v-if="loadingJobs && !hasRenderableJobs" class="jobs-skeleton-wrap">
          <el-row :gutter="24" class="job-row">
            <el-col v-for="n in 8" :key="n" :xs="24" :sm="12" :md="6" :lg="6" class="job-col">
              <div class="job-skeleton-card">
                <el-skeleton animated :rows="5" />
              </div>
            </el-col>
          </el-row>
        </div>
        <template v-else>
          <div class="jobs-toolbar">
            <el-input
              v-model="searchKeyword"
              class="jobs-search"
              clearable
              placeholder="搜索岗位名、公司、领域…"
            />
            <el-select v-model="sortBy" class="jobs-sort" placeholder="排序">
              <el-option label="默认顺序" value="default" />
              <el-option label="岗位名 A-Z" value="nameAsc" />
              <el-option label="岗位名 Z-A" value="nameDesc" />
            </el-select>
          </div>
          <el-row :gutter="24" class="job-row">
            <el-col
              v-for="job in pagedJobs"
              :key="job.id"
              :xs="24"
              :sm="12"
              :md="6"
              :lg="6"
              class="job-col"
            >
              <div
                class="job-card"
                :class="{ 'is-active': activeCardId === job.id }"
                @click="goToJob(job)"
                @mouseenter="activeCardId = job.id"
                @mouseleave="activeCardId = null"
              >
                <div class="job-image-wrap">
                  <img
                    v-if="job.coverUrl"
                    class="job-cover"
                    :src="job.coverUrl"
                    alt=""
                  />
                  <div v-else class="job-image-placeholder">
                    <span class="placeholder-text">图片</span>
                  </div>
                </div>
                <div class="job-info">
                  <h3 class="job-name">{{ job.name }}</h3>
                  <p class="job-subtitle">
                    一技在身
                    <span class="highlight">{{ job.field }}</span>
                  </p>
                  <div class="job-action">
                    <span class="action-text">查看详情</span>
                    <span class="action-arrow">→</span>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
          <div v-if="totalFiltered > pageSize" class="jobs-pagination-wrap">
            <el-pagination
              v-model:current-page="page"
              background
              layout="total, prev, pager, next"
              :total="totalFiltered"
              :page-size="pageSize"
            />
          </div>
        </template>
      </section>

      <section class="stats-dashboard" aria-label="行业数智化洞察">
        <h2 class="stats-dashboard-heading">行业数智化洞察</h2>
        <p class="stats-dashboard-lead">
          基于超 10,000 条岗位样本的语义聚合与薪酬结构化统计（接口：<code class="stats-code">GET /api/v1/jobs/stats</code>）。
        </p>
        <div class="stats-dashboard-grid">
          <div class="stats-card">
            <h3 class="stats-title">🔥 核心技能热力词云</h3>
            <p class="stats-sub">高频技能关键词分布</p>
            <div ref="wordCloudRef" class="chart-box" />
          </div>
          <div class="stats-card">
            <h3 class="stats-title">💰 行业薪资分布态势</h3>
            <p class="stats-sub">岗位月薪区间占比</p>
            <div ref="salaryChartRef" class="chart-box" />
          </div>
        </div>
        <p v-if="statsHint" class="stats-hint">{{ statsHint }}</p>
      </section>

      <!-- 底部说明：协调版面，避免页面过短 -->
      <section class="page-bottom-intro">
        <p class="bottom-intro-text">
          以上岗位画像基于典型校招与行业需求整理，涵盖技能要求、发展路径与换岗方向。点击卡片可查看详情与垂直/换岗图谱。
        </p>
        <p class="bottom-intro-sub">
          如需定制更多岗位或更新维度，可联系管理员或在使用反馈中提出。
        </p>
      </section>

      <footer class="site-footer">
        <span>© {{ new Date().getFullYear() }} 职途智引 · AI职业规划助手</span>
      </footer>
    </main>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import 'echarts-wordcloud'
import { useTheme } from '../composables/useTheme'
import AppHeader from '../components/AppHeader.vue'
import { getJobsStats, getRecommendJobList } from '../api/jobPortraitApi'
import { formatJobPortraitApiError } from '../api/jobPortraitErrors'
import {
  extractJobsArray,
  loadJobListFromCache,
  normalizeText,
  saveJobListCache,
  unwrapData,
} from '../utils/jobPortraitNormalize'
import javaJobPortrait from '../assets/java-job-portrait.png'
import qaJobPortrait from '../assets/qa-job-portrait.png'
import cppJobPortrait from '../assets/cpp-job-portrait.png'
import implementationJobPortrait from '../assets/implementation-job-portrait.png'
import hardwareTestJobPortrait from '../assets/hardware-test-job-portrait.png'
import frontendJobPortrait from '../assets/frontend-job-portrait.png'
import techSupportJobPortrait from '../assets/tech-support-job-portrait.png'
import testEngineerJobPortrait from '../assets/test-engineer-job-portrait.png'
import researcherJobPortrait from '../assets/researcher-job-portrait.png'
import contentReviewJobPortrait from '../assets/content-review-job-portrait.png'

const { theme } = useTheme()
const router = useRouter()

const DEFAULT_STATS_WORDS = [
  { name: 'Java', value: 920 },
  { name: 'Python', value: 880 },
  { name: 'SQL', value: 890 },
  { name: '大数据', value: 760 },
  { name: 'LLM', value: 710 },
  { name: '架构设计', value: 650 },
  { name: 'Vue', value: 620 },
  { name: 'Kubernetes', value: 540 },
  { name: '微服务', value: 580 },
  { name: '云计算', value: 520 },
  { name: 'TypeScript', value: 600 },
  { name: 'Spring', value: 560 },
  { name: 'Go', value: 480 },
  { name: '数据分析', value: 640 },
  { name: '产品经理', value: 430 },
  { name: 'DevOps', value: 410 },
  { name: '机器学习', value: 590 },
  { name: '前端工程化', value: 450 },
]

const DEFAULT_STATS_SALARY = [
  { label: '10k 以下', count: 420 },
  { label: '10k-15k', count: 1850 },
  { label: '15k-25k', count: 3120 },
  { label: '25k-35k', count: 2280 },
  { label: '35k-50k', count: 1420 },
  { label: '50k+', count: 910 },
]

function hashHue(str) {
  let h = 0
  const s = String(str || '')
  for (let i = 0; i < s.length; i += 1) {
    h = h * 31 + s.charCodeAt(i)
    h |= 0
  }
  return Math.abs(h)
}

function normalizeJobStatsResponse(res) {
  const d = unwrapData(res)
  if (!d || typeof d !== 'object') return null

  const kwRaw =
    d.keyword_cloud ||
    d.keywordCloud ||
    d.skill_keywords ||
    d.skillKeywords ||
    d.keywords ||
    d.word_cloud
  const salRaw =
    d.salary_bins ||
    d.salaryBins ||
    d.salary_distribution ||
    d.salaryDistribution ||
    d.salary_histogram

  const wordData = Array.isArray(kwRaw)
    ? kwRaw
        .map((x) => ({
          name: String(x?.name ?? x?.word ?? x?.keyword ?? x?.label ?? x?.text ?? '').trim(),
          value: Number(x?.value ?? x?.weight ?? x?.count ?? x?.freq ?? 0) || 0,
        }))
        .filter((x) => x.name && x.value > 0)
    : []

  const barData = Array.isArray(salRaw)
    ? salRaw
        .map((x) => ({
          label: String(x?.label ?? x?.range ?? x?.bin ?? x?.name ?? '').trim(),
          count: Number(x?.count ?? x?.value ?? x?.jobs ?? x?.num ?? 0) || 0,
        }))
        .filter((x) => x.label)
    : []

  if (!wordData.length && !barData.length) return null
  return {
    wordData: wordData.length ? wordData : [...DEFAULT_STATS_WORDS],
    barData: barData.length ? barData : [...DEFAULT_STATS_SALARY],
  }
}

/**
 * 词云颜色与项目内已有数据一致：
 * - 岗位详情雷达：主系列 #63bfb7、全行业对比 rgba(251,191,36) / 浅色 rgba(180,83,9)
 * - base.css 深色主题：--dm-accent / --dm-accent-secondary / --dm-success / --dm-warm
 */
const WORD_CLOUD_PALETTE_DARK = [
  '#63bfb7',
  '#fbbf24',
  '#7eb8d4',
  '#b8899e',
  '#5fa89e',
  '#b89a6a',
  '#fcd34d',
]

const WORD_CLOUD_PALETTE_LIGHT = [
  '#0f766e',
  '#b45309',
  '#0369a1',
  '#63bfb7',
  '#047857',
  '#a16207',
  '#7c3aed',
]

function decorateWordCloudData(wordData, selectedName, isDark) {
  const sel = (selectedName || '').trim()
  const palette = isDark ? WORD_CLOUD_PALETTE_DARK : WORD_CLOUD_PALETTE_LIGHT
  return (wordData || []).map((d) => {
    const name = d.name
    const hi = !!(sel && name === sel)
    return {
      name,
      value: d.value,
      textStyle: {
        color: hi ? '#fbbf24' : palette[hashHue(name) % palette.length],
        fontWeight: hi ? 900 : 600,
        ...(hi
          ? {
              textBorderColor: isDark ? 'rgba(15, 23, 42, 0.92)' : 'rgba(51, 50, 46, 0.45)',
              textBorderWidth: 1,
            }
          : {}),
      },
    }
  })
}

function buildWordCloudOption(isDark, wordData, selectedKeyword = '') {
  const cloudData = decorateWordCloudData(wordData, selectedKeyword, isDark)

  return {
    backgroundColor: 'transparent',
    tooltip: {
      show: true,
      backgroundColor: isDark ? 'rgba(15, 23, 42, 0.94)' : 'rgba(255, 255, 255, 0.96)',
      borderColor: 'rgba(99, 191, 183, 0.45)',
      textStyle: { color: isDark ? '#e2e8f0' : '#0f172a', fontSize: 12 },
    },
    series: [
      {
        type: 'wordCloud',
        shape: 'circle',
        keepAspect: false,
        left: 'center',
        top: 'center',
        width: '96%',
        height: '92%',
        sizeRange: isDark ? [13, 48] : [12, 44],
        rotationRange: [-42, 42],
        rotationStep: 9,
        gridSize: 10,
        drawOutOfBound: false,
        layoutAnimation: true,
        textStyle: {
          fontFamily: 'system-ui, "Segoe UI", sans-serif',
          fontWeight: 600,
        },
        emphasis: {
          textStyle: {
            shadowBlur: 12,
            shadowColor: isDark ? 'rgba(99, 191, 183, 0.55)' : 'rgba(15, 118, 110, 0.35)',
          },
        },
        data: cloudData,
      },
    ],
  }
}

function buildSalaryBarOption(isDark, barData) {
  const labels = barData.map((b) => b.label)
  const counts = barData.map((b) => b.count)
  const axisColor = isDark ? 'rgba(148, 163, 184, 0.75)' : 'rgba(51, 50, 46, 0.65)'
  const splitLine = isDark ? 'rgba(99, 191, 183, 0.12)' : 'rgba(15, 23, 42, 0.08)'

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: isDark ? 'rgba(15, 23, 42, 0.94)' : 'rgba(255, 255, 255, 0.96)',
      borderColor: 'rgba(99, 191, 183, 0.45)',
      textStyle: { color: isDark ? '#e2e8f0' : '#0f172a' },
    },
    grid: { left: 48, right: 16, top: 20, bottom: 28, containLabel: true },
    xAxis: {
      type: 'category',
      data: labels,
      axisLine: { lineStyle: { color: axisColor } },
      axisTick: { show: false },
      axisLabel: { color: axisColor, fontSize: 11, interval: 0, rotate: labels.length > 6 ? 28 : 0 },
    },
    yAxis: {
      type: 'value',
      name: '岗位数',
      nameTextStyle: { color: axisColor, fontSize: 11 },
      axisLine: { show: false },
      axisLabel: { color: axisColor, fontSize: 11 },
      splitLine: { lineStyle: { color: splitLine, type: 'dashed' } },
    },
    series: [
      {
        type: 'bar',
        data: counts,
        barMaxWidth: 36,
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: isDark ? '#fbbf24' : '#d97706' },
            { offset: 0.55, color: isDark ? '#63bfb7' : '#14b8a6' },
            { offset: 1, color: isDark ? 'rgba(99, 191, 183, 0.35)' : 'rgba(20, 184, 166, 0.45)' },
          ]),
          shadowBlur: isDark ? 14 : 0,
          shadowColor: isDark ? 'rgba(251, 191, 36, 0.25)' : 'transparent',
        },
      },
    ],
  }
}

const wordCloudRef = ref(null)
const salaryChartRef = ref(null)
const statsPayload = ref({
  wordData: [...DEFAULT_STATS_WORDS],
  barData: [...DEFAULT_STATS_SALARY],
})
const statsHint = ref('')
/** 词云点击后同步搜索并高亮该词 */
const selectedWordCloudKeyword = ref('')
let wordCloudChart = null
let salaryBarChart = null
let statsResizeObserver = null

function disposeStatsCharts() {
  if (statsResizeObserver) {
    statsResizeObserver.disconnect()
    statsResizeObserver = null
  }
  if (wordCloudChart) {
    wordCloudChart.dispose()
    wordCloudChart = null
  }
  if (salaryBarChart) {
    salaryBarChart.dispose()
    salaryBarChart = null
  }
}

function bindWordCloudChartClick() {
  if (!wordCloudChart) return
  wordCloudChart.off('click')
  wordCloudChart.on('click', (params) => {
    if (params.seriesType !== 'wordCloud' || !params.name) return
    selectedWordCloudKeyword.value = String(params.name)
    searchKeyword.value = String(params.name)
    page.value = 1
    updateStatsCharts()
  })
}

function updateStatsCharts() {
  const isDark = theme.value === 'dark'
  const { wordData, barData } = statsPayload.value
  if (wordCloudChart && wordData?.length) {
    wordCloudChart.setOption(
      buildWordCloudOption(isDark, wordData, selectedWordCloudKeyword.value),
      true
    )
    bindWordCloudChartClick()
  }
  if (salaryBarChart && barData?.length) {
    salaryBarChart.setOption(buildSalaryBarOption(isDark, barData), true)
  }
}

function initStatsCharts() {
  if (!wordCloudRef.value || !salaryChartRef.value) return
  if (!wordCloudChart) {
    wordCloudChart = echarts.init(wordCloudRef.value, null, { renderer: 'canvas' })
  }
  if (!salaryBarChart) {
    salaryBarChart = echarts.init(salaryChartRef.value, null, { renderer: 'canvas' })
  }
  updateStatsCharts()
  if (!statsResizeObserver && wordCloudRef.value?.parentElement) {
    const wrap = wordCloudRef.value.closest('.stats-dashboard')
    if (wrap) {
      statsResizeObserver = new ResizeObserver(() => {
        wordCloudChart?.resize()
        salaryBarChart?.resize()
      })
      statsResizeObserver.observe(wrap)
    }
  }
}

async function loadJobStats() {
  statsHint.value = ''
  try {
    const res = await getJobsStats()
    const normalized = normalizeJobStatsResponse(res)
    if (normalized) {
      statsPayload.value = normalized
      statsHint.value = ''
    } else {
      statsPayload.value = {
        wordData: [...DEFAULT_STATS_WORDS],
        barData: [...DEFAULT_STATS_SALARY],
      }
      statsHint.value = '统计接口返回为空，已展示示意数据。'
    }
  } catch (e) {
    statsPayload.value = {
      wordData: [...DEFAULT_STATS_WORDS],
      barData: [...DEFAULT_STATS_SALARY],
    }
    statsHint.value = `${normalizeText(formatJobPortraitApiError(e), '统计接口不可用')}，当前为本地示意数据。`
  } finally {
    await nextTick()
    initStatsCharts()
  }
}

watch(
  () => [theme.value, statsPayload.value],
  () => {
    nextTick(() => updateStatsCharts())
  },
  { deep: true }
)

const baseJobs = [
  { id: 1, name: '物联网调试师', field: '万物智联', company: '重庆森什么什么公司' },
  { id: 2, name: '数据分析师', field: '数据智能', company: '某科技发展有限公司' },
  { id: 3, name: '算法工程师', field: 'AI 算法', company: 'AI 科技有限责任公司' },
  { id: 4, name: '产品经理', field: '数智产品', company: '创新产品科技公司' },
  { id: 5, name: '前端工程师', field: 'Web 交互', company: '互联网信息技术有限公司' },
  { id: 6, name: '后端工程师', field: '云端服务', company: '云服务科技有限公司' },
  { id: 7, name: '大数据工程师', field: '海量数据', company: '大数据技术公司' },
  { id: 8, name: '运维工程师', field: '系统稳定', company: '信息运维服务公司' },
  { id: 9, name: '测试工程师', field: '质量保障', company: '软件测试服务公司' },
  { id: 10, name: 'UX 设计师', field: '体验设计', company: '用户体验设计工作室' }
]

function mapRawJobsToCards(list) {
  return list.map((raw, idx) => ({
    id: raw.id ?? `idx_${idx}`,
    name: normalizeText(raw.title, `岗位${idx + 1}`),
    field: fieldFromTags(raw.field_tags),
    company: normalizeText(raw.company, '—'),
    coverUrl: (() => {
      const name = normalizeText(raw.title, `岗位${idx + 1}`)
      const field = fieldFromTags(raw.field_tags)
      const url = normalizeText(
        raw.hero_image || raw.cover_url || raw.image || raw.thumbnail || '',
        ''
      )
      if (isJavaJob(name, field)) return javaJobPortrait
      if (isCppJob(name, field)) return cppJobPortrait
      if (isImplementationJob(name, field)) return implementationJobPortrait
      if (isHardwareTestJob(name, field)) return hardwareTestJobPortrait
      if (isFrontendJob(name, field)) return frontendJobPortrait
      if (isTechSupportJob(name, field)) return techSupportJobPortrait
      if (isGeneralTestEngineerJob(name, field)) return testEngineerJobPortrait
      if (isResearcherJob(name, field)) return researcherJobPortrait
      if (isContentReviewJob(name, field)) return contentReviewJobPortrait
      if (isQaJob(name, field)) return qaJobPortrait
      return url
    })(),
  }))
}

const cachedRawJobs = loadJobListFromCache()
const jobs = ref(cachedRawJobs.length ? mapRawJobsToCards(cachedRawJobs) : [...baseJobs])
const loadingJobs = ref(false)
const jobsError = ref('')
const isUsingMockFallback = ref(!cachedRawJobs.length)

const activeCardId = ref(null)

const searchKeyword = ref('')
const sortBy = ref('default')
const page = ref(1)
const pageSize = ref(8)

const filteredJobs = computed(() => {
  let list = jobs.value
  const q = searchKeyword.value.trim().toLowerCase()
  if (q) {
    list = list.filter(
      (j) =>
        j.name.toLowerCase().includes(q) ||
        j.company.toLowerCase().includes(q) ||
        j.field.toLowerCase().includes(q),
    )
  }
  const arr = [...list]
  if (sortBy.value === 'nameAsc') {
    arr.sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'))
  } else if (sortBy.value === 'nameDesc') {
    arr.sort((a, b) => b.name.localeCompare(a.name, 'zh-CN'))
  }
  return arr
})

const totalFiltered = computed(() => filteredJobs.value.length)
const hasRenderableJobs = computed(() => Array.isArray(jobs.value) && jobs.value.length > 0)

const pagedJobs = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return filteredJobs.value.slice(start, start + pageSize.value)
})

watch([searchKeyword, sortBy], () => {
  page.value = 1
})

watch(searchKeyword, (q) => {
  const t = String(q || '').trim()
  if (selectedWordCloudKeyword.value && t !== selectedWordCloudKeyword.value) {
    selectedWordCloudKeyword.value = ''
    updateStatsCharts()
  }
})

function fieldFromTags(tags) {
  if (!Array.isArray(tags) || !tags.length) return '泛行业'
  const t = tags[0]
  return String(t).replace(/\s+/g, '').slice(0, 8) || '泛行业'
}

function isJavaJob(jobName, field) {
  const s = `${jobName || ''} ${field || ''}`
  return /java/i.test(s)
}

function isQaJob(jobName, field) {
  const s = `${jobName || ''} ${field || ''}`
  // 软件测试/QA（优先级低于“测试工程师/测试开发”，避免覆盖）
  return /(软件测试|qa|quality assurance)/i.test(s)
}

function isCppJob(jobName, field) {
  const s = `${jobName || ''} ${field || ''}`
  return /(c\/c\+\+|c\+\+|\\bc\\b|嵌入式|系统开发|驱动开发|底层|linux内核|rtos)/i.test(s)
}

function isImplementationJob(jobName, field) {
  const s = `${jobName || ''} ${field || ''}`
  return /(实施工程师|系统实施|实施顾问|部署工程师|交付工程师|运维实施|上线实施|deployment)/i.test(s)
}

function isHardwareTestJob(jobName, field) {
  const s = `${jobName || ''} ${field || ''}`
  return /(硬件测试|板级测试|芯片验证|可靠性测试|信号完整性|硬件验证|hardware test|verification)/i.test(s)
}

function isFrontendJob(jobName, field) {
  const s = `${jobName || ''} ${field || ''}`
  return /(前端开发|前端工程师|web前端|web 前端|frontend|front-end)/i.test(s)
}

function isTechSupportJob(jobName, field) {
  const s = `${jobName || ''} ${field || ''}`
  return /(技术支持工程师|技术支持|技术服务|support engineer|technical support)/i.test(s)
}

function isGeneralTestEngineerJob(jobName, field) {
  const s = `${jobName || ''} ${field || ''}`
  if (/(硬件测试|板级测试|芯片验证|可靠性测试|信号完整性|硬件验证|hardware test|verification)/i.test(s)) return false
  return /(测试工程师|测试开发|test engineer|testing engineer)/i.test(s)
}

function isResearcherJob(jobName, field) {
  const s = `${jobName || ''} ${field || ''}`
  return /(科研人员|科学研究人员|研究员|科研工程师|scientist|researcher)/i.test(s)
}

function isContentReviewJob(jobName, field) {
  const s = `${jobName || ''} ${field || ''}`
  return /(内容审核|内容审查|审核专员|风控审核|content moderator|content review)/i.test(s)
}

async function loadJobsFromApi() {
  loadingJobs.value = true
  jobsError.value = ''

  try {
    const res = await getRecommendJobList()
    const list = extractJobsArray(res)
    if (Array.isArray(list) && list.length) {
      saveJobListCache(list)
      jobs.value = mapRawJobsToCards(list)
      isUsingMockFallback.value = false
    } else {
      jobsError.value = '岗位列表为空'
      jobs.value = [...baseJobs]
      isUsingMockFallback.value = true
    }
  } catch (e) {
    jobsError.value = normalizeText(formatJobPortraitApiError(e), '列表接口不可用')
    jobs.value = [...baseJobs]
    isUsingMockFallback.value = true
  } finally {
    loadingJobs.value = false
  }
}

onMounted(() => {
  loadJobsFromApi()
  nextTick(() => {
    initStatsCharts()
  })
  loadJobStats()
})

onBeforeUnmount(() => {
  disposeStatsCharts()
})

const goToJob = (job) => {
  router.push({
    name: 'JobDetail',
    params: { id: job.id },
    query: { title: job.name }
  })
}
</script>

<style scoped>
.jobs-view {
  --u-border-radius: 12px;

  width: 100vw;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--u-body-bg);
  color: var(--u-black);
  font-family: var(--font-family-sans);
}

.jobs-view.dark {
  background: var(--dm-bg);
  color: var(--dm-text);
}

.header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 2vw;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(12px);
  border-bottom: var(--u-border);
}

.jobs-view.dark .header {
  background: var(--dm-header-bg);
  backdrop-filter: blur(12px);
  border-bottom-color: var(--dm-border);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 2vw;
}

.logo-main {
  font-size: clamp(20px, 1.5vw, 28px);
  font-weight: 700;
  letter-spacing: 2px;
}

.nav {
  display: flex;
  gap: 1.5vw;
}

.nav-item {
  font-size: clamp(16px, 1.05vw, 19px);
  color: inherit;
  text-decoration: none;
  position: relative;
  padding-bottom: 4px;
}

.nav-item.active {
  color: var(--u-black);
}

.nav-item.active::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  height: 2px;
  width: 100%;
  background-color: var(--u-black);
}

.jobs-view.dark .nav-item {
  color: var(--dm-text);
}

.jobs-view.dark .nav-item.active {
  color: var(--dm-accent);
}

.jobs-view.dark .nav-item.active::after {
  background-color: var(--dm-accent);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-back {
  font-size: clamp(15px, 0.95vw, 17px);
}

.logo {
  text-decoration: none;
  color: inherit;
}

.theme-toggle {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  background: #f0f2f8;
  padding: 4px;
  font-size: 12px;
}

.jobs-view.dark .theme-toggle {
  background: var(--dm-surface);
}

.theme-option {
  padding: 4px 12px;
  border-radius: 999px;
  cursor: pointer;
  color: #666;
}

.theme-option.active {
  background: #111827;
  color: #fff;
}

.jobs-view.dark .theme-option.active:last-child {
  background: var(--dm-surface-elevated);
  color: var(--dm-text);
}

.page-scroll {
  padding: 32px 6vw 48px;
  flex: 1;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.page-bottom-intro {
  margin-top: 48px;
  padding: 24px 0 16px;
  text-align: center;
  max-width: 720px;
  margin-left: auto;
  margin-right: auto;
}

.bottom-intro-text {
  font-size: var(--fs-body);
  font-weight: var(--fw-body);
  color: #64748b;
  line-height: 1.65;
  margin-bottom: 10px;
}

.jobs-view.dark .bottom-intro-text {
  color: var(--dm-text-secondary);
}

.bottom-intro-sub {
  font-size: var(--fs-small);
  font-weight: var(--fw-body);
  color: #94a3b8;
  line-height: 1.5;
}

.jobs-view.dark .bottom-intro-sub {
  color: var(--dm-text-muted);
}

.site-footer {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid rgba(148, 163, 184, 0.35);
  font-size: var(--fs-small);
  font-weight: var(--fw-body);
  color: #94a3b8;
  text-align: center;
  width: 100%;
}

.jobs-view.dark .site-footer {
  border-top-color: var(--dm-border);
  color: var(--dm-text-muted);
}

.hero-title-area {
  text-align: center;
  margin-bottom: 32px;
}

.page-title {
  font-size: var(--fs-h1);
  font-weight: var(--fw-heading);
  letter-spacing: 2px;
  margin-bottom: 12px;
}

.page-intro {
  font-size: var(--fs-body);
  font-weight: var(--fw-body);
  line-height: 1.6;
  width: 90%;
  max-width: 1200px;
  margin: 0 auto 20px;
  color: rgba(51, 50, 46, 0.78);
}

.jobs-view.dark .page-intro {
  color: var(--dm-text-secondary);
}

.icon-row {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 15px;
}

.small-icon {
  font-size: 12px;
  opacity: 0.8;
}

.stats-dashboard {
  width: 90%;
  max-width: 1600px;
  margin: 36px auto 28px;
  padding: 0 0 8px;
}

.stats-dashboard-heading {
  margin: 0 0 8px;
  font-size: clamp(18px, 1.25vw, 22px);
  font-weight: 800;
  letter-spacing: 0.06em;
  text-align: center;
  background: linear-gradient(90deg, #0f172a 0%, #63bfb7 45%, #d97706 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.jobs-view.dark .stats-dashboard-heading {
  background: linear-gradient(90deg, #e2e8f0 0%, #63bfb7 40%, #fbbf24 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.stats-dashboard-lead {
  margin: 0 auto 18px;
  max-width: 920px;
  text-align: center;
  font-size: 13px;
  line-height: 1.55;
  color: rgba(51, 50, 46, 0.62);
}

.jobs-view.dark .stats-dashboard-lead {
  color: var(--dm-text-secondary);
}

.stats-code {
  font-size: 12px;
  padding: 1px 6px;
  border-radius: 6px;
  background: rgba(99, 191, 183, 0.12);
  border: 1px solid rgba(99, 191, 183, 0.28);
}

.jobs-view.dark .stats-code {
  background: rgba(99, 191, 183, 0.1);
  border-color: rgba(99, 191, 183, 0.35);
  color: var(--dm-text-secondary);
}

.stats-dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  align-items: stretch;
}

@media (max-width: 900px) {
  .stats-dashboard-grid {
    grid-template-columns: 1fr;
  }
}

.stats-card {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(99, 191, 183, 0.32);
  border-radius: 14px;
  padding: 15px 16px 12px;
  backdrop-filter: blur(12px);
  box-shadow: 0 0 0 1px rgba(251, 191, 36, 0.06), 0 12px 40px rgba(15, 23, 42, 0.08);
}

.jobs-view.dark .stats-card {
  background: rgba(15, 23, 42, 0.55);
  border-color: rgba(99, 191, 183, 0.38);
  box-shadow:
    0 0 0 1px rgba(251, 191, 36, 0.12),
    0 0 28px rgba(99, 191, 183, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.stats-title {
  margin: 0 0 4px;
  font-size: 15px;
  font-weight: 800;
  letter-spacing: 0.02em;
  color: rgba(15, 23, 42, 0.92);
}

.jobs-view.dark .stats-title {
  color: var(--dm-text);
}

.stats-sub {
  margin: 0 0 10px;
  font-size: 12px;
  color: rgba(51, 50, 46, 0.55);
}

.jobs-view.dark .stats-sub {
  color: var(--dm-text-secondary);
}

.chart-box {
  height: 260px;
  width: 100%;
  min-height: 220px;
}

.stats-hint {
  margin: 14px 0 0;
  text-align: center;
  font-size: 12px;
  line-height: 1.5;
  color: rgba(180, 83, 9, 0.9);
}

.jobs-view.dark .stats-hint {
  color: #fcd34d;
}

.jobs-grid {
  width: 90%;
  max-width: 1600px;
  margin: 0 auto;
}

.status-panel {
  width: 90%;
  max-width: 1600px;
  margin: 0 auto 12px;
  border: var(--u-border);
  box-shadow: var(--u-box-shadow);
  border-radius: 12px;
  background: var(--u-bg-normal);
  padding: 10px 14px;
}

.status-text {
  margin: 0;
  color: rgba(51, 50, 46, 0.8);
  font-size: clamp(14px, 0.95vw, 16px);
  line-height: 1.6;
}

.status-error {
  color: #b42318;
}

.job-row {
  display: flex;
  flex-wrap: wrap;
}

.job-col {
  display: flex;
  margin-bottom: 24px;
}

/* 统一卡片尺寸：一行四个、占宽 75%，卡片稍长 */
.job-card {
  width: 100%;
  height: 100%;
  min-height: 340px;
  display: flex;
  flex-direction: column;
  border-radius: 18px;
  overflow: hidden;
  padding: 0;
  background: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
  border: var(--u-border);
  box-shadow: var(--u-box-shadow);
  user-select: none;
}

.jobs-view.dark .job-card {
  background: var(--dm-gradient-card);
  border-color: var(--dm-border);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

/* 悬停：上浮 + 阴影 + 边框高亮 */
.job-card:hover {
  transform: translateY(-6px);
  box-shadow: 6px 6px 0px var(--u-black);
  border-color: var(--u-black);
}

.jobs-view.dark .job-card:hover {
  border-color: var(--dm-border-accent);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.3), 0 0 24px rgba(167, 139, 250, 0.1);
}

/* 点击瞬间反馈 */
.job-card:active {
  transform: translateY(-2px) scale(0.98);
}

.job-card.is-active {
  border-color: var(--u-black);
}

.jobs-view.dark .job-card.is-active {
  border-color: var(--dm-accent);
}

.jobs-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
  align-items: center;
}

.jobs-search {
  flex: 1;
  min-width: 200px;
  max-width: 420px;
}

.jobs-sort {
  width: 168px;
}

.jobs-view.dark :deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: transparent;
  --el-table-fixed-box-shadow: none;
  --el-table-border-color: rgba(255, 255, 255, 0.08);
  --el-table-row-hover-bg-color: rgba(255, 255, 255, 0.04);
  background: transparent;
}

.jobs-view.dark :deep(.el-table th.el-table__cell),
.jobs-view.dark :deep(.el-table td.el-table__cell) {
  background: transparent;
  border-bottom-color: rgba(255, 255, 255, 0.08);
}

.jobs-view.dark :deep(.jobs-search .el-input__wrapper) {
  background: #111827;
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.12) inset;
}

.jobs-view.dark :deep(.jobs-search .el-input__inner) {
  color: #ffffff;
}

.jobs-view.dark :deep(.jobs-search .el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.58);
}

.job-skeleton-card {
  min-height: 340px;
  padding: 16px;
  border-radius: 18px;
  border: var(--u-border);
  background: rgba(255, 255, 255, 0.9);
}

.jobs-view.dark .job-skeleton-card {
  background: var(--dm-surface-card);
  border-color: var(--dm-border);
}

.jobs-pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 12px;
  padding-bottom: 20px;
}

/* 图片区：统一高度，稍长 */
.job-image-wrap {
  flex-shrink: 0;
  /* 稍微加大图片占比，但不改变卡片整体尺寸 */
  height: 210px;
  overflow: hidden;
  background: var(--u-bg-normal);
}

.job-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  /* 轻微提亮，避免整体视觉偏“沉” */
  filter: brightness(1.08) saturate(0.92) contrast(0.98);
}

.job-image-placeholder {
  flex-shrink: 0;
  height: 210px;
  background: rgba(255, 255, 255, 0.72); /* 纯色：避免蓝色系，且更浅 */
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 纯色交替：米色/粉色/薄荷绿/浅红（仍使用 Uiineed 色板） */
.job-col:nth-child(4n + 2) .job-image-placeholder {
  background: rgba(255, 248, 225, 0.78); /* 米色系更浅 */
}

.job-col:nth-child(4n + 3) .job-image-placeholder {
  background: rgba(255, 235, 248, 0.78); /* 粉色系更浅 */
}

.job-col:nth-child(4n) .job-image-placeholder {
  background: rgba(220, 245, 234, 0.78); /* 薄荷绿系更浅 */
}

.placeholder-text {
  font-size: 18px;
  color: var(--u-placeholder);
}

.jobs-view.dark .job-image-placeholder {
  background: rgba(255, 255, 255, 0.06);
  border-bottom: 1px solid var(--dm-border);
}

.jobs-view.dark .placeholder-text {
  color: var(--dm-text-secondary);
}

/* 暗色模式下仍保持纯色（用低透明度来保证对比度，不使用蓝色） */
.jobs-view.dark .job-col:nth-child(4n + 2) .job-image-placeholder {
  background: rgba(255, 214, 233, 0.30);
}

.jobs-view.dark .job-col:nth-child(4n + 3) .job-image-placeholder {
  background: rgba(208, 244, 240, 0.30);
}

.jobs-view.dark .job-col:nth-child(4n) .job-image-placeholder {
  background: rgba(255, 240, 238, 0.30);
}

/* 信息区：统一 padding，底部对齐「查看详情」 */
.job-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 18px 20px 20px;
  background: transparent;
  color: var(--u-black);
  min-height: 120px; /* 配合图片高度增加，避免卡片被撑高 */
}

.jobs-view.dark .job-info {
  background: transparent;
  color: var(--dm-text);
}

.jobs-view.dark .job-subtitle,
.jobs-view.dark .job-company {
  color: var(--dm-text-secondary);
}

.jobs-view.dark .highlight {
  color: var(--dm-accent);
}

.job-name {
  font-size: clamp(18px, 1.2vw, 22px);
  font-weight: 700;
  margin-bottom: 6px;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.job-subtitle {
  font-size: clamp(16px, 1.05vw, 18px);
  color: var(--u-placeholder);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.highlight {
  color: var(--u-black);
  background: var(--u-bg-submit);
  border: var(--u-border);
  box-shadow: 2px 2px 0px var(--u-black);
  padding: 0 6px;
  border-radius: 999px;
  margin-left: 4px;
}

.job-company {
  font-size: clamp(15px, 0.95vw, 17px);
  color: var(--u-placeholder);
  margin-bottom: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.job-action {
  margin-top: auto;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: clamp(14px, 0.95vw, 16px);
  color: var(--u-black);
  font-weight: 500;
}

.jobs-view.dark .job-action {
  color: var(--dm-accent);
}

.job-card:hover .action-arrow {
  transform: translateX(4px);
}

.action-arrow {
  display: inline-block;
  transition: transform 0.2s ease;
}

@media (max-width: 1200px) {
  .jobs-grid {
    width: 90%;
  }
}

@media (max-width: 900px) {
  .nav {
    display: none;
  }

  .page-scroll {
    padding-inline: 16px;
  }

  .jobs-grid {
    width: 100%;
  }

  .job-card {
    min-height: 300px;
  }

  .job-image-placeholder {
    height: 140px;
  }

  .job-info {
    min-height: 140px;
  }
}
</style>
