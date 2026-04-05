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
            <div class="compare-card">
              <p class="compare-title">雷达图（学生 vs 岗位）</p>
              <div class="compare-placeholder">
                可接入 ECharts 等雷达图，展示四维度及细分能力对比。
              </div>
            </div>
            <div class="compare-card">
              <p class="compare-title">四维度对比（基础要求 / 职业技能 / 职业素养 / 发展潜力）</p>
              <ul class="compare-list">
                <li v-for="item in compareDimensions" :key="item.name">
                  <span class="dim-name">{{ item.name }}</span>
                  <span class="dim-score">学生：{{ item.student }} / 要求：{{ item.job }}</span>
                </li>
              </ul>
              <p class="weight-hint">综合得分已按维度权重加权计算，具备可解释性。</p>
            </div>
          </div>

          <div class="detail-analysis">
            <p class="section-subtitle">详细差距分析（示意）</p>
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
          <p v-if="!isEditing">{{ baseInfo.summary }}</p>
          <el-input
            v-else
            v-model="draft.baseInfo.summary"
            type="textarea"
            :rows="4"
            placeholder="可编辑：能力画像摘要"
          />
        </section>

        <section class="report-section">
          <h2 class="section-title">3. 职业发展路径（阶段性规划示意）</h2>
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

        <!-- 4. 个人优势与短板 -->
        <section class="report-section">
          <h2 class="section-title">4. 个人优势与短板</h2>
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

        <!-- 5. 短期成长计划（0-6 个月） -->
        <section class="report-section">
          <h2 class="section-title">5. 短期成长计划（0 ~ 6 个月）</h2>
          <p class="hint-text">
            表格中的「量化评估指标」每一项后都有「编辑」按钮，可按下面三步完成修改：
            ① 触发修改 → ② 选择 / 输入修改内容 → ③ 校验 + 确认 + 保存。
          </p>
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
                  <el-button
                    class="u-btn u-btn--text"
                    type="primary"
                    text
                    size="small"
                    :disabled="isEditing"
                    @click="openMetricEditor('short', row)"
                  >
                    编辑
                  </el-button>
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
                  <el-button
                    class="u-btn u-btn--text"
                    type="primary"
                    text
                    size="small"
                    :disabled="isEditing"
                    @click="openMetricEditor('mid', row)"
                  >
                    编辑
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="isEditing" class="plan-edit-actions">
            <el-button class="u-btn u-btn--primary u-btn--sm" size="small" @click="addPlanRow('mid')">添加一行</el-button>
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

    <!-- 量化评估指标编辑弹窗 -->
    <el-dialog
      v-model="metricDialogVisible"
      title="编辑量化评估指标"
      width="520px"
    >
      <div v-if="editingMetricRow">
        <p class="dialog-label">原指标：</p>
        <p class="orig-metric">
          {{ originalMetric }}
        </p>

        <p class="dialog-label">智能体建议（三档可选）：</p>
        <el-radio-group v-model="metricChoice" class="suggest-group">
          <el-radio label="simple">简单版本</el-radio>
          <el-radio label="standard">标准版本</el-radio>
          <el-radio label="advanced">进阶版本</el-radio>
          <el-radio label="custom">自定义</el-radio>
        </el-radio-group>

        <ul class="suggest-list">
          <li><strong>简单：</strong>{{ aiSuggestions.simple }}</li>
          <li><strong>标准：</strong>{{ aiSuggestions.standard }}</li>
          <li><strong>进阶：</strong>{{ aiSuggestions.advanced }}</li>
        </ul>

        <p class="dialog-label">自定义修改（可选）：</p>
        <el-input
          v-model="customMetric"
          type="textarea"
          :rows="3"
          placeholder="如果选择「自定义」，在这里输入新的量化指标描述…"
          @focus="metricChoice = 'custom'"
        />

        <transition name="el-fade-in">
          <div v-if="needReason" class="reason-block">
            <p class="dialog-label">
              调整幅度超出建议区间，请说明理由：
            </p>
            <el-input
              v-model="metricReason"
              type="textarea"
              :rows="2"
              placeholder="例如：已有相关经验、可投入时间更多、希望提前完成某项能力建设等…"
            />
          </div>
        </transition>

        <p class="hint-text">
          智能体会基于目标岗位、你当前基础和时间周期进行三重校验（合理性、安全性、可达成性），
          未通过会给出提示，引导你进一步修正。
        </p>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button class="u-btn u-btn--ghost" @click="metricDialogVisible = false">取 消</el-button>
          <el-button class="u-btn u-btn--primary" type="primary" @click="saveMetric">校验并保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTheme } from '../composables/useTheme'
import { ElMessage } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import AppHeader from '../components/AppHeader.vue'
import learningPathPlaceholder from '../assets/uiineed-carousel-plan.svg'

const router = useRouter()
const studentName = ref('张同学')
const { theme } = useTheme()

// 页面步骤：match（岗位匹配）/ report（职业报告）
const step = ref('match')

// 推荐岗位示例数据
const recommendedJobs = ref([
  { id: 1, name: 'Java 开发工程师', match: 85, requireMatch: 85 },
  { id: 2, name: '前端开发工程师', match: 78, requireMatch: 82 },
  { id: 3, name: '软件测试工程师', match: 72, requireMatch: 80 },
  { id: 4, name: '运维工程师', match: 65, requireMatch: 78 },
  { id: 5, name: '产品经理', match: 58, requireMatch: 80 }
])

const selectedJobId = ref(1)
const currentJob = computed(() =>
  recommendedJobs.value.find((j) => j.id === selectedJobId.value)
)

