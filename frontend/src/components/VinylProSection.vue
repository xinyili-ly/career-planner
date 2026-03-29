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
      <div class="vinyl-scene" aria-hidden="true">
        <div class="turntable">
          <div class="turntable-screw turntable-screw--tl" />
          <div class="turntable-screw turntable-screw--tr" />
          <div class="turntable-screw turntable-screw--bl" />
          <div class="turntable-screw turntable-screw--br" />

          <div class="platter">
            <div class="platter-shimmer" :class="{ 'platter-shimmer--on': isActive }" />
            <div
              class="platter-shimmer platter-shimmer--alt"
              :class="{ 'platter-shimmer--on': isActive }"
            />

            <div class="record" :class="{ 'record--playing': isActive }" :style="recordStyle">
              <div class="record-groove record-groove--1" />
              <div class="record-groove record-groove--2" />
              <div class="record-groove record-groove--3" />
              <div class="record-groove record-groove--4" />
              <div class="record-groove record-groove--5" />

              <div class="record-gloss record-gloss--bar" />
              <div class="record-gloss record-gloss--arc" />
              <div class="record-gloss record-gloss--rim" />

              <div class="record-label">
                <div class="record-label-gloss" />
                <div class="record-label-hole" />
              </div>
            </div>
          </div>

          <div class="needle" :class="{ 'needle--on': isActive }">
            <div class="needle-base" />
            <div class="needle-arm">
              <div class="needle-head">
                <div class="needle-tip" />
              </div>
            </div>
          </div>
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
        <p class="tagline">初心与使用方法</p>
        <h2 class="title">从画像到行动的职业探索</h2>

        <div class="step">
          <span class="num">01</span>
          <h3>启动与进入流程</h3>
          <p>运行项目后，从首页进入“就业岗位画像/学生就业能力”；可切换主题（自动本地记忆）。</p>
        </div>
        <div class="step">
          <span class="num">02</span>
          <h3>岗位画像与能力评分</h3>
          <p>岗位优先请求后端（`/recommend/list`），失败则回退本地兜底；查看岗位维度、晋升与换岗路径，再生成学生能力画像。</p>
        </div>
        <div class="step">
          <span class="num">03</span>
          <h3>匹配报告与训练计划</h3>
          <p>在“匹配与报告”选定目标岗位生成报告；进入“能力培训计划”查看甘特图与 To Do（增删改查并自动本地保存）。</p>
        </div>

        <div class="cta-wrapper">
          <el-button class="u-btn--primary" type="primary" @click="handleAction">
            开始填写画像
          </el-button>
          <p class="footer-note">* 本地演示版说明：部分解析/生成为示例数据，To Do 会保存到本地。</p>
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

/* --- changpian 唱片机视觉（无控制按钮，功能沿用旧逻辑） --- */
.turntable {
  position: absolute;
  inset: clamp(30px, 6vmin, 50px);
  border-radius: 18px;
  /* 参考 uiineed 配色：浅黄底（保持整体更统一） */
  background:rgb(255, 251, 228);
  border: 4px solid #000;
  box-shadow: 8px 8px 0 rgba(0, 0, 0, 1);
}

.turntable-screw {
  position: absolute;
  width: 14px;
  height: 14px;
  background: #c0c0c0;
  border: 2px solid #000;
  border-radius: 999px;
}
.turntable-screw--tl {
  top: 10px;
  left: 10px;
}
.turntable-screw--tr {
  top: 10px;
  right: 10px;
}
.turntable-screw--bl {
  bottom: 10px;
  left: 10px;
}
.turntable-screw--br {
  bottom: 10px;
  right: 10px;
}

.platter {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
}

.platter::before {
  content: '';
  /* 放大约 2 倍（参考 changpian 视觉），必要时允许略溢出容器 */
  width: min(102vmin, 820px);
  height: min(102vmin, 820px);
  /* 参考 uiineed 配色：主按钮底色粉 */
  background: var(--u-bg-submit);
  border: 4px solid #000;
  border-radius: 999px;
  box-sizing: border-box;
}

.platter-shimmer {
  position: absolute;
  width: min(102vmin, 710px);
  height: min(102vmin, 710px);
  border-radius: 999px;
  pointer-events: none;
  z-index: 2;
  opacity: 0;
  transition: opacity 0.25s ease;
  background: linear-gradient(
    145deg,
    rgba(255, 255, 255, 0.35) 0%,
    transparent 25%,
    transparent 75%,
    rgba(0, 0, 0, 0.2) 100%
  );
}

.platter-shimmer--alt {
  background: radial-gradient(
    ellipse 40% 20% at 30% 25%,
    rgba(255, 255, 255, 0.25) 0%,
    transparent 100%
  );
}

