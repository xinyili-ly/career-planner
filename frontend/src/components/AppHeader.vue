<template>
  <header class="header" :class="theme">
    <div class="header-left">
      <RouterLink class="logo" to="/">
        <img class="logo-img" :src="resolvedLogoSrc" alt="职途智引 Logo" />
        <span class="logo-main">职途智引</span>
      </RouterLink>
      <nav class="nav">
        <RouterLink to="/" class="nav-item" :class="{ active: isActive('/') }">
          首页
        </RouterLink>
        <RouterLink
          to="/jobs"
          class="nav-item"
          :class="{ active: isActive('/jobs') }"
        >
          就业岗位画像
        </RouterLink>
        <RouterLink
          to="/student-abilities"
          class="nav-item"
          :class="{ active: isActive('/student-abilities') }"
        >
          学生就业能力
        </RouterLink>
        <RouterLink
          to="/ability-training-plan"
          class="nav-item"
          :class="{ active: isActive('/ability-training-plan') }"
        >
          能力培训计划
        </RouterLink>
      </nav>
    </div>

    <div class="header-right">
      <el-button class="nav-back" text @click="goBack">返回</el-button>
      <div class="theme-toggle" role="tablist" aria-label="主题切换">
        <span
          class="theme-option"
          :class="{ active: theme === 'light' }"
          @click="setTheme('light')"
        >
          light
        </span>
        <span
          class="theme-option"
          :class="{ active: theme === 'dark' }"
          @click="setTheme('dark')"
        >
          black
        </span>
      </div>

      <template v-if="showUtilityIcons">
        <el-button circle class="icon-btn" @click="handleProfileClick">
          <el-icon><User /></el-icon>
        </el-button>
      </template>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { User } from '@element-plus/icons-vue'
import { useTheme } from '../composables/useTheme'
import { popBackTarget, setSkipNextRecord } from '../utils/navigationHistory'

const props = defineProps({
  logoSrc: {
    type: String,
    default: '/logo.png',
  },
  darkLogoSrc: {
    type: String,
    default: '/logo-dark.png',
  },
  backTo: {
    type: [String, Object],
    default: '',
  },
  showUtilityIcons: {
    type: Boolean,
    default: false,
  },
})

const router = useRouter()
const route = useRoute()
const { theme, setTheme } = useTheme()

const resolvedLogoSrc = computed(() =>
  theme.value === 'dark' ? props.darkLogoSrc : props.logoSrc
)

const path = computed(() => String(route.path || '/'))

const isActive = (basePath) => {
  const p = path.value
  if (basePath === '/') return p === '/'
  return p === basePath || p.startsWith(`${basePath}/`)
}

const goBack = () => {
  const currentPath = path.value

  // 主页面点击返回：固定回首页（互不串联）
  if (
    currentPath === '/jobs' ||
    currentPath === '/student-abilities' ||
    currentPath === '/ability-training-plan'
  ) {
    router.push('/')
    return
  }

  // 首页点击返回：不跳转
  if (currentPath === '/') return

  // 子页面：溯源返回到进入当前页之前的确切页面
  const target = popBackTarget()
  if (target) {
    setSkipNextRecord()
    router.replace(target)
    return
  }

  // 兜底：栈为空时，退化到显式 backTo 或首页
  if (props.backTo) {
    router.push(props.backTo)
    return
  }

  router.push('/')
}

const handleProfileClick = () => {
  router.push({ name: 'Profile' })
}
</script>

<style scoped>
.header {
  /* 颜色令牌见 src/assets/main.css（html.dark 夜间覆盖） */
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 2vw;
  background: linear-gradient(135deg, var(--u-gradient-fade), var(--u-header-bg-end));
  backdrop-filter: blur(16px);
  border-bottom: var(--u-border);
  box-shadow: var(--u-box-shadow);
  width: 100%;
  box-sizing: border-box;
}

