<template>
  <div class="career-report-view" :class="theme">
    <AppHeader />

    <main class="page-scroll">
      <!-- 阶段一：岗位匹配与职业探索（对应第一张图） -->
      <section v-if="step === 'match'" class="panel">
        <header class="panel-header match-header">
          <h1 class="page-title">岗位匹配与职业探索</h1>
          <p class="student-tag">【当前学生】{{ studentName }}</p>
        </header>

        <!-- 推荐岗位列表 -->
        <section class="recommend-section">
          <h2 class="section-title">推荐岗位（按匹配度排序）</h2>
          <el-table
            :data="recommendedJobs"
            border
            stripe
            class="job-table"
          >
            <el-table-column label="选择" width="80">
              <template #default="{ row }">
                <el-radio
                  v-model="selectedJobId"
                  :label="row.id"
                />
              </template>
            </el-table-column>
            <el-table-column prop="name" label="岗位名称" min-width="160" />
            <el-table-column prop="match" label="匹配度" width="120">
              <template #default="{ row }">
                {{ row.match }}%匹配
              </template>
            </el-table-column>
            <el-table-column label="操作" width="140">
              <template #default="{ row }">
                <el-button
                  class="u-btn u-btn--text"
                  type="primary"
                  text
                  size="small"
                  @click="viewJobDetail(row)"
                >
                  查看详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </section>

        <!-- 选中岗位的对比与分析 -->
        <section
          v-if="currentJob"
          class="current-job-section"
        >
          <h2 class="section-title">
            当前查看岗位：{{ currentJob.name }}
          </h2>

          <div class="match-summary">
            <span>匹配度：{{ currentJob.match }}%</span>
            <el-progress
              :percentage="currentJob.match"
              :stroke-width="10"
              style="flex: 1; margin-inline: 12px"
            />
            <span>要求：{{ currentJob.requireMatch }}%</span>
          </div>

          <p class="match-hint">
            人岗匹配从基础要求、职业技能、职业素养、发展潜力四维度进行多维度能力分析，
            对各维度岗位要求与学生信息对比后打分，再按当前岗位各维度权重加权综合，得出匹配度（关键技能匹配准确率目标 ≥80%）。
          </p>
          <div class="compare-grid">
            <div class="compare-card compare-card--radar">
              <p class="compare-title">雷达图（学生 vs 岗位）</p>
              <div class="compare-radar-chart" role="img" aria-label="学生与岗位四维度雷达对比">
                <div ref="matchCompareRadarRef" class="compare-radar-echart" />
                <p class="compare-radar-note">可与下方四维度表对照查看；学生分取自匹配详情接口，缺失时使用示意值。</p>
              </div>
            </div>
            <div class="compare-card">
              <p class="compare-title">四维度对比（基础要求 / 职业技能 / 职业素养 / 发展潜力）</p>
              <ul class="compare-list">
                <li v-for="item in compareDimensions" :key="item.name" class="compare-list-item">
                  <div class="dim-row-head">
                    <span class="dim-name">{{ item.name }}</span>
                    <span class="dim-student">学生：<strong>{{ item.student }}</strong></span>
                  </div>
                  <div class="dim-requirement">
                    <span class="dim-requirement-label">岗位要求</span>
                    <p class="dim-requirement-text">{{ item.requirementText }}</p>
                  </div>
                </li>
              </ul>
              <p class="weight-hint">
                学生列为维度得分；岗位要求为岗位画像/报告中的具体说明，缺失时为通用描述。
              </p>
            </div>
          </div>

          <div class="detail-analysis">
            <p class="section-subtitle">详细差距分析</p>
            <ul>
              <li v-for="(d, index) in gapDetails" :key="index">
                {{ d }}
              </li>
            </ul>

            <p class="section-subtitle">提升建议（示意）</p>
            <ul>
              <li v-for="(s, index) in improveSuggestions" :key="index">
                {{ s }}
              </li>
            </ul>
          </div>

          <div class="action-row">
            <el-button
              class="u-btn u-btn--primary u-btn--lg"
              type="primary"
              size="large"
              @click="generateReport"
            >
              📝 生成职业规划报告
            </el-button>
          </div>
        </section>
      </section>

      <!-- 阶段二：职业发展规划报告（对应第二、三张图） -->
      <section v-else class="panel report-panel">
        <!-- 报告头部 -->
        <header class="report-header">
          <div>
            <h1 class="page-title">职业发展规划报告</h1>
            <p class="report-subtitle">
              目标岗位：{{ currentJob?.name || '（示例）Java 开发工程师' }}
              · 生成时间：{{ reportDate }}
            </p>
          </div>
          <div class="header-actions">
            <template v-if="!isEditing">
              <el-button class="u-btn u-btn--ghost" @click="handleEditReport">编辑报告</el-button>
              <el-button class="u-btn u-btn--primary" @click="handlePolish">智能润色</el-button>
            </template>
            <template v-else>
              <el-button class="u-btn u-btn--primary" type="primary" @click="saveReportEdits">完成</el-button>
              <el-button class="u-btn u-btn--ghost" @click="cancelReportEdits">取消</el-button>
            </template>
            <el-dropdown @command="exportReport">
              <el-button class="u-btn u-btn--primary" type="primary">
                导出报告
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="markdown">Markdown</el-dropdown-item>
                  <el-dropdown-item command="pdf">PDF（浏览器打印）</el-dropdown-item>
                  <el-dropdown-item command="word">Word（.doc）</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </header>

        <!-- 报告内容分段 -->
        <section class="report-section">
          <h2 class="section-title">1. 基本信息与目标岗位</h2>
          <div class="edit-row">
            <p v-if="!isEditing">学生姓名：{{ studentName }} · 专业：{{ baseInfo.major }}</p>
            <div v-else class="edit-grid">
              <div class="edit-field">
                <span class="edit-label">学生姓名</span>
                <el-input v-model="draft.studentName" size="small" />
              </div>
              <div class="edit-field">
                <span class="edit-label">专业</span>
                <el-input v-model="draft.baseInfo.major" size="small" />
              </div>
            </div>
          </div>

          <p v-if="!isEditing">目标岗位：{{ currentJob?.name || baseInfo.targetJob }}</p>
          <div v-else class="edit-grid">
            <div class="edit-field">
              <span class="edit-label">目标岗位</span>
              <el-input v-model="draft.baseInfo.targetJob" size="small" />
            </div>
          </div>
        </section>

        <section class="report-section">
          <h2 class="section-title">2. 学生当前能力画像摘要</h2>
          <div v-if="!isEditing" class="summary-lines">
            <p
              v-for="(line, idx) in summaryLines"
              :key="`summary-line-${idx}`"
              class="summary-line"
            >
              {{ line }}
            </p>
          </div>
          <el-input
            v-else
            v-model="draft.baseInfo.summary"
            type="textarea"
            :rows="4"
            placeholder="可编辑：能力画像摘要"
          />
        </section>

        <section class="report-section">
          <h2 class="section-title">3. 个人优势与短板</h2>
          <div class="two-column">
            <div>
              <h3 class="subheading">优势</h3>
              <ul v-if="!isEditing">
                <li v-for="(a, index) in baseInfo.strengths" :key="index">{{ a }}</li>
              </ul>
              <div v-else class="edit-list">
                <div v-for="(a, index) in draft.baseInfo.strengths" :key="index" class="edit-list-row">
                  <el-input v-model="draft.baseInfo.strengths[index]" size="small" />
                    <el-button class="u-btn u-btn--text" text type="danger" @click="removeListItem('strengths', index)">删除</el-button>
                </div>
                <el-button class="u-btn u-btn--primary u-btn--sm" size="small" @click="addListItem('strengths')">添加优势</el-button>
              </div>
            </div>
            <div>
              <h3 class="subheading">待提升点</h3>
              <ul v-if="!isEditing">
                <li v-for="(w, index) in baseInfo.weaknesses" :key="index">{{ w }}</li>
              </ul>
              <div v-else class="edit-list">
                <div v-for="(w, index) in draft.baseInfo.weaknesses" :key="index" class="edit-list-row">
                  <el-input v-model="draft.baseInfo.weaknesses[index]" size="small" />
                    <el-button class="u-btn u-btn--text" text type="danger" @click="removeListItem('weaknesses', index)">删除</el-button>
                </div>
                <el-button class="u-btn u-btn--primary u-btn--sm" size="small" @click="addListItem('weaknesses')">添加待提升点</el-button>
              </div>
            </div>
          </div>
        </section>

        <section class="report-section">
          <h2 class="section-title">4. 职业发展路径（阶段性规划示意）</h2>
          <p class="hint-text">
            下面的表格示意了 6 个月内的阶段性成长路径，未来你可以用自动生成的图片替换这部分。
          </p>
          <figure v-if="!isEditing" class="path-figure">
            <img class="path-img" :src="learningPathPlaceholder" alt="阶段性成长路径（占位示意图）" />
            <figcaption class="path-caption">{{ pathNote }}</figcaption>
          </figure>
          <el-input
            v-else
            v-model="draft.pathNote"
            type="textarea"
            :rows="3"
            placeholder="可编辑：职业发展路径说明/占位内容"
          />
        </section>

        <!-- 5. 短期成长计划（0-6 个月） -->
        <section class="report-section">
          <h2 class="section-title">5. 短期成长计划（0 ~ 6 个月）</h2>
          <el-table
            :data="shortTermPlan"
            border
            class="plan-table"
          >
            <el-table-column label="阶段" width="120">
              <template #default="{ row, $index }">
                <span v-if="!isEditing">{{ row.phase }}</span>
                <el-input v-else v-model="draft.shortTermPlan[$index].phase" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="时间节点" width="160">
              <template #default="{ row, $index }">
                <span v-if="!isEditing">{{ row.time }}</span>
                <el-input v-else v-model="draft.shortTermPlan[$index].time" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="核心提升方向" min-width="180">
              <template #default="{ row, $index }">
                <span v-if="!isEditing">{{ row.direction }}</span>
                <el-input v-else v-model="draft.shortTermPlan[$index].direction" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="具体学习路径" min-width="220">
              <template #default="{ row, $index }">
                <span v-if="!isEditing">{{ row.path }}</span>
                <el-input v-else v-model="draft.shortTermPlan[$index].path" type="textarea" :rows="2" />
              </template>
            </el-table-column>
            <el-table-column label="具体实践安排" min-width="180">
              <template #default="{ row, $index }">
                <span v-if="!isEditing">{{ row.practice }}</span>
                <el-input v-else v-model="draft.shortTermPlan[$index].practice" type="textarea" :rows="2" />
              </template>
            </el-table-column>
            <el-table-column label="量化评估指标" min-width="210">
              <template #default="{ row }">
                <div class="metric-cell">
                  <span v-if="!isEditing" class="metric-text">{{ row.metric }}</span>
                  <el-input
                    v-else
                    v-model="draft.shortTermPlan[draftRowIndex('short', row)].metric"
                    type="textarea"
                    :rows="2"
                  />
                </div>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="isEditing" class="plan-edit-actions">
            <el-button class="u-btn u-btn--primary u-btn--sm" size="small" @click="addPlanRow('short')">添加一行</el-button>
          </div>
        </section>

        <!-- 6. 中期成长计划（6-18 个月） -->
        <section class="report-section">
          <h2 class="section-title">6. 中期成长计划（6 ~ 18 个月）</h2>
          <el-table
            :data="midTermPlan"
            border
            class="plan-table"
          >
            <el-table-column label="阶段" width="120">
              <template #default="{ row, $index }">
                <span v-if="!isEditing">{{ row.phase }}</span>
                <el-input v-else v-model="draft.midTermPlan[$index].phase" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="时间节点" width="160">
              <template #default="{ row, $index }">
                <span v-if="!isEditing">{{ row.time }}</span>
                <el-input v-else v-model="draft.midTermPlan[$index].time" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="核心提升方向" min-width="180">
              <template #default="{ row, $index }">
                <span v-if="!isEditing">{{ row.direction }}</span>
                <el-input v-else v-model="draft.midTermPlan[$index].direction" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="具体学习路径" min-width="220">
              <template #default="{ row, $index }">
                <span v-if="!isEditing">{{ row.path }}</span>
                <el-input v-else v-model="draft.midTermPlan[$index].path" type="textarea" :rows="2" />
              </template>
            </el-table-column>
            <el-table-column label="具体实践安排" min-width="180">
              <template #default="{ row, $index }">
                <span v-if="!isEditing">{{ row.practice }}</span>
                <el-input v-else v-model="draft.midTermPlan[$index].practice" type="textarea" :rows="2" />
              </template>
            </el-table-column>
            <el-table-column label="量化评估指标" min-width="210">
              <template #default="{ row }">
                <div class="metric-cell">
                  <span v-if="!isEditing" class="metric-text">{{ row.metric }}</span>
                  <el-input
                    v-else
                    v-model="draft.midTermPlan[draftRowIndex('mid', row)].metric"
                    type="textarea"
                    :rows="2"
                  />
                </div>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="isEditing" class="plan-edit-actions">
            <el-button class="u-btn u-btn--primary u-btn--sm" size="small" @click="addPlanRow('mid')">添加一行</el-button>
          </div>
        </section>

        <!-- 6b. 行动建议（模块四任务清单，有数据时展示） -->
        <section v-if="todoList.length" class="report-section action-todo-section">
          <h2 class="section-title">行动建议（任务清单）</h2>
          <p class="hint-text">来自报告模块四的行动项，便于对照执行与验收。</p>
          <div class="todo-card-grid">
            <article v-for="(t, idx) in todoList" :key="t.id || `todo-${idx}`" class="todo-card">
              <h3 class="todo-card-title">{{ t.title || '（未命名任务）' }}</h3>
              <p v-if="t.description" class="todo-card-desc">{{ t.description }}</p>
              <div class="todo-card-meta">
                <span v-if="t.target_dimension_label || t.target_dimension" class="todo-chip">
                  {{ t.target_dimension_label || t.target_dimension }}
                </span>
                <span v-if="t.difficulty" class="todo-chip">{{ t.difficulty }}</span>
                <span v-if="t.estimated_hours" class="todo-chip">约 {{ t.estimated_hours }}h</span>
                <span v-if="t.status" class="todo-chip todo-chip--status">{{ t.status }}</span>
              </div>
            </article>
          </div>
        </section>

        <!-- 7. 阶段性达成标准与评估 -->
        <section class="report-section">
          <h2 class="section-title">7. 阶段性达成标准与评估</h2>
          <p v-if="!isEditing">{{ evaluationSummary }}</p>
          <el-input
            v-else
            v-model="draft.evaluationSummary"
            type="textarea"
            :rows="4"
            placeholder="可编辑：阶段性达成标准与评估"
          />
        </section>

        <div class="report-bottom-actions">
          <el-button class="u-btn u-btn--primary u-btn--lg" type="primary" size="large" @click="goGenerateTrainingPlan">
            生成能力培训计划
          </el-button>
        </div>
      </section>

      <footer class="site-footer">
        <span>© {{ new Date().getFullYear() }} 职途智引 · AI职业规划助手</span>
      </footer>
    </main>

  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { useTheme } from '../composables/useTheme'
