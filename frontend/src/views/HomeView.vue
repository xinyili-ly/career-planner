<template>
  <div class="home-view" :class="theme">
    <AppHeader show-utility-icons />

    <!-- 主体滚动内容 -->
    <div class="page-scroll">
      <!-- Hero 区域 -->
      <section class="hero">
        <!-- 左侧主标题和按钮 -->
        <div class="hero-main">
          <div class="hero-title-row">
            <h1 class="hero-title">
              <span>AI ILLUMINATES</span>
              <span>YOURS CAREER</span>
              <span>ODYSSEY</span>
            </h1>
            <div class="hero-title-charm" aria-hidden="true">
              <span class="charm-diamond"></span>
              <span class="charm-stick"></span>
              <span class="charm-circle"></span>
            </div>
          </div>
          <p class="hero-desc">
            以 AI 深度洞察职场坐标，用数据精准锚定成长路径。
            连接万位岗位画像，为每一位学子量身定制可落地的职业进化方案。
          </p>
          <div class="hero-actions">
            <el-button
              type="primary"
              size="large"
              class="primary-btn"
              @click="handleStartClick"
            >
              先试了解
            </el-button>
            <el-button
              type="primary"
              size="large"
              class="primary-btn secondary-btn"
              @click="handleBuildProfileClick"
            >
              构建画像
            </el-button>
          </div>
        </div>

        <section
          class="hero-carousel"
          @pointerdown="onPointerDown"
          @pointermove="onPointerMove"
          @pointerup="onPointerUp"
          @pointercancel="onPointerUp"
          @pointerleave="onPointerUp"
        >
          <button
            class="carousel-nav carousel-nav--prev"
            type="button"
            aria-label="上一张卡片"
            @click="prevCarousel"
          >
            ‹
          </button>

          <div class="carousel-viewport">
            <div class="carousel-stage">
              <a
                v-for="(card, idx) in carouselCards"
                :key="card.id"
                class="carousel-card"
                :class="{ focused: idx === currentIndex }"
                :href="card.url"
                :style="getCardStyle(idx)"
                @click.prevent="goToCarousel(card.url)"
              >
                <img class="carousel-image" :src="card.image" :alt="card.title" />
                <div class="carousel-overlay">
                  <h3>{{ card.title }}</h3>
                  <p>{{ card.desc }}</p>
                </div>
              </a>
            </div>
          </div>

          <button
            class="carousel-nav carousel-nav--next"
            type="button"
            aria-label="下一张卡片"
            @click="nextCarousel"
          >
            ›
          </button>
        </section>
      </section>

      <!-- AI 影响力职业区块 -->
      <section class="ai-impact">
        <div class="ai-impact-left">
          <div class="ai-hand-image">
            <img src="/career-roles.png" alt="职业人物插画" />
          </div>
        </div>
        <div class="ai-impact-right">
          <h2 class="section-title">数智驱动 · 职场进化引擎</h2>
          <p class="section-desc impact-block-title">
            01 | 深度画像：重塑职业认知坐标
          </p>
          <p class="section-desc section-desc-secondary">
            [维度：专业技能 · 创新能力 · 心理抗压 · 学习力 · 沟通协作]
          </p>
          <p class="section-desc">
            从 7 大核心维度结构化解析 AI 时代高影响力岗位。不仅是任职要求，更是对职业灵魂的深度拆解，
            助你精准对标行业顶端人才模型。
          </p>

          <p class="section-desc impact-block-title">
            02 | 路径导航：纵向攀升与横向跃迁
          </p>
          <p class="section-desc section-desc-secondary">
            [功能：垂直晋升图谱 | 跨行换岗血缘]
          </p>
          <p class="section-desc">
            打破职业信息孤岛。清晰呈现岗位从初阶到资深的成长轨迹，并基于“能力血缘”规划 5 大跨行转岗路径，
            让每一次职业选择都拥有确定性。
          </p>

          <p class="section-desc impact-block-title">
            03 | 智核匹配：构建你的数字化竞争力
          </p>
          <p class="section-desc section-desc-secondary">
            [逻辑：背景解析 · 兴趣对标 · 能力映射]
          </p>
          <p class="section-desc">
            系统深度融合你的学术背景与潜能偏好，将晦涩的招聘需求转化为直观的“能力雷达”。通过动态匹配，
            让职业探索从“碎片信息”转变为“连续的进化曲线”。
          </p>
          <div class="ai-impact-btn-wrap">
            <el-button
              type="primary"
              size="large"
              class="ai-impact-btn"
              @click="handleExploreCareersClick"
            >
              洞察岗位特征
            </el-button>
          </div>
        </div>
      </section>

      <!-- AI 专业解析简历 -->
      <section class="ai-resume">
        <div class="ai-resume-header">
          <h2 class="section-title dark">
            数字化底座 · AI 简历透视引擎
          </h2>
          <p class="section-desc dark">
            通过深度语言模型实现从“纸面简历”到“多维能力坐标”的数字转换。不论是文档上传还是对话录入，
            AI 都将精准萃取你的职业基因，量化每一份潜能。
          </p>
        </div>

        <div class="ai-resume-content">
          <div class="ai-resume-left">
            <h3 class="ai-resume-subtitle">数智拆解 · 三大核心效能</h3>
            <div class="ai-resume-features">
              <div class="ai-resume-feature">
                <span class="ai-resume-feature-dot" aria-hidden="true"></span>
                <div class="ai-resume-feature-body">
                  <p class="ai-resume-feature-title">全维语义解构：核心竞争力精准锚定</p>
                  <p class="ai-resume-feature-desc">
                    将非结构化文本深度拆解为专业硬核技能、权威证书、创新内驱、抗压韧性、协作沟通及实战经验等 7 大能力轴线。
                  </p>
                </div>
              </div>
              <div class="ai-resume-feature">
                <span class="ai-resume-feature-dot" aria-hidden="true"></span>
                <div class="ai-resume-feature-body">
                  <p class="ai-resume-feature-title">多维量化评估：完整度与竞争力双重评分</p>
                  <p class="ai-resume-feature-desc">
                    实时生成个体就业竞争力报告。不仅提供全局评分，更通过数据对标市场水位，为职业跃迁提供可解释、可追踪的底层依据。
                  </p>
                </div>
              </div>
              <div class="ai-resume-feature">
                <span class="ai-resume-feature-dot" aria-hidden="true"></span>
                <div class="ai-resume-feature-body">
                  <p class="ai-resume-feature-title">动态鸿沟分析：从“现状”到“目标”的精准对标</p>
                  <p class="ai-resume-feature-desc">
                    自动关联目标岗位画像，量化专业契合度与技能差距。将模糊的“努力方向”转化为颗粒度极细的阶梯式成长行动计划。
                  </p>
                </div>
              </div>
            </div>
            <el-button
              type="primary"
              size="large"
              class="resume-btn"
              @click="handleGetSuggestionClick"
            >
              查阅详细报告
            </el-button>
          </div>

          <!-- 右侧三列卡片：模拟“简历评估结果卡” -->
          <div class="ai-resume-right">
            <div
              v-for="(card, index) in resumeCards"
              :key="index"
              class="resume-card"
            >
              <div class="resume-avatar"></div>
              <div class="resume-card-body">
                <p class="resume-card-title">
                  {{ card.title }}
                </p>
                <p class="resume-card-desc">
                  {{ card.desc }}
                </p>
                <div class="resume-card-tag">
                  {{ card.tag }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 能力培训计划介绍（衔接简历/画像与执行闭环） -->
      <section class="ai-training-teaser" aria-label="能力培训计划">
        <div class="ai-training-teaser-inner">
          <div class="training-teaser-topbar">
            <span class="training-teaser-badge">STEP 04</span>
          </div>

          <div class="training-teaser-grid">
            <div class="training-teaser-copy">
              <h2 class="training-teaser-heading">阶梯达成 · 能力培训计划</h2>
              <p class="training-teaser-lead">
                在岗位画像与人岗匹配的基础上，将「技能鸿沟」转化为可执行节奏。系统生成约 12 周阶梯式甘特图，
                每条里程碑下挂载可编辑的 To Do 任务包；支持状态同步与本地持久化存储，确保成长轨迹刷新不丢，完美适配课堂演示与自主复盘。
              </p>
              <div class="training-teaser-tags" aria-label="能力培训计划要点">
                <span class="training-teaser-tag training-teaser-tag--yellow">12 周甘特</span>
                <span class="training-teaser-tag training-teaser-tag--mint">To Do 闭环</span>
                <span class="training-teaser-tag training-teaser-tag--pink">本地持久化</span>
                <span class="training-teaser-tag training-teaser-tag--outline">演示可离线</span>
              </div>

              <div class="training-teaser-cards">
                <article class="training-mini-card">
                  <h3 class="training-mini-title">
                    里程碑 → 任务包
                    <span class="training-mini-subline">核心逻辑：目标拆解与颗粒度对标</span>
                  </h3>
                  <p class="training-mini-desc">
                    按照目标岗位所需的 7 大维度，自动拆解阶段性节点。每个节点可展开为具体子任务，支持勾选完成态与心得备注，
                    避免规划流于表面，让每一份「想变强」的决心都有具体的动作支撑。
                  </p>
                </article>
                <article class="training-mini-card">
                  <h3 class="training-mini-title">
                    时间轴 × 清单联动
                    <span class="training-mini-subline">核心逻辑：动态执行与优先级管理</span>
                  </h3>
                  <p class="training-mini-desc">
                    甘特图与待办事项实现双轴对标。调整甘特图进度可同步触发清单优先级重排，让执行链路保持高度一致。
                    直观的视觉反馈让你一眼洞察进度的领先或滞后，确保职业规划始终处于「在线运行」状态。
                  </p>
                </article>
                <article class="training-mini-card">
                  <h3 class="training-mini-title">
                    本地存档 · 零门槛试用
                    <span class="training-mini-subline">核心逻辑：数据安全与即时反馈</span>
                  </h3>
                  <p class="training-mini-desc">
                    无需繁琐登录即可体验完整闭环流程。所有训练计划、任务进度数据均加密保存在浏览器本地，适合模拟机房、弱网或路演环境，
                    真正做到随时随地开启进化，数据随用随存，随时可一键重置。
                  </p>
                </article>
              </div>

              <el-button
                type="primary"
                size="large"
                class="resume-btn training-teaser-cta"
                @click="handleTrainingPlanClick"
              >
                进入能力培训计划
              </el-button>
            </div>

            <aside class="training-teaser-visual" aria-hidden="true">
              <div class="training-visual-panel">
                <p class="training-visual-caption">12 周成长节律</p>
                <div class="training-gantt">
                  <div class="training-gantt-row">
                    <span class="training-gantt-label">基础</span>
                    <div class="training-gantt-track">
                      <span class="training-gantt-bar training-gantt-bar--yellow" />
                    </div>
                  </div>
                  <div class="training-gantt-row">
                    <span class="training-gantt-label">强化</span>
                    <div class="training-gantt-track">
                      <span class="training-gantt-bar training-gantt-bar--pink" />
                    </div>
                  </div>
                  <div class="training-gantt-row">
                    <span class="training-gantt-label">项目</span>
                    <div class="training-gantt-track">
                      <span class="training-gantt-bar training-gantt-bar--mint" />
                    </div>
                  </div>
                  <div class="training-gantt-row">
                    <span class="training-gantt-label">冲刺</span>
                    <div class="training-gantt-track">
                      <span class="training-gantt-bar training-gantt-bar--amber" />
                    </div>
                  </div>
                </div>
                <div class="training-week-strip">
                  <span v-for="w in 12" :key="w" class="training-week-pill">W{{ w }}</span>
                </div>
                <div class="training-metrics">
                  <div class="training-metric">
                    <strong>12</strong>
                    <span>周可视排期</span>
                  </div>
                  <div class="training-metric">
                    <strong>To Do</strong>
                    <span>增删改查</span>
                  </div>
                  <div class="training-metric">
                    <strong>local</strong>
                    <span>进度自动存</span>
                  </div>
                </div>
              </div>
            </aside>
          </div>
        </div>
      </section>

      <!-- 全屏沉浸式黑胶叙事区（轮播「使用说明」锚点） -->
      <div id="vinyl-section" class="vinyl-scroll-anchor">
        <VinylProSection />
      </div>

      <!-- 底部简单页脚 -->
      <footer class="footer">
        <span>© {{ new Date().getFullYear() }} 职途智引 · AI职业规划助手</span>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTheme } from '../composables/useTheme'
