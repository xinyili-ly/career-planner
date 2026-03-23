<template>
  <div class="report-detail-view" :class="theme">
    <AppHeader />
    <main class="report-detail-main">
      <el-card class="report-detail-card" shadow="never">
        <template #header>
          <span class="report-detail-title">报告详情</span>
        </template>
        <p v-if="title" class="report-detail-name">{{ title }}</p>
        <p class="report-detail-id">报告编号：{{ id }}</p>
        <p class="report-detail-hint">
          此处为报告详情占位页，后续可接入真实报告内容或跳转到职业生涯报告模块。
        </p>
        <el-button type="primary" @click="goCareerReport">前往职业生涯报告</el-button>
      </el-card>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTheme } from '../composables/useTheme'
import AppHeader from '../components/AppHeader.vue'

const route = useRoute()
const router = useRouter()
const { theme } = useTheme()

const id = computed(() => route.params.id)

const titleMap = {
  1: 'Java开发工程师职业规划报告',
  2: '前端开发工程师职业规划报告',
  3: '软件测试工程师职业规划报告'
}

const title = computed(() => titleMap[String(id.value)] || '')

const goCareerReport = () => {
  router.push({ name: 'CareerReport' })
}
</script>

<style scoped>
.report-detail-view {
  min-height: 100vh;
  background: #e8f6ff;
  color: #33322e;
}

.report-detail-view.dark {
  background: var(--dm-bg);
  color: var(--dm-text);
}

.report-detail-main {
  max-width: 720px;
  margin: 0 auto;
  padding: 24px 20px 48px;
}

.report-detail-card {
  border-radius: 16px;
}

.report-detail-title {
  font-weight: 600;
  font-size: 18px;
}

.report-detail-name {
  font-size: 17px;
  font-weight: 600;
  margin: 0 0 8px;
}

.report-detail-id {
  color: #64748b;
  margin: 0 0 12px;
}

.report-detail-hint {
  line-height: 1.6;
  color: #64748b;
  margin-bottom: 16px;
}
</style>
