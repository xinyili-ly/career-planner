 <template>
  <div class="job-detail-view" :class="theme">
    <AppHeader :back-to="{ name: 'JobRequirements' }" />

    <main class="page-scroll">
      <!-- 顶部大图区域 -->
      <section class="hero">
        <div class="hero-image">
          <img
            :src="heroImageSrc"
            alt="岗位配图"
          />
        </div>
        <div class="hero-overlay">
          <h1 class="job-name">{{ displayJobName }}</h1>
          <p class="job-tag-line">
            {{ job.field }} · {{ job.company }}
          </p>
        </div>
      </section>

      <section v-if="loadingPortrait || errorPortrait || isUsingMockFallback || hasEmptyPortrait" class="section-card status-card">
        <p v-if="loadingPortrait" class="status-text">
          正在从后端加载岗位画像数据...
        </p>
        <p v-else-if="errorPortrait" class="status-text status-error">
          后端接口请求失败：{{ errorPortrait }}，当前已自动切换为本地兜底数据。
        </p>
        <p v-else-if="isUsingMockFallback" class="status-text">
          当前使用本地兜底数据展示，建议检查后端接口与网络连通性。
        </p>
        <p v-else-if="hasEmptyPortrait" class="status-text">
          当前岗位接口返回为空，已使用默认文案渲染页面。
        </p>
      </section>

      <!-- 技能要求 / 申请条件 Tab -->
      <section class="section-card">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="技能要求" name="skills">
            <div
              v-if="detailSkillHtml"
              class="rich-text"
              v-html="detailSkillHtml"
            />
            <ul v-else class="info-list">
              <li v-for="line in displaySkillBullets" :key="line">{{ line }}</li>
            </ul>
          </el-tab-pane>
          <el-tab-pane label="评价申请条件" name="conditions">
            <ul v-if="displayConditionBullets.length" class="info-list">
              <li v-for="line in displayConditionBullets" :key="line">{{ line }}</li>
            </ul>
            <div v-else-if="hasStructuredConditions && jobPortrait" class="two-column">
              <div>
                <p v-if="jobPortrait.conditions.education">
                  <strong>学历要求：</strong>{{ jobPortrait.conditions.education }}
                </p>
                <p v-if="jobPortrait.conditions.majors">
                  <strong>相关专业：</strong>{{ jobPortrait.conditions.majors }}
                </p>
                <p v-if="jobPortrait.conditions.internship">
                  <strong>实习/项目：</strong>{{ jobPortrait.conditions.internship }}
                </p>
              </div>
              <div>
                <p v-if="jobPortrait.conditions.certificates">
                  <strong>核心证书：</strong>{{ jobPortrait.conditions.certificates }}
                </p>
                <p v-if="jobPortrait.conditions.other">
                  <strong>其他说明：</strong>{{ jobPortrait.conditions.other }}
                </p>
              </div>
            </div>
            <div v-else class="two-column">
              <div>
                <p>学历要求：大专及以上（示意；接口返回字段后将自动替换）。</p>
                <p>相关专业：计算机类 / 通信类 / 电子信息等。</p>
                <p>实习或项目经验：有相关项目经历更佳。</p>
              </div>
              <div>
                <p>核心证书：可填写行业证书或资格。</p>
                <p>其他说明：如工作地点、时间安排等要求。</p>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </section>

      <!-- 岗位画像维度（题目要求：专业技能、证书、创新、学习、抗压、沟通、实习等） -->
      <section class="section-card">
        <h2 class="section-title">岗位画像维度</h2>
        <ul class="profile-dim-list" v-if="jobProfileDims.length">
          <li v-for="d in jobProfileDims" :key="d.name">
            <span class="dim-name">{{ d.name }}：</span>
            <span class="dim-desc">{{ d.desc }}</span>
          </li>
        </ul>
        <p v-else class="section-desc">暂无岗位画像维度数据。</p>
      </section>

      <!-- 垂直岗位图谱：岗位描述、晋升路径 -->
      <section class="section-card">
        <h2 class="section-title">垂直岗位图谱</h2>
        <p class="section-desc">涵盖岗位描述与晋升路径关联信息，便于了解本岗位纵向发展。</p>
        <p v-if="jobPortrait" class="section-desc">
          岗位描述：{{ jobPortrait.summary }}
        </p>
        <div class="path-block vertical-path" v-if="verticalPath.length">
          <div
            v-for="(node, i) in verticalPath"
            :key="node.title"
            class="path-node"
          >
            <div class="path-title">
              <span class="path-index">{{ i + 1 }}</span>
              <span class="path-text">{{ node.title }}</span>
            </div>
            <p class="path-desc">{{ node.focus }}</p>
          </div>
        </div>
        <p v-else class="section-desc">暂无垂直岗位图谱数据。</p>
      </section>

      <!-- 换岗路径图谱：当前岗位换岗路径与相关岗位血缘 -->
      <section class="section-card">
        <h2 class="section-title">换岗路径图谱</h2>
        <p class="section-desc">相关岗位血缘关系与转换路径，便于规划横向发展。</p>

        <div v-if="jobPortrait && transferPaths.length" class="transfer-current">
          <p class="transfer-from">从「{{ displayJobName }}」可换岗的路径示例：</p>
          <p v-if="transferUsingFallback" class="section-desc transfer-fallback-hint">
            当前岗位暂无后端返回的换岗明细，以下为通用横向发展示例，接入接口后将自动替换为真实路径。
          </p>
          <div class="transfer-path-list">
            <div v-for="p in transferPaths" :key="p.title" class="transfer-path">
              <p class="transfer-path-title">{{ p.title }}</p>
              <div class="transfer-steps">
                <span v-for="(s, i) in p.steps" :key="`${p.title}-${i}-${s}`" class="transfer-step">
                  {{ s }}<span v-if="i < p.steps.length - 1" class="transfer-arrow">→</span>
                </span>
              </div>
              <ul v-if="p.keyGaps?.length" class="transfer-gaps">
                <li v-for="g in p.keyGaps" :key="g">{{ g }}</li>
              </ul>
            </div>
          </div>

          <div v-if="relationsDisplay.length" class="bloodline">
            <p class="bloodline-title">相关岗位血缘（关联原因）：</p>
            <ul class="bloodline-list">
              <li v-for="r in relationsDisplay" :key="r.role">
                <span class="dim-name">{{ r.role }}：</span>
                <span class="dim-desc">{{ r.reason }}</span>
              </li>
            </ul>
          </div>
        </div>
        <p v-else-if="!loadingPortrait" class="section-desc">暂无换岗路径图谱数据。</p>
      </section>

      <section v-if="showPathChart" class="section-card">
        <h2 class="section-title">岗位发展关系图</h2>
        <p class="section-desc">
          基于后端 path_graph（nodes / edges）或当前换岗路径自动生成的关系图，可拖拽与缩放。
        </p>
        <JobPortraitPathChart
          :path-graph="jobPortrait?.pathGraph ?? null"
          :transfer-paths="transferPaths"
          :theme="theme"
        />
      </section>

      <!-- 学长学姐有话说（评论区简化） -->
      <section class="section-card">
        <h2 class="section-title">学长学姐有话说</h2>
        <div class="comment-list">
          <div
            v-for="(comment, index) in demoComments"
            :key="index"
            class="comment-item"
          >
            <div class="avatar"></div>
            <div class="comment-content">
              <div class="comment-header">
                <span class="author">{{ comment.author }}</span>
                <span class="time">{{ comment.time }}</span>
              </div>
              <p class="comment-text">
                {{ comment.text }}
              </p>
            </div>
          </div>
        </div>

        <div class="comment-input">
          <el-input
            v-model="newComment"
            type="textarea"
            :rows="2"
            placeholder="你可以根据真实设计图，在这里补充评论功能逻辑..."
          />
          <el-button
            type="primary"
            class="comment-btn u-btn u-btn--primary"
            @click="handleSend"
          >
            发表
          </el-button>
        </div>
      </section>

      <!-- 底部引导：探索更多岗位 -->
      <section class="page-bottom-cta">
        <p class="bottom-cta-text">想了解其他岗位的画像与换岗路径？</p>
        <router-link to="/jobs" class="bottom-cta-link">返回岗位列表，查看全部岗位 →</router-link>
      </section>

      <footer class="site-footer">
        <span>© {{ new Date().getFullYear() }} 职途智引 · AI职业规划助手</span>
      </footer>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useTheme } from '../composables/useTheme'
