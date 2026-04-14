# 职业发展报告预览页面连接文档

> 本文档说明 `CareerReportView.vue` 页面与后端 API 的对接方式。
> API 接口详细说明见《前端接入后端接口详细文档.md》。

---

## 一、页面概述

### 1.1 页面结构

`CareerReportView.vue` 是职业规划系统的核心页面，包含两个主要阶段：

| 阶段 | 路由/状态 | 说明 |
|:----:|---------|------|
| **阶段一** | `step === 'match'` | 岗位匹配与职业探索（第一张图） |
| **阶段二** | `step === 'report'` | 职业发展规划报告（第二/三张图） |

### 1.2 URL 参数

页面通过 URL Query 参数接收数据：

| 参数 | 来源 | 说明 |
|------|------|------|
| `profile_cache_id` | 简历解析接口返回 | 学生画像缓存 ID，用于后续 API 调用 |
| `student_name` | 简历解析接口返回 | 学生姓名，用于显示 |

**示例 URL**：
```
/career-report?profile_cache_id=29865f50-387c-4063-9aba-24b91d9c9498&student_name=张三
```

---

## 二、接口调用时序

### 2.1 页面初始化流程

```
onMounted()
    │
    ├── 1. 读取 URL query 参数
    │       ├── profile_cache_id → profileCacheId
    │       └── student_name → studentName
    │
    ├── 2. loadRecommendJobs()  [接口 1]
    │       └── GET /recommend/list
    │           └── recommendedJobs.value = 岗位列表
    │
    └── 3. loadMatchDetail()    [接口 2]
            └── POST /api/v1/match/detail
                └── 填充：currentJob、compareDimensions、gapDetails、improveSuggestions
```

### 2.2 生成报告流程

```
generateReport()
    │
    ├── 1. buildMatchReportPayload()
    │       └── 构建请求体 { job_id, profile_cache_id }
    │
    ├── 2. postMatchReport(payload)  [接口 3]
    │       └── POST /api/v1/match/report
    │
    ├── 3. normalizeMatchReportPayload(raw)
    │       └── 规范化响应数据
    │
    ├── 4. applyNormalizedReport(normalized)
    │       └── 填充报告各模块数据
    │
    ├── 5. step.value = 'report'  [切换到阶段二]
    │
    └── 6. finalizePolishedReport() [接口 4]
            └── POST /api/v1/match/report/finalize
                └── polishedMarkdown.value
```

---

## 三、接口与数据映射

### 3.1 接口 1：获取岗位列表

**API 函数**：`fetchRecommendJobList()`

**后端接口**：`GET /recommend/list`

**前端处理**：

```javascript
// Vue 代码 (line 804-822)
const loadRecommendJobs = async () => {
  const list = await fetchRecommendJobList()
  const mapped = list.map(normalizeJobRow).filter(Boolean)
  recommendedJobs.value = mapped
  selectedJobId.value = String(mapped[0].id)  // 默认选中第一个
}

// normalizeJobRow (line 666-675)
const normalizeJobRow = (row) => {
  const mapped = mapRecommendListItemToJob(row)  // 调用 API 模块函数
  return {
    id: mapped.job_id,
    name: mapped.title,
    match: Math.max(0, Math.min(100, Math.round(Number(mapped.match_score || 0)))),
    requireMatch: 80,  // 固定阈值
  }
}
```

**数据流向**：

| 后端返回 | 映射后字段 | Vue 状态 |
|---------|----------|---------|
| `job_id` | `id` | `recommendedJobs[].id` |
| `title` | `name` | `recommendedJobs[].name` |
| `match_score` | `match` | `recommendedJobs[].match` |
| - | `requireMatch` | 固定值 `80` |

---

### 3.2 接口 2：获取匹配详情

**API 函数**：`postMatchDetail(body)`

**后端接口**：`POST /api/v1/match/detail`

**前端处理**：

```javascript
// Vue 代码 (line 824-840)
const loadMatchDetail = async () => {
  if (!selectedJobId.value) return
  const detail = await postMatchDetail(buildMatchPayload(selectedJobId.value))
  await applyMatchDetail(detail)
}

// buildMatchPayload (line 705-716)
const buildMatchPayload = (jobId) => {
  const payload = { job_id: String(jobId) }
  if (profileCacheId.value) {
    payload.profile_cache_id = profileCacheId.value
  } else if (studentProfile.value) {
    payload.student_profile = studentProfile.value
  }
  return payload
}

// applyMatchDetail (line 718-740)
const applyMatchDetail = async (detail) => {
  lastMatchDetail.value = detail
  currentJob.value = {
    id: String(detail.job_id),
    name: detail.title,
    match: Math.round(detail.match_score),
    requireMatch: 80,
  }
  // 提取四维度分数用于雷达图
  const dimScores = extractFourDimensionScoresFromMatchPayload(detail)
  // 格式化用于表格对比
  const studentByKey = formatFourDimensionScoresForCompareRows(dimScores)
  // 解析岗位要求文本
  const texts = await resolveMatchDimensionRequirementTexts(...)
  // 构建对比行数据
  compareDimensions.value = buildCompareDimensionRows(texts, studentByKey)
  // 解析差距分析和建议
  gapDetails.value = mergeGapDetailStrings(detail, narrative, dimScores)
  improveSuggestions.value = mergeSuggestDetailStrings(detail, narrative, dimScores)
}
```