import { ElMessage } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import AppHeader from '../components/AppHeader.vue'
import learningPathPlaceholder from '../assets/uiineed-carousel-plan.svg'
import {
  buildMatchReportPayload,
  extractFourDimensionScoresFromMatchPayload,
  fetchRecommendJobList,
  formatFourDimensionScoresForCompareRows,
  mapActionPlanItemFromApi,
  mapPlanRow,
  mapRecommendListItemToJob,
  normalizeMatchReportPayload,
  parseMatchRadarFourDimensionValues,
  postMatchDetail,
  postMatchReport,
  readProfileCacheId,
  saveLastMatchResult,
  saveProfileCacheId,
} from '../api/careerAgentApi'
import {
  buildCompareDimensionRows,
  resolveMatchDimensionRequirementTexts,
} from '../utils/matchDimensionRequirements'
import { mergeGapDetailStrings, mergeSuggestDetailStrings } from '../utils/matchAnalysisTextMerge'
import { buildPortraitStyleRadarOption } from '../utils/portraitRadarEchartsOption'

const router = useRouter()
const studentName = ref('张同学')
const { theme } = useTheme()

// 页面步骤：match（岗位匹配）/ report（职业报告）
const step = ref('match')

const recommendedJobs = ref([])
const selectedJobId = ref('')
const profileCacheId = ref('')
const studentProfile = ref(null)
const currentJob = ref(null)

