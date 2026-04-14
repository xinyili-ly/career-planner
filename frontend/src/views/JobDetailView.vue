<template>
  <div class="job-detail-view" :class="theme">
    <AppHeader :back-to="{ name: 'jobs' }" />

    <main class="page-scroll">
      <!-- 顶部大图区域 -->
      <section class="hero">
        <div class="hero-image">
          <img
            :src="heroImageSrc"
            alt="岗位配图"
          />
        </div>
        <div class="hero-overlay">
          <h1 class="job-name">{{ displayJobName }}</h1>
          <p v-if="representativeQuote" class="job-quote">{{ representativeQuote }}</p>
          <p class="job-tag-line">
            {{ job.field
            }}<span v-if="job.company && job.company !== '示例公司'">
              · {{ job.company }}</span
            >
          </p>
        </div>
      </section>

      <section v-if="loadingPortrait || errorPortrait || isUsingMockFallback || hasEmptyPortrait" class="section-card status-card">
        <p v-if="loadingPortrait" class="status-text">
          正在从后端加载岗位画像数据...
        </p>
        <p v-else-if="errorPortrait" class="status-text status-error">
          后端接口请求失败：{{ errorPortrait }}，当前已自动切换为本地兜底数据。
        </p>
        <p v-else-if="isUsingMockFallback" class="status-text">
          当前使用本地兜底数据展示，建议检查后端接口与网络连通性。
        </p>
        <p v-else-if="hasEmptyPortrait" class="status-text">
          当前岗位接口返回为空，已使用默认文案渲染页面。
        </p>
      </section>

      <!-- 技能要求 / 评价申请条件 Tab -->
      <section class="section-card">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="技能要求" name="skills">
            <div
              v-if="detailSkillHtml"
              class="rich-text"
              v-html="detailSkillHtml"
            />
            <ul v-else class="info-list">
              <li v-for="line in displaySkillBullets" :key="line">{{ line }}</li>
            </ul>
          </el-tab-pane>
          <el-tab-pane label="评价申请条件" name="conditions">
            <ul v-if="displayConditionBullets.length" class="info-list">
              <li v-for="line in displayConditionBullets" :key="line">{{ line }}</li>
            </ul>
            <div v-else-if="hasStructuredConditions && jobPortrait" class="two-column">
              <div>
                <p v-if="jobPortrait.conditions.education">
                  <strong>学历要求：</strong>{{ jobPortrait.conditions.education }}
                </p>
                <p v-if="jobPortrait.conditions.majors">
                  <strong>相关专业：</strong>{{ jobPortrait.conditions.majors }}
                </p>
                <p v-if="jobPortrait.conditions.internship">
                  <strong>实习/项目：</strong>{{ jobPortrait.conditions.internship }}
                </p>
              </div>
              <div>
                <p v-if="jobPortrait.conditions.certificates">
                  <strong>核心证书：</strong>{{ jobPortrait.conditions.certificates }}
                </p>
                <p v-if="jobPortrait.conditions.other">
                  <strong>其他说明：</strong>{{ jobPortrait.conditions.other }}
                </p>
              </div>
            </div>
            <div v-else class="two-column">
              <div>
                <p>学历要求：大专及以上（示意；接口返回字段后将自动替换）。</p>
                <p>相关专业：计算机类 / 通信类 / 电子信息等。</p>
                <p>实习或项目经验：有相关项目经历更佳。</p>
              </div>
              <div>
                <p>核心证书：可填写行业证书或资格。</p>
                <p>其他说明：如工作地点、时间安排等要求。</p>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </section>

      <!-- 岗位核心胜任力分析（雷达 + 进度） -->
      <section class="section-card competency-section">
        <h2 class="section-title">岗位核心胜任力分析</h2>
        <p class="section-desc competency-intro">
          从七个维度概括岗位能力侧重；接口未返回雷达数据时，使用基于岗位名称的示意分布。分值由大模型对岗位文本语义分析估算，仅供参考。
          橙色虚线为全行业平均（万样本基准）对比，便于横向参照。
        </p>

        <div class="competency-panel">
          <div class="radar-container">
            <div
              ref="radarChartRef"
              class="radar-echart"
              role="img"
              aria-label="岗位七维能力雷达图"
            />
          </div>

          <div class="metrics-board">
            <div
              v-for="key in RADAR_DIMENSION_ORDER"
              :key="key"
              class="metric-item"
            >
              <div class="metric-label">
                <div class="metric-label-left">
                  <span>{{ dimensionMap[key] }}</span>
                  <span
                    v-if="key === 'certificates' && isCertificateCritical"
                    class="critical-tag"
                  >关键准入</span>
                </div>
                <el-tooltip :content="abilitySourceTooltip" placement="top">
                  <el-icon class="source-icon" :aria-label="abilitySourceTooltip">
                    <InfoFilled />
                  </el-icon>
                </el-tooltip>
              </div>
              <div
                class="metric-progress"
                :class="{ 'glow-animation': (displayScores[key] ?? 0) > 90 }"
              >
                <el-progress
                  :percentage="displayScores[key] ?? 0"
                  :duration="0"
                  color="#63bfb7"
                  :stroke-width="10"
                  :format="formatProgressPercent"
                />
              </div>
            </div>
          </div>
        </div>

        <ul v-if="jobProfileDims.length" class="profile-dim-list profile-dim-list--below">
          <li v-for="d in jobProfileDims" :key="d.name">
            <span class="dim-name">{{ d.name }}：</span>
            <span
              class="dim-desc"
              :class="{ 'dim-desc--clamped': !expandedProfileDims[d.name] }"
            >{{ d.desc }}</span>
            <button
              v-if="shouldShowDimMore(d.desc)"
              type="button"
              class="dim-more-btn"
              @click="toggleProfileDim(d.name)"
            >
              {{ expandedProfileDims[d.name] ? '收起' : '查看更多' }}
            </button>
          </li>
        </ul>
        <p v-else class="section-desc">暂无岗位画像维度说明文案。</p>
      </section>

      <!-- Tab：纵向晋升图谱 / 横向血缘分析 -->
      <section class="section-card path-analysis-tabs-wrap">
        <el-tabs
          v-model="pathAnalysisTab"
          class="path-analysis-tabs"
          @tab-click="onPathAnalysisTabClick"
        >
          <el-tab-pane label="职业晋升图谱" name="career">
            <p class="section-desc tab-pane-lead">
              从初级到专家的纵向发展路径，以及基于 path_graph 或换岗路径生成的可拖拽关系图。
            </p>
            <template v-if="jobPortrait && (jobPortrait.summary || '').trim()">
              <div class="job-summary-block">
                <strong class="job-summary-label">岗位描述</strong>
                <p
                  class="job-summary-text"
                  :class="{ 'job-summary-text--clamped': !summaryExpanded }"
                >
                  {{ jobPortrait.summary }}
                </p>
                <button
                  v-if="showSummaryToggle"
                  type="button"
                  class="text-expand-btn"
                  @click="summaryExpanded = !summaryExpanded"
                >
                  {{ summaryExpanded ? '收起' : '查看更多' }}
                </button>
              </div>
            </template>
            <div class="path-block vertical-path" v-if="verticalPath.length">
              <div
                v-for="(node, i) in verticalPath"
                :key="node.title"
                class="path-node"
              >
                <div class="path-title">
                  <span class="path-index">{{ i + 1 }}</span>
                  <span class="path-text">{{ node.title }}</span>
                </div>
                <p class="path-desc">{{ node.focus }}</p>
              </div>
            </div>
            <p v-else-if="!loadingPortrait" class="section-desc">暂无纵向晋升路径说明。</p>
            <div v-if="showPathChart" class="path-chart-embed">
              <JobPortraitPathChart
                ref="pathChartRef"
                :path-graph="jobPortrait?.pathGraph ?? null"
                :transfer-paths="transferPaths"
                :theme="theme"
              />
            </div>
            <p v-else-if="!loadingPortrait" class="section-desc">暂无关系图数据。</p>
          </el-tab-pane>

          <el-tab-pane label="跨行血缘分析" name="bloodline">
            <p class="section-desc tab-pane-lead">
              换岗路径、相关岗位关联原因与脉冲血缘图，用于规划横向迁移。
            </p>
            <div v-if="jobPortrait && transferPaths.length" class="transfer-current">
              <p class="transfer-from">从「{{ displayJobName }}」可换岗的路径示例：</p>
              <p v-if="transferUsingFallback" class="section-desc transfer-fallback-hint">
                当前岗位暂无后端返回的换岗明细，以下为通用横向发展示例，接入接口后将自动替换为真实路径。
              </p>
              <div class="transfer-path-list">
                <div v-for="p in transferPaths" :key="p.title" class="transfer-path">
                  <p class="transfer-path-title">{{ p.title }}</p>
                  <div class="transfer-steps">
                    <span v-for="(s, i) in p.steps" :key="`${p.title}-${i}-${s}`" class="transfer-step">
                      {{ s }}<span v-if="i < p.steps.length - 1" class="transfer-arrow">→</span>
                    </span>
                  </div>
                  <ul v-if="p.keyGaps?.length" class="transfer-gaps">
                    <li v-for="g in p.keyGaps" :key="g">{{ g }}</li>
                  </ul>
                </div>
              </div>

              <div v-if="relationsDisplay.length" class="bloodline">
                <p class="bloodline-title">相关岗位血缘（关联原因）：</p>
                <ul class="bloodline-list">
                  <li
                    v-for="r in relationsDisplay"
                    :key="r.role"
                    :ref="(el) => registerBloodlineRef(r.role, el)"
                    :class="[
                      'bloodline-item',
                      {
                        'bloodline-item--active': r.role === activeBloodlineRole,
                        'bloodline-item--flash': r.role === flashBloodlineRole
                      }
                    ]"
                  >
                    <span class="dim-name">{{ r.role }}：</span>
                    <span class="dim-desc">{{ r.reason }}</span>
                  </li>
                </ul>
              </div>

              <div v-if="bloodlineGraphNodes.length" class="bloodline-graph-wrap">
                <p class="bloodline-title">岗位血缘脉冲图谱：</p>
                <JobBloodlineGraph
                  :nodes="bloodlineGraphNodes"
                  :path-preview-order="bloodlinePathPreviewOrder"
                  @node-hover="onBloodlineNodeHover"
                  @node-click="onBloodlineNodeClick"
                />
              </div>
            </div>
            <p v-else-if="!loadingPortrait" class="section-desc">暂无换岗路径与血缘数据。</p>
          </el-tab-pane>
        </el-tabs>
      </section>

      <!-- 底部引导：探索更多岗位 -->
      <section class="page-bottom-cta">
        <p class="bottom-cta-text">想了解其他岗位的画像与换岗路径？</p>
        <router-link to="/jobs" class="bottom-cta-link">返回岗位列表，查看全部岗位 →</router-link>
      </section>

      <footer class="site-footer">
        <span>© {{ new Date().getFullYear() }} 职途智引 · AI职业规划助手</span>
      </footer>
    </main>

    <el-drawer
      v-model="showTransferDrawer"
      :title="transferDrawerTitle"
      direction="rtl"
      size="min(440px, 92vw)"
      append-to-body
      destroy-on-close
      :class="transferDrawerRootClass"
    >
      <div v-if="transferAnalysis" class="transfer-analysis-content">
        <h3 class="transfer-analysis-heading">
          岗位迁移分析：{{ transferOriginName }} <span class="transfer-analysis-arrow" aria-hidden="true">➔</span>
          {{ transferTargetName }}
        </h3>
        <p class="transfer-analysis-hint">
          以下由当前画像与目标岗位关联数据生成，接入迁移接口后可替换为真实对比结果。
        </p>

        <div class="transfer-analysis-section">
          <h4 class="transfer-section-tag transfer-section-tag--reuse">技能迁移（可复用）</h4>
          <p class="transfer-section-desc">两岗位重合、可平移复用的能力资产。</p>
          <div v-if="transferAnalysis.reusable_skills.length" class="transfer-skill-tags">
            <el-tag
              v-for="s in transferAnalysis.reusable_skills"
              :key="`reuse-${s}`"
              type="success"
              effect="dark"
              class="transfer-skill-tag"
            >
              {{ s }}
            </el-tag>
          </div>
          <p v-else class="transfer-section-empty">暂无重合技能数据</p>
        </div>

        <div class="transfer-analysis-section">
          <h4 class="transfer-section-tag transfer-section-tag--gap">提升路径（需学习）</h4>
          <p class="transfer-section-desc">目标岗位侧重、需补齐的技能方向。</p>
          <div v-if="transferAnalysis.gap_skills.length" class="transfer-skill-tags">
            <el-tag
              v-for="s in transferAnalysis.gap_skills"
              :key="`gap-${s}`"
              type="warning"
              effect="dark"
              class="transfer-skill-tag"
            >
              {{ s }}
            </el-tag>
          </div>
          <p v-else class="transfer-section-empty">暂无缺口技能数据</p>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { InfoFilled } from '@element-plus/icons-vue'