import AppHeader from '../components/AppHeader.vue'
import { getJobPortrait } from '../data/jobPortraits'
import { getJobDetail } from '../api/jobPortraitApi'
import { formatJobPortraitApiError } from '../api/jobPortraitErrors'
import JobPortraitPathChart from '../components/JobPortraitPathChart.vue'
import {
  loadJobListItemFromCache,
  portraitFromMergedRaw,
  unwrapData,
} from '../utils/jobPortraitNormalize'

const route = useRoute()
const { theme } = useTheme()

const defaultSkillBullets = [
  '掌握岗位相关基础理论与专业知识。',
  '具备独立分析与解决实际问题的能力。',
  '熟悉常见工具与平台，能够完成日常工作任务。',
  '具备良好的沟通协作与学习迭代能力。',
]

/** 优先使用接口 hero_image / cover_url；无则使用默认配图 */
const heroImageSrc = computed(() => {
  const url = jobPortrait.value?.heroImage?.trim()
  if (url) return url
  return '/iot-debugger.jpg'
})

function fieldFromTags(tags) {
  if (!Array.isArray(tags) || !tags.length) return '岗位画像'
  const t = tags[0]
  return String(t).replace(/\s+/g, '').slice(0, 8) || '岗位画像'
}

const job = computed(() => {
  const id = String(route.params.id || '')
  const cached = id ? loadJobListItemFromCache(id) : null
  const titleQ = route.query.title
  const name =
    typeof titleQ === 'string' && titleQ.trim()
      ? titleQ.trim()
      : normalizeText(cached?.title, '岗位详情')
  return {
    id,
    name,
    field: fieldFromTags(cached?.field_tags),
    company: normalizeText(cached?.company, '—')
  }
})