**数据流向**：

| 后端返回 | 前端使用 | Vue 状态 |
|---------|---------|---------|
| `job_id` | 当前岗位 ID | `currentJob.id` |
| `title` | 岗位名称 | `currentJob.name` |
| `match_score` | 匹配度 | `currentJob.match` |
| `dimensions[]` | 雷达图数据 | `matchRadarParsed` (computed) |
| `gap_analysis` / `narrative` | 差距分析文本 | `gapDetails[]` |
| `improvement_suggestions` | 提升建议文本 | `improveSuggestions[]` |

---

### 3.3 接口 3：生成职业报告

**API 函数**：`postMatchReport(body)`

**后端接口**：`POST /api/v1/match/report`

**前端处理**：

```javascript
// Vue 代码 (line 548-581)
const generateReport = async () => {
  const payload = buildMatchReportPayload({
    job_id: selectedJobId.value,
    profile_cache_id: profileCacheId.value || '',
    student_profile: studentProfile.value || null,
    precomputed_module_1: null,
  })
  const raw = await postMatchReport(payload)
  reportPreviewRaw.value = raw
  saveLastMatchResult(raw)
  const normalized = normalizeMatchReportPayload(raw)
  await applyNormalizedReport(normalized)
  step.value = 'report'  // 切换到报告页面
  await finalizePolishedReport()
}
```

**applyNormalizedReport 数据填充** (line 742-802)：

| 报告模块 | 后端字段 | Vue 状态 |
|---------|---------|---------|
| 基本信息 | `career_report.module_1.target_job` | `baseInfo.targetJob` |
| 画像摘要 | `career_report.gap_analysis` | `baseInfo.summary` |
| 优势 | `career_report.strengths` | `baseInfo.strengths[]` |
| 短板 | `career_report.weaknesses` | `baseInfo.weaknesses[]` |
| 职业路径图 | `career_report.module_3.selected_plan.path_image` | `careerPathImage` |
| 路径节点 | `career_report.module_2.career_paths.recommended_path.nodes` | `careerPathNodes[]` |
| 短期计划 | `career_report.short_term_plan` | `shortTermPlan[]` |
| 中期计划 | `career_report.mid_term_plan` | `midTermPlan[]` |
| 评估标准 | `career_report.evaluation_summary` | `evaluationSummary` |
| 任务清单 | `career_report.module_4.todo_items` | `todoList[]` |

---

### 3.4 接口 4：智能润色报告

**API 函数**：`postCareerReportPolishFromPreview(params)`

**后端接口**：
1. `POST /api/v1/match/report-preview` (module_1~3)
2. `POST /api/v1/match/report/finalize` (module_4)

**前端处理**：

```javascript
// Vue 代码 (line 917-933)
const finalizePolishedReport = async () => {
  const payload = buildMatchPayload(selectedJobId.value)
  const finalized = await postCareerReportPolishFromPreview({
    job_id: selectedJobId.value,
    profile_cache_id: profileId,
    preview_data: reportPreviewRaw.value,
  })
  polishedMarkdown.value = finalized.polished_markdown
}
```

**数据流向**：

| 后端返回 | Vue 状态 |
|---------|---------|
| `module_4.polishe_markdown` | `polishedMarkdown` |

---

## 四、页面状态与响应式数据

### 4.1 核心状态变量

| 变量名 | 类型 | 说明 |
|-------|------|------|
| `step` | `ref` | 当前阶段：`'match'` 或 `'report'` |
| `profileCacheId` | `ref` | 画像缓存 ID |
| `studentName` | `ref` | 学生姓名 |
| `recommendedJobs` | `ref[]` | 岗位列表 |
| `selectedJobId` | `ref` | 当前选中岗位 ID |
| `currentJob` | `ref` | 当前查看岗位详情 |
| `compareDimensions` | `ref[]` | 四维度对比数据 |
| `gapDetails` | `ref[]` | 差距分析列表 |
| `improveSuggestions` | `ref[]` | 提升建议列表 |
| `baseInfo` | `ref` | 报告基本信息 |
| `shortTermPlan` | `ref[]` | 短期成长计划 |
| `midTermPlan` | `ref[]` | 中期成长计划 |
| `todoList` | `ref[]` | 行动建议任务清单 |
| `polishedMarkdown` | `ref` | AI 润色后的报告 |
| `isEditing` | `ref` | 是否处于编辑模式 |
| `globalAiLoading` | `ref` | 全局加载状态 |

### 4.2 阶段一数据结构