import AppHeader from '../components/AppHeader.vue'
import VinylProSection from '../components/VinylProSection.vue'
import carouselJobs from '../assets/carousel-job-portrait.png'
import carouselAbilities from '../assets/carousel-ability-portrait.png'
import carouselPlan from '../assets/carousel-training-plan.png'
import carouselGuide from '../assets/carousel-guide.png'
import carouselHistory from '../assets/carousel-history.png'
import { getRecommendJobList } from '../api/jobPortraitApi'
import { extractJobsArray, saveJobListCache } from '../utils/jobPortraitNormalize'

const { theme } = useTheme()
const router = useRouter()
const currentIndex = ref(0)
const isDragging = ref(false)
const dragStartX = ref(0)
const dragDeltaX = ref(0)

const carouselCards = [
  {
    id: 1,
    title: '分界面一：岗位画像',
    desc: '就业岗位画像总览',
    image: carouselJobs,
    url: '/jobs'
  },
  {
    id: 2,
    title: '分界面二：能力画像',
    desc: '学生就业能力评估',
    image: carouselAbilities,
    url: '/student-abilities'
  },
  {
    id: 3,
    title: '分界面三：训练计划',
    desc: '生成能力训练路径',
    image: carouselPlan,
    url: '/ability-training-plan'
  },
  {
    id: 4,
    title: '使用说明',
    desc: '系统使用与操作指引',
    image: carouselGuide,
    url: '#vinyl-section'
  },
  {
    id: 5,
    title: '个人历史记录',
    desc: '查看个人历史报告',
    image: carouselHistory,
    url: '/profile'
  }
]

const normalizeOffset = (offset) => {
  const half = Math.floor(carouselCards.length / 2)
  if (offset > half) return offset - carouselCards.length
  if (offset < -half) return offset + carouselCards.length
  return offset
}

const getCardStyle = (index) => {
  const offset = normalizeOffset(index - currentIndex.value)
  const abs = Math.abs(offset)

  const x = offset === 0 ? 0 : Math.sign(offset) * (abs * 190 + 20)
  const y = abs * 15
  const z = offset === 0 ? 100 : -abs * 120
  const rotateY = offset === 0 ? 0 : (offset < 0 ? 25 : -25)
  const rotateZ = offset * 2
  const scale = Math.max(0.85, 1.1 - abs * 0.18)

  return {
    transform: `translate3d(${x}px, ${y}px, ${z}px) rotateY(${rotateY}deg) rotateZ(${rotateZ}deg) scale(${scale})`,
    zIndex: 120 - abs
  }
}

