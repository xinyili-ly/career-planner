<template>
  <div class="home-view" :class="theme">
    <AppHeader show-utility-icons />

    <!-- 主体滚动内容 -->
    <div class="page-scroll">
      <!-- Hero 区域 -->
      <section class="hero">
        <!-- 左侧主标题和按钮 -->
        <div class="hero-main">
          <p class="hero-eyebrow">AI职业导航</p>
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
            基于大模型与多维度能力分析：构建就业岗位要求画像、学生就业能力画像，
            并生成可操作、可解释的职业探索与生涯发展报告。
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
          <h2 class="section-title">人工智能时代的高影响力职业</h2>
          <p class="section-desc">
            从专业技能、证书要求、创新能力、学习能力、抗压能力、沟通能力、实习能力等多维度
            构建岗位画像，并支持垂直晋升与换岗路径图谱，助你清晰规划发展路径。
          </p>
          <p class="section-desc section-desc-secondary">
            系统将结合你的学习背景、兴趣方向与能力侧重，提供更直观的岗位理解视角，帮助你快速把握不同职业的核心要求与成长空间。
          </p>
          <ul class="impact-points">
            <li>多维度能力要求一图查看</li>
            <li>岗位差异与迁移方向更清晰</li>
            <li>职业探索过程更有连续性</li>
          </ul>
          <el-button
            type="primary"
            size="large"
            class="ai-impact-btn"
            @click="handleExploreCareersClick"
          >
            按钮
          </el-button>
        </div>
      </section>

      <!-- AI 专业解析简历 -->
      <section class="ai-resume">
        <div class="ai-resume-header">
          <h2 class="section-title dark">
            AI 专业解析简历 · 学生就业能力画像
          </h2>
          <p class="section-desc dark">
            通过简历上传或对话录入，由大模型将数据拆解为多维度能力画像，
            并给出完整度与竞争力评分，为后续人岗匹配与生涯报告提供基础。
          </p>
        </div>

        <div class="ai-resume-content">
          <div class="ai-resume-left">
            <h3 class="ai-resume-subtitle">AI 可以：</h3>
            <ul class="ai-resume-list">
              <li>将简历/对话信息拆解为专业技能、证书、创新能力、学习/抗压/沟通/实习能力等维度。</li>
              <li>生成完整度与竞争力评分，为人岗匹配提供可解释依据。</li>
              <li>结合岗位画像进行多维度契合度与差距分析，支撑可操作的成长计划。</li>
            </ul>
            <el-upload
              class="resume-upload"
              drag
              :show-file-list="false"
              :before-upload="handleBeforeUpload"
            >
              <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
              <div class="el-upload__text">
                将简历拖到此处，或 <em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 PDF / DOC / DOCX，大小不超过 5MB。
                </div>
              </template>
            </el-upload>

            <el-button
              type="primary"
              size="large"
              class="resume-btn"
              @click="handleGetSuggestionClick"
            >
              获取建议
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

      <!-- 全屏沉浸式黑胶叙事区 -->
      <VinylProSection />

      <!-- 底部简单页脚 -->
      <footer class="footer">
        <span>© {{ new Date().getFullYear() }} 职途智引 · AI职业规划助手</span>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  UploadFilled
} from '@element-plus/icons-vue'
import { useTheme } from '../composables/useTheme'
import AppHeader from '../components/AppHeader.vue'
import VinylProSection from '../components/VinylProSection.vue'
import carouselJobs from '../assets/carousel-job-portrait.png'
import carouselAbilities from '../assets/carousel-ability-portrait.png'
import carouselPlan from '../assets/carousel-training-plan.png'
import carouselGuide from '../assets/carousel-guide.png'
import carouselHistory from '../assets/carousel-history.png'

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
    url: '/career-report-template'
  },
  {
    id: 5,
    title: '个人历史记录',
    desc: '查看个人历史报告',
    image: carouselHistory,
    url: '/career-report'
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

  const x = offset * 380
  const y = abs * abs * 18
  const z = -abs * 220
  const rotateY = -offset * 15
  // 保持所有卡片同尺寸，仅用层级和透明度体现远近
  const scale = 1

  return {
    transform: `translate3d(${x}px, ${y}px, ${z}px) rotateY(${rotateY}deg) scale(${scale})`,
    zIndex: 99 - abs
  }
}

const prevCarousel = () => {
  currentIndex.value = (currentIndex.value - 1 + carouselCards.length) % carouselCards.length
}

const nextCarousel = () => {
  currentIndex.value = (currentIndex.value + 1) % carouselCards.length
}

const goToCarousel = (url) => {
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
  router.push({ name: 'JobRequirements' })
}

const handleExploreCareersClick = () => {
  router.push({ name: 'JobRequirements' })
}

const handleGetSuggestionClick = () => {
  router.push({ name: 'StudentAbilities' })
}