```javascript
// 岗位列表项
{
  id: 'JOB_001',
  name: 'Java 开发工程师',
  match: 85,
  requireMatch: 80
}

// 四维度对比项
{
  name: '基础要求',      // 维度名称
  student: '85',        // 学生得分
  requirementText: '持有英语四级证书...'  // 岗位要求文本
}

// 当前岗位
{
  id: 'JOB_001',
  name: 'Java 开发工程师',
  match: 85,
  requireMatch: 80
}
```

### 4.3 阶段二数据结构

```javascript
// 报告基本信息
baseInfo: {
  major: '计算机科学与技术',
  targetJob: 'Java 开发工程师',
  summary: '综合能力指数处于...',
  strengths: ['技术基础扎实', '自学能力强'],
  weaknesses: ['项目经验偏少', '沟通经验不多']
}

// 成长计划项
{
  phase: '第一阶段',
  time: '第 1-2 个月',
  direction: '职业技能（MySQL 优化）',
  path: '完成 MySQL 实战课程...',
  practice: '完成 2 个实战案例...',
  metric: '完成不少于 2 万行 SQL 练习...'
}

// 任务清单项
{
  id: 'item_uuid',
  title: '学习 Python 异步编程',
  description: '掌握 asyncio、aiohttp...',
  target_dimension: 'professional_skills',
  target_dimension_label: '专业技能',
  skill_keywords: ['Python', 'asyncio'],
  difficulty: 'standard',
  estimated_hours: 10,
  status: 'pending'
}
```

---

## 五、用户交互与 API 调用

### 5.1 点击「查看详情」按钮

```javascript
// Vue 代码 (line 542-545)
const viewJobDetail = (row) => {
  selectedJobId.value = String(row.id)
  loadMatchDetail()  // 重新调用接口 2
}
```

**流程**：
1. 更新 `selectedJobId`
2. 调用 `loadMatchDetail()`
3. 更新 `currentJob`、`compareDimensions`、`gapDetails`、`improveSuggestions`
4. 重新渲染雷达图

### 5.2 点击「生成职业规划报告」按钮

```javascript
// Vue 代码 (line 548-581)
const generateReport = async () => {
  // 1. 构建请求体
  const payload = buildMatchReportPayload({...})
  
  // 2. 调用接口 3
  const raw = await postMatchReport(payload)
  
  // 3. 保存预览数据
  reportPreviewRaw.value = raw
  
  // 4. 填充报告数据
  await applyNormalizedReport(normalized)
  
  // 5. 切换到报告页面
  step.value = 'report'
  
  // 6. 调用接口 4 生成润色报告
  await finalizePolishedReport()
}
```

### 5.3 点击「智能润色」按钮

```javascript
// Vue 代码 (line 935-950)
const handlePolish = async () => {
  if (!reportPreviewRaw.value) {
    ElMessage.warning('请先生成基础报告，再进行智能润色。')
    return
  }
  globalAiLoading.value = true
  try {
    await finalizePolishedReport()
  } finally {
    globalAiLoading.value = false
  }
}
```

### 5.4 导出报告

```javascript
// Vue 代码 (line 952-971)
const exportReport = (format) => {
  if (format === 'markdown') {
    // 生成 Markdown 内容并下载
    const content = buildMarkdown(payload)
    downloadBlob(content, 'career-report.md')
  } else if (format === 'pdf') {
    // 打开打印窗口（浏览器打印为 PDF）
    openPrintWindow(payload)
  } else if (format === 'word') {
    // 生成 HTML 并以 .doc 下载
    downloadWordDoc(payload, 'career-report.doc')
  }
}
```

---

## 六、辅助工具函数

### 6.1 雷达图数据解析

```javascript
// extractFourDimensionScoresFromMatchPayload
// 位置: careerAgentApi.js -> extractFourDimensionScoresFromMatchPayload

// 输入: 后端 match/detail 响应
// 输出: 四维度分数对象
{
  base: { student: 80, job: 70 },
  skill: { student: 75, job: 85 },
  soft: { student: 70, job: 75 },
  potential: { student: 65, job: 80 }
}
```

### 6.2 数据规范化

```javascript
// normalizeMatchReportPayload
// 位置: careerAgentApi.js

// 输入: 后端 /match/report 响应
// 输出: 规范化结构
{
  summary: {...},
  job_info: {...},
  match_summary: {...},
  career_report: {
    module_1: {...},
    module_2: {...},
    module_3: {...},
    module_4: {...}
  },
  action_plan: {...}
}
```

### 6.3 任务清单映射

```javascript
// mapActionPlanItemFromApi
// 位置: careerAgentApi.js

// 输入: 后端返回的行动项
// 输出: 前端任务卡片格式
{
  id: 'item_uuid',
  title: '任务标题',
  description: '任务描述',
  target_dimension: 'professional_skills',
  target_dimension_label: '专业技能',
  skill_keywords: ['Python'],
  difficulty: 'standard',
  estimated_hours: 10,
  status: 'pending',
  is_rolled_over: false,
  completed_at: null
}
```

### 6.4 雷达图四维数据解析

