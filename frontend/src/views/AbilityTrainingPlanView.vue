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
            <div class="gantt-card-outer">
              <div class="gantt-sticker-tag" aria-hidden="true">甘特图示例</div>
              <div class="gantt-card" role="img" aria-label="甘特图示例">
                <!-- 与实际生成页同款甘特图渲染结构（示例数据） -->
                <div class="gantt" aria-hidden="true">
                  <div class="gantt-head">
                    <div class="corner"></div>
                    <div v-for="w in weeks" :key="w" class="week">W{{ w }}</div>
                  </div>

                  <div v-for="row in ganttRows" :key="row.label" class="gantt-row">
                    <div class="row-label">{{ row.label }}</div>
                    <div class="row-grid">
                      <div
                        v-for="(bar, idx) in row.bars"
                        :key="idx"
                        class="bar"
                        :class="bar.tone"
                        :style="barStyle(bar)"
                      >
                        {{ bar.title }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section class="todo-section">
            <div class="todo-example-wrap">
              <div class="todo-card-outer">
                <div class="todo-card" role="group" aria-label="To Do List 示例">
                  <ul class="todo-list" aria-label="待办事项示例">
                    <li class="todo-li">
                      <label class="todo-item todo-item--done">
                        <input class="todo-checkbox" type="checkbox" checked disabled>
                        <span class="todo-text">第 1 周：完成能力基线测评</span>
                      </label>
                    </li>
                    <li class="todo-li">
                      <label class="todo-item todo-item--done">
                        <input class="todo-checkbox" type="checkbox" checked disabled>
                        <span class="todo-text">第 2 周：学习资源搭建与路线确认</span>
                      </label>
                    </li>
                    <li class="todo-li">
                      <label class="todo-item todo-item--done">
                        <input class="todo-checkbox" type="checkbox" checked disabled>
                        <span class="todo-text">第 3 周：完成基础技能训练（Phase 1）</span>
                      </label>
                    </li>
                    <li class="todo-li">
                      <label class="todo-item todo-item--todo">
                        <input class="todo-checkbox" type="checkbox" disabled>
                        <span class="todo-text">第 4 周：阶段项目任务启动与里程碑拆解</span>
                      </label>
                    </li>
                    <li class="todo-li">
                      <label class="todo-item todo-item--todo">
                        <input class="todo-checkbox" type="checkbox" disabled>
                        <span class="todo-text">第 5 周：产出训练结果并完成自测复盘</span>
                      </label>
                    </li>
                    <li class="todo-li">
                      <label class="todo-item todo-item--todo">
                        <input class="todo-checkbox" type="checkbox" disabled>
                        <span class="todo-text">第 6 周：错题/薄弱点专项强化训练</span>
                      </label>
                    </li>
                    <li class="todo-li">
                      <label class="todo-item todo-item--todo">
                        <input class="todo-checkbox" type="checkbox" disabled>
                        <span class="todo-text">第 7 周：同伴/导师评审与反馈迭代</span>
                      </label>
                    </li>
                    <li class="todo-li">
                      <label class="todo-item todo-item--todo">
                        <input class="todo-checkbox" type="checkbox" disabled>
                        <span class="todo-text">第 8 周：第二阶段综合训练与联动应用</span>
                      </label>
                    </li>
                    <li class="todo-li">
                      <label class="todo-item todo-item--todo">
                        <input class="todo-checkbox" type="checkbox" disabled>
                        <span class="todo-text">第 9 周：沉淀作品集与案例总结</span>
                      </label>
                    </li>
                    <li class="todo-li">
                      <label class="todo-item todo-item--todo">
                        <input class="todo-checkbox" type="checkbox" disabled>
                        <span class="todo-text">第 10 周：复盘总结与下一阶段计划</span>
                      </label>
                    </li>
                  </ul>
                </div>
                <div class="todo-sticker-tag" aria-hidden="true">To Do List 示例</div>
              </div>
            </div>
          </section>

          <section class="guide-bottom">
            <p class="bottom-note">
              {{
                canGeneratePlan
                  ? '已检测到你完成了第二页职业发展报告，可直接进入培训计划生成页。'
                  : '如果你还没有生成基于你的职业发展报告，请先到第二页完成解析与报告生成，再回来生成专属提升计划。'
              }}
            </p>
            <button class="u-btn u-btn--primary u-btn--lg jump-btn" type="button" @click="handleGuideAction">
              {{ canGeneratePlan ? '培训计划生成' : '跳转到第二页' }}
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
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTheme } from '../composables/useTheme'
import AppHeader from '../components/AppHeader.vue'
import { getActionPlanCheckPending, isCareerAgentApiEnabled } from '../api/careerAgentApi'