const displayJobName = computed(() => jobPortrait.value?.name || job.value.name)

const activeTab = ref('skills')
const loadingPortrait = ref(false)
const errorPortrait = ref('')
const isUsingMockFallback = ref(false)

const defaultProfileDims = [
  { name: '专业技能', desc: '掌握本岗位所需的核心技术与工具，能独立完成典型任务。' },
  { name: '证书要求', desc: '相关职业资格或行业认证优先，如无硬性要求则以项目/作品证明为主。' },
  { name: '创新能力', desc: '能提出改进方案、参与技术选型或流程优化。' },
  { name: '学习能力', desc: '快速上手新技术与业务，具备持续学习与复盘习惯。' },
  { name: '抗压能力', desc: '在截止日期与多任务下保持交付质量，遇问题能主动沟通与推进。' },
  { name: '沟通能力', desc: '与产品、测试、运营等协作顺畅，表达清晰、文档规范。' },
  { name: '实习能力', desc: '有对口实习或项目经历，能将所学应用到实际场景。' }
]

const jobPortrait = ref(null)

function normalizeText(value, fallback = '') {
  if (typeof value === 'string') return value
  if (typeof value === 'number') return String(value)
  return fallback
}

function getMockPortrait(jobName) {
  const mock = getJobPortrait(jobName)
  if (!mock) {
    return portraitFromMergedRaw({ title: jobName, name: jobName }, jobName)
  }
  return portraitFromMergedRaw({ ...mock, title: mock.name }, mock.name || jobName)
}

async function loadPortrait() {
  loadingPortrait.value = true
  errorPortrait.value = ''
  const id = String(route.params.id || '')

  if (!id) {
    errorPortrait.value = '缺少岗位 ID'
    const fallbackName =
      typeof route.query.title === 'string' && route.query.title.trim().length
        ? route.query.title.trim()
        : '岗位'
    jobPortrait.value = getMockPortrait(fallbackName)
    isUsingMockFallback.value = true
    loadingPortrait.value = false
    return
  }

  try {
    const res = await getJobDetail(id)
    const data = unwrapData(res)
    if (data && typeof data === 'object' && (data.title || data.id || data.name)) {
      const title = normalizeText(data.title || data.name, id)
      jobPortrait.value = portraitFromMergedRaw(data, title)
      isUsingMockFallback.value = false
    } else {
      throw new Error('岗位详情为空')
    }
  } catch (error) {
    errorPortrait.value = normalizeText(formatJobPortraitApiError(error), '接口请求失败')
    isUsingMockFallback.value = true
    const cached = loadJobListItemFromCache(id)
    jobPortrait.value = getMockPortrait(normalizeText(cached?.title, job.value.name))
  } finally {
    loadingPortrait.value = false
  }
}

onMounted(() => {
  loadPortrait()
})

watch(
  () => [route.params.id, route.query.title],
  () => {
    loadPortrait()
  }
)