```javascript
// parseMatchRadarFourDimensionValues
// 位置: careerAgentApi.js

// 输入: postMatchDetail 响应
// 输出: { student: number[], job: number[] }
// student/job 数组顺序: [基础要求, 职业技能, 职业素养, 发展潜力]

// 示例:
{
  student: [82, 75, 70, 65],  // 学生四维得分
  job: [70, 85, 75, 80]      // 岗位四维要求
}

// 兼容多种后端返回格式:
// 1. 顶层 dimensions[]（student_score / job_required_score）
// 2. details.dimensions 对象
// 3. module_1 four_dimensions (student_score_100 / job_required_score_100)
```

### 6.5 四维分数格式化

```javascript
// formatFourDimensionScoresForCompareRows
// 位置: careerAgentApi.js

// 输入: extractFourDimensionScoresFromMatchPayload 返回值
// 输出: { base: number, skill: number, soft: number, potential: number }

// 兼容别名字段:
// - base: 基础要求 / basic / 基础
// - skill: 职业技能 / professional / 专业
// - soft: 职业素养 / quality / 软技能
// - potential: 发展潜力 / growth / 潜力
```

### 6.6 差距分析文本合并

```javascript
// mergeGapDetailStrings
// 位置: utils/matchAnalysisTextMerge.js

// 输入:
// - detail: postMatchDetail 响应
// - narrative: detail.narrative 字段
// - dimScores: extractFourDimensionScoresFromMatchPayload 返回值
// 输出: string[] 差距分析列表
```

### 6.7 提升建议文本合并

```javascript
// mergeSuggestDetailStrings
// 位置: utils/matchAnalysisTextMerge.js

// 输入: 同 mergeGapDetailStrings
// 输出: string[] 提升建议列表
```

### 6.8 维度要求文本解析

```javascript
// resolveMatchDimensionRequirementTexts
// 位置: utils/matchDimensionRequirements.js

// 输入:
// - detail: postMatchDetail 响应
// - jobId: 岗位 ID
// - jobTitle: 岗位名称
// - module1TargetJob: module_1.target_job 对象
// 输出: { base: string, skill: string, soft: string, potential: string }
//        各维度岗位要求描述文本
```

### 6.9 对比行数据构建

```javascript
// buildCompareDimensionRows
// 位置: utils/matchDimensionRequirements.js

// 输入:
// - texts: resolveMatchDimensionRequirementTexts 返回值
// - studentScores: formatFourDimensionScoresForCompareRows 返回值
// 输出: Array<{ name: string, student: string, requirementText: string }>

// 示例:
[
  { name: '基础要求', student: '82', requirementText: '持有英语四级证书...' },
  { name: '职业技能', student: '75', requirementText: '掌握 Python/FastAPI...' },
  { name: '职业素养', student: '70', requirementText: '良好的沟通协作能力...' },
  { name: '发展潜力', student: '65', requirementText: '持续学习新技术...' }
]
```

---

## 七、错误处理

### 7.1 岗位列表加载失败

```javascript
// Vue 代码 (line 813-821)
try {
  const list = await fetchRecommendJobList()
  // ...
} catch (e) {
  ElMessage.warning(`获取岗位列表失败：${e?.message || '使用示意数据'}`)
  // 使用硬编码的示意数据
  recommendedJobs.value = [
    { id: 'JOB_001', name: 'Java 开发工程师', match: 85, requireMatch: 85 },
    { id: 'JOB_002', name: '前端开发工程师', match: 78, requireMatch: 82 },
    { id: 'JOB_003', name: '软件测试工程师', match: 72, requireMatch: 80 },
  ]
}
```

### 7.2 匹配详情加载失败

```javascript
// Vue 代码 (line 832-839)
try {
  const detail = await postMatchDetail(buildMatchPayload(...))
  await applyMatchDetail(detail)
} catch (e) {
  // 使用岗位列表中的匹配度作为 fallback
  const fallback = recommendedJobs.value.find(...)
  if (fallback) currentJob.value = { ...fallback }
  gapDetails.value = ['接口详情获取失败，当前展示基础信息。']
  improveSuggestions.value = ['请稍后重试，或先直接生成职业规划报告。']
  ElMessage.warning(`加载详情失败：${e?.message || '请稍后重试'}`)
}
```

### 7.3 生成报告失败

```javascript
// Vue 代码 (line 576-578)
try {
  // ...
} catch (e) {
  ElMessage.error(`生成报告失败：${e?.message || '请稍后重试'}`)
} finally {
  globalAiLoading.value = false
}
```

---

## 八、依赖关系

### 8.1 API 模块依赖