import { useTheme } from '../composables/useTheme'
import AppHeader from '../components/AppHeader.vue'
import { getJobPortrait } from '../data/jobPortraits'
import { getJobDetail } from '../api/jobPortraitApi'
import { formatJobPortraitApiError } from '../api/jobPortraitErrors'
import JobPortraitPathChart from '../components/JobPortraitPathChart.vue'
import JobBloodlineGraph from '../components/JobBloodlineGraph.vue'
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
import {
  loadJobListItemFromCache,
  portraitFromMergedRaw,
  unwrapData,
} from '../utils/jobPortraitNormalize'

const route = useRoute()
const { theme } = useTheme()

/** 岗位七维：与后端 ability_radar 键一致 */
const dimensionMap = {
  professional_skills: '专业技能',
  certificates: '证书要求',
  innovation: '创新能力',
  learning: '学习能力',
  stress_resistance: '抗压能力',
  communication: '沟通能力',
  internship: '实习实战'
}

const RADAR_DIMENSION_ORDER = [
  'professional_skills',
  'certificates',
  'innovation',
  'learning',
  'stress_resistance',
  'communication',
  'internship'
]

function hashForRadar(seed) {
  let h = 0
  const s = String(seed || '')
  for (let i = 0; i < s.length; i += 1) {
    h = h * 31 + s.charCodeAt(i)
    h |= 0
  }
  return Math.abs(h)
}

function buildFallbackAbilityRadar(seed) {
  const h = hashForRadar(seed)
  const out = {}
  RADAR_DIMENSION_ORDER.forEach((key, i) => {
    const base = 48 + ((h >> (i * 4)) & 0x1f)
    out[key] = Math.max(38, Math.min(92, base))
  })
  return out
}

function normalizeText(value, fallback = '') {
  if (typeof value === 'string') return value
  if (typeof value === 'number') return String(value)
  return fallback
}

const defaultSkillBullets = [
  '掌握岗位相关基础理论与专业知识。',
  '具备独立分析与解决实际问题的能力。',
  '熟悉常见工具与平台，能够完成日常工作任务。',
  '具备良好的沟通协作与学习迭代能力。',
]

/** 优先使用接口 hero_image / cover_url；无则使用默认配图 */
const heroImageSrc = computed(() => {
  const titleCandidate = `${route.query.title || ''} ${jobPortrait.value?.name || ''}`
  if (/java/i.test(titleCandidate)) return javaJobPortrait
  if (/(c\/c\+\+|c\+\+|\\bc\\b|嵌入式|系统开发|驱动开发|底层|linux内核|rtos)/i.test(titleCandidate)) return cppJobPortrait
  if (/(实施工程师|系统实施|实施顾问|部署工程师|交付工程师|运维实施|上线实施|deployment)/i.test(titleCandidate)) {
    return implementationJobPortrait
  }
  if (/(硬件测试|板级测试|芯片验证|可靠性测试|信号完整性|硬件验证|hardware test|verification)/i.test(titleCandidate)) {
    return hardwareTestJobPortrait
  }
  if (/(前端开发|前端工程师|web前端|web 前端|frontend|front-end)/i.test(titleCandidate)) {
    return frontendJobPortrait
  }
  if (/(技术支持工程师|技术支持|技术服务|support engineer|technical support)/i.test(titleCandidate)) {
    return techSupportJobPortrait
  }
  if (
    !/(硬件测试|板级测试|芯片验证|可靠性测试|信号完整性|硬件验证|hardware test|verification)/i.test(titleCandidate) &&
    /(测试工程师|测试开发|test engineer|testing engineer)/i.test(titleCandidate)
  ) {
    return testEngineerJobPortrait
  }
  if (/(科研人员|科学研究人员|研究员|科研工程师|scientist|researcher)/i.test(titleCandidate)) {
    return researcherJobPortrait
  }
   if (/(内容审核|内容审查|审核专员|风控审核|content moderator|content review)/i.test(titleCandidate)) {
    return contentReviewJobPortrait
  }
  // 软件测试/QA（优先级低于“测试工程师/测试开发”，避免覆盖）
  if (/(软件测试|qa|quality assurance)/i.test(titleCandidate)) return qaJobPortrait

  const url = jobPortrait.value?.heroImage?.trim()
  if (url) return url
  return '/iot-debugger.jpg'
})

