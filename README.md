# 职途智引前端（career-planner-frontend）

基于 **Vue 3 + Vite + Element Plus** 的 **AI 职业规划与就业指导** 单页应用。  
在浏览器中串联「岗位画像 → 学生能力画像 → 人岗匹配 → 职业发展报告 → 能力培训计划」的完整体验，便于演示、课程教学或与后端联调。

---

## 项目用途

| 维度 | 说明 |
|------|------|
| **解决什么问题** | 帮助学生从「了解岗位」到「看清差距」再到「制定培训与行动」，把职业规划流程产品化、可交互。 |
| **谁适合用** | 高校就业指导/生涯课演示、学生求职自测、前端与算法/后端联调流程、产品原型展示。 |
| **与后端关系** | 部分能力为 **示意 + 本地兜底数据**；配置 `VITE_API_BASE_URL` 后可请求真实岗位相关接口，其余模块可按需替换为真实 AI 与存储。 |

---

## 使用说明

### 环境要求

- **Node.js**：`^20.19.0` 或 `>=22.12.0`
- 包管理：推荐使用 **npm**（与 `package.json` 脚本一致）

### 安装与运行

```bash
# 安装依赖
npm install

# 本地开发（默认 http://localhost:5173，以终端输出为准）
npm run dev

# 生产构建
npm run build

# 预览构建产物
npm run preview
```

### 代码质量

```bash
npm run lint    # ESLint + oxlint
npm run format  # oxfmt 格式化 src/
```

### 主题与个性化

- 页面 **右上角**（或各页顶栏）可切换 **浅色 / 深色** 主题。
- 选择会写入浏览器 **localStorage**（键名：`career-planner-theme`），下次打开站点会保持。

### 后端地址（可选）

接口封装见：`src/api/jobPortraitApi.js`。默认示例地址见该文件；覆盖方式：

1. 项目根目录新建 `.env.local`
2. 写入：`VITE_API_BASE_URL=http://你的后端地址:端口`

当前与岗位画像相关的接口示例（以实际后端为准）：

- `GET /recommend?title=岗位名称`
- `GET /path?title=岗位名称`
- `GET /transfer?title=岗位名称`

---

## 页面与路由（实际入口以 `src/router.js` 为准）

| 路径 | 名称 | 说明 |
|------|------|------|
| `/` | 首页 | 总览、轮播、核心入口、简历上传入口等 |
| `/jobs` | 就业岗位画像 | 岗位列表卡片，点击进入详情 |
| `/jobs/:id` | 岗位详情 | 技能维度、发展路径、换岗路径、评论区等 |
| `/student-abilities` | 学生就业能力画像 | 简历上传 / 对话录入、画像与推荐岗位 |
| `/career-report` | 岗位匹配与职业探索 / 职业发展报告 | 匹配分析、报告阅读与编辑、导出等 |
| `/career-report-template` | 报告模板 | 模板化编辑与导出 |
| `/profile` | 个人中心 | 资料与报告列表等 |
| `/report/:id` | 报告详情 | 单份报告查看 |
| `/ability-training-plan` | 能力培训计划（说明与示例） | 甘特图 / To Do 示例说明 |
| `/ability-training-plan/generated` | 培训计划生成结果 | 12 周视图与 To Do，支持本地持久化 |

> 说明：仓库中若还存在 `src/router/index.js`，仅为历史/备用片段；**当前应用挂载的路由以 `src/router.js` 为准**（与 `main.js` 中 `import router from './router'` 的实际解析一致）。

---

## 建议体验顺序

1. 首页 → **就业岗位画像** → 打开某一 **岗位详情**  
2. **学生就业能力画像**：上传简历或对话（示意）  
3. **岗位匹配与职业发展报告**：选岗、看匹配与报告、尝试导出  
4. **能力培训计划** → 进入 **生成结果页** 查看甘特图与 To Do  

---

## 技术栈

- Vue 3、Vue Router、Vite  
- Element Plus、`@element-plus/icons-vue`  
- ECharts（部分图表能力可按需扩展）

开发工具：ESLint、oxlint、oxfmt  

---

## 项目结构（简版）

```text
src/
  api/           # 后端接口封装
  assets/        # 全局样式、静态资源
  components/    # 通用组件（如 AppHeader）
  composables/   # 主题等复用逻辑
  data/          # 本地兜底数据
  views/         # 页面视图
  router.js      # 路由（当前主配置）
```

---

## 注意事项

- 部分 AI 能力为 **前端示意 + mock**，便于先跑通流程；对接真实大模型时需替换简历解析、报告润色等链路。  
- 后端不可用时，多页会使用 **本地兜底数据**，避免白屏。  
- 报告 PDF 常见实现为 **浏览器打印**；Word 导出格式以页面实现为准。  
- 静态资源（如首页插画）放在 `public/`，构建后从站点根路径引用（例如 `/career-roles.png`）。

---

## 可扩展方向（参考）

- 深度使用 ECharts 做雷达图、路径图谱  
- 用户登录与多角色（学生 / 导师 / 管理员）  
- 报告版本管理与云端存储  
- 岗位与运营配置后台  

---

## 许可证与版本

- `package.json` 中 `name` / `version` 可按团队规范自行修改。  
- 本项目为课程/演示用途时请遵守学校与用人单位的数据与隐私要求。