// 人岗匹配四维度：基础要求、职业技能、职业素养、发展潜力（题目要求）
const compareDimensions = ref([
  { name: '基础要求', student: '-', requirementText: '—' },
  { name: '职业技能', student: '-', requirementText: '—' },
  { name: '职业素养', student: '-', requirementText: '—' },
  { name: '发展潜力', student: '-', requirementText: '—' },
])

const gapDetails = ref([])
const improveSuggestions = ref([])

/** 最近一次匹配详情（用于雷达图岗位四维分） */
const lastMatchDetail = ref(null)

const CAREER_MATCH_FOUR_LABELS = ['基础要求', '职业技能', '职业素养', '发展潜力']

const matchRadarParsed = computed(() =>
  parseMatchRadarFourDimensionValues(lastMatchDetail.value || {})
)

const matchRadarJobValues = computed(() => matchRadarParsed.value.job)

const matchRadarStudentValues = computed(() => matchRadarParsed.value.student)

const matchCompareRadarOption = computed(() => {
  const isDark = theme.value === 'dark'
  const indicator = CAREER_MATCH_FOUR_LABELS.map((name) => ({ name, max: 100 }))
  return buildPortraitStyleRadarOption({
    isDark,
    indicator,
    legendData: ['岗位要求', '学生能力'],
    seriesData: [
      {
        value: matchRadarJobValues.value,
        name: '岗位要求',
        lineStyle: { color: '#33322e', width: 2.5 },
        areaStyle: { color: 'rgba(255, 214, 233, 0.55)' },
        itemStyle: { color: 'rgba(255, 214, 233, 0.85)', borderWidth: 0 },
        symbol: 'circle',
        symbolSize: 6,
      },
      {
        value: matchRadarStudentValues.value,
        name: '学生能力',
        lineStyle: { color: '#33322e', width: 2.5 },
        areaStyle: { color: 'rgba(140, 212, 203, 0.42)' },
        itemStyle: { color: 'rgba(140, 212, 203, 0.85)', borderWidth: 0 },
        symbol: 'circle',
        symbolSize: 6,
      },
    ],
  })
})

const viewJobDetail = (row) => {
  selectedJobId.value = String(row.id)
  loadMatchDetail()
}

// 生成报告
const generateReport = async () => {
  if (!selectedJobId.value) {
    ElMessage.warning('请先选择岗位')
    return
  }
  if (!profileCacheId.value) {
    profileCacheId.value = readProfileCacheId() || ''
  }
  try {
    const payload = buildMatchReportPayload({
      job_id: selectedJobId.value,
      profile_cache_id: profileCacheId.value || '',
      student_profile: studentProfile.value || null,
      precomputed_module_1: null,
    })
    const raw = await postMatchReport(payload)
    saveLastMatchResult(raw)
    const normalized = normalizeMatchReportPayload(raw)
    if (normalized) {
      await applyNormalizedReport(normalized)
      syncDraftFromCurrent()
    }
    step.value = 'report'
    ElMessage.success('已生成职业发展规划报告')
  } catch (e) {
    ElMessage.error(`生成报告失败：${e?.message || '请稍后重试'}`)
  }
}

const goGenerateTrainingPlan = () => {
  router.push('/ability-training-plan/generated')
}

// 报告基础信息
const reportDate = new Date().toLocaleDateString()
const pathNote = ref('这里暂时使用第三张图的学习路径表格结构作为占位。')

const baseInfo = ref({
  major: '计算机科学与技术',
  targetJob: 'Java 开发工程师',
  summary:
    '综合能力指数处于同专业学生的中上水平，专业基础扎实，学习能力和自驱力较强，但在实践项目深度、系统设计与抗压能力方面仍有较大提升空间。',
  strengths: [
    'Java、MySQL 等技术基础扎实，代码规范较好。',
    '自学能力强，能够主动完成课程外的扩展学习。',
    '团队项目中有承担核心模块开发的经验。'
  ],
  weaknesses: [
    '真实业务项目经验偏少，对生产环境问题处理经验有限。',
    '与产品、测试的跨角色沟通协作经验不多。',
    '在时间管理与压力管理方面还有提升空间。'
  ]
})

// 短期 / 中期成长计划（参考第三张图结构）
const shortTermPlan = ref([
  {
    phase: '第一阶段',
    time: '第 1-2 个月',
    direction: '职业技能（MySQL 优化、Redis 基础）',
    path: '完成 MySQL 实战课程；学习 Redis 基础与常用命令；每周整理学习笔记。',
    practice: '完成 2 个 MySQL 优化实战案例，并在本地项目中集成 Redis 缓存。',
    metric: '完成不少于 2 万行 SQL/Redis 命令练习，并通过 1 次小测验。'
  },
  {
    phase: '第二阶段',
    time: '第 3-4 个月',
    direction: '后端框架（SpringBoot 进阶）+ 项目实践',
    path: '完成 SpringBoot 进阶课程；阅读开源项目源码；实现完整增删改查模块。',
    practice: '独立完成一个小型后端服务，接入数据库与缓存，编写基础单元测试。',
    metric: '提交不少于 30 次 Git 提交记录，完成 1 个可在简历中展示的项目。'
  }
])

const midTermPlan = ref([
  {
    phase: '第三阶段',
    time: '第 5-6 个月',
    direction: '职业素养（沟通 / 抗压）+ 岗位适配能力',
    path: '参加面试沟通技巧课程；模拟多轮面试；参与团队协作项目并记录复盘。',
    practice: '完成不少于 3 次模拟面试；在团队项目中承担公共模块开发并主导 1 次复盘。',
    metric: '通过 2 次以上技术面试测评，团队成员反馈沟通满意度达到 80% 以上。'
  }
])

/** 模块四行动项（后端 todo_items 等映射） */
const todoList = ref([])

const evaluationSummary = ref(
  '达到目标岗位的核心胜任力：技术能力可证明（项目/指标）、表达清晰（STAR）、能在压力与约束下稳定交付。'
)

// ---------------- 报告编辑模式 ----------------
const isEditing = ref(false)
const draft = ref({
  studentName: '',
  baseInfo: { major: '', targetJob: '', summary: '', strengths: [], weaknesses: [] },
  pathNote: '',
  shortTermPlan: [],
  midTermPlan: [],
  evaluationSummary: '',
})

const deepClone = (v) => JSON.parse(JSON.stringify(v))

const normalizeJobRow = (row) => {
  if (!row || typeof row !== 'object') return null
  const mapped = mapRecommendListItemToJob(row)
  return {
    id: mapped.job_id,
    name: mapped.title,
    match: Math.max(0, Math.min(100, Math.round(Number(mapped.match_score || 0)))),
    requireMatch: 80,
  }
}

const safeArr = (value) => (Array.isArray(value) ? value : [])

const toTextList = (value, fallback = []) => {
  const list = safeArr(value).map((x) => String(x || '').trim()).filter(Boolean)
  return list.length ? list : fallback
}

const summaryLines = computed(() =>
  String(baseInfo.value?.summary || '')
    .split('。')
    .map((x) => x.trim())
    .filter(Boolean)
)

const buildMatchPayload = (jobId) => {
  const payload = { job_id: String(jobId) }
  if (!profileCacheId.value) {
    profileCacheId.value = readProfileCacheId() || ''
  }
  if (profileCacheId.value) {
    payload.profile_cache_id = profileCacheId.value
  } else if (studentProfile.value) {
    payload.student_profile = studentProfile.value
  }
  return payload
}