const handleBeforeUpload = (file) => {
  const isAllowedType = /pdf|doc|docx$/i.test(file.name)
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isAllowedType) {
    ElMessage.error('仅支持 PDF / DOC / DOCX 格式')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('文件大小不能超过 5MB')
    return false
  }
  ElMessage.success(`已上传：${file.name}，后端接口对接后可进行分析。`)
  // 阻止真实上传，仅做演示
  return false
}

const resumeCards = ref([
  {
    title: '你将在下一阶段不断拓展新技能与传播领域的影响力',
    desc: '你已经具备较好的学习基础与表达优势，在跨任务协作、信息整合和成果呈现方面具备可持续增长空间。整体表现稳定，成长势能较强。',
    tag: '潜力良好'
  },
  {
    title: '你在实践经验方面还有成长空间',
    desc: '当前能力结构较完整，但实战沉淀仍有提升余地。你在问题拆解、执行耐心和场景适应性方面具备进一步加强的基础，发展弹性较好。',
    tag: '建议补强'
  },
  {
    title: '你的职业定位还不够清晰',
    desc: '你的兴趣面较广、可选方向较多，说明潜在机会丰富。现阶段更适合持续观察个人优势与岗位特征之间的匹配关系，逐步形成稳定定位。',
    tag: '待明确'
  }
])
</script>

<style scoped>
/* 核心容器：占满整个屏幕 */
.home-view {
  --u-border-radius: 12px;

  width: 100vw; /* 横向占满屏幕宽度 */
  min-height: 100vh; /* 纵向至少占满屏幕高度 */
  height: 100%; /* 高度自适应内容 */
  display: flex;
  flex-direction: column;
  background: var(--u-body-bg);
  color: var(--u-black);
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI',
    sans-serif;
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
  background: var(--dm-gradient-hero);
}

.home-view.dark .ai-impact {
  background: var(--dm-bg); /* 纯色，避免渐变“混色感” */
  border: 1px solid rgba(103, 232, 249, 0.12);
}

.home-view.dark .ai-resume {
  background: var(--dm-surface-card); /* 纯色 */
  color: #ffffff;
  border: 1px solid var(--dm-border-accent);
  box-shadow: 0 8px 32px rgba(167, 139, 250, 0.08);
}

.home-view.dark .ai-resume .section-title,
.home-view.dark .ai-resume .ai-resume-subtitle {
  color: #ffffff;
}

.home-view.dark .ai-resume .section-desc,
.home-view.dark .ai-resume .ai-resume-list,
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
  color: var(--dm-text, #e4e4e4);
}