const { theme } = useTheme()
const router = useRouter()
const TRAINING_PLAN_READY_KEY = 'career_planner_training_plan_ready_v1'
const STUDENT_ID_KEY = 'career_planner_student_id_v1'
const canGeneratePlan = ref(false)

const weeks = Array.from({ length: 12 }, (_, i) => i + 1)

// 示例数据：保持与实际生成页同一套结构（ganttRows -> bars -> barStyle）
const ganttRows = [
  {
    label: '基础能力补齐',
    bars: [
      { title: '算法/计网/OS/数据库梳理', start: 1, end: 4, tone: 'mint' },
      { title: '高频专题强化 + 题单', start: 5, end: 8, tone: 'mint' },
      { title: '面试高频点回炉', start: 9, end: 12, tone: 'pink' },
    ],
  },
  {
    label: '项目与作品集',
    bars: [
      { title: 'MVP 选型与需求拆解', start: 1, end: 2, tone: 'purple' },
      { title: '核心功能开发 + 文档', start: 3, end: 7, tone: 'purple' },
      { title: '上线部署 + 作品集包装', start: 8, end: 12, tone: 'yellow' },
    ],
  },
  {
    label: '求职与表达',
    bars: [
      { title: '项目讲解脚本（STAR）', start: 1, end: 3, tone: 'pink' },
      { title: '模拟面试（技术/项目）', start: 4, end: 9, tone: 'yellow' },
      { title: '投递-复盘-迭代闭环', start: 6, end: 12, tone: 'yellow' },
    ],
  },
]

const barStyle = (bar) => {
  const start = Math.max(1, Math.min(12, Number(bar.start || 1)))
  const end = Math.max(start, Math.min(12, Number(bar.end || start)))
  return { gridColumn: `${start} / ${end + 1}` }
}

const syncPlanReadyState = () => {
  try {
    canGeneratePlan.value = sessionStorage.getItem(TRAINING_PLAN_READY_KEY) === '1'
  } catch {
    canGeneratePlan.value = false
  }
}

const getStudentId = () => {
  try {
    const id = sessionStorage.getItem(STUDENT_ID_KEY)
    return id || 'student_demo_001'
  } catch {
    return 'student_demo_001'
  }
}

const syncPlanReadyFromApi = async () => {
  if (!isCareerAgentApiEnabled()) return
  try {
    const data = await getActionPlanCheckPending(getStudentId())
    const hasPlan = Boolean(
      data?.has_active_plan ??
        data?.has_plan ??
        data?.plan_exists ??
        data?.current_plan ??
        (Array.isArray(data?.items) && data.items.length > 0) ??
        (typeof data?.completion_rate === 'number')
    )
    if (hasPlan) {
      canGeneratePlan.value = true
      try {
        sessionStorage.setItem(TRAINING_PLAN_READY_KEY, '1')
      } catch {
        // ignore write errors
      }
    }
  } catch (e) {
    console.warn('[career-agent] action-plan/check-pending', e)
  }
}

const handleGuideAction = () => {
  if (canGeneratePlan.value) {
    router.push('/ability-training-plan/generated')
    return
  }
  router.push('/student-abilities')
}

onMounted(async () => {
  syncPlanReadyState()
  await syncPlanReadyFromApi()
})
</script>

