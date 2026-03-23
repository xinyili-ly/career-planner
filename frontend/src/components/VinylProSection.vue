<template>
  <section
    ref="sectionRef"
    class="vinyl-container"
    :class="{ 'vinyl-pro--dark': theme === 'dark' }"
    id="trigger-zone"
    aria-label="简历解析与能力画像说明"
  >
    <!-- 左侧：完整唱片居中 + 极简唱臂 -->
    <div class="vinyl-visual">
      <div class="vinyl-scene">
        <div class="vinyl-crop" aria-hidden="true">
          <div class="record" :style="recordStyle">
            <div class="groove-ring groove-ring--1" />
            <div class="groove-ring groove-ring--2" />
            <div class="groove-ring groove-ring--3" />
            <div class="record-label">
              <div class="record-label-disc" />
              <div class="label-text-block">
                <span class="label-line">Hello World</span>
                <span class="label-line">We are</span>
              </div>
            </div>
          </div>
        </div>

        <div
          class="tonearm"
          :class="{ 'tonearm--playing': isActive }"
          aria-hidden="true"
        >
          <svg
            class="tonearm-svg"
            viewBox="0 0 200 360"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <!-- 枢轴 -->
            <circle cx="102" cy="42" r="19" fill="#CCCCCC" />
            <!-- 配重（右上梯形） -->
            <path d="M 116 28 L 172 4 L 182 18 L 128 50 Z" fill="#CCCCCC" />
            <!-- 上臂段：自枢轴向左下 -->
            <path
              d="M 96 60 L 82 58 L 64 168 L 74 172 Z"
              fill="#CCCCCC"
            />
            <!-- 肘部折角 -->
            <path
              d="M 64 168 L 44 252 L 54 258 L 74 172 Z"
              fill="#CCCCCC"
            />
            <!-- 下臂段：指向盘面 -->
            <path
              d="M 44 252 L 18 308 L 26 314 L 54 258 Z"
              fill="#CCCCCC"
            />
            <!-- 唱头 -->
            <rect x="2" y="300" width="30" height="38" rx="2" fill="#3D3D3D" />
          </svg>
        </div>
      </div>
    </div>

    <!-- 右侧：局部滚动叙事（滚动映射唱片角度） -->
    <div
      ref="contentRef"
      class="vinyl-content"
      @scroll.passive="handleContentScroll"
    >
      <div class="content-spacer" aria-hidden="true" />

      <div class="story-card">
        <p class="tagline">HOW IT WORKS</p>
        <h2 class="title">探索你的职场律动</h2>

        <div class="step">
          <span class="num">01</span>
          <h3>简历深度解析</h3>
          <p>基于大模型提取 40+ 维度能力标签，精准还原你的职业底色。</p>
        </div>
        <div class="step">
          <span class="num">02</span>
          <h3>动态岗位匹配</h3>
          <p>实时比对行业画像，发现那些你从未察觉的「高契合」机会。</p>
        </div>
        <div class="step">
          <span class="num">03</span>
          <h3>成长路径演化</h3>
          <p>如同音轨的起伏，为你规划出跨越周期的技能进阶曲线。</p>
        </div>

        <div class="cta-wrapper">
          <el-button class="u-btn--primary" type="primary" @click="handleAction">
            开启职业导航
          </el-button>
          <p class="footer-note">* 数据通过加密传输，仅用于生成你的私人报告</p>
        </div>
      </div>

      <div class="content-spacer" aria-hidden="true" />
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTheme } from '../composables/useTheme'

const { theme } = useTheme()
const router = useRouter()

const sectionRef = ref(null)
const contentRef = ref(null)
const isActive = ref(false)
const scrollRotation = ref(0)

const recordStyle = computed(() => ({
  transform: `rotate(${scrollRotation.value}deg)`
}))

function handleContentScroll(e) {
  const t = e.target
  const { scrollTop, scrollHeight, clientHeight } = t
  const maxScroll = scrollHeight - clientHeight
  const scrollPercent = maxScroll > 0 ? scrollTop / maxScroll : 0
  scrollRotation.value = scrollPercent * 1080
}