const prevCarousel = () => {
  currentIndex.value = (currentIndex.value - 1 + carouselCards.length) % carouselCards.length
}

const nextCarousel = () => {
  currentIndex.value = (currentIndex.value + 1) % carouselCards.length
}

const goToCarousel = (url) => {
  if (typeof url === 'string' && url.startsWith('#')) {
    const id = url.slice(1)
    const el = document.getElementById(id)
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
    return
  }
  router.push(url)
}

const onPointerDown = (event) => {
  isDragging.value = true
  dragStartX.value = event.clientX
  dragDeltaX.value = 0
}

const onPointerMove = (event) => {
  if (!isDragging.value) return
  dragDeltaX.value = event.clientX - dragStartX.value
}

const onPointerUp = () => {
  if (!isDragging.value) return
  if (dragDeltaX.value > 48) prevCarousel()
  if (dragDeltaX.value < -48) nextCarousel()
  isDragging.value = false
  dragDeltaX.value = 0
}

const handleStartClick = () => {
  router.push({ name: 'JobRequirements' })
}

const handleBuildProfileClick = () => {
  router.push({ name: 'StudentAbilities' })
}

const handleExploreCareersClick = () => {
  router.push({ name: 'JobRequirements' })
}

const handleGetSuggestionClick = () => {
  router.push({ name: 'StudentAbilities' })
}

const handleTrainingPlanClick = () => {
  router.push({ name: 'AbilityTrainingPlan' })
}

async function warmupJobPortraitApi() {
  const WARMUP_KEY = 'job_portrait_api_warmup_done_v1'
  try {
    if (sessionStorage.getItem(WARMUP_KEY) === '1') return
  } catch {
    // ignore read errors
  }

  try {
    const res = await getRecommendJobList()
    const list = extractJobsArray(res)
    if (Array.isArray(list) && list.length) {
      saveJobListCache(list)
    }
  } catch {
    // 静默预热：不影响首页体验，也不弹错误
  } finally {
    try {
      sessionStorage.setItem(WARMUP_KEY, '1')
    } catch {
      // ignore write errors
    }
  }
}

onMounted(() => {
  // 首页加载时预热岗位接口，减少首次进入岗位画像页的等待。
  warmupJobPortraitApi()
})

const resumeCards = ref([
  {
    title: '全域影响力重塑：开启职业进阶新周期',
    desc: '你已筑就坚实的知识底层与表达优势，在多维任务协同与高阶信息整合中展现出极强的适应力。建议下一阶段将现有优势沉淀为行业级影响力，实现从“执行驱动”向“影响力引领”的全面转型。',
    tag: '高增长势能'
  },
  {
    title: '实战力深耕：从能力构建走向价值落地',
    desc: '当前能力结构已趋于完整，核心突破点在于复杂场景下的实战沉淀。通过强化问题深度拆解与多环境适应性，你将进一步夯实技术底座的韧性，在真实业务挑战中释放更具穿透力的专业价值。',
    tag: '精进中 · 待释放'
  },
  {
    title: '多维探索：在多元可能中锚定最优坐标',
    desc: '广泛的兴趣维度预示着丰富的潜在机遇，现阶段是构建深度认知的黄金期。建议通过动态对标市场高影响力岗位特征，将个人优势图谱与行业需求进行高频耦合，逐步形成清晰且具竞争力的职业画像。',
    tag: '深度探索中'
  }
])
</script>

<style scoped>
/* 核心容器：占满整个屏幕 */
.home-view {
  --u-border-radius: 12px;
  --home-main-btn-height: 54px;

  width: 100vw; /* 横向占满屏幕宽度 */
  min-height: 100vh; /* 纵向至少占满屏幕高度 */
  height: 100%; /* 高度自适应内容 */
  display: flex;
  flex-direction: column;
  background: var(--u-body-bg);
  color: var(--u-black);
  font-family: var(--font-family-sans);
  margin: 0; /* 清除默认外边距 */
  padding: 0; /* 清除默认内边距 */
  box-sizing: border-box; /* 确保padding不超出容器 */
}

/* 主题适配：夜间模式带渐变与层次 */
.home-view.dark {
  background: var(--dm-bg);
  color: var(--dm-text);
}

.home-view.dark .header {
  background: var(--dm-header-bg);
}

.home-view.dark .hero {
  background: var(--dm-bg);
}

.home-view.dark .page-scroll {
  background: transparent;
}

.home-view.dark .ai-impact {
  background: linear-gradient(
    150deg,
    color-mix(in srgb, var(--u-yellow) 18%, var(--dm-bg)) 0%,
    color-mix(in srgb, var(--u-yellow) 10%, var(--dm-bg)) 52%,
    var(--dm-bg) 100%
  );
  border: 1px solid rgba(103, 232, 249, 0.12);
  box-shadow: none;
}

.home-view.dark .ai-resume {
  background: linear-gradient(
    150deg,
    color-mix(in srgb, var(--u-bg-discard) 22%, var(--dm-surface-card)) 0%,
    color-mix(in srgb, var(--u-bg-discard) 14%, var(--dm-surface-card)) 48%,
    var(--dm-surface-card) 100%
  );
  color: #ffffff;
  border: 1px solid var(--dm-border-accent);
  box-shadow: 0 8px 32px rgba(167, 139, 250, 0.08);
}

.home-view.dark .ai-training-teaser {
  background: linear-gradient(
    150deg,
    var(--dm-bg) 0%,
    color-mix(in srgb, var(--u-bg-completed) 52%, var(--dm-bg)) 48%,
    var(--dm-bg) 100%
  );
  color: var(--dm-text);
  border: 1px solid rgba(103, 232, 249, 0.12);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.2);
}

.home-view.dark .ai-training-teaser::before {
  background: radial-gradient(
    720px 240px at 88% 0%,
    color-mix(in srgb, var(--u-completed) 32%, transparent) 0%,
    transparent 58%
  );
}

.home-view.dark .training-teaser-heading {
  color: #ffffff;
}

.home-view.dark .training-teaser-lead,
.home-view.dark .training-mini-desc {
  color: var(--dm-text-secondary);
}

.home-view.dark .training-teaser-badge {
  background: color-mix(in srgb, var(--u-bg-completed) 65%, var(--dm-surface-card));
  border-color: var(--dm-border);
  color: var(--dm-text);
  box-shadow: 2px 2px 0 #000;
}

.home-view.dark .training-teaser-tag--yellow {
  background: color-mix(in srgb, var(--u-completed) 75%, var(--dm-surface-card));
  color: var(--dm-text);
  border-color: var(--dm-border);
}

.home-view.dark .training-teaser-tag--mint {
  background: color-mix(in srgb, var(--u-bg-completed) 70%, var(--dm-surface-card));
  color: var(--dm-text);
  border-color: var(--dm-border);
}

.home-view.dark .training-teaser-tag--pink {
  background: color-mix(in srgb, var(--u-bg-completed) 45%, var(--dm-surface-card));
  color: var(--dm-text-secondary);
  border-color: var(--dm-border);
}

.home-view.dark .training-teaser-tag--outline {
  background: color-mix(in srgb, var(--dm-bg) 78%, var(--u-bg-completed) 22%);
  color: var(--dm-text-secondary);
  border-color: var(--dm-border);
}

.home-view.dark .training-mini-card {
  background: color-mix(in srgb, var(--u-bg-completed) 28%, var(--dm-surface-card));
  border-color: var(--dm-border);
  box-shadow: 4px 4px 0 #000;
}