// 人岗匹配四维度：基础要求、职业技能、职业素养、发展潜力（题目要求）
const compareDimensions = ref([
  { name: '基础要求', student: '8 分', job: '8 分' },
  { name: '职业技能', student: '7 分', job: '8 分' },
  { name: '职业素养', student: '7 分', job: '8 分' },
  { name: '发展潜力', student: '8 分', job: '8 分' }
])

const gapDetails = ref([
  '专业技能：你的 Java 基础分 8 分，岗位要求 8 分，基本匹配。',
  '实践能力：你的分数 6 分 vs 岗位要求 8 分，存在 2 分差距。',
  '抗压能力：你的分数 6 分 vs 岗位要求 8 分，存在 3 分差距。'
])

const improveSuggestions = ref([
  '尽快寻找一份 Java 岗位相关的实习，以弥补实战经验不足。',
  '多参与项目开发与团队协作，积累解决真实问题的经验。'
])

const viewJobDetail = (row) => {
  selectedJobId.value = row.id
  ElMessage.success(`已切换到岗位「${row.name}」的匹配详情`)
}

// 生成报告
const generateReport = () => {
  step.value = 'report'
  ElMessage.success('已根据当前岗位生成职业发展规划报告（示意）')
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

// 量化指标编辑弹窗逻辑
const metricDialogVisible = ref(false)
const editingPhase = ref('short') // 'short' | 'mid'
const editingMetricRow = ref(null)

const originalMetric = computed(
  () => editingMetricRow.value?.metric || ''
)

const metricChoice = ref('standard')
const customMetric = ref('')
const metricReason = ref('')
const needReason = ref(false)

const aiSuggestions = ref({
  simple: '完成不少于 10 次练习题，并在课堂测验中达到及格以上。',
  standard: '完成不少于 20 次实战练习，阶段测验成绩不低于 80 分。',
  advanced:
    '独立完成进阶项目并通过代码评审，阶段测验成绩不低于 90 分，同时能输出学习总结文档。'
})

const openMetricEditor = (phase, row) => {
  editingPhase.value = phase
  editingMetricRow.value = row
  metricChoice.value = 'standard'
  customMetric.value = ''
  metricReason.value = ''
  needReason.value = false
  metricDialogVisible.value = true
}

const saveMetric = () => {
  if (!editingMetricRow.value) return

  let newMetric = ''
  if (metricChoice.value === 'simple') {
    newMetric = aiSuggestions.value.simple
  } else if (metricChoice.value === 'standard') {
    newMetric = aiSuggestions.value.standard
  } else if (metricChoice.value === 'advanced') {
    newMetric = aiSuggestions.value.advanced
  } else {
    if (!customMetric.value.trim()) {
      ElMessage.error('请在自定义输入框中填写新的量化指标。')
      return
    }
    newMetric = customMetric.value.trim()
  }

  // 简单模拟「超出调整区间」：长度比原文大 1.6 倍以上视为大幅修改
  if (
    metricChoice.value === 'custom' &&
    newMetric.length > originalMetric.value.length * 1.6
  ) {
    if (!metricReason.value.trim()) {
      needReason.value = true
      ElMessage.warning('调整幅度较大，请先补充调整理由。')
      return
    }
  }

  // 三重校验（示意）
  const lengthOk = newMetric.length >= 10
  const containsNumber = /\d/.test(newMetric)
  const containsVerb = /完成|达到|实现|通过/.test(newMetric)

  if (!lengthOk || !containsNumber || !containsVerb) {
    ElMessage.error('未通过智能体三重校验，请确保指标可量化、可操作，再试一次。')
    return
  }

  // 保存到对应计划表中
  const targetList = editingPhase.value === 'short' ? shortTermPlan : midTermPlan
  const idx = targetList.value.findIndex((r) => r === editingMetricRow.value)
  if (idx !== -1) {
    targetList.value[idx] = { ...targetList.value[idx], metric: newMetric }
  }

  metricDialogVisible.value = false
  ElMessage.success('已通过三重校验并保存新的量化评估指标（示意）。')
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
    targetJob: currentJob.value?.name || baseInfo.value.targetJob,
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
  lines.push('## 3. 职业发展路径（阶段性规划示意）')
  lines.push(payload.pathNote || '')
  lines.push('')
  lines.push('## 4. 个人优势与短板')
  lines.push('**优势**')
  for (const s of payload.baseInfo.strengths || []) lines.push(`- ${s}`)
  lines.push('')
  lines.push('**待提升点**')
  for (const w of payload.baseInfo.weaknesses || []) lines.push(`- ${w}`)
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
    body{font-family:system-ui,-apple-system,Segoe UI,Arial,sans-serif;padding:24px;color:#111827;}
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

  <h2>3. 职业发展路径（阶段性规划示意）</h2>
  <p>${esc(payload.pathNote || '')}</p>

  <h2>4. 个人优势与短板</h2>
  <h3>优势</h3>
  <ul>${li(payload.baseInfo.strengths)}</ul>
  <h3>待提升点</h3>
  <ul>${li(payload.baseInfo.weaknesses)}</ul>

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
</script>

<style scoped>
.career-report-view {
  width: 100vw;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fb;
  color: #222;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI',
    sans-serif;
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
.career-report-view.dark .dim-score {
  color: var(--dm-text-secondary);
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

.compare-list {
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: clamp(13px, 0.9vw, 15px);
}

.compare-list li + li {
  margin-top: 4px;
}

.dim-name {
  font-weight: 600;
}

.dim-score {
  margin-left: 8px;
  color: #555;
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