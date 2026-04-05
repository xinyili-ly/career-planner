<template>
  <div class="profile-view" :class="theme">
    <AppHeader show-utility-icons />

    <main class="profile-page">
      <!-- 模块1：个人信息卡片 -->
      <section class="profile-card">
        <div class="profile-card__body">
          <div class="profile-avatar-wrap">
            <el-avatar :size="96" class="profile-avatar">
              <el-icon :size="48"><UserFilled /></el-icon>
            </el-avatar>
          </div>
          <div class="profile-info">
            <h1 class="profile-name">{{ user.name }}</h1>
            <p class="profile-meta">
              {{ user.university }} · {{ user.major }} · {{ user.grade }}
            </p>
            <div class="profile-cv">
              <span class="profile-cv-label">简历完整度</span>
              <el-progress
                :percentage="user.cvCompletion"
                :stroke-width="12"
                :show-text="true"
                color="#63bfb7"
                class="profile-cv-progress"
              />
            </div>
          </div>
        </div>
        <div class="profile-card__footer">
          <el-button type="primary" class="profile-btn" @click="onCompleteProfile">
            完善资料
          </el-button>
        </div>
      </section>

      <!-- 模块2：能力画像速览 -->
      <section class="profile-card ability-snapshot">
        <h2 class="ability-snapshot__title">能力画像速览</h2>
        <div class="ability-snapshot__grid">
          <div ref="radarRef" class="radar-mini" />
          <div class="ability-snapshot__right">
            <p class="ability-score-line">
              综合能力指数
              <strong class="ability-score-num">{{ abilitySummary.score }}</strong>
              分
            </p>
            <p class="ability-rank-line">
              竞争力排位前 <strong>{{ abilitySummary.rankPercent }}%</strong>
            </p>
            <RouterLink class="ability-link" to="/student-abilities">
              查看完整画像 →
            </RouterLink>
          </div>
        </div>
      </section>

      <!-- 模块3：报告历史记录 -->
      <section class="profile-card report-history">
        <h2 class="report-history__title">报告历史记录</h2>
        <el-timeline class="report-timeline">
          <el-timeline-item
            v-for="item in reports"
            :key="item.id"
            :timestamp="item.date"
            placement="top"
          >
            <div class="report-item">
              <p class="report-item__title">{{ item.title }}</p>
              <div class="report-item__actions">
                <el-button type="primary" link @click="viewReport(item.id)">
                  查看
                </el-button>
                <el-button type="primary" link @click="downloadReport(item)">
                  下载
                </el-button>
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { UserFilled } from '@element-plus/icons-vue'
import { useTheme } from '../composables/useTheme'
import AppHeader from '../components/AppHeader.vue'

const { theme } = useTheme()
const router = useRouter()

const user = ref({
  name: '李华',
  university: '某985理工大学',
  major: '软件工程',
  grade: '大四',
  cvCompletion: 95
})

const abilitySummary = ref({
  score: 78,
  rankPercent: 60
})

const radarDimensions = [
  { name: '专业技能', max: 100 },
  { name: '创新能力', max: 100 },
  { name: '学习能力', max: 100 },
  { name: '抗压能力', max: 100 },
  { name: '沟通能力', max: 100 },
  { name: '实习能力', max: 100 }
]

const radarValues = [85, 80, 90, 75, 80, 60]

const reports = ref([
  { id: 1, title: 'Java开发工程师职业规划报告', date: '2026-03-10' },
  { id: 2, title: '前端开发工程师职业规划报告', date: '2026-03-05' },
  { id: 3, title: '软件测试工程师职业规划报告', date: '2026-02-28' }
])

const radarRef = ref(null)
let chartInstance = null
let resizeObserver = null

const initRadar = () => {
  if (!radarRef.value) return
  chartInstance = echarts.init(radarRef.value, null, { renderer: 'canvas' })
  chartInstance.setOption({
    radar: {
      indicator: radarDimensions,
      radius: '68%',
      center: ['50%', '52%'],
      splitNumber: 4,
      axisName: {
        color: 'rgba(51, 50, 46, 0.75)',
        fontSize: 11
      },
      splitLine: {
        lineStyle: { color: 'rgba(51, 50, 46, 0.12)' }
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(99, 191, 183, 0.06)', 'rgba(99, 191, 183, 0.02)']
        }
      }
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: radarValues,
            name: '能力',
            areaStyle: {
              color: 'rgba(99, 191, 183, 0.35)'
            },
            lineStyle: {
              color: '#63bfb7',
              width: 2
            },
            itemStyle: {
              color: '#63bfb7'
            }
          }
        ]
      }
    ]
  })
}