.platter-shimmer--on {
  opacity: 1;
  animation: shimmer 2s ease-in-out infinite;
}

.record {
  position: absolute;
  width: min(98vmin, 790px);
  height: min(98vmin, 790px);
  background: #1a1a1a;
  border: 4px solid #000;
  border-radius: 999px;
  box-sizing: border-box;
  display: grid;
  place-items: center;
  overflow: hidden;
  z-index: 3;
  will-change: transform;
}

.record-groove {
  position: absolute;
  border-radius: 999px;
  border: 2px solid rgba(148, 163, 184, 0.35);
  pointer-events: none;
  box-sizing: border-box;
}
.record-groove--1 {
  inset: 10%;
}
.record-groove--2 {
  inset: 16%;
}
.record-groove--3 {
  inset: 22%;
}
.record-groove--4 {
  inset: 28%;
}
.record-groove--5 {
  inset: 34%;
}

.record-gloss {
  position: absolute;
  inset: 0;
  border-radius: 999px;
  pointer-events: none;
}
.record-gloss--bar {
  background: linear-gradient(
    135deg,
    transparent 30%,
    rgba(255, 255, 255, 0.15) 45%,
    rgba(255, 255, 255, 0.25) 50%,
    rgba(255, 255, 255, 0.15) 55%,
    transparent 70%
  );
  opacity: 0.9;
}
.record-gloss--arc {
  background: conic-gradient(
    from 0deg,
    transparent 0deg,
    rgba(255, 255, 255, 0.1) 30deg,
    transparent 60deg,
    transparent 180deg,
    rgba(255, 255, 255, 0.08) 210deg,
    transparent 240deg
  );
  opacity: 0.85;
}
.record-gloss--rim {
  inset: 0;
  padding: 4px;
  background: linear-gradient(
    145deg,
    rgba(255, 255, 255, 0.2) 0%,
    transparent 30%,
    transparent 70%,
    rgba(0, 0, 0, 0.3) 100%
  );
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  border: 4px solid transparent;
  box-sizing: border-box;
}

.record-label {
  width: min(33vmin, 160px);
  height: min(33vmin, 160px);
  /* 参考 uiineed 配色：暖黄标签 */
  background: #fff9e6;
  border: 4px solid #000;
  border-radius: 999px;
  box-sizing: border-box;
  position: relative;
  z-index: 4;
  display: grid;
  place-items: center;
  overflow: hidden;
}

.record-label-gloss {
  position: absolute;
  inset: 0;
  border-radius: 999px;
  pointer-events: none;
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.4) 0%,
    transparent 50%,
    rgba(0, 0, 0, 0.1) 100%
  );
}

.record-label-hole {
  width: min(5.6vmin, 30px);
  height: min(5.6vmin, 30px);
  background: #000;
  border-radius: 999px;
  z-index: 1;
}

.needle {
  position: absolute;
  top: 18px;
  /* 让唱针整体向左偏一点 */
  right: 50px;
  transform-origin: 16px 16px;
  /* 往左摆动幅度减小（从 -15deg -> -10deg） */
  transform: rotate(-0deg);
  transition: transform 0.5s ease-in-out;
  z-index: 6;
}

.needle--on {
  /* 向右摆动幅度减小（从 25deg -> 18deg） */
  transform: rotate(40deg);
}

.needle-base {
  width: 30px;
  height: 30px;
  background: #c0c0c0;
  border: 4px solid #000;
  border-radius: 999px;
  box-shadow: 4px 4px 0 rgba(0, 0, 0, 1);
  box-sizing: border-box;
}

.needle-arm {
  position: absolute;
  top: 18px;
  left: 50%;
  transform: translateX(-50%);
  width: 12px;
  /* 让唱针臂更长，前端更明显 */
  height: min(34vmin, 300px);
  background: #c0c0c0;
  border: 4px solid #000;
  box-shadow: 4px 4px 0 rgba(0, 0, 0, 1);
  box-sizing: border-box;
  transform-origin: top;
}

.needle-head {
  position: absolute;
  left: 50%;
  bottom: -30px;
  transform: translateX(-50%);
  width: 24px;
  height: 40px;
  /* 参考 uiineed 配色：薄荷绿（不影响黑胶黑色） */
  background: var(--u-bg-completed);
  /* 更鲜亮一点：向白色提亮 */
  background: color-mix(in srgb, var(--u-bg-completed) 78%, #ffffff 22%);
  border: 4px solid #000;
  box-shadow: 3px 3px 0 rgba(0, 0, 0, 1);
  box-sizing: border-box;
}

.needle-tip {
  position: absolute;
  left: 50%;
  bottom: -10px;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 12px solid #000;
}

@keyframes shimmer {
  0%,
  100% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
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

  .turntable {
    inset: 14px;
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