const applyMatchDetail = async (detail) => {
  if (!detail || typeof detail !== 'object') return
  lastMatchDetail.value = detail
  const score = Number(detail.match_score ?? 0)
  currentJob.value = {
    id: String(detail.job_id || selectedJobId.value),
    name: detail.title || currentJob.value?.name || baseInfo.value.targetJob,
    match: Number.isFinite(score) ? Math.round(score) : 0,
    requireMatch: 80,
  }
  const dimScores = extractFourDimensionScoresFromMatchPayload(detail)
  const studentByKey = formatFourDimensionScoresForCompareRows(dimScores)
  const texts = await resolveMatchDimensionRequirementTexts(
    detail,
    String(detail.job_id || selectedJobId.value),
    detail.title || currentJob.value?.name || '',
    null
  )
  compareDimensions.value = buildCompareDimensionRows(texts, studentByKey)
  const narrative = String(detail.narrative || '')
  gapDetails.value = mergeGapDetailStrings(detail, narrative, dimScores)
  improveSuggestions.value = mergeSuggestDetailStrings(detail, narrative, dimScores)
}

const applyNormalizedReport = async (normalized) => {
  if (!normalized || typeof normalized !== 'object') return
  const jobTitle = normalized.job_info?.title || currentJob.value?.name
  if (jobTitle) {
    baseInfo.value.targetJob = jobTitle
  }
  const score = Number(normalized.match_analysis?.match_score ?? currentJob.value?.match ?? 0)
  currentJob.value = {
    id: String(normalized.job_info?.job_id || selectedJobId.value || currentJob.value?.id || ''),
    name: jobTitle || baseInfo.value.targetJob,
    match: Number.isFinite(score) ? Math.round(score) : 0,
    requireMatch: 80,
  }
  const dimScores = extractFourDimensionScoresFromMatchPayload(normalized)
  const studentByKey = formatFourDimensionScoresForCompareRows(dimScores)
  const module1Tj = normalized.career_report?.module_1?.target_job
  const jobId = String(normalized.job_info?.job_id || selectedJobId.value || '')
  const texts = await resolveMatchDimensionRequirementTexts(
    {},
    jobId,
    jobTitle || baseInfo.value.targetJob || '',
    module1Tj || null
  )
  compareDimensions.value = buildCompareDimensionRows(texts, studentByKey)
  const reportNarrative = String(normalized.narrative ?? '')
  gapDetails.value = mergeGapDetailStrings(normalized, reportNarrative, dimScores)
  improveSuggestions.value = mergeSuggestDetailStrings(normalized, reportNarrative, dimScores)

  const report = normalized.career_report || {}
  if (report.gap_analysis) baseInfo.value.summary = String(report.gap_analysis)
  if (report.learning_path) pathNote.value = String(report.learning_path)
  const strengths = toTextList(report.strengths)
  const weaknesses = toTextList(report.weaknesses)
  if (strengths.length) baseInfo.value.strengths = strengths
  if (weaknesses.length) baseInfo.value.weaknesses = weaknesses
  if (report.evaluation_summary) evaluationSummary.value = String(report.evaluation_summary)

  let mappedShort = safeArr(report.short_term_plan).map(mapPlanRow).filter(Boolean)
  let mappedMid = safeArr(report.mid_term_plan).map(mapPlanRow).filter(Boolean)
  const fromModule3Items = safeArr(report.module_3?.plan_items ?? report.module_3?.planItems)
    .map(mapPlanRow)
    .filter(Boolean)
  if ((!mappedShort.length || !mappedMid.length) && fromModule3Items.length) {
    if (!mappedShort.length) mappedShort = fromModule3Items.slice(0, 3)
    if (!mappedMid.length) mappedMid = fromModule3Items.slice(3)
  }
  if (mappedShort.length) shortTermPlan.value = mappedShort
  if (mappedMid.length) midTermPlan.value = mappedMid

  const m4 = report.module_4 || {}
  const todoRaw = m4.todo_items ?? m4.todoItems ?? m4.items ?? []
  const todos = Array.isArray(todoRaw) ? todoRaw : []
  todoList.value = todos.map(mapActionPlanItemFromApi).filter(Boolean)
}

const loadRecommendJobs = async () => {
  try {
    const list = await fetchRecommendJobList()
    const mapped = list.map(normalizeJobRow).filter(Boolean)
    if (mapped.length) {
      recommendedJobs.value = mapped
      selectedJobId.value = String(mapped[0].id)
      return
    }
  } catch (e) {
    ElMessage.warning(`获取岗位列表失败：${e?.message || '使用示意数据'}`)
  }
  recommendedJobs.value = [
    { id: 'JOB_001', name: 'Java 开发工程师', match: 85, requireMatch: 85 },
    { id: 'JOB_002', name: '前端开发工程师', match: 78, requireMatch: 82 },
    { id: 'JOB_003', name: '软件测试工程师', match: 72, requireMatch: 80 },
  ]
  selectedJobId.value = String(recommendedJobs.value[0].id)
}

const loadMatchDetail = async () => {
  if (!selectedJobId.value) return
  lastMatchDetail.value = null
  try {
    const detail = await postMatchDetail(buildMatchPayload(selectedJobId.value))
    saveLastMatchResult(detail)
    await applyMatchDetail(detail)
    ElMessage.success(`已加载岗位「${currentJob.value?.name || ''}」匹配详情`)
  } catch (e) {
    const fallback = recommendedJobs.value.find((x) => String(x.id) === String(selectedJobId.value))
    if (fallback) currentJob.value = { ...fallback }
    lastMatchDetail.value = null
    gapDetails.value = ['接口详情获取失败，当前展示基础信息。']
    improveSuggestions.value = ['请稍后重试，或先直接生成职业规划报告。']
    ElMessage.warning(`加载详情失败：${e?.message || '请稍后重试'}`)
  }
}

const syncDraftFromCurrent = () => {
  draft.value = {
    studentName: studentName.value,
    baseInfo: deepClone(baseInfo.value),
    pathNote: pathNote.value,
    shortTermPlan: deepClone(shortTermPlan.value),
    midTermPlan: deepClone(midTermPlan.value),
    evaluationSummary: evaluationSummary.value,
  }
}

const startEdit = () => {
  draft.value = {
    studentName: studentName.value,
    baseInfo: deepClone(baseInfo.value),
    pathNote: pathNote.value,
    shortTermPlan: deepClone(shortTermPlan.value),
    midTermPlan: deepClone(midTermPlan.value),
    evaluationSummary: evaluationSummary.value,
  }
  isEditing.value = true
}

const handleEditReport = () => {
  startEdit()
  ElMessage.success('已进入编辑模式：可直接修改页面内容。')
}

const saveReportEdits = () => {
  studentName.value = draft.value.studentName || studentName.value
  baseInfo.value = deepClone(draft.value.baseInfo)
  pathNote.value = draft.value.pathNote
  shortTermPlan.value = deepClone(draft.value.shortTermPlan)
  midTermPlan.value = deepClone(draft.value.midTermPlan)
  evaluationSummary.value = draft.value.evaluationSummary
  isEditing.value = false
  ElMessage.success('已完成报告编辑（已保存）。')
}

const cancelReportEdits = () => {
  isEditing.value = false
  ElMessage.info('已取消编辑，未保存更改。')
}

const addListItem = (key) => {
  if (key === 'strengths') draft.value.baseInfo.strengths.push('新增优势（请编辑）')
  if (key === 'weaknesses') draft.value.baseInfo.weaknesses.push('新增待提升点（请编辑）')
}

const removeListItem = (key, index) => {
  if (key === 'strengths') draft.value.baseInfo.strengths.splice(index, 1)
  if (key === 'weaknesses') draft.value.baseInfo.weaknesses.splice(index, 1)
}

const addPlanRow = (phase) => {
  const row = {
    phase: '新增阶段',
    time: '时间节点',
    direction: '核心提升方向',
    path: '具体学习路径',
    practice: '具体实践安排',
    metric: '量化评估指标',
  }
  if (phase === 'short') draft.value.shortTermPlan.push(row)
  if (phase === 'mid') draft.value.midTermPlan.push(row)
}

const draftRowIndex = (phase, row) => {
  const list = phase === 'short' ? draft.value.shortTermPlan : draft.value.midTermPlan
  const idx = list.findIndex((r) => r === row)
  if (idx !== -1) return idx
  // fallback：按 metric 匹配（示意数据下足够）
  return list.findIndex((r) => r.metric === row.metric)
}

// 报告头部按钮功能（示意）
const handlePolish = () => {
  const payload = buildReportPayload()
  try {
    sessionStorage.setItem('career_report_payload_v1', JSON.stringify(payload))
  } catch (e) {
    // ignore
  }
  router.push({ name: 'CareerReportTemplate' })
}