// 岗位画像维度：专业技能、证书要求、创新能力、学习能力、抗压能力、沟通能力、实习能力
const jobProfileDims = computed(() => {
  if (loadingPortrait.value || !jobPortrait.value) return []
  const dims = jobPortrait.value.profileDims
  return dims && dims.length ? dims : defaultProfileDims
})

// 垂直岗位图谱（示例：以当前岗位为起点的晋升路径）
const verticalPath = computed(() => {
  if (loadingPortrait.value) return []
  if (jobPortrait.value?.vertical?.length) return jobPortrait.value.vertical
  if (!jobPortrait.value) return []
  return [
    { title: `${job.value.name}（当前）`, focus: '掌握岗位核心技能并能独立交付。' },
    { title: `中级${job.value.name}（1～3 年）`, focus: '能独立负责模块/项目并持续优化。' },
    { title: `高级${job.value.name} / 技术主管（3～5 年）`, focus: '能主导复杂问题与协作，推动规范与体系建设。' },
    { title: `专家 / 架构师 或 管理岗（5 年+）`, focus: '负责方向规划、平台化与组织级效率提升。' }
  ]
})

/** 后端/本地 mock 有 transfers 时用真实数据，否则给通用横向发展示例（与垂直图谱兜底一致） */
const transferPaths = computed(() => {
  if (loadingPortrait.value) return []
  const raw = jobPortrait.value?.transfers
  if (Array.isArray(raw) && raw.length) return raw
  if (!jobPortrait.value) return []
  const name = displayJobName.value || job.value.name
  return [
    {
      title: `相近技能线：${name} → 同领域相邻岗位 → 高级 / 专家`,
      steps: [name, '同领域相关岗位（技术面延伸）', '高级专家 / 技术负责人'],
      keyGaps: ['补齐相邻方向的核心技能栈', '参与更大范围交付或体系化建设', '跨团队协作与影响力']
    },
    {
      title: `横向扩展线：${name} → 产品 / 交付 / 售前等协作岗`,
      steps: [name, '协作型岗位（产品、交付、售前等）', '复合型负责人'],
      keyGaps: ['业务理解与表达', '需求拆解与推进', '资源协调与沟通闭环']
    }
  ]
})

const transferUsingFallback = computed(() => {
  if (loadingPortrait.value || !jobPortrait.value) return false
  const raw = jobPortrait.value.transfers
  return !Array.isArray(raw) || raw.length === 0
})

const relationsDisplay = computed(() => {
  if (loadingPortrait.value) return []
  const raw = jobPortrait.value?.relations
  if (Array.isArray(raw) && raw.length) return raw
  if (!jobPortrait.value) return []
  return [
    {
      role: '同领域相邻岗位',
      reason: '技能与工具链相近，换岗时可将现有经验平移，主要补齐业务场景差异。'
    },
    {
      role: '上下游协作岗位',
      reason: '在工作流中与当前岗位衔接紧密，换岗时可利用已熟悉的流程与客户/项目语境。'
    }
  ]
})

const detailSkillHtml = computed(() => {
  if (loadingPortrait.value) return ''
  const h = jobPortrait.value?.skillHtml
  return typeof h === 'string' && h.trim() ? h.trim() : ''
})

const displaySkillBullets = computed(() => {
  if (loadingPortrait.value) return defaultSkillBullets
  const b = jobPortrait.value?.skillBullets
  if (Array.isArray(b) && b.length) return b
  return defaultSkillBullets
})

const displayConditionBullets = computed(() => {
  if (loadingPortrait.value) return []
  const b = jobPortrait.value?.conditionBullets
  return Array.isArray(b) ? b : []
})

const hasStructuredConditions = computed(() => {
  if (loadingPortrait.value || !jobPortrait.value?.conditions) return false
  const c = jobPortrait.value.conditions
  return !!(c.education || c.majors || c.internship || c.certificates || c.other)
})

const showPathChart = computed(() => !loadingPortrait.value && !!jobPortrait.value)

const hasEmptyPortrait = computed(() => {
  if (loadingPortrait.value) return false
  if (!jobPortrait.value) return true
  return (
    !(jobPortrait.value?.summary || '').trim() &&
    !jobProfileDims.value.length &&
    !verticalPath.value.length &&
    !(jobPortrait.value?.transfers || []).length
  )
})