<style scoped>
.ability-plan-view {
  --u-border-radius: 12px;
  /* 示例左右卡片统一尺寸：页面宽度的二分之一（中等屏上再做上限收敛） */
  --example-half-width: 50%;
  /* 甘特图示例方框高度：贴近生成页（约 52 + 3*74） */
  --example-height: clamp(280px, 34vh, 360px);
  --todo-side-width: clamp(90px, 9vw, 140px);

  width: 100vw;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--u-body-bg);
  color: var(--u-black);
  font-family: var(--font-family-sans);
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
  font-size: var(--fs-h3);
  font-weight: var(--fw-heading);
  letter-spacing: 2px;
}

.nav {
  display: flex;
  gap: 1.5vw;
}

.nav-item {
  font-size: var(--fs-small);
  font-weight: var(--fw-body);
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
  font-size: var(--fs-small);
  font-weight: var(--fw-body);
}

.theme-toggle {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.75);
  border: var(--u-border);
  box-shadow: 2px 2px 0px var(--u-black);
  padding: 4px;
  font-size: var(--fs-small);
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
  /* 让第二/第三分界面的淡蓝背景透出来：外层不再使用大面积波点/硬边框 */
  background: transparent;
  border-radius: 18px;
  padding: clamp(22px, 2.2vw, 40px);
  border: none;
  box-shadow: none;
}

.ability-plan-view.dark .panel {
  background: transparent;
  border: none;
  box-shadow: none;
}

.guide-wrap {
  /* 让后续“半屏宽度”基于真实页面内容宽度计算 */
  width: 100%;
  margin: 0 auto;
}

.guide-top {
  margin-top: 6px;
  /* 标题+说明收窄并居中（约占页面 2/3 宽度） */
  width: min(86%, 1360px);
  margin-inline: auto;
}

.guide-title {
  font-size: var(--fs-h1);
  letter-spacing: 2px;
  margin: 0 0 12px;
  color: #000000;
  font-weight: var(--fw-heading);
}

.ability-plan-view.dark .guide-title {
  color: var(--dm-text);
}

.guide-desc {
  margin: 0;
  line-height: 1.75;
  font-size: var(--fs-body);
  font-weight: var(--fw-body);
  color: rgba(51, 50, 46, 0.78);
}

@media (max-width: 900px) {
  .guide-top {
    width: 100%;
  }
}

.gantt-section {
  margin-top: clamp(32px, 2.6vw, 40px);
  display: flex;
  justify-content: center;
  width: 100%;
}

.side-label {
  display: grid;
  place-items: center;
  color: rgba(51, 50, 46, 0.65);
  font-weight: 700;
  font-size: var(--fs-h2);
  line-height: 1.2;
  writing-mode: vertical-rl;
  text-orientation: upright;
  letter-spacing: 2px;
}

.gantt-card {
  /* 与外层 16px 圆角、3px 黑边对齐的内侧圆角 */
  border-radius: calc(16px - 3px);
  overflow: hidden;
  box-shadow: none;
  background: transparent;
  border: none;
  height: 100%;
  width: 100%;
  /* 避免创建新的堆叠上下文导致贴纸被图片盖住 */
  transform: none;
  position: relative;
  z-index: 1;
}

.gantt-card-outer {
  position: relative;
  /* 与 To Do 示例外层一致；无内边距，甘特底色铺满至黑边内侧 */
  background: rgba(255, 255, 255, 0.98);
  border: 3px solid var(--u-black); /* 3px 黑边 */
  border-radius: 16px;
  padding: 0;
  box-shadow: 0 18px 40px rgba(16, 24, 40, 0.08);
  width: var(--example-half-width);
  height: var(--example-height);
}

.ability-plan-view.dark .gantt-card-outer {
  background: rgba(28, 33, 40, 0.88);
}

.gantt-sticker-tag {
  position: absolute;
  top: -12px;
  left: -8px;
  z-index: 3;
  pointer-events: none;
  padding: 8px 12px;
  /* 贴纸：白底黑字 + 黑边 */
  background: #ffffff;
  color: #000000;
  border: 2px solid #000000;
  border-radius: 10px;
  font-weight: 900;
  letter-spacing: 1px;
  font-size: var(--fs-small);
  transform: rotate(-2deg);
}

.ability-plan-view.dark .gantt-sticker-tag {
  background: #ffffff;
  color: #000000;
}