| API 函数 | 来源文件 | 说明 |
|---------|---------|------|
| `fetchRecommendJobList` | `careerAgentApi.js` | 获取岗位列表 |
| `postMatchDetail` | `careerAgentApi.js` | 获取匹配详情 |
| `postMatchReport` | `careerAgentApi.js` | 生成职业报告 |
| `postCareerReportPolishFromPreview` | `careerAgentApi.js` | 智能润色 |
| `buildMatchReportPayload` | `careerAgentApi.js` | 构建报告请求体 |
| `normalizeMatchReportPayload` | `careerAgentApi.js` | 规范化报告数据 |
| `extractFourDimensionScoresFromMatchPayload` | `careerAgentApi.js` | 提取雷达图数据 |
| `mapRecommendListItemToJob` | `careerAgentApi.js` | 映射岗位列表项 |
| `mapPlanRow` | `careerAgentApi.js` | 映射计划项 |
| `mapActionPlanItemFromApi` | `careerAgentApi.js` | 映射任务项 |
| `readProfileCacheId` | `careerAgentApi.js` | 读取缓存 ID |
| `saveProfileCacheId` | `careerAgentApi.js` | 保存缓存 ID |
| `saveLastMatchResult` | `careerAgentApi.js` | 保存匹配结果 |

### 8.2 工具模块依赖

| 工具函数 | 来源文件 | 说明 |
|---------|---------|------|
| `buildCompareDimensionRows` | `utils/matchDimensionRequirements.js` | 构建对比行 |
| `resolveMatchDimensionRequirementTexts` | `utils/matchDimensionRequirements.js` | 解析要求文本 |
| `mergeGapDetailStrings` | `utils/matchAnalysisTextMerge.js` | 合并差距分析 |
| `mergeSuggestDetailStrings` | `utils/matchAnalysisTextMerge.js` | 合并建议文本 |
| `buildPortraitStyleRadarOption` | `utils/portraitRadarEchartsOption.js` | 构建雷达图配置 |
| `useTheme` | `composables/useTheme.js` | 主题管理 |

---

## 九、完整调用示例

### 9.1 页面初始化完整流程

```javascript
// 1. 从 URL 获取参数
const profileCacheId = route.query.profile_cache_id
const studentName = route.query.student_name

// 2. 保存到缓存
if (profileCacheId) {
  saveProfileCacheId(profileCacheId)
}

// 3. 加载岗位列表
const jobs = await fetchRecommendJobList()
const normalizedJobs = jobs.map(normalizeJobRow)

// 4. 选中第一个岗位
const firstJobId = normalizedJobs[0].id

// 5. 加载匹配详情
const detail = await postMatchDetail({
  job_id: firstJobId,
  profile_cache_id: profileCacheId
})

// 6. 展示数据
renderJobDetail(detail)
renderRadarChart(detail)
```

### 9.2 生成报告完整流程

```javascript
// 1. 构建请求体
const payload = buildMatchReportPayload({
  job_id: selectedJobId,
  profile_cache_id: profileCacheId,
  student_profile: null,
  precomputed_module_1: null,
})

// 2. 调用报告接口
const rawReport = await postMatchReport(payload)

// 3. 规范化数据
const normalized = normalizeMatchReportPayload(rawReport)

// 4. 填充报告数据
applyNormalizedReport(normalized)

// 5. 切换到报告页面
step.value = 'report'

// 6. 生成润色报告
const polishResult = await postCareerReportPolishFromPreview({
  job_id: selectedJobId,
  profile_cache_id: profileCacheId,
  preview_data: rawReport,
})

// 7. 显示润色结果
polishedMarkdown.value = polishResult.polished_markdown
```

---

## 十、注意事项

### 10.1 缓存 ID 传递

- 页面通过 URL 参数接收 `profile_cache_id`
- 同时会保存到 `localStorage` 和 `sessionStorage`
- 后续接口调用优先使用 URL 参数中的 ID

### 10.2 回退机制

- 岗位列表加载失败时，使用硬编码的示意数据
- 匹配详情加载失败时，使用岗位列表中的匹配度
- 雷达图数据缺失时，显示示意值

### 10.3 加载状态

- 全局加载状态 `globalAiLoading` 用于显示遮罩
- 加载文本 `globalAiLoadingText` 显示当前操作提示
- 生成报告和润色时显示不同的加载提示

### 10.4 报告编辑

- 支持原地编辑报告内容
- 编辑模式下显示输入框，非编辑模式显示文本
- 编辑内容保存在 `draft` 状态中

---

## 十一、前端需要修改的内容

> 以下问题可能导致智能润色功能无法正常工作，请前端开发人员注意。

### 11.1 修复不存在的 API 调用

**问题**：`postCareerReportPolishFromPreview` 函数调用了不存在的接口。

**当前代码** (`careerAgentApi.js` line 355-379)：

```javascript
export async function postCareerReportPolishFromPreview(params) {
  // ...
  const previewData = await postMatchReportPreview(previewBody)  // ❌ /api/v1/match/report-preview 不存在！
  // ...
  const finalized = await postMatchReportFinalize(finalizeBody)
  // ...
}
```

**问题分析**：
- 后端不存在 `/api/v1/match/report-preview` 接口
- 后端实际存在的接口只有：
  - `POST /api/v1/match/report` - 返回 module_1~3
  - `POST /api/v1/match/report/finalize` - 仅返回 module_4

**建议修改方案**：

由于 `/match/report` 接口已经返回了 module_1~3（包含在 `career_report` 中），`finalize` 接口只需要 `preview_data`（即 `/match/report` 的完整返回）即可生成 module_4。

