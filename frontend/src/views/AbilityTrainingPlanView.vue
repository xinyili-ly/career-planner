<template>
  <div class="ability-plan-view" :class="theme">
    <AppHeader />

    <main class="page-scroll">
      <section class="panel guide-panel">
        <div class="guide-wrap">
          <header class="guide-top">
            <h1 class="guide-title">能力培训指引</h1>
            <p class="guide-desc">
              本系统支持通过简历/职业发展报告生成个性化能力培养计划。通过对报告解析出的能力连线、优势特长、短板
              维度及职业目标等信息进行数据建模，自动生成可视化的三个月个性化培养计划甘特图，同时配套输出由浅入深、
              侧重实证推进的学习任务清单（To Do List），为学生提供可直接执行、阶段清晰的成长方案。
            </p>
          </header>

          <section class="gantt-section">
            <div class="side-label" aria-hidden="true">
              <span>甘特图</span>
              <span>示例</span>
            </div>
            <div class="gantt-card" role="img" aria-label="甘特图示例">
              <img class="gantt-img" :src="ganttExampleImg" alt="甘特图示例" />
            </div>
          </section>

          <section class="todo-section">
            <div class="todo-card" role="img" aria-label="To Do List 示例">
              <img class="todo-img" :src="todoExampleImg" alt="To Do List 示例" />
            </div>
            <div class="todo-side" aria-hidden="true">
              <div class="todo-hand">To Do</div>
              <div class="todo-hand">List</div>
            </div>
          </section>

          <section class="guide-bottom">
            <p class="bottom-note">
              如果你还没有生成基于你的职业发展报告，请先生成发展报告请完善生成你的专属提升计划哦，点击下面按钮进行构建学生能力画像。
            </p>
            <button class="u-btn u-btn--primary u-btn--lg" type="button" @click="goStudentAbilities">
              跳转页到第二页
            </button>
          </section>
        </div>
      </section>

      <footer class="site-footer">
        <span>© {{ new Date().getFullYear() }} 职途智引 · AI职业规划助手</span>
      </footer>

    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useTheme } from '../composables/useTheme'
import AppHeader from '../components/AppHeader.vue'
import ganttExampleImg from '../assets/training-guide/gantt-example.png'
import todoExampleImg from '../assets/training-guide/todo-example.png'

const { theme } = useTheme()
const router = useRouter()

const goStudentAbilities = () => {
  router.push('/student-abilities')
}
</script>

<style scoped>
.ability-plan-view {
  --u-border-radius: 12px;

  width: 100vw;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--u-body-bg);
  color: var(--u-black);
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.ability-plan-view.dark {
  background: var(--dm-bg);
  color: var(--dm-text);
}

.ability-plan-view.dark .guide-title {
  color: var(--dm-text);
}

.ability-plan-view.dark .guide-desc {
  color: var(--dm-text-secondary);
}

.ability-plan-view.dark .side-label {
  color: var(--dm-text-secondary);
}

.ability-plan-view.dark .todo-side {
  color: var(--dm-text-secondary);
}

.ability-plan-view.dark .bottom-note {
  color: var(--dm-text-secondary);
}

.ability-plan-view.dark .jump-btn {
  background: var(--dm-surface-elevated);
  color: var(--dm-text);
  box-shadow: 0 10px 26px rgba(0, 0, 0, 0.25);
}

.header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 2vw;
  background: rgba(255, 255, 255, 0.95);
  border-bottom: var(--u-border);
}