const demoComments = ref([
  {
    author: '学长 A',
    time: '刚刚',
    text: '这里可以放你根据第二张设计图整理的真实心得内容。'
  },
  {
    author: '学姐 B',
    time: '1 小时前',
    text: '比如岗位的实际工作节奏、学习建议、证书推荐等等。'
  }
])

const newComment = ref('')

const handleSend = () => {
  if (!newComment.value.trim()) return
  demoComments.value.unshift({
    author: '你',
    time: '刚刚',
    text: newComment.value.trim()
  })
  newComment.value = ''
}

</script>

<style scoped>
.job-detail-view {
  --u-border-radius: 24px;

  /* 柔和糖果色（低饱和） */
  --u-color-cyan-soft: #e0f7f4;
  --u-color-pink-soft: #fff0f6;
  --u-color-yellow-soft: #fff9db;
  --u-color-mint-soft: #ecfdf5;

  --u-black: #33322e;
  --u-border: 2px solid var(--u-black);

  min-height: 100vh;
  background: #f8f9fa;
  color: var(--u-black);
  display: flex;
  flex-direction: column;
}

.job-detail-view.dark {
  background: var(--dm-bg);
  color: var(--dm-text);
}

.job-detail-view.dark .header {
  background: var(--dm-header-bg);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--dm-border);
  color: var(--dm-text);
}

.job-detail-view.dark .nav-item {
  color: var(--dm-text);
}

.header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 2vw;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(12px);
  border-bottom: var(--u-border);
  color: var(--u-black);
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
  color: var(--u-black);
  text-decoration: none;
  position: relative;
  padding-bottom: 4px;
}

.nav-item::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  height: 2px;
  width: 0;
  background: var(--u-black);
  transition: width 0.2s ease;
}

.nav-item:hover::after {
  width: 100%;
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
  background: rgba(255, 255, 255, 0.75);
  border: var(--u-border);
  box-shadow: 2px 2px 0px var(--u-black);
  padding: 4px;
  font-size: 12px;
}

.job-detail-view.dark .theme-toggle {
  background: var(--dm-surface);
}

.theme-option {
  padding: 4px 12px;
  border-radius: 999px;
  cursor: pointer;
  color: #666;
}

.theme-option.active {
  background: var(--u-bg-submit);
  color: var(--u-black);
}

.job-detail-view.dark .theme-option {
  color: var(--dm-text-secondary);
}

.job-detail-view.dark .theme-option.active {
  background: var(--dm-surface-elevated);
  color: var(--dm-text);
}

.nav-back {
  font-size: clamp(15px, 0.95vw, 17px);
}

.page-scroll {
  flex: 1;
  padding: 0 6vw 48px 56px;
}

.page-bottom-cta {
  margin-top: 40px;
  padding: 28px 0 20px;
  text-align: center;
  border-top: var(--u-border);
}

.job-detail-view.dark .page-bottom-cta {
  border-top-color: var(--dm-border);
}

.bottom-cta-text {
  font-size: clamp(16px, 1.05vw, 18px);
  color: rgba(51, 50, 46, 0.78);
  margin-bottom: 12px;
}

.job-detail-view.dark .bottom-cta-text {
  color: var(--dm-text-secondary);
}