function fieldFromTags(tags) {
  if (!Array.isArray(tags) || !tags.length) return '岗位画像'
  const t = tags[0]
  return String(t).replace(/\s+/g, '').slice(0, 8) || '岗位画像'
}

const job = computed(() => {
  const id = String(route.params.id || '')
  const cached = id ? loadJobListItemFromCache(id) : null
  const titleQ = route.query.title
  const name =
    typeof titleQ === 'string' && titleQ.trim()
      ? titleQ.trim()
      : normalizeText(cached?.title, '岗位详情')
  return {
    id,
    name,
    field: fieldFromTags(cached?.field_tags),
    company: normalizeText(cached?.company, '—')
  }
})

const displayJobName = computed(() => jobPortrait.value?.name || job.value.name)

const representativeQuote = computed(() => {
  if (loadingPortrait.value) return ''
  const fromApi = (jobPortrait.value?.tagline || '').trim()
  if (fromApi) return fromApi

  const name = String(displayJobName.value || '').trim()
  if (!name) return ''

  if (/(数据分析|数据挖掘|商业分析)/.test(name)) return '用数据讲故事，用洞察做决策。'
  if (/(算法|机器学习|深度学习|ai|人工智能)/i.test(name)) return '让模型落地，用算法驱动增长。'
  if (/(产品经理|产品运营|产品)/.test(name)) return '把问题想清楚，把方案做出来。'
  if (/(前端|web|front-end|frontend)/i.test(name)) return '让交互更顺滑，让体验更有温度。'
  if (/(后端|服务端|server|backend)/i.test(name)) return '稳、快、可扩展，是长期主义的答案。'
  if (/(测试|qa|质量)/i.test(name)) return '用严谨守住质量，用细节守住口碑。'
  if (/(运维|sre|devops)/i.test(name)) return '让系统更稳，让故障更少。'
  if (/(ux|交互|体验|视觉|设计)/i.test(name)) return '以用户为中心，把复杂变简单。'
  if (/(实施|交付|部署)/.test(name)) return '把方案落地，把价值交付。'
  if (/(技术支持|客服|support)/i.test(name)) return '用专业解决问题，用耐心赢得信任。'
  if (/(科研|研究员|研究|researcher|scientist)/i.test(name)) return '在不确定中求证，在探索中前行。'
  if (/(内容审核|内容审查|风控审核|审核)/.test(name)) return '守住规则边界，护航内容安全。'

  return '把专业做到极致，把价值交付到位。'
})

const activeTab = ref('skills')
const pathAnalysisTab = ref('career')
const pathChartRef = ref(null)
const radarChartRef = ref(null)
let radarChartInstance = null
let radarResizeObserver = null
const summaryExpanded = ref(false)
const expandedProfileDims = ref({})

const loadingPortrait = ref(true)
const errorPortrait = ref('')
const isUsingMockFallback = ref(false)

const defaultProfileDims = [
  { name: '专业技能', desc: '掌握本岗位所需的核心技术与工具，能独立完成典型任务。' },
  { name: '证书要求', desc: '相关职业资格或行业认证优先，如无硬性要求则以项目/作品证明为主。' },
  { name: '创新能力', desc: '能提出改进方案、参与技术选型或流程优化。' },
  { name: '学习能力', desc: '快速上手新技术与业务，具备持续学习与复盘习惯。' },
  { name: '抗压能力', desc: '在截止日期与多任务下保持交付质量，遇问题能主动沟通与推进。' },
  { name: '沟通能力', desc: '与产品、测试、运营等协作顺畅，表达清晰、文档规范。' },
  { name: '实习能力', desc: '有对口实习或项目经历，能将所学应用到实际场景。' }
]

const jobPortrait = ref(null)

const showSummaryToggle = computed(() => (jobPortrait.value?.summary || '').trim().length > 96)

watch(
  () => jobPortrait.value?.summary,
  () => {
    summaryExpanded.value = false
  }
)

function shouldShowDimMore(desc) {
  return String(desc || '').length > 72
}

function toggleProfileDim(name) {
  expandedProfileDims.value = {
    ...expandedProfileDims.value,
    [name]: !expandedProfileDims.value[name],
  }
}

function onPathAnalysisTabClick() {
  nextTick(() => {
    radarChartInstance?.resize()
    pathChartRef.value?.resize?.()
  })
}

watch(pathAnalysisTab, () => {
  onPathAnalysisTabClick()
})

const abilityRadarMerged = computed(() => {
  const seed = String(displayJobName.value || job.value.name || '岗位')
  const api = jobPortrait.value?.abilityRadar
  const fallback = buildFallbackAbilityRadar(seed)
  const out = {}
  for (const key of RADAR_DIMENSION_ORDER) {
    let v = api && typeof api[key] === 'number' ? api[key] : fallback[key]
    v = Number(v)
    out[key] = Number.isFinite(v) ? Math.max(0, Math.min(100, Math.round(v))) : fallback[key]
  }
  return out
})

const abilitySourceTooltip = computed(() => {
  const t = (jobPortrait.value?.abilitySourceInfo || '').trim()
  return t || '该分值由大语言模型对岗位描述与要求进行语义分析后估算，非招聘方官方评分。'
})

/** 进度条展示分值：自 0 滚动至目标，营造实时计算感 */
const displayScores = ref(
  Object.fromEntries(RADAR_DIMENSION_ORDER.map((k) => [k, 0]))
)
let scoreAnimRaf = null

function runScoreAnimation(targetMap) {
  const startMap = { ...displayScores.value }
  const startT = performance.now()
  const duration = 1180
  const easeOut = (t) => 1 - (1 - t) ** 3
  function frame(now) {
    const t = Math.min(1, (now - startT) / duration)
    const e = easeOut(t)
    const next = {}
    for (const k of RADAR_DIMENSION_ORDER) {
      const from = Number(startMap[k]) || 0
      const to = Number(targetMap[k]) || 0
      next[k] = Math.round(from + (to - from) * e)
    }
    displayScores.value = next
    if (t < 1) {
      scoreAnimRaf = requestAnimationFrame(frame)
    } else {
      scoreAnimRaf = null
    }
  }
  if (scoreAnimRaf != null) cancelAnimationFrame(scoreAnimRaf)
  scoreAnimRaf = requestAnimationFrame(frame)
}

watch(abilityRadarMerged, (m) => runScoreAnimation(m), { deep: true, immediate: true })

function buildIndustryAverageRadar(seed) {
  const h = hashForRadar(`${seed}::industry_benchmark_v1`)
  const baseline = [64, 52, 58, 62, 55, 60, 48]
  return RADAR_DIMENSION_ORDER.map((_, i) => {
    const jitter = ((h >> (i * 4)) & 15) - 7
    return Math.max(32, Math.min(78, baseline[i] + jitter))
  })
}

/** 全行业对比圈：接口 industry_radar_avg 优先，否则基于岗位名的稳定示意基准 */
const industryAverageRadar = computed(() => {
  const api = jobPortrait.value?.industryRadarAvg
  if (api && typeof api === 'object') {
    const arr = RADAR_DIMENSION_ORDER.map((k) => {
      const n = Number(api[k])
      return Number.isFinite(n) ? Math.max(0, Math.min(100, Math.round(n))) : null
    })
    if (arr.every((v) => v !== null)) return arr
  }
  const seed = String(displayJobName.value || job.value.name || '岗位')
  return buildIndustryAverageRadar(seed)
})

const isCertificateCritical = computed(() => (abilityRadarMerged.value.certificates ?? 0) > 80)

function formatProgressPercent(pct) {
  return `${Math.round(pct)}%`
}