function handleAction() {
  router.push({ name: 'StudentAbilities' })
}

let observer = null

onMounted(() => {
  observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        isActive.value = entry.isIntersecting
      }
    },
    { threshold: 0.5 }
  )

  if (sectionRef.value) {
    observer.observe(sectionRef.value)
  }
})

onUnmounted(() => {
  observer?.disconnect()
  observer = null
})
</script>

<style scoped>
.vinyl-container {
  display: flex;
  /* 卡片加高；唱片尺寸仍由 .record 的 --disc-size 控制，与卡片高度解耦 */
  height: 92vh;
  min-height: 560px;
  /* 与主界面 HomeView 一致：全局淡蓝底 */
  background: var(--u-body-bg);
  border-radius: 40px;
  /* 与 HomeView 中 ai-impact → ai-resume 的间距一致（.ai-resume 的 margin-top） */
  margin-top: calc(120px + 3vw);
  margin-bottom: 60px;
  overflow: hidden;
  position: relative;
}

/* --- 左侧视觉区：与主界面同色底；容器查询用于整盘尺寸 --- */
.vinyl-visual {
  flex: 1.2;
  position: relative;
  background: var(--u-body-bg);
  display: flex;
  align-items: stretch;
  justify-content: center;
  min-width: 0;
  /* 唱片放大后允许略溢出左栏，避免被裁切 */
  overflow: visible;
  container-type: size;
  container-name: vinyl-pane;
}

.vinyl-scene {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 320px;
}

/* 整盘居中，略留边距避免贴边 */
.vinyl-crop {
  position: absolute;
  inset: 0;
  overflow: visible;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(6px, 1.5vmin, 16px);
  box-sizing: border-box;
}

.record {
  /* 约为原先尺寸的 2 倍 */
  --disc-size: min(64vw, 76vh, 840px);
  position: relative;
  width: var(--disc-size);
  height: var(--disc-size);
  flex-shrink: 0;
  margin: 0;
  background: #000000;
  border-radius: 50%;
  box-sizing: border-box;
  will-change: transform;
}

@supports (width: 1cqmin) {
  .record {
    --disc-size: min(176cqmin, min(184cqw, 184cqb), 920px);
  }
}

/* 细白同心沟槽（2～3 道） */
.groove-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.22);
  pointer-events: none;
  box-sizing: border-box;
}

.groove-ring--1 {
  inset: 14%;
}

.groove-ring--2 {
  inset: 22%;
}

.groove-ring--3 {
  inset: 30%;
}

/* 白标 + 黑字，竖排（与参考站一致） */
.record-label {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  pointer-events: none;
}

.record-label-disc {
  position: absolute;
  width: 42%;
  height: 42%;
  max-width: 360px;
  max-height: 360px;
  background: #ffffff;
  border-radius: 50%;
}

.label-text-block {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: clamp(6px, 1.2vmin, 12px);
  writing-mode: vertical-rl;
  text-orientation: mixed;
  color: #000000;
  font-family:
    ui-sans-serif,
    system-ui,
    -apple-system,
    'Segoe UI',
    Roboto,
    'Helvetica Neue',
    Arial,
    sans-serif;
  font-weight: 600;
  font-size: clamp(8px, 1.25vmin, 11px);
  letter-spacing: 0.06em;
  line-height: 1.2;
}

.label-line {
  display: block;
  white-space: nowrap;
}