**方案**：直接使用已有的 `/match/report` 接口（推荐）

```javascript
export async function postCareerReportPolishFromPreview(params) {
  const job_id = String(params?.job_id ?? '').trim()
  if (!job_id) throw new Error('缺少 job_id')

  const cacheId = params.profile_cache_id != null ? String(params.profile_cache_id).trim() : ''
  const studentProfile = params.student_profile

  // 直接调用 /match/report 获取完整报告
  const reportBody = { job_id }
  if (cacheId) reportBody.profile_cache_id = cacheId
  else if (studentProfile) reportBody.student_profile = studentProfile
  else throw new Error('缺少 profile_cache_id 或 student_profile')

  // 调用 /match/report（已包含 module_1~3）
  const fullReport = await postMatchReport(reportBody)

  // 提取 module_4（如果已生成）或调用 /finalize 获取
  let module4 = fullReport?.career_report?.module_4

  // 如果 module_4 为空，调用 /finalize 单独获取
  if (!module4 && params.preview_data) {
    const finalizeBody = {
      job_id,
      preview_data: fullReport,
    }
    if (cacheId) finalizeBody.profile_cache_id = cacheId
    else if (studentProfile) finalizeBody.student_profile = studentProfile

    const finalized = await postMatchReportFinalize(finalizeBody)
    module4 = finalized?.module_4 ?? null
  }

  const polished_markdown =
    module4?.polished_markdown ?? module4?.polishedMarkdown ?? ''

  return {
    module_4: module4,
    polished_markdown,
    // 同时返回完整报告供前端使用
    full_report: fullReport,
  }
}
```
---

### 11.2 统一后端 API 基础地址

**问题**：`careerAgentApi.js` 中的默认地址与接口文档不一致。

| 来源 | 默认地址 |
|------|---------|
| `careerAgentApi.js` 第 7 行 | `http://192.168.31.93:8002` |
| 接口文档 | `http://192.168.31.92:8002` |

**建议**：确认正确的后端地址后，统一修改为：

```javascript

// 方案：直接修改为正确的地址
const DEFAULT_BASE = 'http://192.168.31.93:8002'  // 确认后端实际运行地址
```

---

### 11.3 确认 career_report 字段路径

**问题**：前端 `applyNormalizedReport` 期望从 `career_report` 直接读取某些字段，但后端实际返回的字段结构在各个 module 子对象内部，且字段名可能不同。

#### 后端 `/match/report` 实际返回结构

```javascript
{
  "summary": {
    "student_name": "张三",
    "target_job": { "job_id": "JOB_001", "title": "Java 开发工程师" },
    "match_score": 75.5,
    "overall_fit_percent": 68.0,
    "top_strengths": ["专业技能"],      // ⚠️ 字符串数组
    "key_gaps": ["项目经验"]           // ⚠️ 字符串数组
  },
  "job_info": { ... },
  "match_summary": {
    "dimensions": { "base": 80, "skill": 75, "soft": 70, "potential": 65 }
  },
  "career_report": {
    "module_1": {                       // ← module_1 内部
      "student_info": { ... },
      "target_job": { ... },
      "fit_analysis": { ... },
      "strengths": [                    // ✅ 存在，但格式是对象数组
        { "dimension_key": "skill", "dimension_label": "专业技能", ... }
      ],
      "gaps": [                        // ⚠️ 是 "gaps" 不是 "weaknesses"
        { "dimension_key": "base", "dimension_label": "基础要求", ... }
      ],
      "personal_strengths_and_gaps": [  // ⚠️ LLM 生成的列表
        { "type": "strength", "content": "Java、MySQL 等技术基础扎实" },
        { "type": "gap", "content": "真实业务项目经验偏少" }
      ],
      "gap_analysis": "...",           // ✅ 存在
      "improvement_suggestions": "..." // ✅ 存在
    },
    "module_2": {                       // ← module_2 内部
      "goal": { ... },
      "market_trend": { ... },
      "career_paths": {
        "recommended_path": {
          "id": "...",
          "type": "vertical",
          "title": "...",
          "nodes": ["初级开发", "中级开发", "高级开发"],  // ✅ 路径节点
          "rationale": "...",
          "trade_off": "..."
        }
      }
    },
    "module_3": {                       // ← module_3 内部
      "selected_plan": {
        "gap_analysis": { ... },
        "timeline": { ... },
        "short_term": {
          "duration_months": 6,
          "dimension": "职业技能",
          "goals": ["攻克「职业技能」维度", "形成至少一个可展示的项目/成果"],
          "skills": [                   // ⚠️ 是 "skills" 不是 "short_term_plan"
            { "skill": "MySQL", "tier": "standard", "duration_weeks": 4, ... }
          ]
        },
        "mid_term": {
          "duration_months": 12,
          "dimension": "职业素养",
          "goals": ["深化「职业素养」维度", "形成稳定的投递-面试-复盘闭环"],
          "skills": [                   // ⚠️ 是 "skills" 不是 "mid_term_plan"
            { "skill": "沟通技巧", "tier": "standard", "duration_weeks": 6, ... }
          ]
        },
        "evaluation": {
          "metrics": [...],
          "review_questions": ["本周期最大的阻碍是什么？", ...]
        },
        "plan_table": {                // ⚠️ 表格数据在这里
          "headers": [...],
          "rows": [
            { "phase": "第一阶段", "time": "第 1-2 个月", "direction": "...", "path": "...", "practice": "...", "metric": "..." }
          ]
        }
      },
      "plan_config": { ... }
    },
    "module_4": null                    // 需单独调用 /finalize 获取
  },
  "action_plan": { ... }
}
```