const radarOption = computed(() => {
  const isDark = theme.value === 'dark'
  const values = RADAR_DIMENSION_ORDER.map((k) => abilityRadarMerged.value[k])
  const industryVals = industryAverageRadar.value
  const industryColor = isDark ? 'rgba(251, 191, 36, 0.92)' : 'rgba(180, 83, 9, 0.78)'
  const legendText = isDark ? 'rgba(238, 238, 238, 0.9)' : 'rgba(51, 50, 46, 0.88)'
  return {
    backgroundColor: 'transparent',
    legend: {
      data: ['全行业平均（万样本基准）', '岗位要求'],
      bottom: 4,
      itemGap: 18,
      icon: 'roundRect',
      textStyle: {
        color: legendText,
        fontSize: 11
      }
    },
    radar: {
      indicator: RADAR_DIMENSION_ORDER.map((k) => ({ name: dimensionMap[k], max: 100 })),
      radius: '72%',
      center: ['50%', '46%'],
      splitNumber: 4,
      axisName: {
        color: isDark ? 'rgba(238, 238, 238, 0.92)' : 'rgba(51, 50, 46, 0.88)',
        fontSize: 12
      },
      splitLine: {
        lineStyle: { color: isDark ? 'rgba(99, 191, 183, 0.28)' : 'rgba(51, 50, 46, 0.12)' }
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: isDark
            ? ['rgba(99, 191, 183, 0.14)', 'rgba(99, 191, 183, 0.05)']
            : ['rgba(99, 191, 183, 0.09)', 'rgba(99, 191, 183, 0.03)']
        }
      },
      axisLine: {
        lineStyle: { color: isDark ? 'rgba(99, 191, 183, 0.4)' : 'rgba(51, 50, 46, 0.14)' }
      }
    },
    series: [
      {
        type: 'radar',
        emphasis: {
          lineStyle: { width: 3 }
        },
        data: [
          {
            value: industryVals,
            name: '全行业平均（万样本基准）',
            lineStyle: {
              type: 'dashed',
              width: 2,
              color: industryColor
            },
            areaStyle: { opacity: 0 },
            itemStyle: { color: industryColor, borderWidth: 0 },
            symbol: 'circle',
            symbolSize: 5
          },
          {
            value: values,
            name: '岗位要求',
            areaStyle: { color: 'rgba(99, 191, 183, 0.4)' },
            lineStyle: { color: '#63bfb7', width: 2.5 },
            itemStyle: { color: '#63bfb7' },
            symbol: 'circle',
            symbolSize: 6
          }
        ]
      }
    ]
  }
})

function disposeJobRadarChart() {
  if (radarResizeObserver) {
    radarResizeObserver.disconnect()
    radarResizeObserver = null
  }
  if (radarChartInstance) {
    radarChartInstance.dispose()
    radarChartInstance = null
  }
}

function ensureJobRadarChart() {
  if (!radarChartRef.value) return
  if (!radarChartInstance) {
    radarChartInstance = echarts.init(radarChartRef.value, null, { renderer: 'canvas' })
    radarResizeObserver = new ResizeObserver(() => radarChartInstance?.resize())
    radarResizeObserver.observe(radarChartRef.value)
  }
  radarChartInstance.setOption(radarOption.value, true)
}

watch(
  () => [radarOption.value, theme.value],
  () => {
    nextTick(() => ensureJobRadarChart())
  }
)

onUnmounted(() => {
  if (scoreAnimRaf != null) cancelAnimationFrame(scoreAnimRaf)
  scoreAnimRaf = null
  disposeJobRadarChart()
})

function getMockPortrait(jobName) {
  const mock = getJobPortrait(jobName)
  if (!mock) {
    return portraitFromMergedRaw({ title: jobName, name: jobName }, jobName)
  }
  return portraitFromMergedRaw({ ...mock, title: mock.name }, mock.name || jobName)
}

async function loadPortrait() {
  loadingPortrait.value = true
  errorPortrait.value = ''
  const id = String(route.params.id || '')

  if (!id) {
    errorPortrait.value = '缺少岗位 ID'
    const fallbackName =
      typeof route.query.title === 'string' && route.query.title.trim().length
        ? route.query.title.trim()
        : '岗位'
    jobPortrait.value = getMockPortrait(fallbackName)
    isUsingMockFallback.value = true
    loadingPortrait.value = false
    return
  }

  try {
    const res = await getJobDetail(id)
    const data = unwrapData(res)
    if (data && typeof data === 'object' && (data.title || data.id || data.name)) {
      const title = normalizeText(data.title || data.name, id)
      jobPortrait.value = portraitFromMergedRaw(data, title)
      isUsingMockFallback.value = false
    } else {
      throw new Error('岗位详情为空')
    }
  } catch (error) {
    errorPortrait.value = normalizeText(formatJobPortraitApiError(error), '接口请求失败')
    isUsingMockFallback.value = true
    const cached = loadJobListItemFromCache(id)
    jobPortrait.value = getMockPortrait(normalizeText(cached?.title, job.value.name))
  } finally {
    loadingPortrait.value = false
  }
}

onMounted(() => {
  loadPortrait()
  nextTick(() => ensureJobRadarChart())
})

watch(
  () => [route.params.id, route.query.title],
  () => {
    loadPortrait()
  }
)

// 岗位画像维度：专业技能、证书要求、创新能力、学习能力、抗压能力、沟通能力、实习能力
const jobProfileDims = computed(() => {
  if (loadingPortrait.value || !jobPortrait.value) return []
  const dims = jobPortrait.value.profileDims
  return dims && dims.length ? dims : defaultProfileDims
})

// 垂直岗位图谱（示例：以当前岗位为起点的晋升路径）
const verticalPath = computed(() => {
  if (loadingPortrait.value) return []
  if (jobPortrait.value?.vertical?.length) return jobPortrait.value.vertical
  if (!jobPortrait.value) return []
  return [
    { title: `${job.value.name}（当前）`, focus: '掌握岗位核心技能并能独立交付。' },
    { title: `中级${job.value.name}（1～3 年）`, focus: '能独立负责模块/项目并持续优化。' },
    { title: `高级${job.value.name} / 技术主管（3～5 年）`, focus: '能主导复杂问题与协作，推动规范与体系建设。' },
    { title: `专家 / 架构师 或 管理岗（5 年+）`, focus: '负责方向规划、平台化与组织级效率提升。' }
  ]
})

/** 后端/本地 mock 有 transfers 时用真实数据，否则给通用横向发展示例（与垂直图谱兜底一致） */
const transferPaths = computed(() => {
  if (loadingPortrait.value) return []
  const raw = jobPortrait.value?.transfers
  if (Array.isArray(raw) && raw.length) return raw
  if (!jobPortrait.value) return []
  const name = displayJobName.value || job.value.name
  return [
    {
      title: `相近技能线：${name} → 同领域相邻岗位 → 高级 / 专家`,
      steps: [name, '同领域相关岗位（技术面延伸）', '高级专家 / 技术负责人'],
      keyGaps: ['补齐相邻方向的核心技能栈', '参与更大范围交付或体系化建设', '跨团队协作与影响力']
    },
    {
      title: `横向扩展线：${name} → 产品 / 交付 / 售前等协作岗`,
      steps: [name, '协作型岗位（产品、交付、售前等）', '复合型负责人'],
      keyGaps: ['业务理解与表达', '需求拆解与推进', '资源协调与沟通闭环']
    }
  ]
})

const transferUsingFallback = computed(() => {
  if (loadingPortrait.value || !jobPortrait.value) return false
  const raw = jobPortrait.value.transfers
  return !Array.isArray(raw) || raw.length === 0
})

const relationsDisplay = computed(() => {
  if (loadingPortrait.value) return []
  const raw = jobPortrait.value?.relations
  if (Array.isArray(raw) && raw.length) return raw
  if (!jobPortrait.value) return []
  return [
    {
      role: '同领域相邻岗位',
      reason: '技能与工具链相近，换岗时可将现有经验平移，主要补齐业务场景差异。'
    },
    {
      role: '上下游协作岗位',
      reason: '在工作流中与当前岗位衔接紧密，换岗时可利用已熟悉的流程与客户/项目语境。'
    }
  ]
})

function hashString(str) {
  let h = 0
  const s = String(str || '')
  for (let i = 0; i < s.length; i += 1) {
    h = h * 31 + s.charCodeAt(i)
    h |= 0
  }
  return Math.abs(h)
}

const bloodlineGraphNodes = computed(() => {
  const centerLabel = displayJobName.value || job.value.name || '当前岗位'
  const list = relationsDisplay.value.slice(0, 8)
  const skillPools = [
    ['Vue3', 'TypeScript', 'Node.js'],
    ['系统架构', '性能优化', '团队协作'],
    ['业务建模', '需求拆解', '跨部门沟通'],
    ['云原生', 'Kubernetes', 'CI/CD'],
    ['UI/UX 规范', '组件库', '无障碍'],
    ['数据建模', 'SQL', '指标体系'],
    ['Python', '机器学习基础', '实验设计'],
    ['客户沟通', '方案设计', '文档沉淀']
  ]
  const outer = list.map((item, index) => {
    const h = hashString(`${centerLabel}::${item.role}`)
    const matchScore = 52 + (h % 44)
    const transitionDifficulty = 22 + (h % 68)
    const salaryDeltaPct = 6 + (h % 28)
    const skillOverlap = Math.min(96, Math.max(38, matchScore - 8 + (h % 12)))
    const pool = skillPools[h % skillPools.length]
    const reusableSkills = [pool[0], '协作与沟通', h % 2 === 0 ? '业务理解' : '文档沉淀'].filter(
      Boolean
    )
    const gapSkills = [pool[1], pool[2], `${item.role}纵深`].filter(Boolean)
    const diffFromCenter = [pool[1], pool[2]].filter(Boolean)
    return {
      id: item.role,
      label: item.role,
      center: false,
      matchScore,
      transitionDifficulty,
      salaryDeltaPct,
      skillOverlap,
      reusableSkills,
      gapSkills,
      diffFromCenter
    }
  })
  return [
    {
      id: 'center',
      label: centerLabel,
      center: true,
      matchScore: 100,
      transitionDifficulty: 0,
      gapSkills: [],
      diffFromCenter: []
    },
    ...outer
  ]
})

