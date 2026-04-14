<template>
  <!-- 根容器，包裹路由出口；夜间模式由 theme 控制，全站一致 -->
  <div id="app" :class="theme">
    <transition name="ai-status-fade">
      <div v-if="showAiFallbackNotice" class="ai-status-banner" :class="{ dark: theme === 'dark' }">
        <div class="ai-status-banner__text">
          当前 AI 逻辑思考中，为您展示本地知识库推荐...
        </div>
        <button
          type="button"
          class="ai-status-banner__btn"
          :disabled="reconnecting"
          @click="retryAiConnection"
        >
          {{ reconnecting ? '连接中...' : '重新连接 AI' }}
        </button>
      </div>
    </transition>
    <router-view />
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, provide, ref, watch } from 'vue'
import { useTheme } from './composables/useTheme'
import { checkCareerAgentConnection } from './api/careerAgentApi'

const { theme, setTheme } = useTheme()
provide('theme', theme)
provide('setTheme', setTheme)
const showAiFallbackNotice = ref(false)
const reconnecting = ref(false)

const handleCareerAgentStatus = (evt) => {
  const ok = Boolean(evt?.detail?.ok)
  showAiFallbackNotice.value = !ok
}

const retryAiConnection = async () => {
  reconnecting.value = true
  try {
    await checkCareerAgentConnection()
    showAiFallbackNotice.value = false
  } catch {
    showAiFallbackNotice.value = true
  } finally {
    reconnecting.value = false
  }
}

watch(
  theme,
  (v) => {
    const root = document.documentElement
    const isDark = v === 'dark'
    root.classList.toggle('dark', isDark)
    root.classList.toggle('light', !isDark)
  },
  { immediate: true },
)

onMounted(() => {
  window.addEventListener('career-agent-status', handleCareerAgentStatus)
})

onUnmounted(() => {
  window.removeEventListener('career-agent-status', handleCareerAgentStatus)
})
</script>

<style>
/* 保持 App 根节点最小化全局样式，避免影响各页面自定义导航布局 */
#app {
  min-height: 100vh;
}

.ai-status-banner {
  position: fixed;
  right: 16px;
  top: 16px;
  z-index: 9999;
  max-width: min(92vw, 430px);
  display: flex;
  align-items: center;
  gap: 12px;
  border-radius: 12px;
  padding: 12px 14px;
  background: linear-gradient(135deg, #e6fffb, #eff6ff);
  border: 1px solid rgba(56, 189, 248, 0.35);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.12);
}

.ai-status-banner.dark {
  background: linear-gradient(135deg, rgba(15, 118, 110, 0.24), rgba(30, 64, 175, 0.24));
  border-color: rgba(125, 211, 252, 0.38);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.35);
}

.ai-status-banner__text {
  flex: 1;
  font-size: 13px;
  line-height: 1.5;
}

.ai-status-banner__btn {
  border: 1px solid rgba(37, 99, 235, 0.35);
  border-radius: 999px;
  padding: 6px 12px;
  background: #fff;
  color: #1d4ed8;
  cursor: pointer;
}

.ai-status-banner__btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.ai-status-fade-enter-active,
.ai-status-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.ai-status-fade-enter-from,
.ai-status-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>