.home-view.dark .training-mini-title {
  color: var(--dm-text);
}

.home-view.dark .training-mini-subline {
  color: var(--dm-text-secondary);
}

.home-view.dark .training-visual-panel {
  background: color-mix(in srgb, var(--u-bg-completed) 35%, var(--dm-surface-card));
  border-color: var(--dm-border);
  box-shadow: 6px 6px 0 #000;
}

.home-view.dark .training-gantt-track {
  background: color-mix(in srgb, var(--u-completed) 18%, rgba(255, 255, 255, 0.06));
  border-color: var(--dm-border);
}

.home-view.dark .training-week-pill {
  background: color-mix(in srgb, var(--u-bg-completed) 40%, var(--dm-surface-card));
  border-color: var(--dm-border);
  color: var(--dm-text-secondary);
}

.home-view.dark .training-metric {
  background: color-mix(in srgb, var(--u-bg-completed) 32%, var(--dm-surface-card));
  border-color: var(--dm-border);
}

.home-view.dark .training-metric strong {
  color: var(--dm-text);
}

.home-view.dark .training-metric span {
  color: var(--dm-text-muted);
}

.home-view.dark .ai-resume .section-title,
.home-view.dark .ai-resume .ai-resume-subtitle,
.home-view.dark .ai-resume .ai-resume-feature-title {
  color: #ffffff;
}

.home-view.dark .ai-resume .section-desc,
.home-view.dark .ai-resume .ai-resume-list,
.home-view.dark .ai-resume .ai-resume-feature-desc,
.home-view.dark .ai-resume .resume-card-desc {
  color: rgba(255, 255, 255, 0.78);
}

.home-view.dark .resume-card {
  background: #121a26; /* 纯色卡片底 */
  color: #ffffff;
  border: 1px solid var(--dm-border);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
}

.home-view.dark .resume-avatar {
  background: rgba(255, 214, 233, 0.14);
  border: 1px solid var(--dm-border);
  box-shadow: 2px 2px 0 rgba(0, 0, 0, 0.35);
}

.home-view.dark .resume-card-tag {
  background: rgba(140, 212, 203, 0.14);
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid var(--dm-border);
  box-shadow: 2px 2px 0 rgba(0, 0, 0, 0.35);
}

.home-view.dark .nav-item {
  color: var(--dm-text);
}

.home-view.dark .hero-eyebrow,
.home-view.dark .hero-desc {
  color: var(--dm-text-secondary);
}

.home-view.dark .hero-title span {
  color: #ffffff;
  -webkit-text-stroke: 1.5px #000000;
  text-shadow:
    6px 6px 0px #ffd642,
    5px 6px 0px #ffd642,
    7px 6px 0px #ffd642,
    6px 5px 0px #ffd642,
    6px 7px 0px #ffd642,
    /* 黑色外轮廓：包裹黄色投影块（加粗） */
    3px 6px 0px #000000,
    9px 6px 0px #000000,
    6px 3px 0px #000000,
    6px 9px 0px #000000,
    4px 4px 0px #000000,
    8px 4px 0px #000000,
    4px 8px 0px #000000,
    8px 8px 0px #000000,
    /* 第二圈更外侧包边：再粗一点 */
    2px 6px 0px #000000,
    10px 6px 0px #000000,
    6px 2px 0px #000000,
    6px 10px 0px #000000,
    3px 3px 0px #000000,
    9px 3px 0px #000000,
    3px 9px 0px #000000,
    9px 9px 0px #000000,
    0 0 10px rgba(255, 214, 66, 0.16),
    0 0 20px rgba(255, 214, 66, 0.08);
}

.home-view.dark .primary-btn.el-button,
.home-view.dark .ai-impact-btn.el-button,
.home-view.dark .resume-btn.el-button {
  background: var(--dm-accent) !important;
  border-color: var(--dm-accent) !important;
  color: #0a0a0a !important;
  box-shadow: 4px 4px 0 var(--u-black) !important;
}

.home-view.dark .primary-btn.el-button:hover,
.home-view.dark .ai-impact-btn.el-button:hover,
.home-view.dark .resume-btn.el-button:hover {
  box-shadow: 6px 6px 0 var(--u-black) !important;
}

.home-view.dark .primary-btn.el-button:active,
.home-view.dark .ai-impact-btn.el-button:active,
.home-view.dark .resume-btn.el-button:active {
  box-shadow: 0 0 0 var(--u-black) !important;
}

/* 将“构建画像”按钮颜色强制改为黄色（覆盖全局 primary 粉色） */
.home-view .hero-actions .secondary-btn.el-button--primary {
  background-color: var(--u-yellow) !important;
  background: var(--u-yellow) !important;
  color: var(--u-black) !important;
  border: 2px solid var(--u-black) !important;
  box-shadow: 4px 4px 0 var(--u-black) !important;
}

.home-view .hero-actions .secondary-btn.el-button--primary:hover {
  background-color: var(--u-yellow) !important;
  background: var(--u-yellow) !important;
  color: var(--u-black) !important;
}

html.dark .home-view .hero-actions .secondary-btn.el-button--primary {
  background-color: var(--u-yellow) !important;
  background: var(--u-yellow) !important;
  color: var(--u-black) !important;
  box-shadow: 4px 4px 0 var(--u-black) !important;
}

/* 顶部导航：自适应屏幕 */
.header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 2vw; /* 用视口单位替代固定px，适配不同屏幕 */
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(16px);
  border-bottom: var(--u-border);
  width: 100%; /* 导航栏占满屏幕宽度 */
  box-sizing: border-box; /* 防止padding超出 */
}

.home-view.dark .header {
  background: var(--dm-header-bg);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--dm-border);
  box-shadow: 0 1px 0 rgba(167, 139, 250, 0.06);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 2vw;
}

.logo {
  text-decoration: none;
  color: inherit;
}

.nav-back {
  font-size: clamp(15px, 0.95vw, 17px);
}

.logo-main {
  font-size: clamp(20px, 1.5vw, 28px);
  font-weight: 700;
  letter-spacing: 2px;
}