.home-view.dark .hero-title span:nth-child(2) {
  background-color: rgba(255, 214, 233, 0.28);
  color: var(--dm-text, #e4e4e4);
  box-shadow: var(--u-box-shadow, 4px 4px 0px #000000);
}

.home-view.dark .primary-btn.el-button,
.home-view.dark .ai-impact-btn.el-button,
.home-view.dark .resume-btn.el-button {
  background: var(--dm-accent) !important;
  border-color: var(--dm-accent) !important;
  color: #0a0a0a !important;
  box-shadow: 4px 4px 0 #000000 !important;
}

.home-view.dark .primary-btn.el-button:hover,
.home-view.dark .ai-impact-btn.el-button:hover,
.home-view.dark .resume-btn.el-button:hover {
  box-shadow: 6px 6px 0 #000000 !important;
}

.home-view.dark .primary-btn.el-button:active,
.home-view.dark .ai-impact-btn.el-button:active,
.home-view.dark .resume-btn.el-button:active {
  box-shadow: 0 0 0 #000000 !important;
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
  box-shadow: 4px 4px 0 #000000 !important;
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

/* Hero：标题在上、轮播在下，拉开节奏 */
.hero {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 60px;
  margin-bottom: 120px;
  width: 100%;
}

.hero-main {
  box-sizing: border-box;
  width: 100%;
  /* 相对页面左缘多留空，让首屏叙事区视觉重心略向右 */
  padding: 0 0 0 clamp(48px, 7vw, 140px);
}

.hero-carousel {
  position: relative;
  width: 100%;
  border-radius: 0;
  background: var(--u-body-bg);
  border: none;
  box-shadow: none;
  min-height: 760px;
  overflow: visible;
  display: flex;
  align-items: center;
  justify-content: center;
  touch-action: pan-y;
}

/* 仅裁切卡片 3D 区域，避免左右导航被 overflow 切掉 */
.carousel-viewport {
  position: relative;
  width: 100%;
  min-height: 760px;
  overflow: hidden;
}

.home-view.dark .hero-carousel {
  background: var(--dm-bg);
  border: none;
  box-shadow: none;
}

.carousel-stage {
  position: relative;
  width: 100%;
  height: 760px;
  perspective: 1400px;
  perspective-origin: 50% 35%;
  transform-style: preserve-3d;
  transform: translateX(0);
}

.carousel-card {
  position: absolute;
  top: 124px;
  left: 50%;
  width: min(620px, 82vw);
  height: 420px;
  margin-left: -310px;
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
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 2px solid var(--u-black, #33322e);
  box-shadow: 4px 4px 0 0 var(--u-black, #33322e);
  background: #ffffff;
  color: var(--u-black, #33322e);
  font-size: 26px;
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
  left: clamp(10px, 2.5vw, 28px);
}

.carousel-nav--next {
  right: clamp(10px, 2.5vw, 28px);
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
  gap: 15px;
  position: relative;
}

.hero-title span {
  font-size: clamp(48px, 5.5vw, 84px);
  line-height: 1.1;
  color: var(--u-black, #33322e);
  -webkit-text-stroke: 0;
  text-stroke: 0;
  text-shadow: none;
  text-transform: uppercase;
  font-weight: 900;
  letter-spacing: 0.02em;
  width: fit-content;
}

/* 第二行：Uiineed 胶带贴纸 */
.hero-title span:nth-child(2) {
  background-color: var(--u-bg-submit, #ffd6e9);
  color: var(--u-black, #33322e);
  padding: 0 24px;
  margin-left: -10px;
  transform: rotate(-1.5deg);
  box-shadow: var(--u-box-shadow, 4px 4px 0px #33322e);
  -webkit-background-clip: border-box;
  background-clip: border-box;
}

.hero-title-charm {
  display: inline-flex;
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
  color: #55544f;
  margin: 30px 0 40px;
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

/* Hero 主按钮尺寸：交互与阴影见全局 main.css */
.home-view:not(.dark) .hero-actions .primary-btn.el-button--primary {
  height: 54px !important;
  padding: 0 40px !important;
}

/* AI 影响力区块：自适应 */
.ai-impact {
  margin-top: 3vw;
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

.ai-impact-right .section-title {
  margin-bottom: 0.8vw;
  text-align: center;
  font-size: clamp(30px, 2.2vw, 38px);
}

.ai-impact-right .section-desc {
  margin-bottom: 1.5vw;
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

.ai-impact-btn {
  border-radius: 999px;
  padding-inline: clamp(22px, 2vw, 32px);
  font-size: clamp(16px, 1.1vw, 19px);
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

.ai-resume-header {
  max-width: 100%; /* 取消宽度限制 */
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

.resume-upload {
  margin-top: 0.5vw;
  width: 100%;
}

/* 上传框：与页面统一为柔和卡片风格，避免突兀 */
:deep(.resume-upload .el-upload) {
  width: 100%;
}

:deep(.resume-upload .el-upload-dragger) {
  width: 100%;
  border: 2px dashed rgba(51, 50, 46, 0.35);
  border-radius: 16px;
  background: linear-gradient(180deg, #fdf8ef 0%, #fff7f5 100%);
  padding: 22px 18px;
  transition: border-color 0.2s ease, background-color 0.2s ease, transform 0.2s ease;
}

:deep(.resume-upload .el-upload-dragger:hover) {
  border-color: rgba(51, 50, 46, 0.62);
  background: linear-gradient(180deg, #fff9f1 0%, #fff4f0 100%);
  transform: translateY(-1px);
}

:deep(.resume-upload .el-upload__text) {
  color: rgba(51, 50, 46, 0.9);
  font-size: clamp(14px, 0.95vw, 16px);
}

:deep(.resume-upload .el-upload__tip) {
  color: rgba(51, 50, 46, 0.72);
  font-size: clamp(12px, 0.85vw, 14px);
}

:deep(.resume-upload .el-icon--upload) {
  color: rgba(51, 50, 46, 0.55);
  margin-bottom: 8px;
}

.home-view.dark :deep(.resume-upload .el-upload-dragger) {
  border-color: var(--dm-border);
  background: var(--dm-surface-card);
}

.home-view.dark :deep(.resume-upload .el-upload-dragger:hover) {
  border-color: var(--dm-border-accent);
  background: var(--dm-surface-elevated);
}

.home-view.dark :deep(.resume-upload .el-upload__text) {
  color: var(--dm-text);
}

.home-view.dark :deep(.resume-upload .el-upload__tip),
.home-view.dark :deep(.resume-upload .el-icon--upload) {
  color: var(--dm-text-secondary);
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
}

.resume-card-desc {
  font-size: clamp(15px, 1.05vw, 19px);
  color: rgba(51, 50, 46, 0.78);
  line-height: 1.75;
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

  .ai-resume-right {
    flex-direction: column;
    flex-wrap: wrap;
  }

  .ai-impact {
    grid-template-columns: 1fr;
    padding: 12px;
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