.ability-plan-view.dark .header {
  background: var(--dm-header-bg);
  backdrop-filter: blur(12px);
  border-bottom-color: var(--dm-border);
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

.ability-plan-view.dark .nav-item {
  color: var(--dm-text);
}

.ability-plan-view.dark .nav-item.active {
  color: var(--dm-accent);
}

.ability-plan-view.dark .nav-item.active::after {
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

.ability-plan-view.dark .theme-toggle {
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

.ability-plan-view.dark .theme-option.active {
  background: var(--dm-surface-elevated);
  color: var(--dm-text);
}

.page-scroll {
  padding: 28px 6vw 56px 64px;
  flex: 1;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 16px;
  /* 外层保留纯色底，波点挪到 panel 上（与纯色“调换位置”） */
  background: linear-gradient(var(--u-body-bg), var(--u-body-bg));
}

.panel {
  background:
    radial-gradient(circle at 12px 12px, rgba(51, 50, 46, 0.1) 1.6px, transparent 2.2px) 0 0 / 28px 28px,
    linear-gradient(135deg, var(--u-gradient-fade), var(--u-gradient-fade-mid));
  border-radius: 18px;
  padding: clamp(22px, 2.2vw, 40px);
  border: var(--u-border);
  box-shadow: var(--u-box-shadow);
}

.ability-plan-view.dark .panel {
  background: var(--dm-gradient-card);
  border: 1px solid var(--dm-border);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.guide-wrap {
  width: min(1240px, 100%);
  margin: 0 auto;
}

.guide-top {
  margin-top: 6px;
  /* 让标题/说明更贴近左侧（不改变整体居中容器） */
  margin-left: clamp(-28px, -2vw, -12px);
}

.guide-title {
  font-size: clamp(36px, 3vw, 52px);
  letter-spacing: 2px;
  margin: 0 0 12px;
  color: rgba(51, 50, 46, 0.78);
  font-weight: 800;
}

.guide-desc {
  margin: 0;
  line-height: 1.75;
  font-size: clamp(15px, 1.05vw, 18px);
  color: rgba(51, 50, 46, 0.78);
}

.gantt-section {
  margin-top: clamp(18px, 2vw, 28px);
  display: grid;
  grid-template-columns: clamp(110px, 9vw, 150px) 1fr;
  align-items: center;
  gap: clamp(14px, 1.8vw, 24px);
}

.side-label {
  display: grid;
  place-items: center;
  color: rgba(51, 50, 46, 0.65);
  font-weight: 700;
  font-size: clamp(20px, 1.8vw, 28px);
  line-height: 1.2;
  writing-mode: vertical-rl;
  text-orientation: upright;
  letter-spacing: 2px;
}

.gantt-card {
  border-radius: 18px;
  overflow: hidden;
  box-shadow: var(--u-box-shadow);
  background: rgba(255, 255, 255, 0.9);
  border: var(--u-border);
  transform: translateZ(0);
}

.gantt-img {
  width: 100%;
  height: auto;
  display: block;
}

.gantt-section .gantt-card {
  background: linear-gradient(135deg, var(--u-body-bg-fade), var(--u-gradient-fade));
}

.todo-section {
  margin-top: clamp(18px, 2vw, 28px);
  display: grid;
  grid-template-columns: 1fr clamp(120px, 10vw, 170px);
  gap: clamp(12px, 1.6vw, 22px);
  align-items: center;
}

.todo-card {
  border-radius: 18px;
  overflow: hidden;
  box-shadow: var(--u-box-shadow);
  background: rgba(255, 255, 255, 0.9);
  border: var(--u-border);
  transform: translateZ(0);
}

@media (min-width: 1200px) {
  /* 大屏下再拉宽一档，让图片更“铺开” */
  .guide-wrap {
    width: min(1400px, 100%);
  }
}

.todo-img {
  width: 100%;
  height: auto;
  display: block;
}

.todo-section .todo-card {
  background: linear-gradient(135deg, var(--u-fade-submit), var(--u-gradient-fade));
}

.todo-side {
  display: grid;
  gap: 8px;
  justify-items: center;
  color: rgba(15, 23, 42, 0.45);
}

.todo-hand {
  font-size: clamp(22px, 2vw, 32px);
  letter-spacing: 2px;
  font-weight: 700;
  transform: rotate(-2deg);
}

.guide-bottom {
  margin-top: 18px;
  text-align: center;
}

.bottom-note {
  margin: 0 auto 14px;
  max-width: 980px;
  font-size: clamp(13px, 0.95vw, 16px);
  line-height: 1.75;
  color: rgba(15, 23, 42, 0.45);
}

.jump-btn {
  border: none;
  cursor: pointer;
  padding: 12px 26px;
  border-radius: 999px;
  background: rgba(253, 230, 200, 0.95);
  color: rgba(180, 90, 20, 0.55);
  font-weight: 800;
  letter-spacing: 1px;
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.08);
}

.jump-btn:hover {
  filter: brightness(1.02);
  transform: translateY(-1px);
}

.jump-btn:active {
  transform: translateY(0);
}

.site-footer {
  margin-top: auto;
  padding-top: 24px;
  border-top: 1px solid rgba(148, 163, 184, 0.35);
  font-size: clamp(14px, 0.9vw, 16px);
  color: #94a3b8;
  text-align: center;
  width: 100%;
}

.ability-plan-view.dark .site-footer {
  border-top-color: var(--dm-border);
  color: var(--dm-text-muted);
}

@media (max-width: 900px) {
  .nav {
    display: none;
  }
  .page-scroll {
    padding-inline: 16px;
  }
  .gantt-section {
    grid-template-columns: 90px 1fr;
    gap: 12px;
  }
  .todo-section {
    grid-template-columns: 1fr;
  }
  .todo-side {
    order: -1;
    grid-auto-flow: column;
    justify-content: center;
  }
}
</style>