const disposeRadar = () => {
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
}

onMounted(() => {
  nextTick(() => {
    initRadar()
    if (radarRef.value && chartInstance) {
      resizeObserver = new ResizeObserver(() => {
        chartInstance?.resize()
      })
      resizeObserver.observe(radarRef.value)
    }
  })
})

onUnmounted(() => {
  disposeRadar()
})

const onCompleteProfile = () => {
  ElMessage.success('已打开完善资料（演示）')
}

const viewReport = (id) => {
  router.push({ name: 'ReportDetail', params: { id: String(id) } })
}

const downloadReport = (item) => {
  ElMessage.info(`下载报告：${item.title}（演示）`)
}
</script>

<style scoped>
.profile-view {
  min-height: 100vh;
  width: 100%;
  background: var(--u-body-bg);
  color: var(--u-black);
}

.profile-view.dark {
  background: var(--dm-bg);
  color: var(--dm-text);
}

.profile-page {
  max-width: 920px;
  margin: 0 auto;
  padding: 24px 20px 48px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.profile-card {
  background: #ffffff;
  border-radius: 16px;
  border: var(--u-border);
  box-shadow: var(--u-box-shadow);
  padding: 24px;
  box-sizing: border-box;
}

.profile-view.dark .profile-card {
  background: var(--dm-surface-card);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35);
  border: 1px solid var(--dm-border);
}

.profile-card__body {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  flex-wrap: wrap;
}

.profile-avatar-wrap {
  flex-shrink: 0;
}

.profile-avatar {
  border: 2px solid rgba(51, 50, 46, 0.12);
  background: linear-gradient(145deg, #e8f6ff, #fef8e7);
  color: rgba(51, 50, 46, 0.65);
}

.profile-info {
  flex: 1;
  min-width: 200px;
}

.profile-name {
  margin: 0 0 8px;
  font-size: clamp(22px, 2vw, 28px);
  font-weight: 700;
}

.profile-meta {
  margin: 0 0 16px;
  font-size: clamp(14px, 1vw, 16px);
  color: rgba(51, 50, 46, 0.72);
  line-height: 1.5;
}

.profile-view.dark .profile-meta {
  color: var(--dm-text-secondary);
}

.profile-cv-label {
  display: block;
  font-size: 14px;
  margin-bottom: 8px;
  color: rgba(51, 50, 46, 0.78);
}

.profile-cv-progress {
  max-width: 100%;
}

:deep(.profile-cv-progress .el-progress-bar__outer) {
  background-color: rgba(51, 50, 46, 0.1);
}

.profile-card__footer {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(51, 50, 46, 0.08);
}

.profile-view.dark .profile-card__footer {
  border-top-color: var(--dm-border);
}

.profile-btn {
  border-radius: 999px;
}

.ability-snapshot__title {
  margin: 0 0 16px;
  font-size: clamp(18px, 1.3vw, 20px);
  font-weight: 600;
}

.ability-snapshot__grid {
  display: grid;
  grid-template-columns: minmax(200px, 260px) 1fr;
  gap: 20px;
  align-items: center;
}

.radar-mini {
  width: 100%;
  height: 220px;
  min-height: 200px;
}

.ability-snapshot__right {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ability-score-line,
.ability-rank-line {
  margin: 0;
  font-size: clamp(15px, 1.05vw, 17px);
  line-height: 1.5;
}

.ability-score-num {
  font-size: clamp(26px, 2vw, 32px);
  margin: 0 4px;
  color: #63bfb7;
}

.ability-link {
  margin-top: 4px;
  font-size: 15px;
  color: #409eff;
  text-decoration: none;
  align-self: flex-start;
}

.ability-link:hover {
  text-decoration: underline;
}

.report-history__title {
  margin: 0 0 16px;
  font-size: clamp(18px, 1.3vw, 20px);
  font-weight: 600;
}

.report-item {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.report-item__title {
  margin: 0;
  font-size: clamp(15px, 1vw, 16px);
  font-weight: 500;
  flex: 1;
  min-width: 0;
}

.report-item__actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

:deep(.report-timeline .el-timeline-item__timestamp) {
  color: rgba(51, 50, 46, 0.55);
  font-size: 13px;
}

.profile-view.dark :deep(.report-timeline .el-timeline-item__timestamp) {
  color: var(--dm-text-muted);
}

@media (max-width: 640px) {
  .profile-page {
    padding: 16px 12px 40px;
  }

  .profile-card {
    padding: 16px;
  }

  .ability-snapshot__grid {
    grid-template-columns: 1fr;
  }

  .radar-mini {
    height: 200px;
  }
}
</style>
