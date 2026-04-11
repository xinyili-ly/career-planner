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
        <h2 class="title">从画像到行动的职业探索指南</h2>

        <div class="step">
          <h3 class="step-head">
            <span class="num">01</span>
            <span class="step-head-text">| 启动与环境接入流程</span>
          </h3>
          <p class="step-meta">[ 核心动作：项目初始化 · 视觉主题定义 ]</p>
          <p>
            <strong>快速启动：</strong>
            运行项目后，从首页（Index）一键直达<strong>「就业岗位画像」或「学生能力画像」</strong>核心入口。
          </p>
          <p>
            <strong>个性化感知：</strong>
            通过顶栏切换<strong>浅色/深色（深邃科技）</strong>主题。系统利用 localStorage
            自动记忆你的视觉偏好，确保每次开启「职业奥德赛」之旅时，界面始终符合你的审美直觉。
          </p>
        </div>

        <div class="step">
          <h3 class="step-head">
            <span class="num">02</span>
            <span class="step-head-text">| 维度画像与深度评分</span>
          </h3>
          <p class="step-meta">[ 核心动作：岗位透视 · 能力拆解 · 路径演化 ]</p>
          <p>
            <strong>岗位深度洞察：</strong>
            优先调取后端动态数据（<code>/recommend/list</code>），若网络受限则自动激活本地数据兜底。解析
            7 大核心维度要求，同步开启「垂直晋升」与「横向换岗」血缘图谱，预判职业天花板。
          </p>
          <p>
            <strong>学生能力建模：</strong>
            通过简历解析或 AI 对话，将个人经历转化为结构化画像。系统实时计算完整度与竞争力评分，将模糊的「自我介绍」转化为可量化的数字化核心竞争力。
          </p>
        </div>

        <div class="step">
          <h3 class="step-head">
            <span class="num">03</span>
            <span class="step-head-text">| 匹配报告与实战训练计划</span>
          </h3>
          <p class="step-meta">[ 核心动作：契合度对标 · 动态执行 · 本地持久化 ]</p>
          <p>
            <strong>智能报告生成：</strong>
            在「匹配与报告」模块选定目标岗位，AI 自动执行四维能力对标，识别技能鸿沟，生成可润色、可导出的个性化职业生涯发展报告。
          </p>
          <p>
            <strong>能力进化闭环：</strong>
            进入「能力培训计划」，系统自动排布 12 周阶梯式甘特图。支持对 To Do
            任务清单进行增删改查，所有进度与调整均实现本地自动保存，确保你的每一个成长节点都精准落地。
          </p>
        </div>

        <div class="story-tips">
          <p class="tips-lead">💡 操作小贴士：</p>
          <p>
            <strong>优先体验：</strong>
            建议先在 02 中完成简历解析，再进入 03 生成报告，这样 AI
            才能基于你的真实画像给出精准建议。
          </p>
          <p>
            <strong>数据保障：</strong>
            即使在离线演示状态下，系统依然能凭借内置的 mock data 跑通全流程，保证演示的连续性。
          </p>
        </div>
      </div>

      <div class="content-spacer" aria-hidden="true" />
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useTheme } from '../composables/useTheme'

const { theme } = useTheme()

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
  gap: clamp(26px, 3.2vw, 34px);
  max-width: min(46rem, 100%);
  margin-left: clamp(32px, 4.2vw, 64px);
}

.title {
  font-size: clamp(26px, 3.5vw, 42px);
  font-weight: 900;
  margin: 0;
  padding-bottom: clamp(12px, 1.6vw, 18px);
  line-height: 1.18;
  color: #111;
  border-bottom: 2px solid rgba(17, 17, 17, 0.1);
}

.step {
  display: flex;
  flex-direction: column;
  gap: 0;
  border-bottom: 1px solid rgba(17, 17, 17, 0.1);
  padding-bottom: clamp(22px, 2.8vw, 30px);
}

.step:last-of-type {
  border-bottom: none;
  padding-bottom: 0;
}

.step-head {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 0 0.4em;
  font-size: clamp(17px, 1.45vw, 21px);
  font-weight: 800;
  margin: 0 0 10px;
  line-height: 1.32;
  color: #111;
}

.step-head .num {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: clamp(19px, 2vw, 23px);
  color: #ffb8d9;
  font-style: italic;
  font-weight: bold;
}

.step-meta {
  margin: 0 0 16px;
  padding: 10px 14px;
  font-size: clamp(12.5px, 0.95vw, 14.5px);
  color: #555;
  font-weight: 600;
  letter-spacing: 0.03em;
  line-height: 1.5;
  background: rgba(17, 17, 17, 0.04);
  border-radius: 10px;
  border-left: 3px solid #ffb8d9;
}

.step p {
  margin: 0 0 14px;
  line-height: 1.72;
  color: #555;
  font-size: clamp(14px, 1.05vw, 16.5px);
}

.step p:last-child {
  margin-bottom: 0;
}

.step p strong {
  font-weight: 800;
  color: #1a1a1a;
}

.step code {
  font-size: 0.9em;
  padding: 0.15em 0.45em;
  background: rgba(0, 0, 0, 0.07);
  border-radius: 5px;
  font-family: ui-monospace, 'Cascadia Code', monospace;
}

.story-tips {
  margin-top: clamp(4px, 0.6vw, 8px);
  padding: clamp(18px, 2.2vw, 22px) clamp(16px, 2vw, 20px);
  border-radius: 14px;
  background: rgba(59, 130, 246, 0.07);
  border: 1px solid rgba(17, 17, 17, 0.08);
}

.story-tips p {
  margin: 0 0 14px;
  line-height: 1.72;
  color: #555;
  font-size: clamp(14px, 1.05vw, 16.5px);
}

.story-tips p:last-child {
  margin-bottom: 0;
}

.tips-lead {
  font-weight: 800;
  color: #111;
  font-size: clamp(14px, 1.1vw, 16px);
  margin: 0 0 12px !important;
}

.story-tips p strong {
  font-weight: 800;
  color: #1a1a1a;
}

/* 深色主题：与全局 --u-body-bg（html.dark）一致 */
.vinyl-pro--dark.vinyl-container {
  background: var(--u-body-bg);
}

.vinyl-pro--dark .vinyl-visual {
  background: var(--u-body-bg);
}

.vinyl-pro--dark .title {
  color: var(--dm-text, #e4e4e4);
  border-bottom-color: rgba(255, 255, 255, 0.14);
}

.vinyl-pro--dark .step-head,
.vinyl-pro--dark .tips-lead {
  color: var(--dm-text, #e4e4e4);
}

.vinyl-pro--dark .step p,
.vinyl-pro--dark .story-tips p {
  color: var(--dm-text-secondary, rgba(228, 228, 228, 0.78));
}

.vinyl-pro--dark .step p strong,
.vinyl-pro--dark .story-tips p strong {
  color: var(--dm-text, #e4e4e4);
}

.vinyl-pro--dark .step-meta {
  color: var(--dm-text-secondary, rgba(228, 228, 228, 0.78));
  background: rgba(255, 255, 255, 0.06);
  border-left-color: rgba(255, 184, 217, 0.85);
}

.vinyl-pro--dark .step code {
  background: rgba(255, 255, 255, 0.1);
  color: var(--dm-text, #e4e4e4);
}

.vinyl-pro--dark .step {
  border-bottom-color: rgba(255, 255, 255, 0.12);
}

.vinyl-pro--dark .story-tips {
  background: rgba(96, 165, 250, 0.1);
  border-color: rgba(255, 255, 255, 0.1);
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
}
</style>