const exportReport = (format) => {
  const payload = buildReportPayload()
  if (format === 'markdown') {
    const content = buildMarkdown(payload)
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'career-report.md'
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('已导出 Markdown 报告文件，你可以根据需要转换为其他格式。')
  } else if (format === 'pdf') {
    openPrintWindow(payload)
    ElMessage.success('已打开打印窗口：可选择“另存为 PDF”。')
  } else if (format === 'word') {
    downloadWordDoc(payload, 'career-report.doc')
    ElMessage.success('已导出 Word（.doc）文件。')
  }
}

function buildReportPayload() {
  return {
    studentName: studentName.value,
    reportDate,
    theme: theme.value,
    jobId: String(selectedJobId.value || currentJob.value?.id || ''),
    targetJob: currentJob.value?.name || baseInfo.value.targetJob,
    profile_cache_id: String(profileCacheId.value || readProfileCacheId() || '').trim(),
    student_profile: studentProfile.value ? deepClone(studentProfile.value) : null,
    baseInfo: deepClone(baseInfo.value),
    pathNote: pathNote.value,
    shortTermPlan: deepClone(shortTermPlan.value),
    midTermPlan: deepClone(midTermPlan.value),
    evaluationSummary: evaluationSummary.value,
  }
}

function buildMarkdown(payload) {
  const lines = []
  lines.push(`# 职业发展规划报告`)
  lines.push('')
  lines.push(`学生：${payload.studentName}`)
  lines.push(`目标岗位：${payload.targetJob}`)
  lines.push(`生成时间：${payload.reportDate}`)
  lines.push('')
  lines.push('## 1. 基本信息与目标岗位')
  lines.push(`- 专业：${payload.baseInfo.major}`)
  lines.push(`- 目标岗位：${payload.targetJob}`)
  lines.push('')
  lines.push('## 2. 学生当前能力画像摘要')
  lines.push(payload.baseInfo.summary)
  lines.push('')
  lines.push('## 3. 个人优势与短板')
  lines.push('**优势**')
  for (const s of payload.baseInfo.strengths || []) lines.push(`- ${s}`)
  lines.push('')
  lines.push('**待提升点**')
  for (const w of payload.baseInfo.weaknesses || []) lines.push(`- ${w}`)
  lines.push('')
  lines.push('## 4. 职业发展路径（阶段性规划示意）')
  lines.push(payload.pathNote || '')
  lines.push('')
  lines.push('## 5. 短期成长计划（0 ~ 6 个月）')
  for (const r of payload.shortTermPlan || []) {
    lines.push(`- ${r.phase}（${r.time}）：${r.direction}`)
    lines.push(`  - 学习路径：${r.path}`)
    lines.push(`  - 实践安排：${r.practice}`)
    lines.push(`  - 指标：${r.metric}`)
  }
  lines.push('')
  lines.push('## 6. 中期成长计划（6 ~ 18 个月）')
  for (const r of payload.midTermPlan || []) {
    lines.push(`- ${r.phase}（${r.time}）：${r.direction}`)
    lines.push(`  - 学习路径：${r.path}`)
    lines.push(`  - 实践安排：${r.practice}`)
    lines.push(`  - 指标：${r.metric}`)
  }
  lines.push('')
  lines.push('## 7. 阶段性达成标准与评估')
  lines.push(payload.evaluationSummary || '')
  lines.push('')
  return lines.join('\n')
}

function buildHtml(payload) {
  const esc = (s) =>
    String(s ?? '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#39;')

  const li = (items) => (items || []).map((x) => `<li>${esc(x)}</li>`).join('')
  const planRows = (rows) =>
    (rows || [])
      .map(
        (r) => `<tr>
  <td>${esc(r.phase)}</td>
  <td>${esc(r.time)}</td>
  <td>${esc(r.direction)}</td>
  <td>${esc(r.path)}</td>
  <td>${esc(r.practice)}</td>
  <td>${esc(r.metric)}</td>
</tr>`
      )
      .join('')

  return `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>职业发展规划报告</title>
  <style>
    body{font-family:'Source Han Sans SC','Source Han Sans CN','Source Han Sans','Noto Sans CJK SC','Noto Sans SC',Roboto,'Helvetica Neue',Helvetica,Arial,sans-serif;padding:24px;color:#111827;}
    h1{margin:0 0 6px;}
    .meta{color:#475569;margin:0 0 18px;}
    h2{margin:18px 0 10px;}
    table{width:100%;border-collapse:collapse;}
    th,td{border:1px solid #e5e7eb;padding:8px;vertical-align:top;font-size:12px;line-height:1.45;}
    th{background:#f8fafc;text-align:left;}
    ul{margin:8px 0 0;padding-left:18px;}
  </style>
</head>
<body>
  <h1>职业发展规划报告</h1>
  <p class="meta">学生：${esc(payload.studentName)} · 目标岗位：${esc(payload.targetJob)} · 生成时间：${esc(
    payload.reportDate
  )}</p>

  <h2>1. 基本信息与目标岗位</h2>
  <p>专业：${esc(payload.baseInfo.major)}<br/>目标岗位：${esc(payload.targetJob)}</p>

  <h2>2. 学生当前能力画像摘要</h2>
  <p>${esc(payload.baseInfo.summary)}</p>

  <h2>3. 个人优势与短板</h2>
  <h3>优势</h3>
  <ul>${li(payload.baseInfo.strengths)}</ul>
  <h3>待提升点</h3>
  <ul>${li(payload.baseInfo.weaknesses)}</ul>

  <h2>4. 职业发展路径（阶段性规划示意）</h2>
  <p>${esc(payload.pathNote || '')}</p>

  <h2>5. 短期成长计划（0 ~ 6 个月）</h2>
  <table>
    <thead><tr><th>阶段</th><th>时间节点</th><th>核心提升方向</th><th>具体学习路径</th><th>具体实践安排</th><th>量化评估指标</th></tr></thead>
    <tbody>${planRows(payload.shortTermPlan)}</tbody>
  </table>

  <h2>6. 中期成长计划（6 ~ 18 个月）</h2>
  <table>
    <thead><tr><th>阶段</th><th>时间节点</th><th>核心提升方向</th><th>具体学习路径</th><th>具体实践安排</th><th>量化评估指标</th></tr></thead>
    <tbody>${planRows(payload.midTermPlan)}</tbody>
  </table>

  <h2>7. 阶段性达成标准与评估</h2>
  <p>${esc(payload.evaluationSummary || '')}</p>
</body>
</html>`
}

function openPrintWindow(payload) {
  const html = buildHtml(payload)
  const w = window.open('', '_blank', 'noopener,noreferrer')
  if (!w) return
  w.document.open()
  w.document.write(html)
  w.document.close()
  w.focus()
  setTimeout(() => {
    try {
      w.print()
    } catch (e) {
      // ignore
    }
  }, 200)
}