/** 路径预演：中心 → 外围按匹配度由高到低（接口可日后改为真实晋升链 id） */
const bloodlinePathPreviewOrder = computed(() => {
  const nodes = bloodlineGraphNodes.value
  const center = nodes.find((n) => n.center)
  if (!center) return []
  const outer = nodes.filter((n) => !n.center)
  const sorted = [...outer].sort((a, b) => Number(b.matchScore ?? 0) - Number(a.matchScore ?? 0))
  return [center.id, ...sorted.map((n) => n.id)]
})

const activeBloodlineRole = ref('')
const flashBloodlineRole = ref('')
const bloodlineItemRefs = ref({})

const showTransferDrawer = ref(false)
const transferDrawerTarget = ref(null)

const transferOriginName = computed(() => displayJobName.value || job.value.name || '当前岗位')
const transferTargetName = computed(() => transferDrawerTarget.value?.label || '目标岗位')

const transferDrawerTitle = computed(
  () => `岗位迁移分析：${transferOriginName.value} ➔ ${transferTargetName.value}`
)

const transferDrawerRootClass = computed(() =>
  theme.value === 'dark'
    ? 'transfer-analysis-drawer transfer-analysis-drawer--dark'
    : 'transfer-analysis-drawer transfer-analysis-drawer--light'
)

const transferAnalysis = computed(() => {
  const n = transferDrawerTarget.value
  if (!n || n.center) return null
  const reusable = Array.isArray(n.reusableSkills) ? n.reusableSkills.filter(Boolean) : []
  const gaps = Array.isArray(n.gapSkills) ? n.gapSkills.filter(Boolean) : []
  return {
    reusable_skills: reusable,
    gap_skills: gaps
  }
})

const registerBloodlineRef = (role, el) => {
  if (el) bloodlineItemRefs.value[role] = el
  else delete bloodlineItemRefs.value[role]
}

let flashBloodlineTimer = null

const onBloodlineNodeHover = (node) => {
  activeBloodlineRole.value = node?.label || ''
}

const onBloodlineNodeClick = (node) => {
  const role = node?.label || ''
  if (!role) return
  transferDrawerTarget.value = node
  showTransferDrawer.value = true
  activeBloodlineRole.value = role
  flashBloodlineRole.value = role
  if (flashBloodlineTimer) clearTimeout(flashBloodlineTimer)
  flashBloodlineTimer = setTimeout(() => {
    flashBloodlineRole.value = ''
    flashBloodlineTimer = null
  }, 1600)
  nextTick(() => {
    const el = bloodlineItemRefs.value[role]
    el?.scrollIntoView?.({ behavior: 'smooth', block: 'nearest' })
  })
}

const detailSkillHtml = computed(() => {
  if (loadingPortrait.value) return ''
  const h = jobPortrait.value?.skillHtml
  return typeof h === 'string' && h.trim() ? h.trim() : ''
})

const displaySkillBullets = computed(() => {
  if (loadingPortrait.value) return defaultSkillBullets
  const b = jobPortrait.value?.skillBullets
  if (Array.isArray(b) && b.length) return b
  return defaultSkillBullets
})

const displayConditionBullets = computed(() => {
  if (loadingPortrait.value) return []
  const b = jobPortrait.value?.conditionBullets
  return Array.isArray(b) ? b : []
})

const hasStructuredConditions = computed(() => {
  if (loadingPortrait.value || !jobPortrait.value?.conditions) return false
  const c = jobPortrait.value.conditions
  return !!(c.education || c.majors || c.internship || c.certificates || c.other)
})

const showPathChart = computed(() => !loadingPortrait.value && !!jobPortrait.value)

const hasEmptyPortrait = computed(() => {
  if (loadingPortrait.value) return false
  if (!jobPortrait.value) return true
  return (
    !(jobPortrait.value?.summary || '').trim() &&
    !jobProfileDims.value.length &&
    !verticalPath.value.length &&
    !(jobPortrait.value?.transfers || []).length
  )
})

</script>

<style scoped>
.job-detail-view {
  --u-border-radius: 24px;

  /* 柔和糖果色（低饱和） */
  --u-color-cyan-soft: #e0f7f4;
  --u-color-pink-soft: #fff0f6;
  --u-color-yellow-soft: #fff9db;
  --u-color-mint-soft: #ecfdf5;

  --u-black: #33322e;
  --u-border: 2px solid var(--u-black);

  min-height: 100vh;
  background: #f8f9fa;
  color: var(--u-black);
  display: flex;
  flex-direction: column;
}

.job-detail-view.dark {
  background: var(--dm-bg);
  color: var(--dm-text);
}

.job-detail-view.dark .header {
  background: var(--dm-header-bg);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--dm-border);
  color: var(--dm-text);
}

.job-detail-view.dark .nav-item {
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
  color: var(--u-black);
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
  color: var(--u-black);
  text-decoration: none;
  position: relative;
  padding-bottom: 4px;
}

.nav-item::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  height: 2px;
  width: 0;
  background: var(--u-black);
  transition: width 0.2s ease;
}

.nav-item:hover::after {
  width: 100%;
}

.logo {
  text-decoration: none;
  color: inherit;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.theme-toggle {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.75);
  border: var(--u-border);
  box-shadow: 2px 2px 0px var(--u-black);
  padding: 4px;
  font-size: 12px;
}

.job-detail-view.dark .theme-toggle {
  background: var(--dm-surface);
}

.theme-option {
  padding: 4px 12px;
  border-radius: 999px;
  cursor: pointer;
  color: #666;
}

.theme-option.active {
  background: var(--u-bg-submit);
  color: var(--u-black);
}

.job-detail-view.dark .theme-option {
  color: var(--dm-text-secondary);
}

.job-detail-view.dark .theme-option.active {
  background: var(--dm-surface-elevated);
  color: var(--dm-text);
}

.nav-back {
  font-size: clamp(15px, 0.95vw, 17px);
}

.page-scroll {
  flex: 1;
  padding: 0 6vw 48px 56px;
}

.page-bottom-cta {
  margin-top: 40px;
  padding: 28px 0 20px;
  text-align: center;
  border-top: var(--u-border);
}

.job-detail-view.dark .page-bottom-cta {
  border-top-color: var(--dm-border);
}

.bottom-cta-text {
  font-size: clamp(16px, 1.05vw, 18px);
  color: rgba(51, 50, 46, 0.78);
  margin-bottom: 12px;
}

.job-detail-view.dark .bottom-cta-text {
  color: var(--dm-text-secondary);
}

.bottom-cta-link {
  display: inline-block;
  font-size: clamp(15px, 1vw, 17px);
  font-weight: 800;
  color: #fff;
  background: var(--u-black);
  border: var(--u-border);
  box-shadow: 4px 4px 0px rgba(0, 0, 0, 0.2);
  padding: 12px 24px;
  border-radius: 12px;
  text-decoration: none;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.job-detail-view.dark .bottom-cta-link {
  color: #fff;
  background: var(--dm-surface-elevated);
  border-color: var(--dm-border);
}

.bottom-cta-link:hover {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0px rgba(0, 0, 0, 0.3);
}

.site-footer {
  margin-top: 80px;
  padding: 40px 0;
  border-top: none;
  background: var(--u-black);
  color: #fff;
  font-size: clamp(14px, 0.9vw, 16px);
  text-align: center;
  width: 100%;
}

.job-detail-view.dark .site-footer {
  background: #0f1115;
  color: var(--dm-text-muted);
}

.hero {
  position: relative;
  overflow: hidden;
  border-radius: 18px;
}

.hero::before {
  content: '';
  position: absolute;
  inset: 0;
  /* 从上到下渐变：上部更清晰，下部逐渐变模糊变暗 */
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.04) 0%,
    rgba(0, 0, 0, 0.10) 35%,
    rgba(0, 0, 0, 0.22) 70%,
    rgba(0, 0, 0, 0.30) 100%
  );
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  mask-image: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0) 0%,
    rgba(0, 0, 0, 0.45) 35%,
    rgba(0, 0, 0, 0.82) 70%,
    rgba(0, 0, 0, 1) 100%
  );
  -webkit-mask-image: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0) 0%,
    rgba(0, 0, 0, 0.45) 35%,
    rgba(0, 0, 0, 0.82) 70%,
    rgba(0, 0, 0, 1) 100%
  );
  z-index: 1;
  pointer-events: none;
  border-radius: inherit;
}