.nav {
  display: flex;
  gap: 1.5vw; /* 自适应间距 */
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
  background: linear-gradient(90deg, #409eff, #67c23a);
  transition: width 0.2s ease;
}

.nav-item:hover::after,
.nav-item.active::after {
  width: 100%;
}

.nav-item.active {
  color: var(--u-black);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1vw; /* 自适应间距 */
}

.theme-toggle {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  background: #f0f2f8;
  padding: 4px;
  font-size: clamp(14px, 0.95vw, 17px);
}

.home-view.dark .theme-toggle {
  background: var(--dm-surface);
}

.theme-option {
  padding: 4px 1vw; /* 自适应内边距 */
  border-radius: 999px;
  cursor: pointer;
  color: #666;
  user-select: none;
}

.theme-option.active {
  background: #111827;
  color: #fff;
}

.home-view.dark .theme-option.active {
  background: var(--dm-surface-elevated);
  color: var(--dm-text);
}

.icon-btn {
  border: none;
  background: #f5f7fb;
  font-size: clamp(18px, 1.2vw, 20px);
}

.home-view.dark .icon-btn {
  background: var(--dm-surface);
  color: var(--dm-text);
}

/* 滚动内容区：全宽 + 随视口伸缩的安全留白 */
.page-scroll {
  max-width: none;
  margin: 0;
  padding: clamp(40px, 5vh, 72px) clamp(24px, 4vw, 48px);
  flex: 1;
  width: 100%;
  box-sizing: border-box;
  overflow-x: hidden;
}

/* 轮播「使用说明」跳转唱片区时，避免被 sticky 顶栏遮挡 */
.vinyl-scroll-anchor {
  scroll-margin-top: 72px;
}

/* Hero：标题在上、轮播在下，拉开节奏 */
.hero {
  --carousel-scale: 0.80;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: clamp(12px, 2vw, 28px);
  margin-top: 90px;
  margin-bottom: 120px;
  width: 100%;
}

.hero-main {
  box-sizing: border-box;
  flex: 0 1 46%;
  /* 相对页面左缘多留空，让首屏叙事区视觉重心略向右 */
  padding: 0 0 0 clamp(15px, 4.6vw, 96px);
  margin-top: 8px;
}

.hero-carousel {
  position: relative;
  flex: 0 1 54%;
  width: min(1120px, 54vw);
  border-radius: 0;
  background: var(--u-body-bg);
  border: none;
  box-shadow: none;
  min-height: calc(760px * var(--carousel-scale));
  overflow: visible;
  display: flex;
  align-items: center;
  justify-content: center;
  touch-action: pan-y;
  transform: translate(-80px, 62px);
  perspective: 1500px;
  perspective-origin: 50% 35%;
}

/* 仅裁切卡片 3D 区域，避免左右导航被 overflow 切掉 */
.carousel-viewport {
  position: relative;
  width: 100%;
  min-height: calc(760px * var(--carousel-scale));
  overflow: visible;
}

.home-view.dark .hero-carousel {
  background: var(--dm-bg);
  border: none;
  box-shadow: none;
}

.home-view.dark .hero-carousel .carousel-card:not(.focused) {
  opacity: 0.4 !important;
}

.home-view.dark .hero-carousel .carousel-card:not(.focused) .carousel-image {
  filter: brightness(0.7);
}

.carousel-stage {
  position: relative;
  width: 100%;
  height: calc(760px * var(--carousel-scale));
  transform-style: preserve-3d;
  transform: translateX(0);
}

.carousel-card {
  position: absolute;
  /* 高影响力职业卡片整体上移：-50px */
  top: calc(94px * var(--carousel-scale));
  left: 50%;
  width: min(calc(620px * var(--carousel-scale)), 82vw);
  height: calc(420px * var(--carousel-scale));
  margin-left: calc(-310px * var(--carousel-scale));
  border-radius: 18px;
  overflow: hidden;
  /* uiineed 风格：粗黑描边 + 立体偏移阴影 */
  border: 4px solid #000;
  /* 图片不需要阴影：去掉 box-shadow */
  box-shadow: none;
  transition: transform 0.5s cubic-bezier(0.22, 0.61, 0.36, 1);
  text-decoration: none;
  opacity: 1 !important;
  background: #ffffff;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
}

.carousel-card.focused {
  /* 中间聚焦卡片：黑色边框再加粗 */
  border: 4px solid #000;
  outline: none;
}

.carousel-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 1 !important;
  display: block;
}

.carousel-overlay {
  position: absolute;
  inset: auto 0 0 0;
  background: linear-gradient(180deg, transparent 0%, rgba(0, 0, 0, 0.72) 100%);
  color: #fff;
  padding: 10px 12px;
}

.carousel-overlay h3 {
  margin: 0;
  font-size: clamp(14px, 1vw, 17px);
}

.carousel-overlay p {
  margin: 4px 0 0;
  font-size: clamp(12px, 0.85vw, 14px);
}