function downloadWordDoc(payload, filename) {
  const html = buildHtml(payload)
  const blob = new Blob([html], { type: 'application/msword;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename || 'career-report.doc'
  a.click()
  URL.revokeObjectURL(url)
}

const matchCompareRadarRef = ref(null)
let matchCompareRadarInstance = null
let matchCompareRadarResizeObserver = null

function disposeMatchCompareRadarChart() {
  if (matchCompareRadarResizeObserver) {
    matchCompareRadarResizeObserver.disconnect()
    matchCompareRadarResizeObserver = null
  }
  if (matchCompareRadarInstance) {
    matchCompareRadarInstance.dispose()
    matchCompareRadarInstance = null
  }
}

function ensureMatchCompareRadarChart() {
  if (step.value !== 'match' || !currentJob.value || !matchCompareRadarRef.value) return
  if (!matchCompareRadarInstance) {
    matchCompareRadarInstance = echarts.init(matchCompareRadarRef.value, null, { renderer: 'canvas' })
    matchCompareRadarResizeObserver = new ResizeObserver(() => matchCompareRadarInstance?.resize())
    matchCompareRadarResizeObserver.observe(matchCompareRadarRef.value)
  }
  matchCompareRadarInstance.setOption(matchCompareRadarOption.value, true)
}

watch(
  () => [matchCompareRadarOption.value, theme.value],
  () => {
    nextTick(() => ensureMatchCompareRadarChart())
  }
)

watch(step, (s) => {
  nextTick(() => {
    if (s !== 'match') disposeMatchCompareRadarChart()
    else if (currentJob.value) ensureMatchCompareRadarChart()
  })
})

watch(
  () => currentJob.value?.id,
  () => {
    if (step.value === 'match' && currentJob.value) {
      nextTick(() => ensureMatchCompareRadarChart())
    }
  }
)

onUnmounted(() => {
  disposeMatchCompareRadarChart()
})

onMounted(async () => {
  try {
    const routeCacheId = router.currentRoute.value.query?.profile_cache_id
    const routeName = router.currentRoute.value.query?.student_name
    if (routeCacheId) profileCacheId.value = String(routeCacheId)
    if (routeCacheId) saveProfileCacheId(routeCacheId)
    if (!profileCacheId.value) {
      profileCacheId.value = readProfileCacheId() || ''
    }
    if (routeName) studentName.value = String(routeName)
  } catch {
    // ignore
  }
  await loadRecommendJobs()
  await loadMatchDetail()
  nextTick(() => ensureMatchCompareRadarChart())
})
</script>

<style scoped>
.career-report-view {
  width: 100vw;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fb;
  color: #222;
  font-family: var(--font-family-sans);
  /* 该页字体整体偏大：这里单页再下调一档（不影响其它页面） */
  font-size: 16px;
  line-height: 1.6;
  /* 同步缩小 Element Plus 在本页的字号基准 */
  --el-font-size-base: 14px;
  --el-font-size-small: 13px;
  --el-font-size-extra-small: 12px;
  --el-font-size-medium: 15px;
  --el-font-size-large: 16px;
}

.career-report-view.dark {
  background: var(--dm-bg);
  color: var(--dm-text);
}

.career-report-view.dark .header {
  background: var(--dm-header-bg);
  backdrop-filter: blur(12px);
  border-bottom-color: var(--dm-border);
}

.career-report-view.dark .nav-item {
  color: var(--dm-text);
}

.career-report-view.dark .nav-item.active {
  color: var(--dm-accent);
}

.career-report-view.dark .nav-item.active::after {
  background-color: var(--dm-accent);
}

.career-report-view.dark .panel {
  background: var(--dm-gradient-card);
  box-shadow: 0 10px 26px rgba(0, 0, 0, 0.25);
  border: 1px solid var(--dm-border);
}

.career-report-view.dark .page-title,
.career-report-view.dark .section-title {
  color: var(--dm-text);
}

.career-report-view.dark .student-tag,
.career-report-view.dark .match-hint,
.career-report-view.dark .weight-hint,
.career-report-view.dark .dim-student,
.career-report-view.dark .dim-requirement-text {
  color: var(--dm-text-secondary);
}

.career-report-view.dark .dim-requirement-label {
  color: var(--dm-text-muted, var(--dm-text-secondary));
}

.career-report-view.dark .compare-list-item {
  background: color-mix(in srgb, var(--dm-surface-card, #1a1d24) 92%, transparent);
  border-color: color-mix(in srgb, var(--dm-border, #333) 70%, transparent);
}

.career-report-view.dark .report-panel .report-subtitle,
.career-report-view.dark .report-panel .hint-text {
  color: var(--dm-text-secondary);
}

.career-report-view.dark .match-hint {
  background: var(--dm-accent-soft);
}

.career-report-view.dark .compare-card {
  background: var(--dm-surface-card);
  border: 1px solid var(--dm-border);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.career-report-view.dark .compare-placeholder {
  background: var(--dm-surface);
  color: var(--dm-text-secondary);
}

.career-report-view.dark .report-panel {
  background: var(--dm-bg);
}

.career-report-view.dark .report-panel .section-title {
  color: var(--dm-text);
}

.career-report-view.dark .report-section {
  background: var(--dm-surface-card);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  border: 1px solid var(--dm-border);
}

.career-report-view.dark .report-section::before {
  opacity: 0.35;
}

.career-report-view.dark .report-panel .report-section > p,
.career-report-view.dark .report-panel .report-section li {
  color: var(--dm-text-secondary);
}

.career-report-view.dark .report-panel .path-placeholder {
  background: var(--dm-surface);
  border-color: var(--dm-border);
  color: var(--dm-text-secondary);
}

.career-report-view.dark .report-panel .path-img {
  border-color: var(--dm-border);
  background: var(--dm-surface);
}

.career-report-view.dark .report-panel .path-caption {
  color: var(--dm-text-secondary);
}

.career-report-view.dark .report-panel .subheading {
  color: var(--dm-text);
}

.career-report-view.dark .subheading {
  color: var(--dm-text);
}

.career-report-view.dark .report-panel .two-column {
  color: var(--dm-text-secondary);
}

.career-report-view.dark .detail-analysis {
  color: var(--dm-text-secondary);
}

.career-report-view.dark .detail-analysis ul,
.career-report-view.dark .compare-list,
.career-report-view.dark .suggest-list {
  color: var(--dm-text-secondary);
}

.career-report-view.dark .detail-analysis li,
.career-report-view.dark .compare-list li {
  color: var(--dm-text-secondary);
}

.career-report-view.dark p {
  color: var(--dm-text);
}

.career-report-view.dark .match-summary {
  color: var(--dm-text);
}

.career-report-view.dark .metric-text,
.career-report-view.dark .orig-metric,
.career-report-view.dark .dialog-label {
  color: var(--dm-text);
}

.career-report-view.dark .orig-metric {
  background: var(--dm-surface-elevated);
}

.edit-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
  margin-top: 8px;
}

.edit-field {
  display: grid;
  gap: 6px;
}

.edit-label {
  font-size: 12px;
  color: #64748b;
}

.career-report-view.dark .edit-label {
  color: var(--dm-text-muted);
}

.edit-list {
  display: grid;
  gap: 10px;
}

.edit-list-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
  align-items: center;
}

.plan-edit-actions {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}

/* Element Plus 表格夜间模式：保证表头与单元格文字可读 */
.career-report-view.dark :deep(.el-table) {
  --el-table-bg-color: var(--dm-surface);
  --el-table-tr-bg-color: var(--dm-surface);
  --el-table-header-bg-color: var(--dm-surface-elevated);
  --el-table-row-hover-bg-color: rgba(208, 244, 240, 0.18);
}

.career-report-view.dark :deep(.el-table th.el-table__cell),
.career-report-view.dark :deep(.el-table td.el-table__cell) {
  background-color: transparent;
  color: var(--dm-text);
  border-color: var(--dm-border);
}

.career-report-view.dark :deep(.el-table .el-table__inner-wrapper::before) {
  background-color: var(--dm-border);
}

/* 浅色：把内部分隔线底色拉到明显一点 */
.career-report-view :deep(.el-table .el-table__inner-wrapper::before) {
  background-color: rgba(51, 50, 46, 0.55) !important;
}

.career-report-view.dark :deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background: rgba(208, 244, 240, 0.12);
}

/* 覆盖亮色表格 !important（确保暗色下不再出现米/粉浅底） */
.career-report-view.dark .job-table :deep(.el-table) {
  border: 2px solid var(--dm-border);
}

.career-report-view.dark .job-table :deep(th.el-table__cell) {
  background: var(--dm-surface-elevated) !important;
  color: var(--dm-text) !important;
  border-color: var(--dm-border) !important;
  border-style: solid !important;
  border-width: 2px !important;
  border-right: 2px solid var(--dm-border) !important;
  border-bottom: 2px solid var(--dm-border) !important;
}

.career-report-view.dark .job-table :deep(td.el-table__cell) {
  border-color: var(--dm-border) !important;
  background: var(--dm-surface) !important;
  border-style: solid !important;
  border-width: 2px !important;
  border-right: 2px solid var(--dm-border) !important;
  border-bottom: 2px solid var(--dm-border) !important;
}

.career-report-view.dark .job-table :deep(.el-table__body tr.el-table__row--striped td.el-table__cell) {
  background: rgba(255, 255, 255, 0.04) !important;
}

.career-report-view.dark .job-table :deep(.el-table__body tr.el-table__row--hover td.el-table__cell) {
  background: rgba(208, 244, 240, 0.16) !important;
}

.career-report-view.dark .report-panel .plan-table {
  --el-table-bg-color: var(--dm-surface);
  --el-table-tr-bg-color: var(--dm-surface);
  --el-table-row-hover-bg-color: rgba(208, 244, 240, 0.18);
}

.career-report-view.dark .report-panel .plan-table :deep(th.el-table__cell) {
  background: var(--dm-surface-elevated) !important;
  border-color: var(--dm-border) !important;
  border-style: solid !important;
  border-width: 2px !important;
  border-right: 2px solid var(--dm-border) !important;
  border-bottom: 2px solid var(--dm-border) !important;
}

.career-report-view.dark .report-panel .plan-table :deep(td.el-table__cell) {
  background: var(--dm-surface) !important;
  border-color: var(--dm-border) !important;
  border-style: solid !important;
  border-width: 2px !important;
  border-right: 2px solid var(--dm-border) !important;
  border-bottom: 2px solid var(--dm-border) !important;
}

.career-report-view.dark .report-panel .plan-table :deep(.el-table__body tr.el-table__row--striped td.el-table__cell) {
  background: rgba(255, 255, 255, 0.04) !important;
}

.career-report-view.dark .report-panel .plan-table :deep(.el-table__body tr.el-table__row--hover td.el-table__cell) {
  background: rgba(208, 244, 240, 0.16) !important;
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
  border-bottom: 1px solid #edf0f5;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 2vw;
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
  color: #444;
  text-decoration: none;
  position: relative;
  padding-bottom: 4px;
}

.logo {
  text-decoration: none;
  color: inherit;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.theme-toggle {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  background: #f0f2f8;
  padding: 4px;
  font-size: 12px;
}

.theme-option {
  padding: 4px 12px;
  border-radius: 999px;
  cursor: pointer;
  color: #666;
}

.theme-option.active {
  background: #111827;
  color: #fff;
}

.career-report-view.dark .theme-toggle {
  background: var(--dm-surface);
}

.career-report-view.dark .theme-option {
  color: var(--dm-text-secondary);
}

.career-report-view.dark .theme-option.active {
  background: var(--dm-surface-elevated);
  color: var(--dm-text);
}

.nav-back {
  font-size: var(--fs-small);
  font-weight: var(--fw-body);
}

.nav-item.active {
  color: #f9b437;
}

.nav-item.active::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
  height: 2px;
  background-color: #f9b437;
}

.page-scroll {
  padding: 24px 6vw 48px 56px;
  flex: 1;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.site-footer {
  margin-top: auto;
  padding-top: 32px;
  padding-bottom: 16px;
  border-top: 1px solid rgba(148, 163, 184, 0.35);
  font-size: var(--fs-small);
  font-weight: var(--fw-body);
  color: #94a3b8;
  text-align: center;
  width: 100%;
}

.career-report-view.dark .site-footer {
  border-top-color: var(--dm-border);
  color: var(--dm-text-muted);
}

.panel {
  background: #f5fbff;
  border-radius: 18px;
  padding: 20px 22px 24px;
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.08);
}

.page-title {
  font-size: var(--fs-h1);
  font-weight: var(--fw-heading);
  margin: 0 0 6px;
}

.section-title {
  font-size: var(--fs-h2);
  font-weight: var(--fw-heading);
  margin-bottom: 10px;
}

.student-tag {
  font-size: clamp(13px, 0.95vw, 15px);
  color: #555;
}

.match-hint {
  font-size: clamp(13px, 0.9vw, 15px);
  color: #555;
  line-height: 1.6;
  margin-bottom: 14px;
  padding: 10px 12px;
  background: #f0f9ff;
  border-radius: 10px;
}

.weight-hint {
  font-size: clamp(13px, 0.9vw, 15px);
  color: #666;
  margin-top: 8px;
}

.match-header {
  margin-bottom: 12px;
}

.recommend-section {
  margin-top: 8px;
}

.job-table {
  margin-top: 8px;
  /* Uiineed：统一表格浅底 + 单一强调色，避免与卡片背景“融为一体” */
  --el-table-border-color: rgba(51, 50, 46, 0.42);
  --el-table-bg-color: var(--u-bg-normal);
  --el-table-tr-bg-color: var(--u-bg-normal);
  --el-table-row-hover-bg-color: rgba(208, 244, 240, 0.40);
}

.job-table :deep(.el-table) {
  border-radius: calc(var(--u-border-radius) - 4px);
  overflow: hidden;
  border: 2px solid rgba(51, 50, 46, 0.25);
  box-shadow: 3px 3px 0 rgba(51, 50, 46, 0.10);
}

.job-table :deep(th.el-table__cell) {
  background: var(--u-bg-normal) !important;
  color: var(--u-black);
  font-weight: 800;
  border-color: rgba(51, 50, 46, 0.55) !important;
  border-style: solid !important;
  border-width: 2px !important;
  border-right: 2px solid rgba(51, 50, 46, 0.55) !important;
  border-bottom: 2px solid rgba(51, 50, 46, 0.7) !important;
}

.job-table :deep(td.el-table__cell) {
  border-color: rgba(51, 50, 46, 0.38) !important;
  background: var(--u-bg-normal) !important;
  border-style: solid !important;
  border-width: 2px !important;
  border-right: 2px solid rgba(51, 50, 46, 0.38) !important;
  border-bottom: 2px solid rgba(51, 50, 46, 0.7) !important;
}

.job-table :deep(.el-table__body tr.el-table__row--striped td.el-table__cell) {
  background: rgba(208, 244, 240, 0.28) !important;
}

.job-table :deep(.el-table__body tr.el-table__row--hover td.el-table__cell) {
  background: rgba(208, 244, 240, 0.44) !important;
}

.current-job-section {
  margin-top: 18px;
}

.match-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 8px 0 12px;
  font-size: clamp(13px, 0.9vw, 15px);
}

.compare-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 14px 20px;
}

.compare-card {
  background:
    radial-gradient(circle at 12px 12px, rgba(51, 50, 46, 0.06) 1.4px, transparent 2.1px)
      0 0 / 28px 28px,
    linear-gradient(135deg, var(--u-bg-normal), var(--u-gradient-fade));
  border-radius: 12px;
  padding: 12px 14px;
  box-shadow: 0 4px 10px rgba(15, 23, 42, 0.04);
}

/* 混搭：对比卡片交替底色 */
.compare-grid .compare-card:nth-child(2) {
  background:
    radial-gradient(circle at 12px 12px, rgba(51, 50, 46, 0.06) 1.4px, transparent 2.1px)
      0 0 / 28px 28px,
    linear-gradient(135deg, var(--u-body-bg), var(--u-gradient-fade));
}

.compare-title {
  font-size: clamp(15px, 1vw, 17px);
  margin-bottom: 8px;
}

.compare-placeholder {
  height: 180px;
  border-radius: 10px;
  background: #f5f7fb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #777;
  text-align: center;
}

.compare-card--radar .compare-radar-chart {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.compare-radar-echart {
  width: 100%;
  max-width: min(100%, 400px);
  height: clamp(280px, 38vh, 400px);
  min-height: 260px;
  margin-inline: auto;
}

.compare-radar-note {
  margin: 0;
  font-size: clamp(12px, 0.85vw, 13px);
  color: #666;
  text-align: center;
}

.career-report-view.dark .compare-radar-note {
  color: var(--dm-text-secondary);
}

.compare-list {
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: clamp(13px, 0.9vw, 15px);
}

.compare-list li + li {
  margin-top: 12px;
}

.compare-list-item {
  padding: 10px 12px;
  border-radius: 10px;
  background: color-mix(in srgb, var(--u-body-bg, #fafafa) 55%, var(--u-panel, #fff));
  border: 1px solid color-mix(in srgb, var(--u-border-color, #e5e7eb) 80%, transparent);
}

.dim-row-head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 8px 12px;
  margin-bottom: 8px;
}

.dim-name {
  font-weight: 600;
}

.dim-student {
  font-size: clamp(12px, 0.88vw, 14px);
  color: #555;
}

.dim-requirement {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dim-requirement-label {
  font-size: clamp(11px, 0.78vw, 12px);
  font-weight: 600;
  color: #888;
}

.dim-requirement-text {
  margin: 0;
  font-size: clamp(12px, 0.85vw, 14px);
  line-height: 1.55;
  color: #444;
}

.detail-analysis {
  margin-top: 14px;
  font-size: clamp(13px, 0.9vw, 15px);
  line-height: 1.5;
}

.section-subtitle {
  font-weight: 600;
  font-size: clamp(14px, 0.95vw, 16px);
  margin: 8px 0 6px;
}

.action-row {
  margin-top: 12px;
  text-align: right;
}

/* 报告样式：与全站首页 / 简历智评报告页字号一致 */
.report-panel {
  background: var(--u-body-bg);
}

.report-panel .page-title {
  font-size: clamp(28px, 2.2vw, 38px);
  font-weight: 700;
  margin-bottom: 8px;
  line-height: 1.2;
}

.report-panel .report-subtitle {
  font-size: clamp(17px, 1.1vw, 20px);
  line-height: 1.6;
  color: rgba(51, 50, 46, 0.78);
  margin: 0;
}

.report-panel .section-title {
  font-size: clamp(16px, 1.05vw, 18px);
  font-weight: 600;
  margin: 0 0 8px;
  line-height: 1.35;
  color: var(--u-black);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 16px;
}

.header-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.report-section {
  margin-top: 14px;
  position: relative;
  overflow: hidden;
  --_section-accent: rgba(208, 244, 240, 0.85);
  background: rgba(249, 243, 229, 0.88);
  border-radius: 14px;
  padding: clamp(14px, 1.2vw, 18px);
  box-shadow: 0 4px 10px rgba(15, 23, 42, 0.04);
}

/* 左侧细色条：用色更克制，避免大面积配色混乱 */
.report-section::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 10px;
  height: 100%;
  background: var(--_section-accent);
  z-index: 0;
}

.report-section > * {
  position: relative;
  z-index: 1;
}

.report-panel .report-section > p,
.report-panel .report-section > ul,
.report-panel .report-section li {
  font-size: clamp(15px, 0.95vw, 17px);
  line-height: 1.65;
  color: var(--u-black);
}

.report-panel .report-section > p + p {
  margin-top: 8px;
}

.summary-lines {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.summary-line {
  margin: 0;
  line-height: 1.6;
}

.summary-line::before {
  content: '·';
  margin-right: 6px;
  font-weight: 700;
}

.report-panel .report-section ul {
  margin: 8px 0 0;
  padding-left: 1.25em;
}

/* 混搭：报告分段卡片按 Uiineed 色板交替 */
.report-panel .report-section:nth-of-type(4n + 2) {
  --_section-accent: rgba(208, 244, 240, 0.85);
}

.report-panel .report-section:nth-of-type(4n + 3) {
  --_section-accent: rgba(208, 244, 240, 0.85);
}

.report-panel .report-section:nth-of-type(4n) {
  --_section-accent: rgba(208, 244, 240, 0.85);
}

.report-panel .hint-text {
  font-size: clamp(15px, 0.95vw, 17px);
  color: var(--u-placeholder);
  margin-bottom: 10px;
  line-height: 1.6;
}

.report-panel .path-placeholder {
  margin-top: 8px;
  border-radius: 12px;
  border: 2px dashed rgba(51, 50, 46, 0.22);
  padding: 14px 16px;
  font-size: clamp(15px, 0.95vw, 17px);
  color: rgba(51, 50, 46, 0.78);
  background: rgba(249, 243, 229, 0.55);
  line-height: 1.6;
}

.report-panel .path-figure {
  margin: 10px 0 0;
}

.report-panel .path-img {
  width: 100%;
  display: block;
  border-radius: 14px;
  border: 2px solid rgba(51, 50, 46, 0.18);
  background: #ffffff;
}

.report-panel .path-caption {
  margin-top: 10px;
  font-size: clamp(15px, 0.95vw, 17px);
  color: rgba(51, 50, 46, 0.78);
  line-height: 1.6;
}

.report-panel .two-column {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px 24px;
  font-size: clamp(15px, 0.95vw, 17px);
  line-height: 1.65;
}

.report-panel .subheading {
  font-size: clamp(16px, 1.05vw, 18px);
  font-weight: 600;
  margin: 0 0 8px;
  color: var(--u-black);
}

.report-panel .plan-table {
  margin-top: 10px;
  font-size: clamp(14px, 0.92vw, 16px);
  --el-table-bg-color: var(--u-panel);
  --el-table-tr-bg-color: var(--u-panel);
  --el-table-row-hover-bg-color: rgba(208, 244, 240, 0.42);
}

.report-panel .plan-table :deep(.el-table th),
.report-panel .plan-table :deep(.el-table td) {
  font-size: inherit;
}

.report-panel .plan-table :deep(th.el-table__cell) {
  font-size: clamp(14px, 0.92vw, 16px);
  background: var(--u-panel) !important;
  color: var(--u-black);
  font-weight: 800;
  border-color: rgba(51, 50, 46, 0.55) !important;
  border-style: solid !important;
  border-width: 2px !important;
  border-right: 2px solid rgba(51, 50, 46, 0.55) !important;
  border-bottom: 2px solid rgba(51, 50, 46, 0.7) !important;
}

.report-panel .plan-table :deep(td.el-table__cell) {
  background: var(--u-panel) !important;
  border-color: rgba(51, 50, 46, 0.38) !important;
  border-style: solid !important;
  border-width: 2px !important;
  border-right: 2px solid rgba(51, 50, 46, 0.38) !important;
  border-bottom: 2px solid rgba(51, 50, 46, 0.7) !important;
}

.report-panel .plan-table :deep(.el-table__body tr.el-table__row--striped td.el-table__cell) {
  background: rgba(208, 244, 240, 0.28) !important;
}

.report-panel .plan-table :deep(.el-table__body tr.el-table__row--hover td.el-table__cell) {
  background: rgba(208, 244, 240, 0.44) !important;
}

.action-todo-section .todo-card-grid {
  display: grid;
  gap: 12px;
  margin-top: 10px;
}

@media (min-width: 720px) {
  .action-todo-section .todo-card-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.report-panel .todo-card {
  border: 2px solid rgba(51, 50, 46, 0.38);
  border-radius: 10px;
  padding: 14px 16px;
  background: var(--u-panel);
}

.report-panel .todo-card-title {
  margin: 0 0 8px;
  font-size: clamp(15px, 0.95vw, 17px);
  font-weight: 700;
  color: var(--u-black);
}

.report-panel .todo-card-desc {
  margin: 0 0 10px;
  font-size: clamp(14px, 0.9vw, 15px);
  line-height: 1.55;
  color: rgba(51, 50, 46, 0.88);
}

.report-panel .todo-card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.report-panel .todo-chip {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 999px;
  border: 1px solid rgba(51, 50, 46, 0.28);
  background: rgba(208, 244, 240, 0.22);
}

.report-panel .todo-chip--status {
  text-transform: capitalize;
}

.career-report-view.dark .report-panel .todo-card {
  border-color: var(--dm-border);
  background: var(--dm-surface);
}

.career-report-view.dark .report-panel .todo-card-title {
  color: var(--dm-text);
}

.career-report-view.dark .report-panel .todo-card-desc {
  color: color-mix(in srgb, var(--dm-text) 88%, transparent);
}

.career-report-view.dark .report-panel .todo-chip {
  border-color: var(--dm-border);
  background: rgba(255, 255, 255, 0.06);
}

.metric-cell {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
}

.metric-text {
  flex: 1;
}

.report-bottom-actions {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.dialog-label {
  margin: 8px 0 4px;
  font-size: clamp(15px, 0.95vw, 17px);
  font-weight: 600;
}

.orig-metric {
  padding: 8px 10px;
  background: #f5f7fb;
  border-radius: 8px;
  font-size: clamp(15px, 0.95vw, 17px);
  line-height: 1.55;
}

.suggest-group {
  margin: 4px 0 6px;
}

.suggest-list {
  font-size: clamp(15px, 0.95vw, 17px);
  padding-left: 18px;
  margin: 0 0 8px;
  line-height: 1.6;
}

.reason-block {
  margin-top: 6px;
}

@media (max-width: 900px) {
  .nav {
    display: none;
  }

  .page-scroll {
    padding-inline: 16px;
  }

  .report-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .match-summary {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>