.bottom-cta-link {
  display: inline-block;
  font-size: clamp(15px, 1vw, 17px);
  font-weight: 800;
  color: #fff;
  background: var(--u-black);
  border: var(--u-border);
  box-shadow: 4px 4px 0px rgba(0, 0, 0, 0.2);
  padding: 12px 24px;
  border-radius: 12px;
  text-decoration: none;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.job-detail-view.dark .bottom-cta-link {
  color: #fff;
  background: var(--dm-surface-elevated);
  border-color: var(--dm-border);
}

.bottom-cta-link:hover {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0px rgba(0, 0, 0, 0.3);
}

.site-footer {
  margin-top: 80px;
  padding: 40px 0;
  border-top: none;
  background: var(--u-black);
  color: #fff;
  font-size: clamp(14px, 0.9vw, 16px);
  text-align: center;
  width: 100%;
}

.job-detail-view.dark .site-footer {
  background: #0f1115;
  color: var(--dm-text-muted);
}

.hero {
  position: relative;
}

.hero-image img {
  width: 100%;
  height: auto;
  display: block;
  vertical-align: middle;
  background: rgba(255, 255, 255, 0.8);
}

.hero-overlay {
  position: absolute;
  left: 6vw;
  bottom: 24px;
  color: #fff;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.4);
}

.job-name {
  font-size: clamp(28px, 2.4vw, 38px);
  margin-bottom: 4px;
}

.job-tag-line {
  font-size: clamp(17px, 1.1vw, 20px);
}

.section-card {
  margin-top: 32px;
  border-radius: var(--u-border-radius);
  padding: 30px;
  border: var(--u-border);
  box-shadow: 8px 8px 0px var(--u-black);
  transition: transform 0.2s ease;
}

/* 首个为 hero，其后 section-card 按 4 色循环（与状态条等共同计数） */
.page-scroll > section.section-card:nth-child(4n + 2) {
  background-color: var(--u-color-cyan-soft);
}

.page-scroll > section.section-card:nth-child(4n + 3) {
  background-color: var(--u-color-pink-soft);
}

.page-scroll > section.section-card:nth-child(4n + 4) {
  background-color: var(--u-color-yellow-soft);
}

.page-scroll > section.section-card:nth-child(4n + 5) {
  background-color: var(--u-color-mint-soft);
}

.status-card {
  margin-top: 16px;
}

.status-text {
  margin: 0;
  font-size: clamp(15px, 1vw, 17px);
  line-height: 1.6;
  color: rgba(51, 50, 46, 0.82);
}

.status-error {
  color: #b42318;
}

.job-detail-view.dark .section-card {
  box-shadow: 8px 8px 0px rgba(0, 0, 0, 0.35);
  border: 2px solid var(--dm-border);
}

.job-detail-view.dark .page-scroll > section.section-card:nth-child(4n + 2) {
  background-color: rgba(224, 247, 244, 0.12);
}

.job-detail-view.dark .page-scroll > section.section-card:nth-child(4n + 3) {
  background-color: rgba(255, 240, 246, 0.1);
}

.job-detail-view.dark .page-scroll > section.section-card:nth-child(4n + 4) {
  background-color: rgba(255, 249, 219, 0.08);
}

.job-detail-view.dark .page-scroll > section.section-card:nth-child(4n + 5) {
  background-color: rgba(236, 253, 245, 0.14);
}

.job-detail-view.dark .section-title {
  color: var(--dm-text);
}

:deep(.el-tabs__item.is-active) {
  color: var(--u-black) !important;
  font-weight: 900;
}

:deep(.el-tabs__active-bar) {
  background-color: var(--u-black) !important;
  height: 3px;
}

.job-detail-view.dark :deep(.el-tabs__item.is-active) {
  color: var(--dm-text) !important;
}

.job-detail-view.dark :deep(.el-tabs__active-bar) {
  background-color: var(--dm-accent) !important;
}

.job-detail-view.dark .section-desc {
  color: var(--dm-text-secondary);
}

.job-detail-view.dark .dim-desc {
  color: var(--dm-text-secondary);
}

.job-detail-view.dark .path-node {
  background: var(--dm-surface-card);
  border: 2px solid var(--dm-border);
  box-shadow: 4px 4px 0px rgba(0, 0, 0, 0.35);
  color: var(--dm-text);
}

.job-detail-view.dark .path-index {
  background: var(--dm-surface-card);
  border: 1.5px solid var(--dm-border);
  box-shadow: 2px 2px 0px rgba(0, 0, 0, 0.35);
  color: var(--dm-text);
}

.job-detail-view.dark .hero-image img {
  background: var(--dm-surface);
}

.job-detail-view.dark .avatar {
  background: var(--dm-surface-elevated);
}

.job-detail-view.dark .comment-header {
  color: var(--dm-text-secondary);
}

.section-title {
  font-size: clamp(20px, 1.35vw, 24px);
  font-weight: 900;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--u-black);
}

.section-title::before {
  content: '';
  width: 8px;
  height: 24px;
  flex-shrink: 0;
  background: var(--u-black);
  border-radius: 4px;
}

.job-detail-view.dark .section-title::before {
  background: var(--dm-accent);
}

.section-desc {
  font-size: clamp(16px, 1.1vw, 18px);
  color: #555;
  margin-bottom: 12px;
  line-height: 1.5;
}

.rich-text {
  font-size: clamp(16px, 1.1vw, 18px);
  line-height: 1.55;
  color: inherit;
}

.rich-text :deep(p) {
  margin: 0 0 10px;
}

.rich-text :deep(ul) {
  margin: 0 0 10px;
  padding-left: 1.25em;
}

.info-list {
  padding-left: 22px;
  margin: 0;
}