.header.dark {
  background: rgba(10, 14, 20, 0.72);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
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
  display: inline-flex;
  align-items: center;
  gap: 14px;
}

.logo-img {
  width: clamp(64px, 4.8vw, 88px);
  height: clamp(64px, 4.8vw, 88px);
  object-fit: contain;
  flex: 0 0 auto;
  filter: drop-shadow(2px 2px 0 rgba(51, 50, 46, 0.16));
}

.header.dark .logo-img {
  filter: drop-shadow(0 1px 0 rgba(255, 255, 255, 0.06));
}

.logo-main {
  font-size: clamp(20px, 1.5vw, 28px);
  font-weight: var(--fw-heading);
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
  padding: 8px 12px;
  border-radius: 999px;
  border: var(--u-border);
  box-shadow: 2px 2px 0px var(--u-black);
  background: rgba(255, 255, 255, 0.85);
}

.header.dark .nav-item {
  color: var(--dm-text);
}

.nav-item::after {
  content: none;
}

.nav-item:hover {
  transform: translateY(-1px);
  background: var(--u-bg-completed);
  box-shadow: 3px 3px 0px var(--u-black);
}

.nav-item.active {
  background: var(--u-bg-submit);
  color: var(--u-black);
  box-shadow: 3px 3px 0px var(--u-black);
}

.header.dark .nav-item.active {
  color: var(--dm-accent);
}

.header.dark .nav-item.active::after {
  background: linear-gradient(90deg, var(--dm-accent), var(--dm-accent-secondary));
}

/* 夜间模式也统一“胶囊贴纸”效果（用 dm 变量点缀） */
.header.dark .nav-item {
  background: rgba(18, 24, 32, 0.55);
  border: 2px solid var(--u-stroke);
  box-shadow: 2px 2px 0 var(--u-black);
}

.header.dark .nav-item:hover {
  background: rgba(140, 212, 203, 0.12);
}

.header.dark .nav-item.active {
  background: rgba(255, 214, 233, 0.12);
  color: var(--dm-text);
}

.header.dark .theme-toggle {
  border: 2px solid var(--u-stroke);
  box-shadow: 2px 2px 0 var(--u-black);
}

.header.dark .theme-option.active {
  background: var(--dm-accent-soft);
  color: var(--dm-text);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-back {
  font-size: clamp(15px, 0.95vw, 17px);
  font-weight: var(--fw-body);
}

.header:not(.dark) .nav-back {
  background: var(--u-bg-discard);
  border: var(--u-border);
  box-shadow: 2px 2px 0px var(--u-black);
  color: var(--u-black);
  border-radius: 999px;
  padding: 8px 12px;
}

.theme-toggle {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.82);
  border: var(--u-border);
  box-shadow: 2px 2px 0px var(--u-black);
  padding: 4px;
  font-size: clamp(14px, 0.95vw, 17px);
}

.header.dark .theme-toggle {
  background: var(--dm-surface);
}

.theme-option {
  padding: 4px 12px;
  border-radius: 999px;
  cursor: pointer;
  color: var(--u-black);
  user-select: none;
}

.header.dark .theme-option {
  color: var(--dm-text-secondary);
}

.theme-option.active {
  background: var(--u-bg-submit);
  color: var(--u-black);
}

.header:not(.dark) .theme-option:not(.active):hover {
  background: var(--u-bg-normal);
}

.header.dark .theme-option.active {
  background: var(--dm-surface-elevated);
  color: var(--dm-text);
}

.icon-btn {
  border: none;
  background: rgba(255, 255, 255, 0.85);
  border: var(--u-border);
  box-shadow: 2px 2px 0px var(--u-black);
  font-size: clamp(18px, 1.2vw, 20px);
}

.header.dark .icon-btn {
  background: var(--dm-surface);
  color: var(--dm-text);
  border: 2px solid var(--u-stroke);
  box-shadow: 2px 2px 0 var(--u-black);
}

@media (max-width: 900px) {
  .nav {
    display: none;
  }
}
</style>