.gantt {
  height: 100%;
  border-radius: 0;
  /* 与示例卡片主色一致，纯色底；圆角由 .gantt-card 裁切 */
  background: var(--u-bg-normal);
  border: none;
  overflow: hidden;
}

.ability-plan-view.dark .gantt {
  background: var(--dm-surface-card);
  border: none;
}

.gantt-head {
  display: grid;
  grid-template-columns: 160px repeat(12, 1fr);
  align-items: center;
  background: transparent;
  border-bottom: 1px solid rgba(148, 163, 184, 0.25);
}

.ability-plan-view.dark .gantt-head {
  background: transparent;
  border-bottom-color: var(--dm-border);
}

.corner {
  height: 52px;
}

.week {
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  color: var(--u-black);
  font-size: var(--fs-tiny);
}

.ability-plan-view.dark .week {
  color: var(--dm-text);
}

.gantt-row {
  display: grid;
  grid-template-columns: 160px 1fr;
  min-height: 74px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.22);
}

.gantt-row:last-child {
  border-bottom: none;
}

.row-label {
  padding: 14px 12px;
  font-size: var(--fs-small);
  font-weight: 700;
  line-height: 1.35;
  background: transparent;
  color: var(--u-black);
  display: flex;
  align-items: center;
}

.ability-plan-view.dark .row-label {
  background: transparent;
  color: var(--dm-text);
}

.row-grid {
  position: relative;
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  align-items: center;
  padding: 10px 12px;
  gap: 10px;
}

.bar {
  border-radius: 14px;
  padding: 10px 12px;
  color: var(--u-black);
  font-size: var(--fs-small);
  line-height: 1.25;
  box-shadow: 2px 2px 0px var(--u-black);
  border: var(--u-border);
}

.ability-plan-view.dark .bar {
  background: rgba(255, 255, 255, 0.06);
  color: var(--dm-text);
  border-color: var(--dm-border);
}

.bar.mint {
  background: var(--u-bg-completed);
}

.bar.purple {
  background: var(--u-body-bg);
}

.bar.yellow {
  background: var(--u-bg-normal);
}

.bar.pink {
  background: var(--u-bg-submit);
}

@media (max-width: 900px) {
  .gantt-head {
    grid-template-columns: 120px repeat(12, 1fr);
  }

  .gantt-row {
    grid-template-columns: 120px 1fr;
  }
}

.todo-section {
  margin-top: clamp(44px, 3.6vw, 58px);
  display: flex;
  justify-content: center;
  width: 100%;
}

.todo-example-wrap {
  width: var(--example-half-width);
  height: var(--example-height);
  display: block;
}

.todo-card-outer {
  position: relative;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.98);
  border: 3px solid var(--u-black);
  border-radius: 16px;
  padding: 0;
  box-shadow: 0 18px 40px rgba(16, 24, 40, 0.08);
}

.ability-plan-view.dark .todo-card-outer {
  background: rgba(28, 33, 40, 0.88);
}

.todo-card {
  border-radius: calc(16px - 3px);
  overflow: hidden;
  box-shadow: none;
  /* 与「已完成」条同款薄荷绿底，替代原先黄/米色 */
  background: var(--u-bg-completed);
  border: none;
  padding: 14px 14px 16px;
  transform: none;
  height: 100%;
  width: 100%;
}

.ability-plan-view.dark .todo-card {
  background: var(--u-bg-completed);
  box-shadow: none;
}

.ability-plan-view.dark .gantt-card {
  border: none;
  box-shadow: none;
}

@media (min-width: 1200px) {
  /* 大屏下再拉宽一档，让图片更“铺开” */
  .guide-wrap {
    width: 100%;
  }
}

.todo-img {
  width: 100%;
  height: auto;
  display: block;
}

.todo-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 100%;
  overflow: auto;
  /* 为右侧 sticker 留出空间（避免遮挡内容） */
  padding-right: 8px;
}

.todo-li {
  margin: 0;
}

.todo-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 10px;
  border-radius: 12px;
  border: 2px solid var(--u-black);
  background: var(--u-bg-normal);
}