/* 极简几何唱臂：枢轴在左上白区，整组绕枢轴旋转 */
.tonearm {
  position: absolute;
  top: 4%;
  /* 略靠右（相对左栏右缘内移） */
  right: -3%;
  width: min(42%, 200px);
  height: auto;
  aspect-ratio: 200 / 360;
  z-index: 10;
  transform-origin: 51% 12%;
  /* 抬起角更大，与播放态差更大 → 摆动幅度更明显 */
  transform: translateX(6px) rotate(-24deg);
  transition: transform 0.85s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.tonearm--playing {
  transform: translateX(6px) rotate(16deg);
}

.tonearm-svg {
  display: block;
  width: 100%;
  height: auto;
  filter: drop-shadow(0 1px 0 rgba(0, 0, 0, 0.06));
}

/* --- 右侧内容区（叠在放大的唱片之上，保证可点可读） --- */
.vinyl-content {
  flex: 1;
  min-width: 0;
  position: relative;
  z-index: 2;
  overflow-y: auto;
  padding: 0 clamp(24px, 4vw, 60px);
  scroll-behavior: smooth;
  scrollbar-width: none;
  -webkit-overflow-scrolling: touch;
}

.vinyl-content::-webkit-scrollbar {
  display: none;
}

.content-spacer {
  height: 35vh;
  flex-shrink: 0;
}

.story-card {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.tagline {
  color: #3b82f6;
  font-weight: 800;
  letter-spacing: 2px;
  font-size: clamp(11px, 1.1vw, 13px);
  margin: 0;
}

.title {
  font-size: clamp(26px, 3.5vw, 42px);
  font-weight: 900;
  margin: 0 0 20px;
  line-height: 1.15;
  color: #111;
}

.step {
  border-bottom: 2px dashed #ccc;
  padding-bottom: 20px;
}

.step:last-of-type {
  border-bottom: none;
}

.step .num {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: clamp(20px, 2.2vw, 24px);
  color: #ffb8d9;
  font-style: italic;
  font-weight: bold;
  margin-bottom: 10px;
  display: block;
}

.step h3 {
  font-size: clamp(18px, 1.5vw, 22px);
  font-weight: 800;
  margin: 0 0 12px;
  color: #111;
}

.step p {
  margin: 0;
  line-height: 1.6;
  color: #666;
  font-size: clamp(14px, 1.1vw, 17px);
}

.cta-wrapper {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 14px;
  padding-top: 8px;
}

.footer-note {
  margin: 0;
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
  line-height: 1.5;
  max-width: 420px;
}

.u-btn--primary {
  background: #fde047 !important;
  color: #000 !important;
  font-weight: 900 !important;
  border: 3px solid #000 !important;
  box-shadow: 6px 6px 0 #000 !important;
  padding: 25px 40px !important;
  border-radius: 15px !important;
  height: auto !important;
}

.u-btn--primary:hover {
  transform: translate(-2px, -2px);
  box-shadow: 8px 8px 0 #000 !important;
}

.u-btn--primary:active {
  transform: translate(2px, 2px);
  box-shadow: 2px 2px 0 #000 !important;
}

/* 深色主题：与全局 --u-body-bg（html.dark）一致 */
.vinyl-pro--dark.vinyl-container {
  background: var(--u-body-bg);
}

.vinyl-pro--dark .vinyl-visual {
  background: var(--u-body-bg);
}

.vinyl-pro--dark .title,
.vinyl-pro--dark .step h3 {
  color: var(--dm-text, #e4e4e4);
}

.vinyl-pro--dark .step p {
  color: var(--dm-text-secondary, rgba(228, 228, 228, 0.78));
}

.vinyl-pro--dark .step {
  border-bottom-color: rgba(255, 255, 255, 0.2);
}

.vinyl-pro--dark .footer-note {
  color: var(--dm-text-muted, rgba(228, 228, 228, 0.48));
}

@media (max-width: 900px) {
  .vinyl-container {
    flex-direction: column;
    height: auto;
    min-height: 88vh;
    max-height: none;
  }

  .vinyl-visual {
    overflow: visible;
    min-height: min(38vh, 320px);
    justify-content: center;
    padding: 24px 0;
  }

  .record {
    /* 窄屏约为原先 2 倍 */
    --disc-size: min(86vw, min(56vh, 640px));
  }

  .tonearm {
    top: 2%;
    right: -5%;
    width: min(48%, 160px);
    transform: translateX(4px) rotate(-24deg);
  }

  .tonearm--playing {
    transform: translateX(4px) rotate(16deg);
  }

  .vinyl-content {
    max-height: 55vh;
  }
}

@media (prefers-reduced-motion: reduce) {
  .tonearm {
    transition: none;
  }

  .vinyl-content {
    scroll-behavior: auto;
  }

  .u-btn--primary:hover,
  .u-btn--primary:active {
    transform: none;
  }
}
</style>
