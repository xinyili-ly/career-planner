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
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useTheme } from '../composables/useTheme'
import AppHeader from '../components/AppHeader.vue'
import { getRecommendJobList } from '../api/jobPortraitApi'
import { formatJobPortraitApiError } from '../api/jobPortraitErrors'
import {
  extractJobsArray,
  loadJobListFromCache,
  normalizeText,
  saveJobListCache,
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
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
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