#### 前端期望 vs 后端实际字段映射表

| 前端期望字段 | 后端实际路径 | 状态 | 说明 |
|------------|------------|:---:|------|
| `career_report.gap_analysis` | `career_report.module_1.gap_analysis` | ✅ | 存在，但需要正确路径 |
| `career_report.strengths` | `career_report.module_1.personal_strengths_and_gaps` (type="strength") | ⚠️ | 需过滤 type="strength" |
| `career_report.weaknesses` | `career_report.module_1.personal_strengths_and_gaps` (type="gap") | ⚠️ | 需过滤 type="gap" |
| `career_report.short_term_plan` | `career_report.module_3.selected_plan.plan_table.rows` | ⚠️ | 结构不同，需按时间过滤 |
| `career_report.mid_term_plan` | `career_report.module_3.selected_plan.plan_table.rows` | ⚠️ | 需按 phase/时间分段 |
| `career_report.evaluation_summary` | `career_report.module_3.selected_plan.evaluation.review_questions` | ⚠️ | 需自行组装文本 |
| `career_report.module_3.plan_items` | `module_3.selected_plan.short_term.skills` + `mid_term.skills` | ⚠️ | 字段名不同 |
| `career_report.learning_path` | `career_report.module_2.career_paths.recommended_path.nodes` | ⚠️ | 路径是数组，需转为字符串 |

#### 具体的修改建议

**1. 提取 strengths/weaknesses（当前端代码约 line 780-783）**

```javascript
// 当前代码（可能取不到值）
const strengths = toTextList(report.strengths)
const weaknesses = toTextList(report.weaknesses)

// 建议修改为
const module1 = report.module_1 || report.module1 || {}
const personalItems = module1.personal_strengths_and_gaps || []
const strengths = personalItems
  .filter(item => item.type === 'strength')
  .map(item => item.content)
const weaknesses = personalItems
  .filter(item => item.type === 'gap')
  .map(item => item.content)
```

**2. 提取 short_term_plan / mid_term_plan（当前端代码约 line 786-796）**

```javascript
// 当前代码
let mappedShort = safeArr(report.short_term_plan).map(mapPlanRow).filter(Boolean)
let mappedMid = safeArr(report.mid_term_plan).map(mapPlanRow).filter(Boolean)
const fromModule3Items = safeArr(report.module_3?.plan_items ?? report.module_3?.planItems)

// 建议修改为
const module3 = report.module_3 || report.module3 || {}
const planTable = module3.selected_plan?.plan_table
const tableRows = safeArr(planTable?.rows || [])

// 从 plan_table.rows 提取（按时间节点判断短期/中期）
const shortMonths = module3.selected_plan?.short_term?.duration_months || 6
const midMonths = module3.selected_plan?.mid_term?.duration_months || 12

const mappedShort = tableRows
  .filter(row => {
    const time = row.time || ''
    return time.includes('1') || time.includes('2') || time.includes('3') ||
           time.includes('4') || time.includes('5') || time.includes('6')
  })
  .map(mapPlanRow)
  .filter(Boolean)

const mappedMid = tableRows
  .filter(row => {
    const time = row.time || ''
    return time.includes('7') || time.includes('8') || time.includes('9') ||
           time.includes('10') || time.includes('11') || time.includes('12') ||
           time.includes('18')
  })
  .map(mapPlanRow)
  .filter(Boolean)

// 如果 plan_table.rows 为空，回退到 skills 数组
if (!mappedShort.length) {
  const shortSkills = safeArr(module3.selected_plan?.short_term?.skills || [])
  mappedShort = shortSkills.slice(0, 3).map(mapSkillToPlanRow)
}
if (!mappedMid.length) {
  const midSkills = safeArr(module3.selected_plan?.mid_term?.skills || [])
  mappedMid = midSkills.slice(0, 3).map(mapSkillToPlanRow)
}
```

**3. 提取 evaluation_summary（当前端代码约 line 784）**

```javascript
// 当前代码
if (report.evaluation_summary) evaluationSummary.value = String(report.evaluation_summary)

// 建议修改为
const module3 = report.module_3 || {}
const evaluation = module3.selected_plan?.evaluation || {}
const reviewQuestions = safeArr(evaluation.review_questions || [])
if (reviewQuestions.length) {
  evaluationSummary.value = `达成标准：${reviewQuestions.join('；')}`
}
```

**4. 提取 learning_path / pathNote（当前端代码约 line 775-778）**