.todo-item--done {
  background: var(--u-bg-completed);
}

.todo-item--todo {
  background: var(--u-bg-discard);
}

.ability-plan-view.dark .todo-item {
  background: var(--dm-surface-card);
}

.ability-plan-view.dark .todo-item--done {
  background: rgba(126, 179, 176, 0.18);
}

.ability-plan-view.dark .todo-item--todo {
  background: rgba(109, 59, 82, 0.14);
}

.todo-checkbox {
  appearance: none;
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  border: 3px solid var(--u-black); /* 黑粗边 */
  border-radius: 6px;
  background: var(--u-bg-normal);
  margin: 0;
  display: inline-grid;
  place-items: center;
  flex: 0 0 auto;
}

.todo-checkbox:checked {
  background: var(--u-black);
}

.todo-checkbox:checked::after {
  content: '';
  width: 8px;
  height: 12px;
  border-right: 3px solid #ffffff;
  border-bottom: 3px solid #ffffff;
  transform: rotate(45deg) translate(-1px, -1px);
  display: block;
}

.todo-checkbox:disabled {
  opacity: 1; /* 保持视觉一致 */
}

.todo-text {
  font-size: var(--fs-small);
  line-height: 1.3;
  font-weight: 700;
  color: var(--u-black);
}

.todo-side {
  position: absolute;
  top: 14px;
  right: 10px;
  display: grid;
  gap: 8px;
  justify-items: center;
  color: rgba(15, 23, 42, 0.45);
}

.todo-sticker-tag {
  position: absolute;
  top: -12px;
  right: -8px;
  left: auto;
  z-index: 3;
  pointer-events: none;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.98);
  border: 2px solid var(--u-black);
  border-radius: 10px;
  font-weight: 800;
  letter-spacing: 1px;
  font-size: var(--fs-small);
  transform: rotate(-2deg);
}

.ability-plan-view.dark .todo-sticker-tag {
  background: rgba(28, 33, 40, 0.88);
}

.guide-bottom {
  margin-top: 18px;
  text-align: center;
}

.bottom-note {
  margin: 0 auto 14px;
  max-width: 980px;
  font-size: var(--fs-body);
  font-weight: var(--fw-body);
  line-height: 1.75;
  color: rgba(15, 23, 42, 0.45);
}

.jump-btn {
  border: 2px solid rgba(51, 50, 46, 0.25);
  cursor: pointer;
  padding: 12px 34px;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(253, 230, 200, 0.98) 0%, rgba(255, 214, 233, 0.98) 100%);
  color: rgba(51, 50, 46, 0.88);
  font-weight: 900;
  letter-spacing: 0.8px;
  box-shadow: 0 18px 44px rgba(16, 24, 40, 0.12);
  transition:
    transform 0.18s ease,
    box-shadow 0.18s ease,
    filter 0.18s ease;
}

.jump-btn:hover {
  filter: none;
  transform: translateY(-2px);
  box-shadow: 0 26px 70px rgba(16, 24, 40, 0.16);
}

.jump-btn:active {
  transform: translateY(-1px);
  box-shadow: 0 14px 40px rgba(16, 24, 40, 0.12);
}

.ability-plan-view.dark .jump-btn {
  border: 2px solid rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.92);
  background: var(--dm-gradient-card);
  box-shadow: 0 22px 60px rgba(0, 0, 0, 0.35);
}

.ability-plan-view.dark .jump-btn:hover {
  box-shadow: 0 28px 80px rgba(0, 0, 0, 0.45);
}

.site-footer {
  margin-top: auto;
  padding-top: 24px;
  border-top: 1px solid rgba(124, 141, 167, 0.35);
  font-size: var(--fs-small);
  font-weight: var(--fw-body);
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
  .gantt-card-outer,
  .todo-example-wrap {
    width: 100%;
  }

  .todo-example-wrap {
    /* todo-side 在该断点改为静态布局，不再使用 grid */
  }

  .todo-side {
    position: static;
    margin-top: 10px;
  }

  .todo-list {
    padding-right: 8px;
  }
}
</style>