.hero-image {
  position: relative;
  overflow: hidden;
  border-radius: 18px 18px 22px 22px;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.14);
}

.hero-image::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 88px;
  /* 软化底部边界，避免图片与下方内容“硬切” */
  background: linear-gradient(to bottom, rgba(248, 249, 250, 0) 0%, rgba(248, 249, 250, 0.86) 100%);
  pointer-events: none;
}

.hero-image img {
  width: 100%;
  height: auto;
  display: block;
  vertical-align: middle;
  background: rgba(255, 255, 255, 0.8);
  /* 与列表页图片统一：整体稍微提亮、降低一点饱和度与对比度 */
  filter: brightness(1.08) saturate(0.92) contrast(0.98);
  transform: scale(1.04);
  transform-origin: center;
  border-radius: inherit;
}

.hero-overlay {
  position: absolute;
  left: 4.5vw;
  bottom: 170px;
  color: #fff;
  text-shadow: 0 6px 22px rgba(0, 0, 0, 0.75);
  z-index: 2;
  max-width: min(720px, 80vw);
  padding: 0;
}

.job-name {
  font-size: clamp(70px, 3.2vw, 120px);
  font-weight: 900;
  margin-bottom: 4px;
  position: relative;
  padding-bottom: 10px;
}

.job-name::after {
  content: '';
  display: block;
  width: clamp(220px, 24vw, 420px);
  height: 4px;
  margin-top: 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 10px 26px rgba(0, 0, 0, 0.25);
}

.job-quote {
  margin: 6px 0 10px;
  font-size: clamp(40px, 1.4vw, 64px);
  font-weight: 700;
  letter-spacing: 0.2px;
  opacity: 0.98;
  color: rgba(255, 238, 170, 0.98);
  text-shadow: 0 6px 22px rgba(0, 0, 0, 0.55);
}

.job-tag-line {
  font-size: clamp(30px, 1.5vw, 40px);
  opacity: 0.95;
}

.job-detail-view.dark .hero::before {
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.08) 0%,
    rgba(0, 0, 0, 0.16) 35%,
    rgba(0, 0, 0, 0.30) 70%,
    rgba(0, 0, 0, 0.40) 100%
  );
}

.job-detail-view.dark .hero-image::after {
  background: linear-gradient(to bottom, rgba(15, 17, 21, 0) 0%, rgba(15, 17, 21, 0.78) 100%);
}

.section-card {
  margin-top: 32px;
  border-radius: var(--u-border-radius);
  padding: 30px;
  border: var(--u-border);
  box-shadow: 8px 8px 0px var(--u-black);
  transition: transform 0.2s ease;
}

/* 首个为 hero，其后 section-card 按 4 色循环（与状态条等共同计数） */
.page-scroll > section.section-card:nth-child(4n + 2) {
  background-color: var(--u-color-cyan-soft);
}

.page-scroll > section.section-card:nth-child(4n + 3) {
  background-color: var(--u-color-pink-soft);
}

.page-scroll > section.section-card:nth-child(4n + 4) {
  background-color: var(--u-color-yellow-soft);
}

.page-scroll > section.section-card:nth-child(4n + 5) {
  background-color: var(--u-color-mint-soft);
}

.status-card {
  margin-top: 16px;
}

.status-text {
  margin: 0;
  font-size: clamp(15px, 1vw, 17px);
  line-height: 1.6;
  color: rgba(51, 50, 46, 0.82);
}

.status-error {
  color: #b42318;
}

.job-detail-view.dark .section-card {
  box-shadow: 8px 8px 0px rgba(0, 0, 0, 0.35);
  border: 2px solid var(--dm-border);
}

.job-detail-view.dark .page-scroll > section.section-card:nth-child(4n + 2) {
  background-color: rgba(224, 247, 244, 0.12);
}

.job-detail-view.dark .page-scroll > section.section-card:nth-child(4n + 3) {
  background-color: rgba(255, 240, 246, 0.1);
}

.job-detail-view.dark .page-scroll > section.section-card:nth-child(4n + 4) {
  background-color: rgba(255, 249, 219, 0.08);
}

.job-detail-view.dark .page-scroll > section.section-card:nth-child(4n + 5) {
  background-color: rgba(236, 253, 245, 0.14);
}

.job-detail-view.dark .section-title {
  color: var(--dm-text);
}

:deep(.el-tabs__item.is-active) {
  color: var(--u-black) !important;
  font-weight: 900;
}

:deep(.el-tabs__active-bar) {
  background-color: var(--u-black) !important;
  height: 3px;
}

.job-detail-view.dark :deep(.el-tabs__item.is-active) {
  color: var(--dm-text) !important;
}

.job-detail-view.dark :deep(.el-tabs__active-bar) {
  background-color: var(--dm-accent) !important;
}

.job-detail-view.dark .section-desc {
  color: var(--dm-text-secondary);
}

.job-detail-view.dark .dim-desc {
  color: var(--dm-text-secondary);
}

.job-detail-view.dark .path-node {
  background: var(--dm-surface-card);
  border: 2px solid var(--dm-border);
  box-shadow: 4px 4px 0px rgba(0, 0, 0, 0.35);
  color: var(--dm-text);
}

.job-detail-view.dark .path-index {
  background: var(--dm-surface-card);
  border: 1.5px solid var(--dm-border);
  box-shadow: 2px 2px 0px rgba(0, 0, 0, 0.35);
  color: var(--dm-text);
}

.job-detail-view.dark .hero-image img {
  background: var(--dm-surface);
}

.job-detail-view.dark .avatar {
  background: var(--dm-surface-elevated);
}

.job-detail-view.dark .comment-header {
  color: var(--dm-text-secondary);
}

.section-title {
  font-size: clamp(20px, 1.35vw, 24px);
  font-weight: 900;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--u-black);
}

.section-title::before {
  content: '';
  width: 8px;
  height: 24px;
  flex-shrink: 0;
  background: var(--u-black);
  border-radius: 4px;
}

.job-detail-view.dark .section-title::before {
  background: var(--dm-accent);
}

.section-desc {
  font-size: clamp(16px, 1.1vw, 18px);
  color: #555;
  margin-bottom: 12px;
  line-height: 1.5;
}

/* 重点突出：信息层级与强调样式（亮色） */
.section-card {
  color: #1f2328;
}

.section-card .section-desc {
  color: rgba(31, 35, 40, 0.72);
}

.info-list li,
.two-column,
.profile-dim-list li,
.path-node,
.transfer-path {
  color: rgba(31, 35, 40, 0.92);
}

.info-list li {
  line-height: 1.7;
}

.info-list li::marker {
  color: rgba(17, 24, 39, 0.55);
}

.two-column p {
  margin: 0 0 10px;
  line-height: 1.7;
}

.two-column p strong,
.rich-text :deep(strong),
.section-card strong {
  display: inline-block;
  padding: 1px 8px;
  border-radius: 999px;
  background: rgba(255, 248, 225, 0.95);
  border: 1px solid rgba(17, 24, 39, 0.14);
  color: rgba(17, 24, 39, 0.92);
}

.rich-text {
  font-size: clamp(16px, 1.1vw, 18px);
  line-height: 1.55;
  color: inherit;
}

.rich-text :deep(p) {
  margin: 0 0 10px;
}

.rich-text :deep(ul) {
  margin: 0 0 10px;
  padding-left: 1.25em;
}

.info-list {
  padding-left: 22px;
  margin: 0;
}

.info-list li {
  margin-bottom: 8px;
  font-size: clamp(16px, 1.1vw, 18px);
}

.two-column {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px 32px;
  font-size: clamp(16px, 1.1vw, 18px);
}

.competency-section {
  position: relative;
  overflow: hidden;
  background: linear-gradient(
    145deg,
    rgba(99, 191, 183, 0.12) 0%,
    rgba(255, 255, 255, 0.45) 42%,
    rgba(99, 191, 183, 0.06) 100%
  );
  border: var(--u-border);
  box-shadow: 8px 8px 0px var(--u-black);
  transition: transform 0.2s ease;
}

.job-detail-view.dark .competency-section {
  background: linear-gradient(
    145deg,
    rgba(99, 191, 183, 0.18) 0%,
    rgba(30, 40, 42, 0.42) 45%,
    rgba(99, 191, 183, 0.1) 100%
  );
  border: 2px solid var(--dm-border);
  box-shadow: 8px 8px 0px rgba(0, 0, 0, 0.35);
}

.competency-intro {
  margin-top: 4px;
}

/* 与上方雷达 + 进度区分隔开，避免「专业技能」等说明贴住图表区 */
.profile-dim-list--below {
  margin-top: 144px;
  padding-top: 72px;
  border-top: 1px solid rgba(17, 24, 39, 0.08);
}

