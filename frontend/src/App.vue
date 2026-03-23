<template>
  <!-- 根容器，包裹路由出口；夜间模式由 theme 控制，全站一致 -->
  <div id="app" :class="theme">
    <router-view />
  </div>
</template>

<script setup>
import { provide, watch } from 'vue'
import { useTheme } from './composables/useTheme'

const { theme, setTheme } = useTheme()
provide('theme', theme)
provide('setTheme', setTheme)

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
</script>

<style>
/* 保持 App 根节点最小化全局样式，避免影响各页面自定义导航布局 */
#app {
  min-height: 100vh;
}
</style>