.info-list li {
  margin-bottom: 8px;
  font-size: clamp(16px, 1.1vw, 18px);
}

.two-column {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px 32px;
  font-size: clamp(16px, 1.1vw, 18px);
}

.profile-dim-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.profile-dim-list li {
  margin-bottom: 10px;
  font-size: clamp(16px, 1.1vw, 18px);
}

.dim-name {
  font-weight: 600;
  margin-right: 4px;
}

.dim-desc {
  color: rgba(51, 50, 46, 0.78);
}

.path-block.vertical-path {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.path-node {
  padding: 10px 14px;
  background: #ffffff;
  border-radius: 10px;
  font-size: clamp(16px, 1.1vw, 18px);
  border: var(--u-border);
  box-shadow: 4px 4px 0px var(--u-black);
}

.path-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.path-index {
  width: 26px;
  height: 26px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #ffffff;
  border: 1.5px solid var(--u-black);
  box-shadow: 2px 2px 0px var(--u-black);
  font-weight: 900;
  flex: 0 0 auto;
}

.path-text {
  font-weight: 700;
}

.path-desc {
  margin: 8px 0 0;
  font-size: clamp(15px, 1vw, 17px);
  color: rgba(51, 50, 46, 0.78);
  line-height: 1.5;
}

.job-detail-view.dark .path-desc {
  color: var(--dm-text-secondary);
}

.transfer-current {
  margin-bottom: 14px;
}

.transfer-path-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
  margin: 10px 0 14px;
}

.transfer-path {
  background: #ffffff;
  border-radius: 12px;
  padding: 12px 14px;
  border: 2px solid var(--u-black);
  box-shadow: 4px 4px 0px rgba(0, 0, 0, 0.15);
}

.job-detail-view.dark .transfer-path {
  background: var(--dm-surface-card);
  border: 2px solid var(--dm-border);
  box-shadow: 4px 4px 0px rgba(0, 0, 0, 0.35);
}

.transfer-path-title {
  font-weight: 700;
  margin: 0 0 8px;
  font-size: clamp(15px, 1vw, 17px);
}

.transfer-steps {
  font-size: clamp(15px, 1vw, 17px);
  margin-bottom: 8px;
  line-height: 1.6;
}

.transfer-step {
  white-space: nowrap;
}

.transfer-arrow {
  margin: 0 6px;
  color: rgba(51, 50, 46, 0.55);
}

.job-detail-view.dark .transfer-arrow {
  color: var(--dm-text-muted);
}

.transfer-gaps {
  padding-left: 18px;
  margin: 0;
  font-size: clamp(14px, 0.95vw, 16px);
  color: rgba(51, 50, 46, 0.78);
}

.job-detail-view.dark .transfer-gaps {
  color: var(--dm-text-secondary);
}

.bloodline {
  margin-top: 6px;
}

.bloodline-title {
  font-weight: 700;
  margin: 10px 0 8px;
}

.bloodline-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.bloodline-list li {
  margin-bottom: 8px;
  font-size: clamp(15px, 1vw, 17px);
}

.transfer-from {
  font-weight: 600;
  font-size: clamp(16px, 1.1vw, 18px);
  margin-bottom: 8px;
}

.transfer-fallback-hint {
  font-size: clamp(13px, 0.9vw, 15px);
  color: #666;
  margin: 0 0 10px;
}

.job-detail-view.dark .transfer-fallback-hint {
  color: var(--dm-text-secondary);
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 12px;
}

.comment-item {
  display: flex;
  gap: 10px;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  background: var(--u-bg-submit);
  border: var(--u-border);
  box-shadow: 2px 2px 0px var(--u-black);
}

.comment-content {
  flex: 1;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  font-size: clamp(15px, 0.95vw, 17px);
  margin-bottom: 2px;
}

.comment-text {
  font-size: clamp(16px, 1.1vw, 18px);
}

.comment-input {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  margin-top: 8px;
}

.comment-btn {
  white-space: nowrap;
}

.job-detail-view:not(.dark) .comment-btn {
  background: var(--u-bg-submit);
  border: var(--u-border);
  box-shadow: var(--u-box-shadow);
  color: var(--u-black);
}

@media (max-width: 900px) {
  .nav {
    display: none;
  }

  .page-scroll {
    padding-inline: 16px;
  }

  .hero-overlay {
    left: 16px;
    bottom: 16px;
  }
}
</style>