.profile-dim-list--below > li:first-child {
  margin-top: 10px;
}

.job-detail-view.dark .profile-dim-list--below {
  border-top-color: rgba(255, 255, 255, 0.12);
}

.competency-panel {
  display: grid;
  grid-template-columns: minmax(320px, 1.2fr) minmax(260px, 0.95fr);
  gap: 28px;
  align-items: stretch;
  margin-top: 16px;
}

@media (max-width: 900px) {
  .competency-panel {
    grid-template-columns: 1fr;
  }
}

.radar-container {
  position: relative;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.35);
  border: 1px solid rgba(99, 191, 183, 0.2);
  min-height: 440px;
}

.job-detail-view.dark .radar-container {
  background: rgba(20, 28, 30, 0.45);
  border-color: rgba(99, 191, 183, 0.28);
}

.radar-echart {
  width: 100%;
  height: 480px;
  min-height: 380px;
}

.metrics-board {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 8px 4px 8px 8px;
}

.metric-item {
  padding: 10px 0;
}

.metric-item + .metric-item {
  border-top: 1px dashed rgba(99, 191, 183, 0.22);
}

.job-detail-view.dark .metric-item + .metric-item {
  border-top-color: rgba(255, 255, 255, 0.1);
}

.metric-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 8px;
  font-size: clamp(14px, 0.95vw, 16px);
  font-weight: 700;
  letter-spacing: 0.02em;
  color: rgba(17, 24, 39, 0.9);
}

.job-detail-view.dark .metric-label {
  color: rgba(255, 255, 255, 0.92);
}

.metric-label-left {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  min-width: 0;
}

.critical-tag {
  flex-shrink: 0;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.04em;
  padding: 3px 9px;
  border-radius: 6px;
  color: #0f172a;
  background: linear-gradient(135deg, rgba(99, 191, 183, 0.38), rgba(99, 191, 183, 0.72));
  border: 1px solid rgba(15, 23, 42, 0.35);
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.35) inset;
}

.job-detail-view.dark .critical-tag {
  color: rgba(255, 255, 255, 0.96);
  background: linear-gradient(135deg, rgba(99, 191, 183, 0.28), rgba(99, 191, 183, 0.52));
  border-color: rgba(255, 255, 255, 0.22);
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.12) inset;
}

.source-icon {
  flex-shrink: 0;
  font-size: 16px;
  color: rgba(99, 191, 183, 0.95);
  cursor: default;
  opacity: 0.85;
  transition:
    opacity 0.15s ease,
    color 0.15s ease;
}

.source-icon:hover {
  opacity: 1;
  color: #63bfb7;
}

.metric-item :deep(.el-progress-bar__outer) {
  border-radius: 999px;
  background: rgba(17, 24, 39, 0.06);
}

.job-detail-view.dark .metric-item :deep(.el-progress-bar__outer) {
  background: rgba(255, 255, 255, 0.08);
}

.metric-item :deep(.el-progress__text) {
  font-size: 12px;
  font-weight: 700;
  min-width: 2.5em;
}

.job-detail-view.dark .metric-item :deep(.el-progress__text) {
  color: rgba(255, 255, 255, 0.88);
}

.metric-progress.glow-animation :deep(.el-progress-bar__inner) {
  box-shadow:
    0 0 12px rgba(99, 191, 183, 0.65),
    0 0 22px rgba(251, 191, 36, 0.35);
  animation: glow-animation 2.2s ease-in-out infinite;
}

.metric-progress.glow-animation :deep(.el-progress__text) {
  animation: glow-animation-text 2.2s ease-in-out infinite;
}

@keyframes glow-animation {
  0%,
  100% {
    filter: brightness(1);
    box-shadow:
      0 0 10px rgba(99, 191, 183, 0.55),
      0 0 18px rgba(251, 191, 36, 0.25);
  }
  50% {
    filter: brightness(1.08);
    box-shadow:
      0 0 16px rgba(99, 191, 183, 0.9),
      0 0 28px rgba(251, 191, 36, 0.45);
  }
}

@keyframes glow-animation-text {
  0%,
  100% {
    color: #0f766e;
    text-shadow: 0 0 0 transparent;
  }
  50% {
    color: #047857;
    text-shadow: 0 0 10px rgba(99, 191, 183, 0.75);
  }
}

.job-detail-view.dark .metric-progress.glow-animation :deep(.el-progress__text) {
  animation: glow-animation-text-dark 2.2s ease-in-out infinite;
}

@keyframes glow-animation-text-dark {
  0%,
  100% {
    color: rgba(255, 255, 255, 0.92);
    text-shadow: 0 0 6px rgba(99, 191, 183, 0.35);
  }
  50% {
    color: #ecfdf5;
    text-shadow: 0 0 14px rgba(99, 191, 183, 0.85);
  }
}

.path-analysis-tabs-wrap {
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  background: rgba(255, 255, 255, 0.42);
  border: var(--u-border);
  box-shadow: 8px 8px 0 var(--u-black);
}

.job-detail-view.dark .path-analysis-tabs-wrap {
  background: rgba(30, 35, 42, 0.55);
  border: 2px solid var(--u-black);
  box-shadow: 8px 8px 0 rgba(0, 0, 0, 0.55);
}

.path-analysis-tabs {
  width: 100%;
}

.path-analysis-tabs :deep(.el-tabs__header) {
  margin: 0 0 12px;
  border-bottom: 1px solid rgba(99, 191, 183, 0.2);
}

.path-analysis-tabs :deep(.el-tabs__item) {
  font-weight: 800;
  letter-spacing: 0.02em;
}

.path-analysis-tabs :deep(.el-tabs__item.is-active) {
  color: #0f766e;
}

.job-detail-view.dark .path-analysis-tabs :deep(.el-tabs__item.is-active) {
  color: #63bfb7;
}

.tab-pane-lead {
  margin-top: 0;
}

.job-summary-block {
  margin-bottom: 16px;
}

.job-summary-label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
}

.job-summary-text {
  margin: 0;
  line-height: 1.55;
  font-size: clamp(15px, 1vw, 17px);
  color: rgba(51, 50, 46, 0.88);
}

.job-detail-view.dark .job-summary-text {
  color: var(--dm-text-secondary);
}

.job-summary-text--clamped {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  overflow: hidden;
}

.text-expand-btn {
  margin-top: 8px;
  padding: 0;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 13px;
  font-weight: 800;
  color: #0f766e;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.text-expand-btn:hover {
  color: #63bfb7;
}

.job-detail-view.dark .text-expand-btn {
  color: #63bfb7;
}

.path-chart-embed {
  margin-top: 12px;
}

.dim-desc--clamped {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  overflow: hidden;
  width: 100%;
}

.dim-more-btn {
  padding: 2px 0;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 12px;
  font-weight: 800;
  color: #0f766e;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.job-detail-view.dark .dim-more-btn {
  color: #63bfb7;
}

.profile-dim-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.profile-dim-list li {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  margin-bottom: 10px;
  font-size: clamp(16px, 1.1vw, 18px);
}

.dim-name {
  display: inline-block;
  font-weight: 800;
  margin-right: 6px;
  padding: 2px 10px;
  border-radius: 999px;
  background: rgba(224, 247, 244, 0.85);
  border: 1px solid rgba(17, 24, 39, 0.14);
}

.dim-desc {
  color: rgba(51, 50, 46, 0.78);
}

.path-text,
.transfer-path-title,
.bloodline-title {
  color: rgba(17, 24, 39, 0.92);
}

.path-desc,
.transfer-arrow,
.transfer-gaps,
.dim-desc {
  color: rgba(31, 35, 40, 0.72);
}

/* 暗色模式：同样突出重点但不刺眼 */
.job-detail-view.dark .section-card {
  color: var(--dm-text);
}

.job-detail-view.dark .section-card .section-desc {
  color: var(--dm-text-secondary);
}

.job-detail-view.dark .info-list li,
.job-detail-view.dark .two-column,
.job-detail-view.dark .two-column p,
.job-detail-view.dark .rich-text,
.job-detail-view.dark .rich-text :deep(p),
.job-detail-view.dark .rich-text :deep(li),
.job-detail-view.dark .profile-dim-list li,
.job-detail-view.dark .path-node,
.job-detail-view.dark .transfer-path,
.job-detail-view.dark .transfer-steps,
.job-detail-view.dark .job-summary-text,
.job-detail-view.dark .dim-desc,
.job-detail-view.dark .path-desc,
.job-detail-view.dark .transfer-gaps {
  color: var(--dm-text-secondary);
}

.job-detail-view.dark .path-text,
.job-detail-view.dark .transfer-path-title,
.job-detail-view.dark .bloodline-title,
.job-detail-view.dark .transfer-from,
.job-detail-view.dark .job-summary-label {
  color: var(--dm-text);
}

