// 保留你原有的代码，只新增 Element Plus 相关导入和注册
import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// 新增：导入 Element Plus 核心库和全局样式
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'

const app = createApp(App)

// 原有逻辑：注册路由
app.use(router)

// 新增：全局注册 Element Plus
app.use(ElementPlus)

app.mount('#app')