```javascript
// 当前代码
if (report.learning_path) pathNote.value = String(report.learning_path)

// 建议修改为
const module2 = report.module_2 || {}
const recommendedPath = module2.career_paths?.recommended_path || {}
const nodes = recommendedPath.nodes || []
if (nodes.length) {
  pathNote.value = `推荐路径：${nodes.join(' -> ')}`
}
```

---

### 11.4 移除未使用的 API 函数

以下函数需要移除或禁用：

| 函数 | 调用的接口 | 状态 | 原因 |
|------|-----------|:----:|------|
| `postMatchReportPreview` | `/api/v1/match/report-preview` | ❌ 后端不存在 | 后端没有这个接口，调用会返回 404 |
| `postCareerReportPolishFromPreview` | 内部调用 `postMatchReportPreview` | ❌ 无法工作 | 调用链中包含不存在的接口 |
| `postSmartPolish` | `/api/v1/match/polish` | ❌ 后端不存在 | 死代码，前端从未调用 |
| `postReportPolish` | `/api/v1/report/polish` | ❌ 后端不存在 | 死代码，前端从未调用 |

**问题根源**：前端 `finalizePolishedReport` 调用了 `postCareerReportPolishFromPreview`，而该函数内部又调用了不存在的 `postMatchReportPreview`，导致"智能润色"功能失效。

**正确的润色流程**（见问题五的修复方案）：
1. `generateReport()` 调用 `/match/report` 获取 module_1~3
2. `finalizePolishedReport()` 直接调用 `/match/report/finalize` 获取 module_4

---

### 11.5 finalizePolishedReport 调用逻辑调整

**当前代码** (`CareerReportView.vue` line 574, 943)：

```javascript
// 在 generateReport 中调用
await finalizePolishedReport()

// 在 handlePolish 中调用
await finalizePolishedReport()
```

**问题**：`finalizePolishedReport` 内部调用了 `postCareerReportPolishFromPreview`，而该函数调用的接口不存在。

**建议修改**：

```javascript
const finalizePolishedReport = async () => {
  if (!selectedJobId.value) return

  // 如果 reportPreviewRaw.value 已包含 module_4，直接使用
  if (reportPreviewRaw.value?.career_report?.module_4) {
    polishedMarkdown.value = reportPreviewRaw.value.career_report.module_4.polishe_markdown || ''
    return
  }

  // 否则调用 /finalize 获取 module_4
  const profileId = String(profileCacheId.value || readProfileCacheId() || '').trim()
  const payload = buildMatchPayload(selectedJobId.value)

  try {
    // 直接调用 /finalize（只需 preview_data 和 job_id）
    const finalizeBody = {
      job_id: selectedJobId.value,
      preview_data: reportPreviewRaw.value,  // /report 返回的完整数据
    }
    if (profileId) finalizeBody.profile_cache_id = profileId
    else finalizeBody.student_profile = payload.student_profile

    const finalized = await postMatchReportFinalize(finalizeBody)
    polishedMarkdown.value = String(
      finalized?.module_4?.polished_markdown ||
      finalized?.module_4?.polishedMarkdown ||
      ''
    ).trim()
  } catch (e) {
    polishedMarkdown.value = ''
    throw e
  }
}
```

---

### 11.6 确认 job_id 参数类型

**问题**：部分接口期望 `job_id`，部分期望 `target_job_id`。

| 接口 | 字段 |
|------|------|
| `/match/detail` | `job_id` ✅ |
| `/match/report` | `job_id` ✅ |
| `/match/report/finalize` | `job_id` ✅ |
| `postSmartPolish` | `target_job_id` (旧接口) |

确保前端所有接口调用使用一致的字段名 `job_id`。

---

### 11.7 补充缺失的 API 包装

如果需要支持一次性生成完整报告（含 module_4），建议添加：

```javascript
/**
 * 一次性生成完整职业规划报告（module_1~4）
 * 内部调用两次后端接口：/match/report + /match/report/finalize
 */
export async function generateFullReport(body) {
  // 1. 调用 /match/report 获取 module_1~3
  const reportData = await postMatchReport(body)

  // 2. 调用 /match/report/finalize 获取 module_4
  const finalizeBody = {
    job_id: body.job_id,
    preview_data: reportData,
  }
  if (body.profile_cache_id) finalizeBody.profile_cache_id = body.profile_cache_id
  else if (body.student_profile) finalizeBody.student_profile = body.student_profile

  const finalized = await postMatchReportFinalize(finalizeBody)

  // 3. 合并结果
  if (reportData.career_report) {
    reportData.career_report.module_4 = finalized?.module_4 ?? null
  }

  return reportData
}
```

---

*文档版本：v1.1 | 创建日期：2026-04-13 | 更新：2026-04-13*

> **更新说明（v1.1）**：
> - 新增「十一、前端需要修改的内容」章节
> - 指出 `postCareerReportPolishFromPreview` 调用了不存在的接口
> - 指出后端 URL 不一致问题
> - 提供具体的修改建议和代码示例