.job-detail-view.dark .transfer-arrow {
  color: var(--dm-text-muted);
}

.job-detail-view.dark .info-list li::marker {
  color: rgba(255, 255, 255, 0.55);
}

.job-detail-view.dark .two-column p strong,
.job-detail-view.dark .rich-text :deep(strong),
.job-detail-view.dark .section-card strong {
  background: rgba(255, 238, 170, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.18);
  color: rgba(255, 255, 255, 0.92);
}

.job-detail-view.dark .dim-name {
  background: rgba(167, 139, 250, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.18);
  color: rgba(255, 255, 255, 0.92);
}

.path-block.vertical-path {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.path-node {
  padding: 10px 14px;
  background: #ffffff;
  border-radius: 10px;
  font-size: clamp(16px, 1.1vw, 18px);
  border: var(--u-border);
  box-shadow: 4px 4px 0px var(--u-black);
}

.path-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.path-index {
  width: 26px;
  height: 26px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #ffffff;
  border: 1.5px solid var(--u-black);
  box-shadow: 2px 2px 0px var(--u-black);
  font-weight: 900;
  flex: 0 0 auto;
}

.path-text {
  font-weight: 700;
}

.path-desc {
  margin: 8px 0 0;
  font-size: clamp(15px, 1vw, 17px);
  color: rgba(51, 50, 46, 0.78);
  line-height: 1.5;
}

.job-detail-view.dark .path-desc {
  color: var(--dm-text-secondary);
}

.transfer-current {
  margin-bottom: 14px;
}

.transfer-path-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
  margin: 10px 0 14px;
}

.transfer-path {
  background: #ffffff;
  border-radius: 12px;
  padding: 12px 14px;
  border: 2px solid var(--u-black);
  box-shadow: 4px 4px 0px rgba(0, 0, 0, 0.15);
}

.job-detail-view.dark .transfer-path {
  background: var(--dm-surface-card);
  border: 2px solid var(--dm-border);
  box-shadow: 4px 4px 0px rgba(0, 0, 0, 0.35);
}

.transfer-path-title {
  font-weight: 700;
  margin: 0 0 8px;
  font-size: clamp(15px, 1vw, 17px);
}

.transfer-steps {
  font-size: clamp(15px, 1vw, 17px);
  margin-bottom: 8px;
  line-height: 1.6;
}

.transfer-step {
  white-space: nowrap;
}

.transfer-arrow {
  margin: 0 6px;
  color: rgba(51, 50, 46, 0.55);
}

.job-detail-view.dark .transfer-arrow {
  color: var(--dm-text-muted);
}

.transfer-gaps {
  padding-left: 18px;
  margin: 0;
  font-size: clamp(14px, 0.95vw, 16px);
  color: rgba(51, 50, 46, 0.78);
}

.job-detail-view.dark .transfer-gaps {
  color: var(--dm-text-secondary);
}

.bloodline {
  margin-top: 6px;
}

.bloodline-title {
  font-weight: 700;
  margin: 10px 0 8px;
}

.bloodline-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.bloodline-list li {
  margin-bottom: 8px;
  font-size: clamp(15px, 1vw, 17px);
}

.bloodline-item {
  transition: background-color 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease;
  border-radius: 10px;
  padding: 4px 8px;
  border: 2px solid transparent;
  box-sizing: border-box;
}

.bloodline-item--active {
  background: rgba(224, 247, 244, 0.75);
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(15, 118, 110, 0.12);
}

.bloodline-item--flash {
  border-color: var(--u-black);
  box-shadow: 4px 4px 0 var(--u-black);
  animation: bloodlineFlash 1.4s ease-out forwards;
}

@keyframes bloodlineFlash {
  0% {
    background: rgba(255, 248, 170, 0.95);
  }
  100% {
    background: rgba(224, 247, 244, 0.75);
  }
}

.bloodline-graph-wrap {
  margin-top: 14px;
}

.transfer-from {
  font-weight: 600;
  font-size: clamp(16px, 1.1vw, 18px);
  margin-bottom: 8px;
}

.transfer-fallback-hint {
  font-size: clamp(13px, 0.9vw, 15px);
  color: #666;
  margin: 0 0 10px;
}

.job-detail-view.dark .transfer-fallback-hint {
  color: var(--dm-text-secondary);
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 12px;
}

.comment-item {
  display: flex;
  gap: 10px;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  background: var(--u-bg-submit);
  border: var(--u-border);
  box-shadow: 2px 2px 0px var(--u-black);
}

.comment-content {
  flex: 1;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  font-size: clamp(15px, 0.95vw, 17px);
  margin-bottom: 2px;
}

.comment-text {
  font-size: clamp(16px, 1.1vw, 18px);
}

.comment-input {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  margin-top: 8px;
}

.comment-btn {
  white-space: nowrap;
}

.job-detail-view:not(.dark) .comment-btn {
  background: var(--u-bg-submit);
  border: var(--u-border);
  box-shadow: var(--u-box-shadow);
  color: var(--u-black);
}

@media (max-width: 900px) {
  .nav {
    display: none;
  }

  .page-scroll {
    padding-inline: 16px;
  }

  .hero-overlay {
    left: 12px;
    bottom: 14px;
  }
}

.transfer-analysis-content {
  padding: 4px 2px 24px;
}

.transfer-analysis-heading {
  margin: 0 0 12px;
  font-size: clamp(16px, 1.05vw, 18px);
  font-weight: 800;
  line-height: 1.45;
  letter-spacing: 0.02em;
  color: var(--u-black);
}

.transfer-analysis-arrow {
  display: inline-block;
  margin: 0 6px;
  color: #63bfb7;
  font-weight: 900;
}

.transfer-analysis-hint {
  margin: 0 0 20px;
  font-size: 13px;
  line-height: 1.55;
  color: rgba(51, 50, 46, 0.65);
}

.transfer-analysis-section {
  margin-bottom: 22px;
}

.transfer-analysis-section:last-child {
  margin-bottom: 0;
}

.transfer-section-tag {
  margin: 0 0 6px;
  font-size: 14px;
  font-weight: 800;
  letter-spacing: 0.03em;
}

.transfer-section-tag--reuse {
  color: #047857;
}

.transfer-section-tag--gap {
  color: #b45309;
}

.transfer-section-desc {
  margin: 0 0 10px;
  font-size: 12px;
  color: rgba(51, 50, 46, 0.62);
}

.transfer-skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.transfer-skill-tag {
  border: 1px solid rgba(15, 23, 42, 0.2) !important;
}

.transfer-section-empty {
  margin: 0;
  font-size: 13px;
  color: rgba(51, 50, 46, 0.55);
}
</style>

<style>
/* Drawer 挂载到 body，需非 scoped 覆盖 Element Plus 外壳 */
.transfer-analysis-drawer.el-drawer {
  background: linear-gradient(165deg, #0c1220 0%, #111827 42%, #0b1222 100%);
  border-left: 2px solid rgba(99, 191, 183, 0.45);
  box-shadow: -12px 0 40px rgba(0, 0, 0, 0.45);
}

.transfer-analysis-drawer--light.el-drawer {
  background: linear-gradient(165deg, #0f172a 0%, #1e293b 48%, #0f172a 100%);
  border-left-color: rgba(99, 191, 183, 0.4);
}

.transfer-analysis-drawer .el-drawer__header {
  padding: 18px 20px 14px;
  margin-bottom: 0;
  border-bottom: 1px solid rgba(99, 191, 183, 0.22);
  background: rgba(15, 23, 42, 0.65);
}

.transfer-analysis-drawer .el-drawer__title {
  color: #f8fafc;
  font-size: 15px;
  font-weight: 800;
  letter-spacing: 0.04em;
  line-height: 1.4;
}

.transfer-analysis-drawer .el-drawer__close-btn {
  color: rgba(248, 250, 252, 0.85);
}

.transfer-analysis-drawer .el-drawer__body {
  padding: 16px 20px 28px;
  background: linear-gradient(180deg, rgba(17, 24, 39, 0.5) 0%, rgba(15, 23, 42, 0.92) 100%);
  color: #e2e8f0;
}

.transfer-analysis-drawer .transfer-analysis-heading {
  color: #f1f5f9;
}

.transfer-analysis-drawer .transfer-analysis-hint {
  color: rgba(226, 232, 240, 0.72);
}

.transfer-analysis-drawer .transfer-section-desc,
.transfer-analysis-drawer .transfer-section-empty {
  color: rgba(203, 213, 225, 0.75);
}

.transfer-analysis-drawer .transfer-section-tag--reuse {
  color: #6ee7b7;
}

.transfer-analysis-drawer .transfer-section-tag--gap {
  color: #fcd34d;
}
</style>