.carousel-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: calc(48px * var(--carousel-scale));
  height: calc(48px * var(--carousel-scale));
  border-radius: 50%;
  border: 2px solid var(--u-black, #33322e);
  box-shadow: 4px 4px 0 0 var(--u-black, #33322e);
  background: #ffffff;
  color: var(--u-black, #33322e);
  font-size: calc(26px * var(--carousel-scale));
  font-weight: 700;
  line-height: 0;
  display: grid;
  place-items: center;
  z-index: 30;
  cursor: pointer;
  padding: 0;
  transition:
    transform 0.15s ease,
    box-shadow 0.15s ease;
}

.carousel-nav:hover {
  transform: translateY(-50%) translate(-1px, -1px);
  box-shadow: 5px 5px 0 0 var(--u-black, #33322e);
}

.carousel-nav:active {
  transform: translateY(-50%) translate(2px, 2px);
  box-shadow: 2px 2px 0 0 var(--u-black, #33322e);
}

.carousel-nav--prev {
  left: clamp(-88px, -4.8vw, -40px);
}

.carousel-nav--next {
  right: clamp(-88px, -4.8vw, -40px);
}

.home-view.dark .carousel-nav {
  border-color: var(--u-stroke, rgba(255, 255, 255, 0.78));
  box-shadow: 4px 4px 0 0 #000000;
  background: var(--dm-surface-card, #252a32);
  color: var(--dm-text, #e4e4e4);
}

.home-view.dark .carousel-nav:hover {
  box-shadow: 5px 5px 0 0 #000000;
}

.home-view.dark .carousel-nav:active {
  box-shadow: 2px 2px 0 0 #000000;
}

.hero-title-row {
  display: inline-flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 0;
}

.hero-eyebrow {
  font-size: clamp(15px, 0.95vw, 18px);
  color: var(--u-placeholder);
  margin-bottom: 0.5vw;
}

.hero-title {
  background: transparent;
  border: none;
  box-shadow: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 30px;
  position: relative;
}

.hero-title span {
  font-size: clamp(3.3rem, 9.2vw, 7.1rem);
  line-height: 1.1;
  color: #ffffff;
  -webkit-text-stroke: 1.5px #000000;
  text-shadow:
    6px 6px 0px #ffd642,
    5px 6px 0px #ffd642,
    7px 6px 0px #ffd642,
    6px 5px 0px #ffd642,
    6px 7px 0px #ffd642,
    /* 黑色外轮廓：包裹黄色投影块（加粗） */
    3px 6px 0px #000000,
    9px 6px 0px #000000,
    6px 3px 0px #000000,
    6px 9px 0px #000000,
    4px 4px 0px #000000,
    8px 4px 0px #000000,
    4px 8px 0px #000000,
    8px 8px 0px #000000,
    /* 第二圈更外侧包边：再粗一点 */
    2px 6px 0px #000000,
    10px 6px 0px #000000,
    6px 2px 0px #000000,
    6px 10px 0px #000000,
    3px 3px 0px #000000,
    9px 3px 0px #000000,
    3px 9px 0px #000000,
    9px 9px 0px #000000;
  font-family: 'Archivo Black', Impact, 'Arial Black', sans-serif;
  text-transform: uppercase;
  font-weight: 900;
  letter-spacing: -0.02rem;
  width: fit-content;
  transform: rotate(-1.5deg) scaleX(1.06);
  transform-origin: left center;
  transition: transform 0.2s ease, text-shadow 0.2s ease;
}

/* 第二行：Uiineed 胶带贴纸 */
.hero-title span:nth-child(2) {
  background: transparent;
  padding: 0;
  margin-left: 0;
  transform: translateY(-10px) rotate(1.5deg) scaleX(1.06);
}

.hero-title span:nth-child(2)::before {
  content: '';
  position: absolute;
  inset: -0.01em -0.56em -0.06em -0.60em;
  background: #ffd6e9;
  /* 左右锯齿边（胶带撕边感） */
  clip-path: polygon(
    /* left: irregular teeth (depth/spacing vary) */
    0% 0%,
    5% 8%,
    1% 17%,
    6% 30%,
    0% 43%,
    4% 57%,
    0.5% 71%,
    6% 84%,
    2% 93%,
    0% 100%,
    /* bottom + right: asymmetric irregular teeth */
    100% 100%,
    95% 94%,
    100% 86%,
    93.5% 74%,
    100% 63%,
    96% 49%,
    100% 36%,
    94.5% 23%,
    100% 12%,
    97% 5%,
    100% 0%
  );
  /* 贴纸不再单独旋转：与该行文字保持同一倾斜（跟随父级 transform） */
  transform: none;
  z-index: -1;
}

.hero-title span:hover {
  text-shadow:
    3px 3px 0px #ffd642,
    2px 3px 0px #ffd642,
    4px 3px 0px #ffd642,
    3px 2px 0px #ffd642,
    3px 4px 0px #ffd642,
    /* 黑色外轮廓：包裹黄色投影块（hover 加粗） */
    0px 3px 0px #000000,
    6px 3px 0px #000000,
    3px 0px 0px #000000,
    3px 6px 0px #000000,
    1px 1px 0px #000000,
    5px 1px 0px #000000,
    1px 5px 0px #000000,
    5px 5px 0px #000000,
    /* 第二圈更外侧包边：hover 再粗一点 */
    -1px 3px 0px #000000,
    7px 3px 0px #000000,
    3px -1px 0px #000000,
    3px 7px 0px #000000,
    0px 0px 0px #000000,
    6px 0px 0px #000000,
    0px 6px 0px #000000,
    6px 6px 0px #000000;
  transform: translateY(-3px) rotate(-2.5deg) scaleX(1.06);
}

.hero-title span:nth-child(2):hover {
  transform: translateY(3px) rotate(2.5deg) scaleX(1.06);
}

.hero-title-charm {
  display: none;
  align-items: center;
  gap: 4px;
  padding-bottom: 0.4vw;
}

.charm-diamond {
  width: 9px;
  height: 9px;
  transform: rotate(45deg);
  border-radius: 3px;
  background: #ffd6e9;
  border: 2px solid var(--u-black);
}

.charm-stick {
  width: 1px;
  height: 18px;
  background: var(--u-black);
  border-radius: 999px;
}

.charm-circle {
  width: 11px;
  height: 11px;
  border-radius: 999px;
  background: #ffe6a7;
  border: 2px solid var(--u-black);
}

.hero-desc {
  font-size: clamp(18px, 1.25vw, 20px);
  line-height: 1.8;
  letter-spacing: 0.03em;
  max-width: min(700px, 100%);
  width: 100%;
  color: #666666;
  font-weight: 700;
  background: linear-gradient(
    105deg,
    #5c5c5c 0%,
    #7a7a7a 32%,
    #9a9a9a 45%,
    #757575 58%,
    #5e5e5e 100%
  );
  background-size: 220% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 30px 0 40px;
  animation: hero-desc-shimmer 4.6s ease-in-out infinite;
}

@keyframes hero-desc-shimmer {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.hero-actions {
  display: flex;
  gap: 1vw;
  flex-wrap: wrap; /* 小屏幕自动换行 */
}

.primary-btn,
.secondary-btn {
  border-radius: 999px;
  font-size: clamp(16px, 1.1vw, 19px);
}

/* 主界面关键按钮统一高度（Hero / 分区 CTA / 培训计划 CTA） */
.home-view .primary-btn.el-button,
.home-view .ai-impact-btn.el-button,
.home-view .resume-btn.el-button {
  height: var(--home-main-btn-height) !important;
  min-height: var(--home-main-btn-height);
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}

/* Hero 主按钮额外保持更宽横向留白 */
.home-view .hero-actions .primary-btn.el-button--primary {
  padding-left: 40px !important;
  padding-right: 40px !important;
}

/* AI 影响力区块：自适应 */
.ai-impact {
  margin-top: calc(3vw + 100px);
  border-radius: clamp(14px, 2vw, 22px);
  padding: clamp(12px, 1.5vw, 20px);
  background: var(--u-bg-normal); /* 纯色 */
  border: var(--u-border);
  box-shadow: var(--u-box-shadow);
  display: grid;
  grid-template-columns: minmax(220px, 1fr) minmax(420px, 2fr);
  gap: clamp(12px, 1.4vw, 18px);
  align-items: stretch;
  width: 100%;
  box-sizing: border-box;
}

.ai-impact-left {
  display: flex;
  justify-content: center;
  width: 100%;
}

/* AI城市图：自适应尺寸 */
.ai-hand-image {
  width: 100%;
  max-width: 100%; /* 取消最大宽度限制 */
  height: auto;
  aspect-ratio: 1 / 1;
  border-radius: clamp(12px, 1.6vw, 18px);
  background: #ffffff; /* 让整图更清晰 */
  border: 1px solid #c4ddff;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.ai-hand-image img {
  width: 100%;
  height: 100%;
  object-fit: contain; /* 全图展示，不裁切 */
  display: block;
  border-radius: inherit;
}

.home-view.dark .ai-hand-image {
  background: var(--dm-surface-card); /* 纯色 */
  border-color: rgba(103, 232, 249, 0.2);
}

.ai-impact-right {
  /* 与主标题 padding-left 一致，用于标题与按钮同一视觉中线 */
  --ai-impact-title-pad: clamp(18px, 2.8vw, 40px);
  padding-top: clamp(16px, 2vw, 32px);
}

.ai-impact-right .section-title {
  margin-top: clamp(-12px, -1.1vw, -5px);
  margin-bottom: 0;
  padding-bottom: clamp(18px, 2vw, 30px);
  text-align: center;
  font-size: clamp(30px, 2.2vw, 38px);
  padding-left: var(--ai-impact-title-pad);
}

/* ai-impact 内：小标题 / 标签行 / 正文分层间距，避免 section-desc 统一 1.5vw 过松 */
.ai-impact-right .section-desc.impact-block-title {
  margin-top: 0.85vw;
  margin-bottom: 0.18rem;
  font-weight: 700;
  color: #33322e;
}

.ai-impact-right .section-title + .section-desc.impact-block-title {
  margin-top: clamp(10px, 1.15vw, 18px);
}

.ai-impact-right .section-desc.section-desc-secondary {
  margin-top: 0;
  margin-bottom: 0.4rem;
  color: rgba(51, 50, 46, 0.72);
}

.ai-impact-right .section-desc:not(.impact-block-title):not(.section-desc-secondary) {
  margin-bottom: 0.95vw;
}

/* 正文段与紧随其后的 02 / 03 小标题之间略加间距（01 仍紧跟主标题） */
.ai-impact-right
  .section-desc:not(.impact-block-title):not(.section-desc-secondary)
  + .section-desc.impact-block-title {
  margin-top: clamp(1.85rem, 4.4vw, 3.75rem);
}

.impact-block-title {
  margin-top: 1.1vw;
  margin-bottom: 0.45vw;
  font-weight: 700;
  color: #33322e;
}

.section-desc-secondary {
  margin-top: -0.4vw;
  margin-bottom: 0.9vw;
  color: rgba(51, 50, 46, 0.72);
}

.impact-points {
  margin: 0 0 1vw;
  padding-left: 1.2em;
  color: rgba(51, 50, 46, 0.82);
  font-size: clamp(15px, 0.98vw, 17px);
  line-height: 1.75;
}

.impact-points li + li {
  margin-top: 4px;
}

.home-view.dark .section-desc-secondary,
.home-view.dark .impact-points {
  color: var(--dm-text-secondary);
}

.home-view.dark .impact-block-title {
  color: var(--dm-text);
}

.ai-impact-btn {
  border-radius: 999px;
  padding-inline: clamp(22px, 2vw, 32px);
  font-size: clamp(16px, 1.1vw, 19px);
}

/* 与标题同宽内容区 + 居中，使按钮中线与「数智驱动 · 职场进化引擎」文字中线重合 */
.ai-impact-right .ai-impact-btn-wrap {
  display: flex;
  justify-content: center;
  width: 100%;
  box-sizing: border-box;
  padding-left: var(--ai-impact-title-pad);
  margin-top: calc(50px + clamp(10px, 1.35vw, 20px));
}

.section-title {
  font-size: clamp(22px, 1.7vw, 30px);
  font-weight: 700;
}

.section-title.dark {
  color: var(--dm-text);
}

.section-desc {
  font-size: clamp(17px, 1.1vw, 20px);
  color: #555;
  line-height: 1.6;
}

.section-desc.dark {
  color: var(--dm-text-secondary);
}

/* AI 简历分析区：自适应（与 Hero→ai-impact 间距对齐：120px + 3vw） */
.ai-resume {
  margin-top: calc(120px + 3vw);
  border-radius: clamp(16px, 2.5vw, 28px);
  padding: clamp(16px, 2vw, 28px);
  background: var(--u-bg-discard); /* 纯色，和 ai-impact 分区形成纯色区块区分 */
  color: var(--u-black);
  border: var(--u-border);
  box-shadow: var(--u-box-shadow);
  width: 100%;
  box-sizing: border-box;
}

/* 能力培训计划介绍卡片（位于「数字化底座」区块下方；与 ai-resume 上间距同量级） */
.ai-training-teaser {
  margin-top: calc(120px + 3vw);
  border-radius: clamp(16px, 2.5vw, 28px);
  padding: clamp(22px, 2.8vw, 36px);
  width: 100%;
  box-sizing: border-box;
  border: var(--u-border);
  box-shadow: var(--u-box-shadow);
  /* Uiineed 成功/完成色：薄荷绿底 + 浅天蓝过渡 */
  background: linear-gradient(
    145deg,
    var(--u-bg-completed) 0%,
    var(--u-fade-completed) 40%,
    var(--u-body-bg) 100%
  );
  position: relative;
  overflow: hidden;
}

.ai-training-teaser::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(
    780px 260px at 90% 6%,
    color-mix(in srgb, var(--u-completed) 38%, transparent) 0%,
    transparent 56%
  );
  pointer-events: none;
}

.ai-training-teaser-inner {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 100%;
}

.training-teaser-topbar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 10px 16px;
  margin-bottom: 0;
}

.training-teaser-badge {
  display: inline-flex;
  align-items: center;
  padding: 5px 12px;
  font-size: clamp(11px, 0.9vw, 12px);
  font-weight: 900;
  letter-spacing: 0.06em;
  border-radius: 10px;
  border: 2px solid var(--u-black);
  background: var(--u-bg-completed);
  box-shadow: 3px 3px 0 var(--u-black);
}

.training-teaser-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.12fr) minmax(220px, 0.88fr);
  gap: clamp(22px, 3.5vw, 44px);
  align-items: start;
}

.training-teaser-copy {
  min-width: 0;
}

.training-teaser-heading {
  margin: clamp(-26px, -2vw, -12px) 0 clamp(12px, 1.4vw, 18px);
  font-size: clamp(30px, 2.2vw, 38px);
  font-weight: 700;
  line-height: 1.2;
  color: var(--u-black);
}

.training-teaser-lead {
  margin: 0 0 clamp(18px, 2vw, 24px);
  font-size: clamp(17px, 1.15vw, 20px);
  line-height: 1.72;
  color: rgba(51, 50, 46, 0.88);
}

.training-teaser-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 10px;
  margin-bottom: clamp(18px, 2vw, 24px);
}

.training-teaser-tag {
  display: inline-flex;
  align-items: center;
  padding: 6px 13px;
  border-radius: 999px;
  border: 2px solid var(--u-black);
  font-size: clamp(12px, 0.9vw, 13px);
  font-weight: 800;
  line-height: 1.2;
}

/* 标签统一在 Uiineed 绿色谱系内做层次 */
.training-teaser-tag--yellow {
  background: var(--u-completed);
}

.training-teaser-tag--mint {
  background: var(--u-bg-completed);
}

.training-teaser-tag--pink {
  background: color-mix(in srgb, var(--u-bg-completed) 58%, #ffffff 42%);
}

.training-teaser-tag--outline {
  background: color-mix(in srgb, var(--u-body-bg) 72%, var(--u-bg-completed) 28%);
}

.training-teaser-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: clamp(12px, 1.4vw, 16px);
  margin-bottom: clamp(22px, 2.4vw, 28px);
}

.training-mini-card {
  margin: 0;
  padding: clamp(14px, 1.5vw, 18px);
  border-radius: 14px;
  border: 2px solid var(--u-black);
  background: color-mix(in srgb, var(--u-bg-completed) 22%, #ffffff);
  box-shadow: 4px 4px 0 var(--u-black);
}

.training-mini-title {
  margin: 0 0 8px;
  font-size: clamp(15px, 1.05vw, 17px);
  font-weight: 800;
  color: var(--u-black);
  line-height: 1.3;
}

.training-mini-subline {
  display: block;
  margin-top: clamp(10px, 1.15vw, 14px);
  font-size: clamp(13px, 0.92vw, 15px);
  font-weight: 700;
  line-height: 1.35;
  color: rgba(51, 50, 46, 0.72);
}

.training-mini-desc {
  margin: 0;
  font-size: clamp(14px, 0.98vw, 16px);
  line-height: 1.65;
  color: rgba(51, 50, 46, 0.78);
}

.training-teaser-cta {
  margin-top: 2px;
}

.training-teaser-visual {
  min-width: 0;
  margin-top: clamp(16px, 1.75vw, 28px);
}

.training-visual-panel {
  display: flex;
  flex-direction: column;
  border-radius: 16px;
  border: 3px solid var(--u-black);
  background: color-mix(in srgb, var(--u-bg-completed) 42%, #ffffff);
  box-shadow: 6px 6px 0 var(--u-black);
  padding: clamp(22px, 2.8vw, 32px);
  min-height: clamp(340px, 44vh, 520px);
}

.training-visual-caption {
  margin: 0 0 clamp(20px, 2.4vw, 28px);
  font-size: clamp(15px, 1.25vw, 18px);
  font-weight: 800;
  letter-spacing: 0.04em;
  color: var(--u-black);
}

.training-gantt {
  display: flex;
  flex-direction: column;
  gap: clamp(16px, 2vw, 22px);
  margin-bottom: clamp(22px, 2.8vw, 30px);
}

.training-gantt-row {
  display: grid;
  grid-template-columns: minmax(58px, 4.2rem) 1fr;
  align-items: center;
  gap: clamp(14px, 1.6vw, 18px);
}

.training-gantt-label {
  font-size: clamp(12px, 1vw, 14px);
  font-weight: 800;
  color: var(--u-black);
}

.training-gantt-track {
  height: 16px;
  border-radius: 999px;
  border: 2px solid var(--u-black);
  background: color-mix(in srgb, var(--u-completed) 12%, #ffffff);
  overflow: hidden;
  box-sizing: border-box;
}

.training-gantt-bar {
  display: block;
  height: 100%;
  border-radius: inherit;
  border-right: 2px solid var(--u-black);
}

.training-gantt-bar--yellow {
  width: 78%;
  background: var(--u-completed);
}

.training-gantt-bar--pink {
  width: 62%;
  margin-left: 12%;
  background: color-mix(in srgb, var(--u-completed) 52%, var(--u-bg-completed));
}

.training-gantt-bar--mint {
  width: 88%;
  margin-left: 4%;
  background: var(--u-bg-completed);
}

.training-gantt-bar--amber {
  width: 48%;
  margin-left: 36%;
  background: color-mix(in srgb, var(--u-mint) 22%, var(--u-bg-completed));
}

.training-week-strip {
  display: flex;
  flex-wrap: wrap;
  gap: clamp(8px, 1vw, 11px);
  margin-bottom: clamp(22px, 2.8vw, 30px);
}

.training-week-pill {
  flex: 1 1 0;
  min-width: 2.35rem;
  padding: 8px 7px;
  text-align: center;
  font-size: clamp(10px, 0.85vw, 11px);
  font-weight: 800;
  border-radius: 6px;
  border: 2px solid var(--u-black);
  background: color-mix(in srgb, var(--u-bg-completed) 38%, #ffffff);
}

.training-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: clamp(10px, 1.2vw, 14px);
  margin-top: auto;
  padding-top: clamp(10px, 1.4vw, 16px);
}

.training-metric {
  padding: 12px 8px;
  border-radius: 12px;
  border: 2px solid var(--u-black);
  background: color-mix(in srgb, var(--u-bg-completed) 32%, #ffffff);
  text-align: center;
}

.training-metric strong {
  display: block;
  font-size: clamp(14px, 1.1vw, 16px);
  font-weight: 900;
  margin-bottom: 4px;
  color: var(--u-black);
}

.training-metric span {
  display: block;
  font-size: 10px;
  font-weight: 700;
  line-height: 1.35;
  color: rgba(51, 50, 46, 0.62);
}

.ai-resume-header {
  max-width: 100%; /* 取消宽度限制 */
}

/* 与「数智驱动 · 职场进化引擎」主标题字号一致 */
.ai-resume-header .section-title {
  font-size: clamp(30px, 2.2vw, 38px);
}

.ai-resume-content {
  margin-top: 2vw;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); /* 第三分界面默认更宽 */
  gap: clamp(16px, 2vw, 28px);
  align-items: start;
}

.ai-resume-left {
  display: flex;
  flex-direction: column;
  gap: 1vw;
  width: 100%;
}

.ai-resume-subtitle {
  font-size: clamp(19px, 1.35vw, 24px);
  font-weight: 600;
}

.ai-resume-list {
  padding-left: 1.5vw;
  margin: 0;
  font-size: clamp(17px, 1.2vw, 21px);
  line-height: 1.7;
}

.ai-resume-features {
  display: flex;
  flex-direction: column;
  gap: clamp(14px, 1.35vw, 20px);
  width: 100%;
}

.ai-resume-feature {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
}

.ai-resume-feature-dot {
  flex-shrink: 0;
  width: 8px;
  height: 8px;
  margin-top: 0.52em;
  border-radius: 50%;
  background: var(--u-black);
}

.ai-resume-feature-body {
  flex: 1;
  min-width: 0;
}

.home-view.dark .ai-resume .ai-resume-feature-dot {
  background: rgba(255, 255, 255, 0.88);
}

.ai-resume-feature-title {
  margin: 0 0 0.4rem;
  font-size: clamp(16px, 1.12vw, 19px);
  font-weight: 700;
  color: var(--u-black);
  line-height: 1.45;
}

.ai-resume-feature-desc {
  margin: 0;
  font-size: clamp(16px, 1.05vw, 20px);
  line-height: 1.75;
  color: #555;
}

.resume-btn {
  margin-top: 1vw;
  border-radius: 999px;
  align-self: flex-start;
  padding-inline: clamp(20px, 1.7vw, 28px);
  font-size: clamp(16px, 1.1vw, 19px);
}

/* 右侧卡片：自适应 */
.ai-resume-right {
  display: flex;
  gap: clamp(12px, 1.4vw, 18px);
  align-items: stretch;
  flex-wrap: nowrap;
  width: 100%;
}

.resume-card {
  flex: 1;
  min-width: 280px; /* 拉长卡片宽度 */
  min-height: 290px; /* 增加高度，承载补充文案 */
  background: #ffffff; /* 纯色卡片底 */
  border-radius: clamp(14px, 1.5vw, 20px);
  padding: clamp(14px, 1.35vw, 20px);
  display: flex;
  flex-direction: column;
  gap: clamp(10px, 1vw, 14px);
  color: var(--u-black);
  border: var(--u-border);
  box-shadow: var(--u-box-shadow);
}

.resume-card-body {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

.resume-avatar {
  width: clamp(28px, 2.2vw, 36px); /* 第三分界面略放大 */
  height: clamp(28px, 2.2vw, 36px);
  border-radius: 999px;
  background: var(--u-bg-submit);
  border: var(--u-border);
  box-shadow: 2px 2px 0px var(--u-black);
  margin-bottom: 0.5vw;
}

.resume-card-title {
  font-size: clamp(17px, 1.15vw, 21px);
  font-weight: 600;
  margin: 0 0 clamp(14px, 1.35vw, 22px);
}

.resume-card-desc {
  font-size: clamp(15px, 1.05vw, 19px);
  color: rgba(51, 50, 46, 0.78);
  line-height: 1.75;
  margin: 0 0 clamp(18px, 1.55vw, 28px);
}

.resume-card-tag {
  margin-top: auto;
  align-self: flex-start;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: clamp(12px, 0.85vw, 14px);
  background: var(--u-bg-completed);
  color: var(--u-black);
  border: var(--u-border);
  box-shadow: 2px 2px 0px var(--u-black);
}

/* 页脚：自适应，与全站统一留白 */
.footer {
  margin-top: 3vw;
  padding-top: 1.5vw;
  padding-bottom: 1vw;
  border-top: 1px solid rgba(148, 163, 184, 0.4);
  font-size: clamp(15px, 0.95vw, 17px);
  color: #9ca3af;
  text-align: center;
  width: 100%;
}

.home-view.dark .footer {
  border-top-color: var(--dm-border);
  color: var(--dm-text-muted);
}

/* 响应式优化：小屏幕适配 */
@media (max-width: 900px) {
  .header-left .nav {
    display: none;
  }

  .hero {
    --carousel-scale: 1;
    flex-direction: column;
    align-items: flex-start;
    gap: 60px;
  }

  .hero-main {
    flex: 1 1 auto;
    width: 100%;
  }

  .hero-carousel {
    flex: 1 1 auto;
    width: 100%;
    transform: none;
  }

  .ai-resume-right {
    flex-direction: column;
    flex-wrap: wrap;
  }

  .ai-impact {
    grid-template-columns: 1fr;
    padding: 12px;
  }

  .training-teaser-grid {
    grid-template-columns: 1fr;
  }

  .training-teaser-visual {
    order: -1;
  }
}

@media (min-width: 1200px) {
  /* 第三个分界面（ai-resume）在大屏下更“拉开” */
  .ai-resume {
    padding-left: clamp(24px, 3vw, 44px);
    padding-right: clamp(24px, 3vw, 44px);
  }

  .ai-resume-content {
    grid-template-columns: minmax(520px, 1.1fr) minmax(520px, 1fr);
    gap: 32px 40px;
  }

  .resume-card {
    min-width: 280px;
  }
}
</style>