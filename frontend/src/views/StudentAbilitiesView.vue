<template>
  <div class="abilities-view" :class="theme">
    <AppHeader />

    <main class="page-scroll">
      <!-- 步骤一：选择入口（上传 or AI 对话） -->
      <section v-if="step === 'entry'" class="panel entry-panel">
        <div class="panel-header">
          <h1 class="page-title">欢迎来到简历智评中心</h1>
          <p class="page-intro">
            基于大语言模型深度理解你的职业轨迹。无论是静态文档还是实时对话，系统都将通过<strong>7 大维度</strong>精准萃取你的职业基因，量化生成个人就业能力评分，为后续的人岗精准匹配与生涯进化报告夯实底层数据。
          </p>
        </div>

        <div class="entry-cards">
          <button type="button" class="entry-card entry-card--upload" @click="step = 'upload'">
            <div class="entry-card-icon">📄</div>
            <h3 class="entry-card-title">上传解析简历</h3>
            <p class="entry-card-desc">
              已有简历文件？点击上传，AI 将秒级实现非结构化文本的深度语义拆解，将你的过往经历转化为标准化的能力坐标与竞争力评分，让潜能即刻可见。
            </p>
            <span class="entry-card-link">去上传 →</span>
          </button>
          <button type="button" class="entry-card entry-card--chat" @click="goToChat">
            <div class="entry-card-icon">💬</div>
            <h3 class="entry-card-title">AI 对话获取</h3>
            <p class="entry-card-desc">
              暂无完整简历？通过与 AI 进行多轮沉浸式沟通，逐步梳理并补全你的实战细节。由大模型协助你整理出颗粒度更细、更具说服力的能力画像。
            </p>
            <span class="entry-card-link">开始对话 →</span>
          </button>
        </div>

        <section class="trust-panel trust-panel--entry">
          <h3 class="trust-title">专业底座 · 深度解码你的职场基因</h3>
          <div class="trust-grid">
            <div
              class="trust-item"
              v-for="(item, index) in trustPoints"
              :key="item.title"
              :class="`trust-item--${index}`"
            >
              <div class="trust-icon" aria-hidden="true">
                {{ item.icon ?? '📌' }}
              </div>
              <div>
                <p class="trust-item-title">{{ item.title }}</p>
                <p class="trust-item-desc">{{ item.desc }}</p>
              </div>
            </div>
          </div>
        </section>

      </section>

      <!-- 上传解析简历：仅上传相关 -->
      <section v-else-if="step === 'upload'" class="panel upload-panel">
        <div class="upload-header">
          <h1 class="page-title upload-page-title">上传解析简历</h1>
          <el-button class="step-back u-btn u-btn--ghost" @click="step = 'entry'">返回</el-button>
        </div>
        <p class="upload-intro">
          上传一份你已有的简历（PDF 或 Word），系统将基于大模型对内容进行多维度解析：
          从专业技能、证书、创新能力、学习与抗压能力、沟通与实习经历等维度生成你的就业能力画像，
          并给出完整度与竞争力评分，为后续岗位匹配与职业规划报告提供依据。
        </p>

        <div class="upload-visual">
          <span class="upload-visual-item">📄 文档解析</span>
          <span class="upload-visual-item">📊 多维画像</span>
          <span class="upload-visual-item">⭐ 竞争力评分</span>
        </div>

        <div class="upload-area-wrap">
          <el-upload
            class="upload-area"
            drag
            :before-upload="handleBeforeUpload"
            :show-file-list="false"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将简历拖到此处，或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 PDF / DOC / DOCX，单文件不超过 5MB。上传后将自动进入解析流程。
              </div>
            </template>
          </el-upload>
        </div>

        <section class="trust-panel trust-panel--upload-explain">
          <h3 class="trust-title">解析说明</h3>
          <ul class="upload-tips">
            <li>解析结果包含专业技能、证书、创新能力、学习能力、抗压能力、沟通能力、实习能力等维度。</li>
            <li>完整度与竞争力评分将用于人岗匹配与生涯报告生成，数据仅用于本地分析。</li>
          </ul>
        </section>
      </section>

      <!-- AI 对话获取：仅对话相关 -->
      <section v-else-if="step === 'chat'" class="panel chat-panel">
        <header class="chat-header">
          <div class="chat-header-top">
            <h1 class="page-title chat-page-title">AI 对话引导 · 简历录入</h1>
            <el-button class="step-back u-btn u-btn--ghost" @click="step = 'entry'">返回</el-button>
          </div>
          <p class="chat-intro">
            通过多轮对话，我们会逐步收集你的教育背景、项目经历、技能与意向，并自动整理成能力画像。
            请按助手提示依次回答即可，完成后可一键生成学生就业能力画像。
          </p>
          <div class="chat-visual">
            <span class="chat-visual-item">🎓 教育</span>
            <span class="chat-visual-item">📋 经历</span>
            <span class="chat-visual-item">💡 技能与意向</span>
          </div>
        </header>

        <div class="chat-window">
          <div
            v-for="(msg, idx) in chatMessages"
            :key="`${msg.role}-${idx}`"
            class="chat-message"
            :class="msg.role === 'bot' ? 'bot' : 'user'"
          >
            <div class="avatar">{{ msg.role === 'bot' ? '🤖' : '👤' }}</div>
            <div class="bubble">{{ msg.text }}</div>
          </div>

          <div v-if="chatLoading" class="chat-placeholder">
            AI 正在思考中...
          </div>
          <div v-else-if="!chatMessages.length" class="chat-placeholder">
            暂无对话内容，点击下方发送后将开始问答。
          </div>
        </div>

        <div class="chat-input-bar">
          <el-input
            v-model="chatInput"
            placeholder="请输入你的回答"
            :disabled="chatLoading || chatCompleted"
            @keyup.enter="sendChat"
          />
          <el-button
            class="u-btn u-btn--primary"
            type="primary"
            :loading="chatLoading"
            :disabled="chatCompleted"
            @click="sendChat"
          >
            发送
          </el-button>
        </div>

        <div class="chat-footer">
          <div class="progress-wrapper">
            <span>进度条</span>
            <el-progress :percentage="progress" :stroke-width="12" />
            <span class="progress-text">
              {{ chatCompleted ? '问答已完成，可生成画像' : `${progress}%（AI 问答进行中）` }}
            </span>
          </div>
          <el-button
            class="u-btn u-btn--success u-btn--lg"
            type="success"
            :disabled="!chatCompleted || chatLoading"
            @click="finishChat"
          >
            收集完成，开始构建学生能力画像
          </el-button>
        </div>

      </section>

      <!-- 步骤三：学生就业能力画像（对应第三张图） -->
      <section v-else-if="step === 'result'" class="panel result-panel">
        <header class="result-header">
          <div class="result-header-left">
            <h1 class="page-title result-page-title">学生就业能力画像</h1>
            <span class="tag">分析完成</span>
          </div>
          <el-button class="step-back u-btn u-btn--ghost" @click="step = 'entry'">返回</el-button>
        </header>

        <div class="result-grid">
          <aside class="result-left">
            <div class="info-card">
              <p class="info-title">个人信息栏</p>
              <div class="info-stack">
                <p class="info-line">姓名：{{ profile.name }}</p>
                <p class="info-line">学校：{{ profile.school }}</p>
                <p class="info-line">专业：{{ profile.major }}</p>
                <p class="info-line">
                  简历完整度：{{ profile.cvCompletion }}%【{{ profile.cvLabel }}】
                </p>
              </div>
            </div>

            <div class="radar-card">
              <p class="radar-title">雷达图（七维度）</p>
              <div class="radar-chart" role="img" aria-label="个人能力七维雷达图">
                <div
                  ref="abilityRadarChartRef"
                  class="radar-echart abilities-radar-echart"
                />
              </div>
            </div>
          </aside>

          <section class="result-right">
            <div class="score-card">
              <p class="score-label">综合能力指数</p>
              <p class="score-number">{{ profile.score }}</p>
              <p class="score-sub">
                综合得分 · 竞争力相对位次约 {{ profile.rank }}%
              </p>
              <el-progress :percentage="profile.rank" :stroke-width="10" />
            </div>

            <div class="ability-card">
              <p class="ability-title">能力维度详情</p>
              <div
                v-for="ability in abilities"
                :key="ability.name"
                class="ability-item"
              >
                <div class="ability-header">
                  <span class="ability-name">{{ ability.name }}</span>
                  <span class="ability-score">{{ ability.score }}分</span>
                </div>
                <el-progress
                  :percentage="scoreToPercentage(ability.score)"
                  :stroke-width="10"
                  :show-text="false"
                  color="#8cd4cb"
                  class="ability-progress"
                />
                <p class="ability-desc">{{ ability.desc }}</p>
              </div>
            </div>

            <div class="suggest-card">
              <p class="suggest-title">待提升建议</p>
              <ul>
                <li v-for="(item, index) in suggestions" :key="index">
                  {{ item }}
                </li>
              </ul>
            </div>

            <div class="result-actions">
              <el-button class="u-btn u-btn--primary u-btn--lg" type="primary" @click="goToMatch">
                🔍 查看匹配岗位
              </el-button>
            </div>
          </section>
        </div>
      </section>

      <!-- 步骤四：岗位匹配与职业探索（原 职业生涯发展页中的人岗匹配部分） -->
      <section v-else-if="step === 'match'" class="panel match-panel">
        <header class="panel-header match-header">
          <div>
            <h1 class="page-title match-page-title">岗位匹配与职业探索</h1>
            <p class="student-tag">【当前学生】{{ studentName }}</p>
          </div>
          <el-button class="step-back u-btn u-btn--ghost" @click="step = 'result'">返回</el-button>
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

          <el-collapse v-model="otherJobsExpanded" class="other-jobs-collapse">
            <el-collapse-item name="other" title="其他岗位（展开查看）">
              <el-table
                :data="otherJobs"
                border
                stripe
                class="job-table other-job-table"
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
            </el-collapse-item>
          </el-collapse>
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
          <div class="match-analysis-block">
            <div v-if="matchAnalysisDetailLoading" class="ai-thinking-loader" role="status" aria-live="polite">
              <div class="ai-thinking-loader__head">
                <span class="ai-thinking-loader__dot" />
                <span class="ai-thinking-loader__title">{{ currentAiThinkingText }}</span>
              </div>
              <el-skeleton animated :throttle="120">
                <template #template>
                  <div class="ai-thinking-loader__skeleton">
                    <el-skeleton-item variant="p" style="width: 68%; height: 18px;" />
                    <el-skeleton-item variant="rect" style="width: 100%; height: 220px; margin-top: 14px;" />
                    <el-skeleton-item variant="p" style="width: 92%; margin-top: 14px;" />
                    <el-skeleton-item variant="p" style="width: 86%; margin-top: 10px;" />
                    <el-skeleton-item variant="p" style="width: 90%; margin-top: 10px;" />
                    <el-skeleton-item variant="rect" style="width: 100%; height: 146px; margin-top: 18px;" />
                  </div>
                </template>
              </el-skeleton>
            </div>
            <template v-else>
              <div class="compare-grid">
                <div class="compare-card compare-card--radar">
                  <p class="compare-title">雷达图（学生 vs 岗位）</p>
                  <div
                    class="compare-radar-chart"
                    role="img"
                    aria-label="学生与岗位四维度雷达对比"
                  >
                    <div
                      ref="matchCompareRadarRef"
                      class="compare-radar-echart"
                    />
                  </div>
                </div>
                <div class="compare-card">
                  <p class="compare-title">四维度对比（基础要求 / 职业技能 / 职业素养 / 发展潜力）</p>
                  <ul class="compare-list">
                    <li v-for="item in compareDimensionsWithRows" :key="item.name" class="compare-list-item">
                      <div class="dim-row-head">
                        <span class="dim-name">{{ item.name }}</span>
                        <span class="dim-student">学生：<strong>{{ item.student }}</strong></span>
                      </div>
                      <div class="dim-requirement">
                        <span class="dim-requirement-label">岗位要求</span>
                        <div v-if="item.requirementRows.length" class="dim-requirement-text-list">
                          <div
                            v-for="row in item.requirementRows"
                            :key="item.name + '-req-' + row.order"
                            class="analysis-point analysis-point--compact"
                          >
                            <p class="analysis-point-text">{{ row.text }}</p>
                          </div>
                        </div>
                        <p v-else class="dim-requirement-text dim-requirement-text--empty">—</p>
                      </div>
                    </li>
                  </ul>
                  <p class="weight-hint">
                    学生列为能力得分示意或与接口一致；岗位要求为当前岗位在该维度的具体说明（来自岗位画像或匹配报告，缺失时显示通用描述）。
                  </p>
                </div>
              </div>

              <div class="detail-analysis">
                <p class="section-subtitle">详细差距分析</p>
                <div class="analysis-point-list" role="list">
                  <div
                    v-for="row in gapAnalysisFormatted"
                    :key="'gap-' + row.order"
                    class="analysis-point"
                    role="listitem"
                  >
                    <el-tag type="primary" effect="plain" round size="small" class="analysis-point-tag">
                      {{ row.order }}
                    </el-tag>
                    <p class="analysis-point-text">{{ row.text }}</p>
                  </div>
                </div>
                <p v-if="!gapAnalysisFormatted.length" class="analysis-empty" aria-hidden="true">—</p>

                <p class="section-subtitle">提升建议（示意）</p>
                <div class="analysis-point-list" role="list">
                  <div
                    v-for="row in improveSuggestionFormatted"
                    :key="'sug-' + row.order"
                    class="analysis-point"
                    role="listitem"
                  >
                    <el-tag type="primary" effect="plain" round size="small" class="analysis-point-tag">
                      {{ row.order }}
                    </el-tag>
                    <p class="analysis-point-text">{{ row.text }}</p>
                  </div>
                </div>
                <p v-if="!improveSuggestionFormatted.length" class="analysis-empty" aria-hidden="true">—</p>
              </div>
            </template>
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

      <!-- 步骤五：职业发展规划报告（原 职业生涯发展页中的报告部分） -->
      <section v-else class="panel report-panel">
        <!-- 报告头部 -->
        <header class="report-header">
          <div>
            <h1 class="page-title report-page-title">职业发展规划报告</h1>
            <p class="report-subtitle">
              目标岗位：{{ currentJob?.name || baseInfo.targetJob }}
              · 生成时间：{{ reportDate }}
            </p>
          </div>
          <div class="header-actions">
            <el-button class="u-btn u-btn--ghost" @click="step = 'match'">返回</el-button>
            <el-button class="u-btn u-btn--ghost" @click="handleEditReport">编辑报告</el-button>
            <el-button class="u-btn u-btn--ghost" @click="handlePolish">智能润色</el-button>
            <el-dropdown @command="exportReport">
              <el-button class="u-btn u-btn--primary" type="primary">
                导出报告
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="markdown">Markdown</el-dropdown-item>
                  <el-dropdown-item command="pdf">PDF（占位）</el-dropdown-item>
                  <el-dropdown-item command="word">Word（占位）</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </header>

        <!-- 报告内容分段 -->
        <section class="report-section">
          <h2 class="section-title">1. 基本信息与目标岗位</h2>
          <p>学生姓名：{{ studentName }} · 专业：{{ baseInfo.major }}</p>
          <p>目标岗位：{{ currentJob?.name || baseInfo.targetJob }}</p>
        </section>

        <section class="report-section">
          <h2 class="section-title">2. 学生当前能力画像摘要</h2>
          <div class="summary-lines">
            <p
              v-for="(line, idx) in summaryLines"
              :key="`summary-line-${idx}`"
              class="summary-line"
            >
              {{ line }}
            </p>
          </div>
        </section>

        <section class="report-section">
          <h2 class="section-title">3. 个人优势与短板</h2>
          <div class="two-column">
            <div>
              <h3 class="subheading">优势</h3>
              <ul v-if="baseInfo.strengths.length">
                <li v-for="(a, index) in baseInfo.strengths" :key="index">
                  {{ a }}
                </li>
              </ul>
              <p v-else class="empty-text">接口未返回优势信息。</p>
            </div>
            <div>
              <h3 class="subheading">待提升点</h3>
              <ul v-if="baseInfo.weaknesses.length">
                <li v-for="(w, index) in baseInfo.weaknesses" :key="index">
                  {{ w }}
                </li>
              </ul>
              <p v-else class="empty-text">接口未返回待提升点信息。</p>
            </div>
          </div>
        </section>

        <section class="report-section">
          <h2 class="section-title">4. 职业发展路径（阶段性规划示意）</h2>
          <p class="hint-text">以下内容优先展示接口返回的职业路径说明与路线图。</p>
          <figure v-if="learningPathImage" class="path-figure">
            <img class="path-img" :src="learningPathImage" alt="阶段性成长路径图" />
            <figcaption class="path-caption">{{ learningPathText }}</figcaption>
          </figure>
          <template v-else>
            <p class="path-text">{{ learningPathText }}</p>
            <div class="path-placeholder">
              <span>接口暂未返回路径图片，当前先展示文字版路径说明。</span>
            </div>
          </template>
        </section>

        <!-- 5. 短期成长计划（0-6 个月） -->
        <section class="report-section">
          <h2 class="section-title">5. 短期成长计划（0 ~ 6 个月）</h2>
          <el-table
            :data="shortTermPlan"
            border
            class="plan-table"
          >
            <el-table-column prop="phase" label="阶段" width="120" />
            <el-table-column prop="time" label="时间节点" width="160" />
            <el-table-column prop="direction" label="核心提升方向" min-width="180" />
            <el-table-column prop="path" label="具体学习路径" min-width="220" />
            <el-table-column prop="practice" label="具体实践安排" min-width="180" />
            <el-table-column label="量化评估指标" min-width="210">
              <template #default="{ row }">
                <div class="metric-cell">
                  <span class="metric-text">{{ row.metric }}</span>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </section>

        <!-- 6. 中期成长计划（6-18 个月） -->
        <section class="report-section">
          <h2 class="section-title">6. 中期成长计划（6 ~ 18 个月）</h2>
          <el-table
            :data="midTermPlan"
            border
            class="plan-table"
          >
            <el-table-column prop="phase" label="阶段" width="120" />
            <el-table-column prop="time" label="时间节点" width="160" />
            <el-table-column prop="direction" label="核心提升方向" min-width="180" />
            <el-table-column prop="path" label="具体学习路径" min-width="220" />
            <el-table-column prop="practice" label="具体实践安排" min-width="180" />
            <el-table-column label="量化评估指标" min-width="210">
              <template #default="{ row }">
                <div class="metric-cell">
                  <span class="metric-text">{{ row.metric }}</span>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </section>

        <!-- 7. 阶段性达成标准与评估 -->
        <section class="report-section">
          <h2 class="section-title">7. 阶段性达成标准与评估</h2>
          <p class="multi-line-text">{{ evaluationSummary }}</p>
        </section>

        <div class="report-bottom-actions">
          <el-button class="u-btn u-btn--primary u-btn--lg" type="primary" size="large" @click="goGenerateTrainingPlan">
            生成能力培训计划
          </el-button>
        </div>
      </section>

      <!-- 简历智评中心页面底部说明区：三列布局，无细线框 -->
      <section class="resume-bottom-explain" aria-label="简历智评中心底部说明区">
        <div class="resume-bottom-cols">
          <div class="resume-bottom-col">
            <h3 class="resume-bottom-col-title">
              <span class="resume-bottom-col-icon" aria-hidden="true">●</span>
              能力维度说明
            </h3>
            <p class="resume-bottom-col-text">
              本中心从专业技能、证书资质、创新能力、学习能力、抗压能力、沟通能力、实习经历等七个维度对简历进行解析，
              并综合生成完整度与竞争力评分。完成后可前往「职业生涯发展」进行人岗匹配与规划报告生成。
            </p>
          </div>

          <div class="resume-bottom-col">
            <h3 class="resume-bottom-col-title">
              <span class="resume-bottom-col-icon" aria-hidden="true">●</span>
              上传须知
            </h3>
            <ul class="resume-bottom-list upload-tips">
              <li>请确保简历内容真实、完整，便于系统准确提取教育背景、项目经历与技能信息。</li>
              <li>建议使用一页或两页的简历版本，格式清晰、无大量表格嵌套时解析效果更佳。</li>
              <li>解析完成后将自动跳转至能力画像结果页，您可查看雷达图与综合评分，并前往职业生涯发展页进行岗位匹配。</li>
            </ul>
          </div>

          <div class="resume-bottom-col">
            <h3 class="resume-bottom-col-title">
              <span class="resume-bottom-col-icon" aria-hidden="true">●</span>
              {{ ['result', 'match', 'report'].includes(step) ? '关于本能力画像' : '填写建议' }}
            </h3>

            <template v-if="['result', 'match', 'report'].includes(step)">
              <p class="resume-bottom-col-text">
                上述雷达图与综合能力指数基于您填写的简历或对话内容生成，从多维度反映当前就业能力水平。
                建议先「查看匹配岗位」了解适合的岗位方向，再在职业生涯发展页选择目标岗位并「生成报告」，
                获取可执行的成长计划与量化评估指标。
              </p>
            </template>
            <template v-else>
              <p class="resume-bottom-col-text">
                请按助手提问顺序如实填写，教育背景、项目经历、技能证书等信息将直接影响后续能力画像与岗位匹配结果。
                若某项暂时没有，可简要说明或填「暂无」，完成后可随时在结果页查看并前往「职业生涯发展」生成规划报告。
              </p>
            </template>
          </div>
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
import { useRoute, useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { useTheme } from '../composables/useTheme'
import { ElMessage } from 'element-plus'
import { UploadFilled, ArrowDown } from '@element-plus/icons-vue'
import AppHeader from '../components/AppHeader.vue'
import {
  buildMatchReportPayload,
  extractFourDimensionScoresFromMatchPayload,
  fetchRecommendJobList,
  formatFourDimensionScoresForCompareRows,
  intakeAnswer,
  intakeFinish,
  intakeStart,
  isCareerAgentApiEnabled,
  mapParseResponseToState,
  mapPlanRow,
  mapRecommendListItemToJob,
  normalizeMatchReportPayload,
  parseResumeFile,
  parseResumeText,
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
import {
  cleanAndFormatText,
  mergeGapDetailStrings,
  mergeSuggestDetailStrings,
} from '../utils/matchAnalysisTextMerge'
import {
  abilitiesJobAreaGradient,
  abilitiesPrimaryAreaGradient,
  buildPortraitStyleRadarOption,
} from '../utils/portraitRadarEchartsOption'

const { theme } = useTheme()

/** 能力结果页七维顺序与岗位详情页 ability_radar 一致（展示为 0–100） */
const RESULT_RADAR_SPECS = [
  { label: '专业技能', getScore: (c) => c.professional_skills?.score },
  { label: '证书要求', getScore: (c) => c.certificate_requirements?.score },
  { label: '创新能力', getScore: (c) => c.innovation_capability?.score },
  { label: '学习能力', getScore: (c) => c.learning_capability?.score },
  { label: '抗压能力', getScore: (c) => c.stress_resistance?.score },
  { label: '沟通能力', getScore: (c) => c.communication_skills?.score },
  { label: '实习能力', getScore: (c) => c.internship_experience?.score },
]

function scoreToRadar100(score) {
  const s = Number(score)
  if (!Number.isFinite(s)) return 0
  const x = s <= 10 ? s * 10 : s
  return Math.max(0, Math.min(100, Math.round(x)))
}

const MATCH_FOUR_LABELS = ['基础要求', '职业技能', '职业素养', '发展潜力']
const route = useRoute()
const router = useRouter()

// ----------------- 本地 mock 数据（不调用接口） -----------------
const MOCK_PARSE_RESPONSE = {
  student_profile: {
    basic_info: {
      name: '李华',
      university: '某985理工大学',
      major: '软件工程',
      education_level: '本科',
      graduation_year: 2025
    },
    career_intent: {
      expected_salary: '15k-20k',
      target_industries: ['互联网', '金融科技'],
      job_preferences: ['后端开发', '分布式系统']
    },
    competencies: {
      professional_skills: {
        score: 9,
        keywords: ['Java', 'Spring Boot', 'MySQL'],
        evidence: '独立负责过高并发电商秒杀系统后端'
      },
      certificate_requirements: { score: 8, items: ['CET-6'], missing: [] },
      innovation_capability: { score: 7, evidence: '参与开源项目贡献代码' },
      learning_capability: { score: 9, evidence: '自学 Go 语言并在两周内重构模块' },
      stress_resistance: { score: 8, evidence: '在大促期间连续两周高强度排查线上故障' },
      communication_skills: { score: 7, evidence: '担任技术组长，协调前后端联调' },
      internship_experience: {
        score: 8,
        history: [{ company: '蚂蚁金服', position: 'Java研发实习生', duration: '6个月' }],
        evaluation: '核心业务线实习经历'
      }
    }
  },
  analysis_summary: {
    completeness: 95.0,
    competitiveness: 85.5,
    overall_comment: '简历质量极高，工程实践能力突出，非常适合技术导向型岗位。'
  },
  recommended_jobs: [
    {
      job_id: 'job_backend_001',
      title: 'Java 高级后端开发',
      match_score: 96.5,
      tags: ['高并发', '分布式', '核心业务']
    },
    {
      job_id: 'job_arch_002',
      title: '分布式系统架构师（初级）',
      match_score: 92.0,
      tags: ['架构设计', '中间件', '高潜']
    },
    {
      job_id: 'job_fintech_003',
      title: '金融科技研发工程师',
      match_score: 89.5,
      tags: ['金融业务', '数据安全', '严谨']
    }
  ],
  other_jobs: [
    { job_id: 'job_fullstack_004', title: '全栈开发工程师', match_score: 85.0, tags: ['前端', 'Node.js'] },
    { job_id: 'job_devops_005', title: 'DevOps 工程师', match_score: 82.5, tags: ['CI/CD', 'K8s'] },
    { job_id: 'job_bigdata_006', title: '大数据开发工程师', match_score: 78.0, tags: ['Hadoop', 'Spark'] },
    { job_id: 'job_ai_007', title: 'AI 平台开发', match_score: 75.5, tags: ['Python', '模型部署'] },
    { job_id: 'job_qa_008', title: '测试开发工程师', match_score: 72.0, tags: ['自动化测试', '工具开发'] },
    { job_id: 'job_pm_009', title: '技术产品经理', match_score: 68.5, tags: ['需求分析', '沟通'] },
    { job_id: 'job_pre_sales_010', title: '售前技术支持', match_score: 65.0, tags: ['方案撰写', '客户沟通'] }
  ]
}

const MOCK_MATCH_REPORTS = {
  job_arch_002: {
    job_info: {
      job_id: 'job_arch_002',
      title: '分布式系统架构师（初级）',
      company: '某独角兽科技公司',
      description: '负责微服务架构演进，中间件选型与优化...',
      salary_range: '20k-35k',
      location: '杭州'
    },
    match_analysis: {
      match_score: 92.0,
      details: {
        dimensions: { base: 90, skill: 95, soft: 85, potential: 98 },
        reasons: [
          '具备扎实的 Java 基础和高并发项目经验',
          '在校期间有过中间件源码阅读经历，潜力巨大',
          '实习期间接触过大规模微服务集群'
        ],
        warnings: [
          '缺乏 Service Mesh 等云原生架构的实操经验',
          '作为架构师角色，系统设计的方法论沉淀稍显不足'
        ]
      }
    },
    career_report: {
      gap_analysis:
        '你在代码实现层面已经非常优秀，但架构师更看重技术选型的决策能力和全局视野。目前你在复杂系统的设计文档撰写、以及对不同技术方案的 Trade-off（权衡）分析上还有提升空间。',
      action_plan:
        '1. 深入学习 DDD（领域驱动设计）并在下一个项目中尝试落地；2. 阅读《架构整洁之道》，提升系统设计的理论高度。',
      learning_path: '源码阅读 -> 架构模式学习 -> 云原生架构实战 -> 技术决策力培养'
    }
  }
}

const buildFallbackMatchReport = (jobId) => {
  const job = [...MOCK_PARSE_RESPONSE.recommended_jobs, ...MOCK_PARSE_RESPONSE.other_jobs].find(
    (j) => j.job_id === jobId
  )
  if (!job) return null

  return {
    job_info: {
      job_id: job.job_id,
      title: job.title,
      company: '某科技公司（示意）',
      description: '岗位职责与要求（示意）：结合业务场景完成核心功能研发，持续优化性能与工程质量。',
      salary_range: '面议',
      location: '城市不限'
    },
    match_analysis: {
      match_score: job.match_score ?? 0,
      details: {
        dimensions: {
          base: Math.max(0, Math.round((job.match_score ?? 0) - 5)),
          skill: Math.max(0, Math.round((job.match_score ?? 0) + 2)),
          soft: Math.max(0, Math.round((job.match_score ?? 0) - 10)),
          potential: Math.min(100, Math.round((job.match_score ?? 0) + 6))
        },
        reasons: ['与你的技能栈与项目经历契合度较高（示意）', '学习能力与迁移能力较强（示意）'],
        warnings: ['建议补齐岗位核心工具链的项目实践（示意）', '建议沉淀可复用的方法论与总结（示意）']
      }
    },
    career_report: {
      gap_analysis: '该岗位更强调关键能力的系统化沉淀与可迁移经验，你可以在项目复盘与技术选型能力上进一步提升（示意）。',
      action_plan: '1. 选定一条主线能力深挖；2. 结合真实项目做输出；3. 针对岗位 JD 梳理缺口并补齐（示意）。',
      learning_path: '基础巩固 -> 专项突破 -> 项目实战 -> 总结沉淀（示意）'
    }
  }
}

// 页面步骤：
// entry（选择入口） / upload（上传页） / chat（AI 对话） /
// result（能力画像） / match（岗位匹配） / report（职业规划报告）
const step = ref('entry')

// 方法说明卡片数据
const trustPoints = [
  {
    icon: '🧠',
    title: 'NLP 语义深度解析：超越关键词搜索',
    desc: '依托大模型深度分析简历与岗位的语义关联度。系统模拟资深 HR 筛选逻辑，结合实校招聘场景数据，深度理解经历背后的能力权重，拒绝机械式的词汇扫描。'
  },
  {
    icon: '📈',
    title: '全域动态岗位池：实时对标市场水位',
    desc: '数据实时同步各大就业网与企业官网等官方渠道。通过 AI 自动剔除过期与虚假信息，确保每一条推荐都指向真实、高价值的现聘岗位，让决策基于最新的市场现实。'
  },
  {
    icon: '🧩',
    title: '职业心理学驱动：科学的人岗契合模型',
    desc: '匹配引擎内嵌霍兰德职业兴趣等经典测评理论。匹配逻辑不只停留于技能堆砌，而是从你的职业特质与性格潜能出发，寻找能激发长久动力的岗位“最优解”。'
  }
]

// 上传简历 -> 调用解析接口并进入结果页
const handleBeforeUpload = async (file) => {
  const isAllowedType = /\.(pdf|docx)$/i.test(file.name)
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isAllowedType) {
    ElMessage.error('仅支持 PDF / DOCX 格式')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('文件大小不能超过 5MB')
    return false
  }

  ElMessage.success(`已上传：${file.name}，正在解析...`)
  await fetchParseResult({ file })
  step.value = 'result'
  return false // 阻止 Element Plus 默认上传，由我们自行请求后端
}

// 进入 AI 对话录入页面
const goToChat = async () => {
  step.value = 'chat'
  await startChatSession()
}

// 对话输入与进度
const chatInput = ref('')
const progress = ref(15)
const chatMessages = ref([])
const chatLoading = ref(false)
const chatCompleted = ref(false)
const intakeSessionId = ref('')

function questionToText(question) {
  if (!question) return ''
  if (typeof question === 'string') return question
  if (typeof question === 'object') {
    return (
      question.assistant_message ||
      question.text ||
      question.question ||
      question.prompt ||
      question.title ||
      question.content ||
      ''
    )
  }
  return ''
}

function pushBotMessage(text) {
  if (!text || !String(text).trim()) return
  chatMessages.value.push({ role: 'bot', text: String(text).trim() })
}

function buildResumeTextFromChat() {
  const userAnswers = chatMessages.value
    .filter((m) => m.role === 'user' && String(m.text || '').trim())
    .map((m, idx) => `${idx + 1}. ${String(m.text).trim()}`)
  return userAnswers.join('\n')
}

async function startChatSession() {
  chatInput.value = ''
  chatMessages.value = []
  progress.value = 5
  chatCompleted.value = false
  intakeSessionId.value = ''

  if (!isCareerAgentApiEnabled()) {
    pushBotMessage('你好！请先告诉我你的姓名。')
    return
  }

  chatLoading.value = true
  try {
    const res = await intakeStart()
    intakeSessionId.value = res?.session_id || ''
    pushBotMessage(questionToText(res?.question) || '你好，请先介绍你的基本信息。')
    progress.value = 10
  } catch (err) {
    ElMessage.error(`启动 AI 对话失败：${err.message}`)
    pushBotMessage('对话接口暂不可用，请先描述你的姓名、专业、院校、项目经历。')
  } finally {
    chatLoading.value = false
  }
}

const sendChat = async () => {
  const answer = chatInput.value.trim()
  if (!answer || chatLoading.value || chatCompleted.value) return

  chatMessages.value.push({ role: 'user', text: answer })
  chatInput.value = ''

  if (!isCareerAgentApiEnabled() || !intakeSessionId.value) {
    pushBotMessage('已记录。你可以继续补充教育背景、项目经历、技能与求职意向。')
    progress.value = Math.min(progress.value + 8, 95)
    return
  }

  chatLoading.value = true
  try {
    const res = await intakeAnswer({
      session_id: intakeSessionId.value,
      answer,
    })
    const nextQuestion = questionToText(res?.question)
    if (nextQuestion) {
      pushBotMessage(nextQuestion)
    } else if (!res?.is_complete) {
      pushBotMessage('我已收到你的回答，请继续补充更多信息（姓名、学历、专业、技能、意向岗位等）。')
    }

    if (res?.is_complete) {
      chatCompleted.value = true
      progress.value = 100
      pushBotMessage('信息收集已完成，请点击下方按钮生成能力画像。')
    } else {
      progress.value = Math.min(progress.value + 10, 95)
    }
  } catch (err) {
    ElMessage.error(`提交回答失败：${err.message}`)
  } finally {
    chatLoading.value = false
  }
}

const finishChat = async () => {
  if (isCareerAgentApiEnabled() && intakeSessionId.value) {
    try {
      await intakeFinish({ session_id: intakeSessionId.value })
    } catch (err) {
      console.warn('[career-agent] intake/finish', err)
    }
  }

  const resumeText = buildResumeTextFromChat()
  if (resumeText) {
    await fetchParseResult({ resumeText })
  } else {
    await fetchParseResult()
  }
  step.value = 'result'
}

// API 响应数据
const studentProfile = ref(null)
const analysisSummary = ref(null)
const recommendedJobsApi = ref([])
const otherJobsApi = ref([])
const matchReport = ref(null)
const matchReportRaw = ref(null)
/** 阶段一解析返回的 profile_cache_id，供阶段二优先使用 */
const profileCacheId = ref(null)

const profile = computed(() => {
  if (!studentProfile.value || !analysisSummary.value) {
    return {
      name: '-',
      school: '-',
      major: '-',
      cvCompletion: 0,
      cvLabel: '-',
      score: 0,
      rank: 0
    }
  }

  const basic = studentProfile.value.basic_info || {}
  const completion = analysisSummary.value.completeness || 0
  const label = completion >= 90 ? '优秀' : completion >= 75 ? '良好' : '需完善'
  const score = analysisSummary.value.competitiveness || 0

  return {
    name: basic.name || '-',
    school: basic.university || '-',
    major: basic.major || '-',
    cvCompletion: completion,
    cvLabel: label,
    score,
    rank: Math.round(score)
  }
})

const abilities = computed(() => {
  const comp = studentProfile.value?.competencies || {}
  const cert = comp.certificate_requirements || {}
  const certItems = cert.items || []
  const certMissing = cert.missing || []
  const certDescParts = []
  if (certItems.length) certDescParts.push(`已获得：${certItems.join('、')}`)
  if (certMissing.length) certDescParts.push(`缺失：${certMissing.join('、')}`)

  return [
    {
      name: '专业技能',
      score: comp.professional_skills?.score || 0,
      desc: comp.professional_skills?.evidence || ''
    },
    {
      name: '证书',
      score: cert.score || 0,
      desc: certDescParts.join('，')
    },
    {
      name: '创新能力',
      score: comp.innovation_capability?.score || 0,
      desc: comp.innovation_capability?.evidence || ''
    },
    {
      name: '学习能力',
      score: comp.learning_capability?.score || 0,
      desc: comp.learning_capability?.evidence || ''
    },
    {
      name: '抗压能力',
      score: comp.stress_resistance?.score || 0,
      desc: comp.stress_resistance?.evidence || ''
    },
    {
      name: '沟通能力',
      score: comp.communication_skills?.score || 0,
      desc: comp.communication_skills?.evidence || ''
    },
    {
      name: '实习能力',
      score: comp.internship_experience?.score || 0,
      desc: comp.internship_experience
        ? `经历：${(comp.internship_experience.history || [])
            .map((h) => `${h.company} ${h.position} (${h.duration})`)
            .join('；')}；评估：${comp.internship_experience.evaluation || ''}`
        : ''
    }
  ]
})

const clamp = (value, min, max) => Math.max(min, Math.min(max, value))

const abilityRadarValues = computed(() => {
  const c = studentProfile.value?.competencies || {}
  return RESULT_RADAR_SPECS.map(({ getScore }) => scoreToRadar100(getScore(c)))
})

const abilityRadarOption = computed(() => {
  const isDark = theme.value === 'dark'
  const indicator = RESULT_RADAR_SPECS.map((s) => ({ name: s.label, max: 100 }))
  return buildPortraitStyleRadarOption({
    variant: 'abilitiesFlat',
    isDark,
    indicator,
    legendData: ['个人能力'],
    seriesData: [
      {
        value: abilityRadarValues.value,
        name: '个人能力',
        areaStyle: { color: abilitiesPrimaryAreaGradient() },
        lineStyle: { color: '#8cd4cb', width: 2 },
        itemStyle: { color: '#8cd4cb', borderWidth: 0 },
        symbol: 'circle',
        symbolSize: 5,
      },
    ],
  })
})

const matchRadarParsed = computed(() => {
  const src =
    matchDetail.value && typeof matchDetail.value === 'object' && Object.keys(matchDetail.value).length
      ? matchDetail.value
      : {}
  const parsed = parseMatchRadarFourDimensionValues(src)
  const hasApiStudent = parsed.student.some((n) => n > 0)
  if (!hasApiStudent && matchReport.value?.match_analysis) {
    return parseMatchRadarFourDimensionValues({
      match_analysis: matchReport.value.match_analysis,
      dimensions: matchReport.value.match_analysis?.details?.dimensions,
    })
  }
  return parsed
})

const matchRadarJobValues = computed(() => matchRadarParsed.value.job)

const matchRadarStudentValues = computed(() => matchRadarParsed.value.student)

const matchCompareRadarOption = computed(() => {
  const isDark = theme.value === 'dark'
  const indicator = MATCH_FOUR_LABELS.map((name) => ({ name, max: 100 }))
  const option = buildPortraitStyleRadarOption({
    variant: 'abilitiesFlat',
    isDark,
    indicator,
    legendData: ['岗位要求', '学生能力'],
    seriesData: [
      {
        value: matchRadarJobValues.value,
        name: '岗位要求',
        lineStyle: { color: '#D489A8', width: 2 },
        areaStyle: { color: abilitiesJobAreaGradient() },
        itemStyle: { color: '#D489A8', borderWidth: 0 },
        symbol: 'circle',
        symbolSize: 5,
      },
      {
        value: matchRadarStudentValues.value,
        name: '学生能力',
        lineStyle: { color: '#8cd4cb', width: 2 },
        areaStyle: { color: abilitiesPrimaryAreaGradient() },
        itemStyle: { color: '#8cd4cb', borderWidth: 0 },
        symbol: 'circle',
        symbolSize: 5,
      },
    ],
  })
  return {
    ...option,
    legend: {
      ...(option.legend || {}),
      bottom: 8,
    },
    radar: {
      ...(option.radar || {}),
      center: ['50%', '50%'],
      radius: '62%',
    },
  }
})

const suggestions = computed(() => {
  if (!analysisSummary.value) return []
  const comment = analysisSummary.value.overall_comment || ''
  return comment.trim() ? [comment.trim()] : []
})

const scoreToPercentage = (score) => {
  const numeric = Number(score) || 0
  // 兼容 10 分制与 100 分制数据
  const normalized = numeric <= 10 ? numeric * 10 : numeric
  return Math.max(0, Math.min(100, Math.round(normalized)))
}

const studentName = computed(() => studentProfile.value?.basic_info?.name || '学生')

const allJobs = computed(() => [...recommendedJobsApi.value, ...otherJobsApi.value])

const recommendedJobs = computed(() =>
  recommendedJobsApi.value.map((job) => ({
    id: job.job_id,
    name: job.title,
    match: job.match_score,
    tags: job.tags || []
  }))
)

const otherJobs = computed(() =>
  otherJobsApi.value.map((job) => ({
    id: job.job_id,
    name: job.title,
    match: job.match_score,
    tags: job.tags || []
  }))
)

const selectedJobId = ref('')
const otherJobsExpanded = ref([])
const matchDetail = ref(null)

const currentJob = computed(() => {
  if (step.value === 'match' && matchDetail.value) {
    return {
      ...matchDetail.value,
      name: matchDetail.value.title || matchDetail.value.name,
      match: matchDetail.value.match_score ?? 0
    }
  }
  if (matchReport.value?.job_info) {
    const info = matchReport.value.job_info
    return {
      ...info,
      name: info.title || info.name,
      match: matchReport.value.match_analysis?.match_score ?? 0
    }
  }
  return allJobs.value.find((j) => j.id === selectedJobId.value) || null
})

const compareDimensions = ref([])
const gapDetails = ref([])
const improveSuggestions = ref([])
/** 岗位匹配分析区（四维度 + 详细差距 + 提升建议）拉取接口时的遮罩，避免未清洗的 Markdown 闪现 */
const matchAnalysisDetailLoading = ref(false)
const aiThinkingTexts = ['正在分析简历语义...', '正在匹配行业坐标...', '正在量化竞争力...']
const aiThinkingIndex = ref(0)
const currentAiThinkingText = computed(() => aiThinkingTexts[aiThinkingIndex.value] || aiThinkingTexts[0])
let aiThinkingTimer = null

const abilityRadarChartRef = ref(null)
let abilityRadarChartInstance = null
let abilityRadarResizeObserver = null

const matchCompareRadarRef = ref(null)
let matchCompareRadarInstance = null
let matchCompareRadarResizeObserver = null
/** 避免每次 setOption(notMerge) 整图重绘导致「一闪」；首次全量，之后合并以走缓动 */
let abilityRadarDidFirstSet = false
let matchCompareRadarDidFirstSet = false
let abilityRadarChartTheme = null
let matchCompareRadarTheme = null

function getEchartsThemeName() {
  return theme.value === 'dark' ? 'dark' : null
}

function disposeAbilityRadarChart() {
  if (abilityRadarResizeObserver) {
    abilityRadarResizeObserver.disconnect()
    abilityRadarResizeObserver = null
  }
  if (abilityRadarChartInstance) {
    abilityRadarChartInstance.dispose()
    abilityRadarChartInstance = null
  }
  abilityRadarDidFirstSet = false
  abilityRadarChartTheme = null
}

function ensureAbilityRadarChart() {
  if (step.value !== 'result' || !abilityRadarChartRef.value) return
  const currentThemeName = getEchartsThemeName()
  if (abilityRadarChartInstance && abilityRadarChartTheme !== currentThemeName) {
    disposeAbilityRadarChart()
  }
  if (!abilityRadarChartInstance) {
    abilityRadarChartInstance = echarts.init(abilityRadarChartRef.value, currentThemeName, {
      renderer: 'canvas'
    })
    abilityRadarChartTheme = currentThemeName
    abilityRadarResizeObserver = new ResizeObserver(() => abilityRadarChartInstance?.resize())
    abilityRadarResizeObserver.observe(abilityRadarChartRef.value)
    abilityRadarDidFirstSet = false
  }
  const opt = abilityRadarOption.value
  if (!abilityRadarDidFirstSet) {
    abilityRadarChartInstance.setOption(opt, true)
    abilityRadarDidFirstSet = true
  } else {
    abilityRadarChartInstance.setOption(opt, false)
  }
}

function disposeMatchCompareRadarChart() {
  if (matchCompareRadarResizeObserver) {
    matchCompareRadarResizeObserver.disconnect()
    matchCompareRadarResizeObserver = null
  }
  if (matchCompareRadarInstance) {
    matchCompareRadarInstance.dispose()
    matchCompareRadarInstance = null
  }
  matchCompareRadarDidFirstSet = false
  matchCompareRadarTheme = null
}

function ensureMatchCompareRadarChart() {
  if (step.value !== 'match' || !currentJob.value || !matchCompareRadarRef.value) return
  const currentThemeName = getEchartsThemeName()
  if (matchCompareRadarInstance && matchCompareRadarTheme !== currentThemeName) {
    disposeMatchCompareRadarChart()
  }
  if (!matchCompareRadarInstance) {
    matchCompareRadarInstance = echarts.init(matchCompareRadarRef.value, currentThemeName, {
      renderer: 'canvas'
    })
    matchCompareRadarTheme = currentThemeName
    matchCompareRadarResizeObserver = new ResizeObserver(() => matchCompareRadarInstance?.resize())
    matchCompareRadarResizeObserver.observe(matchCompareRadarRef.value)
    matchCompareRadarDidFirstSet = false
  }
  const opt = matchCompareRadarOption.value
  if (!matchCompareRadarDidFirstSet) {
    matchCompareRadarInstance.setOption(opt, true)
    matchCompareRadarDidFirstSet = true
  } else {
    matchCompareRadarInstance.setOption(opt, false)
  }
}

watch(
  () => [abilityRadarOption.value, theme.value],
  () => {
    nextTick(() => ensureAbilityRadarChart())
  }
)

watch(
  () => [matchCompareRadarOption.value, theme.value],
  () => {
    nextTick(() => ensureMatchCompareRadarChart())
  }
)

watch(step, (s) => {
  nextTick(() => {
    if (s !== 'result') disposeAbilityRadarChart()
    else ensureAbilityRadarChart()
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

watch(matchAnalysisDetailLoading, (loading) => {
  if (loading) {
    aiThinkingIndex.value = 0
    if (aiThinkingTimer) {
      clearInterval(aiThinkingTimer)
      aiThinkingTimer = null
    }
    aiThinkingTimer = setInterval(() => {
      aiThinkingIndex.value = (aiThinkingIndex.value + 1) % aiThinkingTexts.length
    }, 1400)
    return
  }
  if (aiThinkingTimer) {
    clearInterval(aiThinkingTimer)
    aiThinkingTimer = null
  }
  nextTick(() => {
    // 详情区使用 v-if/v-else，loading 结束后 ref 才真正可用；
    // 这里必须重新 ensure 一次，避免出现“文本有了但雷达图没挂上”的空白情况。
    ensureMatchCompareRadarChart()
    matchCompareRadarInstance?.resize()
  })
})

onMounted(() => {
  nextTick(() => {
    if (step.value === 'result') ensureAbilityRadarChart()
    if (step.value === 'match' && currentJob.value) ensureMatchCompareRadarChart()
  })
})

onUnmounted(() => {
  if (aiThinkingTimer) {
    clearInterval(aiThinkingTimer)
    aiThinkingTimer = null
  }
  disposeAbilityRadarChart()
  disposeMatchCompareRadarChart()
})

const gapAnalysisFormatted = computed(() =>
  cleanAndFormatText(gapDetails.value, { splitNumbered: false })
)
const improveSuggestionFormatted = computed(() =>
  cleanAndFormatText(improveSuggestions.value, { splitNumbered: false })
)
const compareDimensionsWithRows = computed(() =>
  compareDimensions.value.map((item) => ({
    name: item.name,
    student: item.student,
    requirementRows: cleanAndFormatText(item.requirementText),
  }))
)
const asTrimmedString = (v) => (typeof v === 'string' ? v.trim() : '')
const isLikelyImageUrl = (v) =>
  typeof v === 'string' &&
  /^(https?:\/\/|data:image\/|\/)/i.test(v.trim())

const flattenText = (value) => {
  if (!value) return []
  if (typeof value === 'string') return value.trim() ? [value.trim()] : []
  if (Array.isArray(value)) return value.flatMap((item) => flattenText(item))
  if (typeof value === 'object') {
    return Object.values(value).flatMap((item) => flattenText(item))
  }
  return []
}

const uniqueTexts = (items) => [...new Set(items.map((x) => x.trim()).filter(Boolean))]

const flattenGapItems = (items) => {
  if (!Array.isArray(items)) return []
  return items.flatMap((item) => {
    if (!item || typeof item !== 'object') return []
    return [
      item.point,
      item.suggestion,
      item.dimension_label,
      item.dimension,
      item.dimension_key,
      item.text,
      item.desc,
    ]
      .map((x) => String(x || '').trim())
      .filter(Boolean)
  })
}

const careerReportRaw = computed(() => matchReportRaw.value?.career_report || {})
const careerReportNormalized = computed(() => matchReport.value?.career_report || {})
const module1Raw = computed(
  () => careerReportRaw.value.module_1 || careerReportRaw.value.module1 || {}
)
const module3Raw = computed(
  () => careerReportRaw.value.module_3 || careerReportRaw.value.module3 || {}
)
const selectedPlanRaw = computed(
  () => module3Raw.value.selected_plan || module3Raw.value.selectedPlan || {}
)

const learningPathImage = computed(() => {
  const candidates = [
    careerReportRaw.value.learning_path_image,
    careerReportRaw.value.learningPathImage,
    careerReportRaw.value.path_image,
    careerReportRaw.value.pathImage,
    module3Raw.value.path_image,
    module3Raw.value.pathImage,
    selectedPlanRaw.value.path_image,
    selectedPlanRaw.value.pathImage,
    selectedPlanRaw.value.roadmap_image,
    selectedPlanRaw.value.roadmapImage,
  ]
  return candidates.find((x) => isLikelyImageUrl(x)) || ''
})

const learningPathText = computed(() => {
  return (
    asTrimmedString(careerReportNormalized.value.learning_path) ||
    asTrimmedString(careerReportRaw.value.learning_path) ||
    asTrimmedString(careerReportRaw.value.learningPath) ||
    asTrimmedString(selectedPlanRaw.value.summary) ||
    asTrimmedString(selectedPlanRaw.value.overall_summary) ||
    '接口暂未返回学习路径说明。'
  )
})

const reportStrengths = computed(() => {
  const normalized = matchReport.value?.match_analysis?.details?.reasons || []
  const rawCandidates = [
    careerReportRaw.value.strengths,
    careerReportRaw.value.advantages,
    careerReportRaw.value.personal_strengths,
    module1Raw.value.strengths,
    module1Raw.value.advantages,
    module1Raw.value.personal_strengths,
    module1Raw.value.key_strengths,
  ]
  return uniqueTexts([...normalized, ...rawCandidates.flatMap((x) => flattenText(x))])
})

const reportWeaknesses = computed(() => {
  const normalized = matchReport.value?.match_analysis?.details?.warnings || []
  const module1GapItems = flattenGapItems(module1Raw.value.gaps)
  const rawCandidates = [
    careerReportRaw.value.weaknesses,
    careerReportRaw.value.gaps,
    careerReportRaw.value.risks,
    module1Raw.value.weaknesses,
    module1Raw.value.gaps,
    module1Raw.value.risks,
    module1Raw.value.improvement_points,
  ]
  return uniqueTexts([
    ...normalized,
    ...module1GapItems,
    ...rawCandidates.flatMap((x) => flattenText(x)),
  ])
})

const baseInfo = computed(() => {
  return {
    major: studentProfile.value?.basic_info?.major || '-',
    targetJob: currentJob.value?.title || currentJob.value?.name || '-',
    summary:
      matchReport.value?.career_report?.gap_analysis ||
      analysisSummary.value?.overall_comment ||
      '暂无分析摘要',
    strengths: reportStrengths.value,
    weaknesses: reportWeaknesses.value,
  }
})

const summaryLines = computed(() =>
  String(baseInfo.value?.summary || '')
    .split('。')
    .map((x) => x.trim())
    .filter(Boolean)
)

/**
 * 从 GET /recommend/list 拉取岗位，保证 job_id 与阶段二接口一致
 */
const hydrateJobsFromRecommendList = async () => {
  if (!isCareerAgentApiEnabled()) return
  try {
    const list = await fetchRecommendJobList()
    const mapped = list.map(mapRecommendListItemToJob)
    if (!mapped.length) return
    const mid = Math.min(5, mapped.length)
    recommendedJobsApi.value = mapped.slice(0, mid)
    otherJobsApi.value = mapped.slice(mid)
    if (!selectedJobId.value || !mapped.some((j) => j.job_id === selectedJobId.value)) {
      selectedJobId.value = recommendedJobsApi.value[0]?.job_id || mapped[0].job_id
    }
  } catch (e) {
    console.warn('[career-agent] recommend/list', e)
  }
}

// 解析简历并获取推荐岗位（阶段一：POST /api/v1/student/parse 或 /parse/manual）
const fetchParseResult = async (options = {}) => {
  const { file, resumeText } = options
  profileCacheId.value = null

  try {
    if (isCareerAgentApiEnabled() && file) {
      const raw = await parseResumeFile(file)
      const mapped = mapParseResponseToState(raw)
      studentProfile.value = mapped.student_profile
      analysisSummary.value = mapped.analysis_summary
      recommendedJobsApi.value = mapped.recommended_jobs || []
      otherJobsApi.value = mapped.other_jobs || []
      profileCacheId.value = mapped.profile_cache_id || null
      if (profileCacheId.value) {
        saveProfileCacheId(profileCacheId.value)
      }
      if (!recommendedJobsApi.value.length && !otherJobsApi.value.length) {
        await hydrateJobsFromRecommendList()
      }
    } else if (isCareerAgentApiEnabled() && resumeText && String(resumeText).trim()) {
      const raw = await parseResumeText(String(resumeText).trim())
      const mapped = mapParseResponseToState(raw)
      studentProfile.value = mapped.student_profile
      analysisSummary.value = mapped.analysis_summary
      recommendedJobsApi.value = mapped.recommended_jobs || []
      otherJobsApi.value = mapped.other_jobs || []
      profileCacheId.value = mapped.profile_cache_id || null
      if (profileCacheId.value) {
        saveProfileCacheId(profileCacheId.value)
      }
      if (!recommendedJobsApi.value.length && !otherJobsApi.value.length) {
        await hydrateJobsFromRecommendList()
      }
    } else {
      const data = MOCK_PARSE_RESPONSE
      studentProfile.value = data.student_profile
      analysisSummary.value = data.analysis_summary
      recommendedJobsApi.value = data.recommended_jobs || []
      otherJobsApi.value = data.other_jobs || []
      if (isCareerAgentApiEnabled()) {
        await hydrateJobsFromRecommendList()
      }
    }

    if (recommendedJobsApi.value.length > 0) {
      selectedJobId.value = recommendedJobsApi.value[0].job_id
    } else if (otherJobsApi.value.length > 0) {
      selectedJobId.value = otherJobsApi.value[0].job_id
    }
  } catch (err) {
    ElMessage.error(`解析失败：${err.message}`)
    if (isCareerAgentApiEnabled()) {
      // API 模式：不回退到李华 mock，避免误导用户；保留已有输入并尝试拉真实岗位
      if (!studentProfile.value) {
        studentProfile.value = {
          basic_info: { name: '学生', major: '-', education_level: '-' },
          career_intent: {},
          competencies: {},
          experiences: {},
        }
      }
      if (!analysisSummary.value) {
        analysisSummary.value = {
          completeness: 0,
          competitiveness: 0,
          overall_comment: '解析未完成，请根据提示补充信息后重试。',
        }
      }
      await hydrateJobsFromRecommendList()
      if (recommendedJobsApi.value.length > 0) {
        selectedJobId.value = recommendedJobsApi.value[0].job_id
      }
      return
    }

    // 非 API 模式保留原有 mock 逻辑
    const data = MOCK_PARSE_RESPONSE
    studentProfile.value = data.student_profile
    analysisSummary.value = data.analysis_summary
    recommendedJobsApi.value = data.recommended_jobs || []
    otherJobsApi.value = data.other_jobs || []
    if (recommendedJobsApi.value.length > 0) {
      selectedJobId.value = recommendedJobsApi.value[0].job_id
    }
  }
}

// 加载岗位匹配详情（第二分界面：POST /api/v1/match/detail）
const loadMatchDetail = async () => {
  if (!selectedJobId.value || !studentProfile.value) return

  const hasMinimumProfile =
    !!studentProfile.value?.basic_info &&
    !!studentProfile.value?.competencies &&
    !!studentProfile.value?.experiences

  if (isCareerAgentApiEnabled()) {
    if (!profileCacheId.value && !hasMinimumProfile) {
      const persistedProfileCacheId = readProfileCacheId()
      if (persistedProfileCacheId) {
        profileCacheId.value = persistedProfileCacheId
      }
    }
    if (!profileCacheId.value && !hasMinimumProfile) {
      ElMessage.error('缺少有效的学生画像数据，无法调用岗位匹配接口。请先重新完成简历解析。')
      return
    }
  }

  matchAnalysisDetailLoading.value = true
  gapDetails.value = []
  improveSuggestions.value = []
  compareDimensions.value = []

  const applyLocalMockReport = async () => {
    const data =
      MOCK_MATCH_REPORTS[selectedJobId.value] || buildFallbackMatchReport(selectedJobId.value)
    if (!data) return
    matchDetail.value = {
      job_id: data.job_info?.job_id || selectedJobId.value,
      title: data.job_info?.title || data.job_info?.name || '',
      match_score: data.match_analysis?.match_score || 0,
      dimensions: data.match_analysis?.details?.dimensions || {},
      gap_analysis: (data.match_analysis?.details?.reasons || []).join('\n'),
      improvement_suggestions: (data.match_analysis?.details?.warnings || []).join('\n'),
      narrative: '',
    }
    const dimScores = extractFourDimensionScoresFromMatchPayload({
      match_analysis: data.match_analysis,
    })
    const studentByKey = formatFourDimensionScoresForCompareRows(dimScores)
    const m1tj = matchReport.value?.career_report?.module_1?.target_job
    const module1TargetJob =
      m1tj && String(m1tj.job_id || '') === String(selectedJobId.value) ? m1tj : null
    const texts = await resolveMatchDimensionRequirementTexts(
      matchDetail.value,
      selectedJobId.value,
      data.job_info?.title || data.job_info?.name || '',
      module1TargetJob
    )
    compareDimensions.value = buildCompareDimensionRows(texts, studentByKey)
    gapDetails.value = mergeGapDetailStrings(
      { match_analysis: data.match_analysis, gap_analysis: matchDetail.value.gap_analysis },
      '',
      dimScores
    )
    improveSuggestions.value = mergeSuggestDetailStrings(
      {
        match_analysis: data.match_analysis,
        improvement_suggestions: matchDetail.value.improvement_suggestions,
      },
      '',
      dimScores
    )
  }

  try {
    if (isCareerAgentApiEnabled()) {
      const payload = { job_id: selectedJobId.value }
      if (profileCacheId.value) {
        payload.profile_cache_id = profileCacheId.value
      } else {
        payload.student_profile = studentProfile.value
      }
      const detail = await postMatchDetail(payload)
      matchDetail.value = detail
      const dimScores = extractFourDimensionScoresFromMatchPayload(detail)
      const studentByKey = formatFourDimensionScoresForCompareRows(dimScores)
      const m1tj = matchReport.value?.career_report?.module_1?.target_job
      const module1TargetJob =
        m1tj && String(m1tj.job_id || '') === String(selectedJobId.value) ? m1tj : null
      const texts = await resolveMatchDimensionRequirementTexts(
        detail,
        selectedJobId.value,
        detail?.title || detail?.name || '',
        module1TargetJob
      )
      compareDimensions.value = buildCompareDimensionRows(texts, studentByKey)
      const narrative = String(detail?.narrative || '')
      gapDetails.value = mergeGapDetailStrings(detail, narrative, dimScores)
      improveSuggestions.value = mergeSuggestDetailStrings(detail, narrative, dimScores)
    } else {
      await applyLocalMockReport()
    }
  } catch (err) {
    console.warn('[career-agent] match/detail', err)
    if (isCareerAgentApiEnabled()) {
      ElMessage.error(`岗位匹配详情加载失败：${err.message}`)
      return
    }
    ElMessage.warning(`接口获取匹配详情失败，已使用本地示意数据：${err.message}`)
    await applyLocalMockReport()
  } finally {
    matchAnalysisDetailLoading.value = false
  }
}

// 查看匹配岗位 -> 切换到「岗位匹配与职业探索」步骤
const goToMatch = async () => {
  step.value = 'match'
  await loadMatchDetail()
}

const enterStepByRouteQuery = async () => {
  if (route.query.step !== 'match') return
  await fetchParseResult()
  step.value = 'match'
  await loadMatchDetail()
}

// ----------------- 以下为岗位匹配与职业规划报告相关逻辑（原 CareerReportView） -----------------

// 选中岗位详情
const viewJobDetail = async (row) => {
  selectedJobId.value = row.id
  ElMessage.success(`已切换到岗位「${row.name}」的匹配详情`)
  await loadMatchDetail()
}

// 从匹配页生成报告（第三分界面：POST /api/v1/match/report）
const generateReport = async () => {
  if (!selectedJobId.value) {
    ElMessage.warning('请先选择岗位')
    return
  }
  const hasMinimumProfile =
    !!studentProfile.value?.basic_info &&
    !!studentProfile.value?.competencies &&
    !!studentProfile.value?.experiences
  if (!profileCacheId.value && !hasMinimumProfile) {
    const persistedProfileCacheId = readProfileCacheId()
    if (persistedProfileCacheId) {
      profileCacheId.value = persistedProfileCacheId
    }
  }
  if (!profileCacheId.value && !hasMinimumProfile) {
    ElMessage.error('缺少有效的学生画像数据，无法生成职业报告。请先重新完成简历解析。')
    return
  }
  try {
    const payload = buildMatchReportPayload({
      job_id: selectedJobId.value,
      profile_cache_id: profileCacheId.value || '',
      student_profile: studentProfile.value || null,
      precomputed_module_1: matchReport.value?.career_report?.module_1 || null,
    })
    const raw = await postMatchReport(payload)
    saveLastMatchResult(raw)
    const normalized = normalizeMatchReportPayload(raw) || raw
    matchReport.value = normalized
    matchReportRaw.value = raw
  } catch (err) {
    ElMessage.error(`生成职业报告失败：${err.message}`)
    return
  }
  step.value = 'report'
  ElMessage.success(
    isCareerAgentApiEnabled()
      ? '已根据当前岗位与接口数据生成职业发展规划报告'
      : '已根据当前岗位生成职业发展规划报告（示意）'
  )
}

const goGenerateTrainingPlan = () => {
  if (matchReportRaw.value && typeof matchReportRaw.value === 'object') {
    saveLastMatchResult(matchReportRaw.value)
  }
  try {
    sessionStorage.setItem('career_planner_training_plan_ready_v1', '1')
  } catch {
    // ignore write errors
  }
  router.push('/ability-training-plan')
}

const routeProfileCacheId = typeof route.query.profile_cache_id === 'string' ? route.query.profile_cache_id : ''
if (routeProfileCacheId) {
  profileCacheId.value = routeProfileCacheId
  saveProfileCacheId(routeProfileCacheId)
}
enterStepByRouteQuery()
if (!profileCacheId.value) {
  const persistedProfileCacheId = readProfileCacheId()
  if (persistedProfileCacheId) {
    profileCacheId.value = persistedProfileCacheId
  }
}

// 报告基础信息
const reportDate = new Date().toLocaleDateString()

// 短期 / 中期成长计划
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

/** 阶段二接口若在 career_report 中带短期/中期计划，同步到报告页表格 */
watch(
  () => matchReport.value?.career_report,
  (cr) => {
    if (!cr) return
    const st = cr.short_term_plan
    const mt = cr.mid_term_plan
    if (Array.isArray(st) && st.length) {
      const rows = st.map(mapPlanRow).filter(Boolean)
      if (rows.length) shortTermPlan.value = rows
    }
    if (Array.isArray(mt) && mt.length) {
      const rows = mt.map(mapPlanRow).filter(Boolean)
      if (rows.length) midTermPlan.value = rows
    }
  },
  { deep: true }
)

const evaluationSummary = computed(() => {
  const normalized = careerReportNormalized.value
  const raw = careerReportRaw.value
  const actionPlan = asTrimmedString(normalized.action_plan) || asTrimmedString(raw.action_plan)
  const directSummaryCandidates = [
    raw.evaluation_summary,
    raw.evaluationSummary,
    raw.stage_evaluation,
    raw.stageEvaluation,
    raw.assessment,
    raw.review,
    selectedPlanRaw.value?.llm_commentary?.overall_summary,
  ]
  const directSummary = uniqueTexts(directSummaryCandidates.flatMap((x) => flattenText(x))).join('\n')

  const metricHints = [
    ...(shortTermPlan.value || []).map((x) => x?.metric).filter(Boolean),
    ...(midTermPlan.value || []).map((x) => x?.metric).filter(Boolean),
  ].slice(0, 3)

  if (directSummary) {
    const parts = [directSummary]
    if (actionPlan) parts.push(`执行重点：${actionPlan}`)
    if (metricHints.length) parts.push(`建议重点追踪指标：${metricHints.join('；')}`)
    return parts.join('\n')
  }

  const fallbackParts = [
    '在每个阶段结束时，对照量化指标进行自评与导师评估，根据达成情况适当调整后续学习与实践计划。',
  ]
  if (actionPlan) fallbackParts.push(`执行重点：${actionPlan}`)
  if (metricHints.length) fallbackParts.push(`建议重点追踪指标：${metricHints.join('；')}`)
  return fallbackParts.join('\n')
})

// 报告头部按钮功能（示意）
const handleEditReport = () => {
  ElMessage.info('这里可以接入富文本编辑器，对报告内容进行人工编辑。')
}

const handlePolish = () => {
  ElMessage.success('已调用智能润色（示意），实际可接入大模型优化报告文案。')
}

const exportReport = (format) => {
  if (format === 'markdown') {
    const content = `# 职业发展规划报告（示例）\n\n目标岗位：${
      currentJob.value?.name || baseInfo.value.targetJob
    }\n生成时间：${reportDate}\n`
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'career-report.md'
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('已导出 Markdown 报告文件，你可以根据需要转换为其他格式。')
  } else if (format === 'pdf') {
    ElMessage.info('PDF 导出为占位功能，可后续接入后端或前端 PDF 生成库。')
  } else if (format === 'word') {
    ElMessage.info('Word 导出为占位功能，可后续接入后端文档生成服务。')
  }
}
</script>

<style scoped>
.abilities-view {
  --u-border-radius: 12px;
  /* 与 uiineed 示意图一致：标签贴纸蓝 */
  --u-uiineed-sticker: #7eb8d4;
  /* 主色仍为 #e8f6ff 系；略掺奶黄，与 Uiineed 马卡龙协调 */
  --u-panel: #f5f4f0;
  --u-bg-normal: #f9f3e5;
  --u-gradient-fade: rgba(249, 243, 229, 0.58);
  --u-gradient-fade-soft: rgba(240, 249, 255, 0.78);
  --u-gradient-fade-mid: rgba(232, 246, 255, 0.5);
  /* 与主界面一致：纯色浅蓝，无渐变 */
  --abilities-page-bg: var(--u-body-bg);

  width: 100vw;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--abilities-page-bg);
  color: var(--u-black);
  font-family: var(--font-family-sans);
}

.abilities-view.dark {
  background: var(--dm-bg);
  color: var(--dm-text);
}

.abilities-view.dark .page-scroll {
  background: var(--dm-bg);
}

.abilities-view.dark .match-panel {
  background: var(--dm-bg);
}

.abilities-view.dark .panel {
  /* 去掉第二页外层大方框：外层只负责布局，不负责“卡片底”视觉 */
  background: transparent;
  border: none;
  box-shadow: none;
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
  background: rgba(255, 255, 255, 0.95);
  border-bottom: var(--u-border);
}

.abilities-view.dark .header {
  background: var(--dm-header-bg);
  backdrop-filter: blur(12px);
  border-bottom-color: var(--dm-border);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 2vw;
}

.logo {
  text-decoration: none;
  color: inherit;
}

.nav-back {
  font-size: clamp(15px, 0.95vw, 17px);
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

.abilities-view.dark .nav-item {
  color: var(--dm-text);
}

.abilities-view.dark .nav-item.active {
  color: var(--dm-accent);
}

.abilities-view.dark .nav-item.active::after {
  background-color: var(--dm-accent);
}

.header-right {
  display: flex;
  align-items: center;
}

.theme-toggle {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  background: rgba(186, 212, 238, 0.55);
  border: 1px solid rgba(51, 50, 46, 0.12);
  padding: 4px;
  font-size: 12px;
}

.abilities-view.dark .theme-toggle {
  background: var(--dm-surface);
}

.theme-option {
  padding: 4px 12px;
  border-radius: 999px;
  cursor: pointer;
  color: #666;
}

.theme-option.active {
  background: var(--u-black);
  color: #fdf8ef;
}

.page-scroll {
  padding: 28px 6vw 56px 64px;
  flex: 1;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  background: var(--abilities-page-bg);
  min-height: 100%;
}

.site-footer {
  margin-top: auto;
  padding-top: 32px;
  padding-bottom: 16px;
  border-top: 1px solid rgba(148, 163, 184, 0.35);
  font-size: clamp(14px, 0.9vw, 16px);
  color: #94a3b8;
  text-align: center;
  width: 100%;
}

.abilities-view.dark .site-footer {
  border-top-color: var(--dm-border);
  color: var(--dm-text-muted);
}

/* 各步骤底部补充说明，拉长页面、避免过短 */
.page-extra-intro {
  margin-top: 32px;
  padding: 24px 20px 28px;
  background: rgba(186, 230, 253, 0.45);
  border-radius: 14px;
  /* 去掉细线框 */
  border: none;
}

.abilities-view.dark .page-extra-intro {
  background: var(--dm-surface-elevated);
  border-color: transparent;
}

.resume-bottom-explain {
  margin-top: 24px;
  padding: 16px 20px 20px;
  background: rgba(186, 230, 253, 0.4);
  border-radius: 16px;
}

.abilities-view.dark .resume-bottom-explain {
  background: var(--dm-surface-elevated);
}

.resume-bottom-cols {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px 22px;
}

.resume-bottom-col {
  min-width: 0;
}

.resume-bottom-col-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: clamp(16px, 1.1vw, 18px);
  font-weight: 700;
  margin: 0 0 10px;
  color: #0f172a;
}

.abilities-view.dark .resume-bottom-col-title {
  color: var(--dm-text);
}

.resume-bottom-col-icon {
  display: inline-flex;
  width: 18px;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  line-height: 1;
  color: #000;
  flex: 0 0 auto;
}

.resume-bottom-col-text {
  margin: 0;
  font-size: clamp(14px, 0.95vw, 16px);
  line-height: 1.75;
  color: #475569;
}

.abilities-view.dark .resume-bottom-col-text {
  color: var(--dm-text-secondary);
}

.resume-bottom-list {
  margin-top: 0 !important;
}

@media (max-width: 900px) {
  .resume-bottom-cols {
    grid-template-columns: 1fr;
  }
}

.extra-intro-title {
  font-size: clamp(17px, 1.1vw, 20px);
  font-weight: 600;
  margin-bottom: 12px;
  color: #334155;
}

.abilities-view.dark .extra-intro-title {
  color: var(--dm-text);
}

.extra-intro-text {
  font-size: clamp(15px, 1vw, 17px);
  line-height: 1.7;
  color: #475569;
}

.abilities-view.dark .extra-intro-text {
  color: var(--dm-text-secondary);
}

.page-extra-intro .upload-tips {
  margin-top: 8px;
}

.result-intro {
  margin-top: 28px;
}

.panel {
  /* 去掉第二页外层大方框：不再给外层卡片底色/边框/阴影 */
  background: transparent;
  border-radius: 18px;
  backdrop-filter: none;
  padding: 24px 24px 32px;
  border: none;
  box-shadow: none;
}

.entry-panel {
  min-height: 72vh;
}

.upload-panel {
  min-height: 70vh;
}

.chat-panel {
  min-height: 74vh;
}

.result-panel {
  min-height: 70vh;
}

.panel + .panel {
  margin-top: 24px;
}

/* 本页按钮交互强化：确保 hover 有明显“上浮+阴影拉长” */
.abilities-view .u-btn:not(.u-btn--text):not(.is-disabled):hover,
.abilities-view .u-btn.el-button:not(.u-btn--text):not(.is-disabled):hover {
  transform: translate(-2px, -2px) !important;
  box-shadow: 7px 7px 0 var(--u-black) !important;
}

.abilities-view.dark .u-btn:not(.u-btn--text):not(.is-disabled):hover,
.abilities-view.dark .u-btn.el-button:not(.u-btn--text):not(.is-disabled):hover {
  box-shadow: 7px 7px 0 var(--u-black) !important;
}

.panel-header {
  margin-bottom: 16px;
}

.match-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.result-header-left {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.result-page-title {
  margin-bottom: 0;
}

.page-title {
  font-size: var(--fs-h1);
  font-weight: var(--fw-heading);
  margin-bottom: 10px;
}

.upload-page-title,
.chat-page-title,
.result-page-title,
.match-page-title,
.report-page-title {
  /* 小一点：比欢迎来到简历智评中心的 --fs-h1 再小一档 */
  font-size: var(--fs-h2);
}

.page-intro {
  font-size: var(--fs-body);
  font-weight: var(--fw-body);
  line-height: 1.6;
  margin-bottom: 14px;
  color: rgba(51, 50, 46, 0.78);
}

.abilities-view.dark .page-title {
  color: var(--dm-text);
}

.abilities-view.dark .page-intro {
  color: var(--dm-text-secondary);
}

.abilities-view.dark .trust-title,
.abilities-view.dark .trust-item-title {
  color: var(--dm-text);
}

.trust-panel {
  margin-top: 20px;
  /* 同样移除厚重波点，让卡片悬浮但不“糊住”底色 */
  background: rgba(186, 230, 253, 0.38);
  border-radius: 16px;
  padding: 16px 18px 18px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(125, 211, 252, 0.45);
  box-shadow: 0 18px 40px rgba(14, 116, 188, 0.06);
}

.abilities-view.dark .trust-panel {
  background: rgba(28, 33, 40, 0.62);
  border: 1px solid var(--dm-border);
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.35);
}

.trust-panel--entry {
  /* 入口页：该区域本身也作为卡片展示（黑色边框） */
  background: rgba(186, 230, 253, 0.38);
  border-radius: 16px;
  padding: 16px 18px 35px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(125, 211, 252, 0.45);
  box-shadow: 0 18px 40px rgba(14, 116, 188, 0.06);
  margin-top: 60px;
}

.abilities-view.dark .trust-panel--entry {
  background: rgba(28, 33, 40, 0.62);
  border: 1px solid var(--dm-border);
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.35);
}

.abilities-view.dark .trust-item-desc {
  color: var(--dm-text-secondary);
}

.trust-panel--upload-explain {
  margin-top: 65px;
  border: 2px solid var(--u-black);
  box-shadow: 2px 2px 0px var(--u-black);
}

.abilities-view.dark .trust-panel--upload-explain {
  border: 3px solid var(--u-black);
  box-shadow: 2px 2px 0px var(--u-black);
}

.trust-title {
  font-size: clamp(18px, 1.2vw, 22px);
  margin-bottom: 10px;
}

.trust-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px 18px;
  align-items: stretch;
  margin-top: 50px;
}

/* 入口页：主标题与三张说明卡更紧凑 */
.trust-panel--entry .trust-title {
  margin-bottom: 6px;
}

.trust-panel--entry .trust-grid {
  margin-top: 18px;
}

.trust-item--0 {
  background: rgba(232, 246, 255, 0.68);
  border: 2px solid var(--u-black);
}

.trust-item--1 {
  background: rgba(255, 214, 233, 0.68);
  border: 2px solid var(--u-black);
}

.trust-item--2 {
  background: rgba(226, 255, 236, 0.68);
  border: 2px solid var(--u-black);
}

.abilities-view.dark .trust-item--0 {
  background: rgba(56, 189, 248, 0.12);
  border: 2px solid var(--u-black);
}

.abilities-view.dark .trust-item--1 {
  background: rgba(236, 72, 153, 0.12);
  border: 2px solid var(--u-black);
}

.abilities-view.dark .trust-item--2 {
  background: rgba(34, 197, 94, 0.12);
  border: 2px solid var(--u-black);
}

@media (max-width: 900px) {
  .trust-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }
}

.trust-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 14px 14px 16px;
  border-radius: 14px;
  box-shadow:
    0 14px 26px rgba(16, 24, 40, 0.06),
    3px 3px 0px var(--u-black);
}

.trust-icon {
  font-size: 18px;
  /* 让左侧图标与标题文字对齐更自然（“图片部分”整体略下移） */
  margin-top: 2px;
}

.trust-item-title {
  font-size: clamp(17px, 1.1vw, 19px);
  font-weight: 600;
  margin: 0 0 12px;
}

.trust-item-desc {
  font-size: clamp(16px, 1.05vw, 18px);
  color: rgba(51, 50, 46, 0.78);
  line-height: 1.5;
  margin: 0;
}

/* 入口：两个卡片 */
.entry-cards {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 28px;
  margin-top: 24px;
}

.entry-card {
  width: 100%;
  text-align: left;
  background: transparent;
  border-radius: 20px;
  padding: clamp(26px, 3vw, 36px) clamp(18px, 2.3vw, 28px);
  border: 2px solid var(--u-black);
  box-shadow: 6px 6px 0px var(--u-black);
  cursor: pointer;
  min-height: clamp(220px, 26vh, 320px);
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition:
    transform 0.14s ease,
    box-shadow 0.14s ease,
    border-color 0.14s ease;
}

.entry-card--upload {
  background: #e8f6ff; /* 淡蓝 */
}

.entry-card--chat {
  background: #ffd6e9; /* 莫兰迪粉 */
}

.entry-card:focus-visible {
  outline: 3px solid var(--u-black);
  outline-offset: 4px;
}

.entry-card:hover {
  /* hover：硬阴影消失 + 右下位移模拟“按下” */
  box-shadow: none;
  transform: translate(5px, 6px);
}

.abilities-view.dark .entry-card:hover {
  box-shadow:
    0 0 0 1px rgba(140, 212, 203, 0.65),
    0 0 18px rgba(140, 212, 203, 0.35),
    0 0 30px rgba(167, 139, 250, 0.2);
  border-color: rgba(140, 212, 203, 0.72);
  transform: translate(5px, 6px);
}

.entry-card:active {
  transform: translate(3px, 4px);
  box-shadow: none;
}

.entry-card-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.entry-card-title {
  font-size: clamp(22px, 1.6vw, 28px);
  font-weight: 700;
  margin-bottom: 10px;
}

.entry-card-desc {
  font-size: clamp(16px, 1.1vw, 18px);
  color: #555;
  line-height: 1.55;
  margin-bottom: 16px;
}

.abilities-view.dark .entry-card-title {
  color: var(--dm-text);
}

.abilities-view.dark .entry-card-desc {
  color: #cbd5e1;
}

.abilities-view.dark .entry-card--upload {
  background: rgba(56, 189, 248, 0.12);
}

.abilities-view.dark .entry-card--chat {
  background: rgba(236, 72, 153, 0.12);
}

.entry-card-link {
  font-size: clamp(15px, 1vw, 17px);
  color: #409eff;
  font-weight: 500;
}

.abilities-view.dark .entry-card-link {
  color: var(--dm-accent);
}

/* 返回按钮 */
.step-back {
  margin-bottom: 16px;
  font-size: clamp(15px, 0.95vw, 17px);
}

/* 上传页 */
.upload-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.upload-header .page-title {
  margin-bottom: 0;
}

.upload-header .step-back {
  margin-bottom: 0;
}

.upload-panel .page-title {
  /* 标题已由 .upload-header 控制间距 */
  margin-bottom: 0;
}

.upload-intro {
  font-size: clamp(16px, 1.05vw, 18px);
  line-height: 1.65;
  color: #444;
  margin-bottom: 20px;
  max-width: 720px;
}

.abilities-view.dark .upload-intro {
  color: var(--dm-text-secondary);
}

.upload-visual {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 24px;
}

.upload-visual-item {
  padding: 10px 18px;
  background: var(--u-body-bg);
  border-radius: 999px;
  font-size: clamp(15px, 1vw, 17px);
  color: var(--u-black);
  border: var(--u-border);
  box-shadow: 2px 2px 0px var(--u-black);
}

.abilities-view.dark .upload-visual-item {
  background: var(--dm-accent-soft);
  color: var(--dm-accent);
}

.upload-area-wrap {
  margin: 20px 0 28px;
}

.upload-area-wrap .upload-area {
  margin: 0;
}

/* 上传框：复用主界面 HomeView 的“简历上传框”效果 */
.upload-area-wrap :deep(.el-upload) {
  width: 100%;
}

.upload-area-wrap :deep(.el-upload-dragger) {
  width: 100%;
  border: 2px dashed rgba(51, 50, 46, 0.35);
  border-radius: 16px;
  background: rgba(203, 230, 253, 0.72);
  padding: 22px 18px;
  transition:
    border-color 0.2s ease,
    background-color 0.2s ease,
    transform 0.2s ease;
}

.upload-area-wrap :deep(.el-upload-dragger:hover) {
  border-color: rgba(51, 50, 46, 0.62);
  background: rgba(186, 218, 254, 0.82);
  transform: translateY(-1px);
}

.upload-area-wrap :deep(.el-upload__text) {
  color: rgba(51, 50, 46, 0.9);
  font-size: clamp(14px, 0.95vw, 16px);
}

.upload-area-wrap :deep(.el-upload__tip) {
  color: rgba(51, 50, 46, 0.72);
  font-size: clamp(12px, 0.85vw, 14px);
}

.upload-area-wrap :deep(.el-icon--upload) {
  color: rgba(51, 50, 46, 0.55);
  margin-bottom: 8px;
}

.abilities-view.dark :deep(.upload-area .el-upload-dragger) {
  border-color: var(--dm-border);
  background: var(--dm-surface-card);
}

.abilities-view.dark :deep(.upload-area .el-upload-dragger:hover) {
  border-color: var(--dm-border-accent);
  background: var(--dm-surface-elevated);
}

.abilities-view.dark :deep(.upload-area .el-upload__text) {
  color: var(--dm-text);
}

.abilities-view.dark :deep(.upload-area .el-upload__tip),
.abilities-view.dark :deep(.upload-area .el-icon--upload) {
  color: var(--dm-text-secondary);
}

.upload-tips {
  padding-left: 22px;
  margin: 12px 0 0;
  font-size: clamp(15px, 1vw, 17px);
  color: rgba(51, 50, 46, 0.78);
  line-height: 1.6;
}

.abilities-view.dark .upload-tips {
  color: var(--dm-text-secondary);
}

.upload-tips li + li {
  margin-top: 6px;
}

/* Chat 面板 */
.chat-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chat-header {
  margin-bottom: 4px;
}

.chat-header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.chat-header .chat-page-title {
  font-size: var(--fs-h2);
  margin-bottom: 10px;
  margin-right: auto;
  font-weight: var(--fw-heading);
}

.chat-intro {
  font-size: clamp(15px, 1vw, 17px);
  color: rgba(51, 50, 46, 0.78);
  line-height: 1.55;
  margin-bottom: 14px;
}

.abilities-view.dark .chat-intro {
  color: var(--dm-text-secondary);
}

.chat-visual {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 8px;
}

.chat-visual-item {
  padding: 6px 14px;
  background: #f0fdf4;
  border-radius: 999px;
  font-size: clamp(14px, 0.95vw, 16px);
  color: #166534;
}

.abilities-view.dark .chat-visual-item {
  background: rgba(34, 197, 94, 0.2);
  color: #86efac;
}

.abilities-view.dark .chat-header h2 {
  color: var(--dm-text);
}

.abilities-view.dark .chat-window {
  background: var(--dm-surface);
  border: 2px solid var(--u-black);
  box-shadow: 3px 3px 0px var(--u-black);
}

.abilities-view.dark .bubble {
  background: var(--dm-surface-elevated);
  color: var(--dm-text);
}

.abilities-view.dark .chat-message.user .bubble {
  background: var(--dm-accent-soft);
  color: var(--dm-text);
}

.abilities-view.dark .chat-placeholder {
  background: var(--dm-surface);
  color: var(--dm-text-secondary);
}

/* 结果面板夜间模式 */
.abilities-view.dark .result-panel {
  background: var(--dm-bg);
}

.abilities-view.dark .info-card,
.abilities-view.dark .radar-card {
  background: var(--dm-surface);
  border: 2px solid var(--u-black);
  box-shadow: 4px 4px 0 var(--u-black);
  color: var(--dm-text);
}

.abilities-view.dark .info-title,
.abilities-view.dark .radar-title,
.abilities-view.dark .score-label,
.abilities-view.dark .ability-title {
  color: var(--dm-text);
}

.abilities-view.dark .info-line,
.abilities-view.dark .progress-text {
  color: var(--dm-text-secondary);
}

.abilities-view.dark .radar-placeholder {
  background: var(--dm-surface-elevated);
  color: var(--dm-text-secondary);
}

.abilities-view.dark .radar-chart {
  background: var(--dm-surface-elevated);
  border-color: rgba(228, 228, 228, 0.2);
}

.abilities-view.dark .tag {
  background: #4a7a8f;
  color: #fdf8ef;
  border: 2px solid var(--u-black);
  box-shadow: 2px 2px 0 #000000;
}

.abilities-view.dark .score-card,
.abilities-view.dark .ability-card,
.abilities-view.dark .suggest-card {
  border: 2px solid var(--u-black);
  box-shadow: 4px 4px 0 #000000;
}

.abilities-view.dark .result-right > .score-card {
  background: var(--dm-surface);
}

.abilities-view.dark .result-right > .ability-card {
  background: var(--dm-surface-elevated);
}

.abilities-view.dark .result-right > .suggest-card {
  background: var(--dm-surface);
}

.abilities-view.dark .ability-desc {
  color: var(--dm-text-secondary);
}

.chat-window {
  background: #e6f0fa;
  border-radius: 12px;
  padding: 12px 14px;
  min-height: 380px;
  max-height: 480px;
  overflow-y: auto;
  border: 2px solid var(--u-black);
  box-shadow: 3px 3px 0px var(--u-black);
}

.chat-message {
  display: flex;
  gap: 10px;
  margin-bottom: 8px;
}

.chat-message.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  background: #e0e7ff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.bubble {
  max-width: 70%;
  padding: 10px 12px;
  border-radius: 10px;
  font-size: clamp(16px, 1.1vw, 18px);
  background: #e4e9fb;
  border: 1px solid rgba(51, 50, 46, 0.1);
}

.chat-message.user .bubble {
  background: #d4eef5;
  border: 1px solid rgba(51, 50, 46, 0.1);
}

.chat-placeholder {
  margin-top: 8px;
  padding: 8px 10px;
  border-radius: 8px;
  font-size: 12px;
  background: var(--u-bg-normal);
  color: var(--u-placeholder);
  border: 1px dashed rgba(51, 50, 46, 0.2);
}

.chat-input-bar {
  display: flex;
  gap: 10px;
  align-items: center;
}

.chat-input-bar :deep(.el-input__wrapper) {
  border: 2px solid var(--u-black);
  box-shadow: none;
}

.chat-footer {
  margin-top: 4px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: space-between;
  align-items: center;
}

.progress-wrapper {
  min-width: 240px;
}

.progress-text {
  font-size: 12px;
  color: #555;
}

/* 结果面板（学生能力画像）：与整页统一蓝底 */
.result-panel {
  background: var(--abilities-page-bg);
  position: relative;
  padding-bottom: 80px; /* 为右下角按钮留出空间，避免内容被遮挡 */
}

.result-header {
  margin-bottom: 8px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.result-header .step-back {
  margin-bottom: 0;
  align-self: flex-start;
}

.tag {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 999px;
  background: var(--u-uiineed-sticker);
  color: #fdf8ef;
  font-size: clamp(13px, 0.95vw, 15px);
  font-weight: 800;
  border: 2px solid var(--u-black);
  box-shadow: 2px 2px 0 var(--u-black);
}

.result-grid {
  display: grid;
  grid-template-columns: minmax(320px, 0.95fr) minmax(520px, 1.55fr);
  gap: 20px 32px;
  margin-top: 8px;
  align-items: start;
}

.result-left {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-card {
  background: var(--u-bg-normal);
  border-radius: var(--u-border-radius);
  padding: clamp(14px, 1.2vw, 20px);
  border: var(--u-border);
  box-shadow: var(--u-box-shadow);
}

.radar-card {
  background: var(--u-panel);
  border-radius: var(--u-border-radius);
  padding: clamp(14px, 1.2vw, 20px);
  border: var(--u-border);
  box-shadow: var(--u-box-shadow);
}

.info-title {
  font-size: clamp(16px, 1.05vw, 18px);
  margin-bottom: 10px;
  font-weight: 600;
}

.info-stack {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-line {
  margin: 0;
  font-size: clamp(15px, 0.95vw, 17px);
  line-height: 1.55;
}

.radar-title {
  font-size: clamp(16px, 1.05vw, 18px);
  margin-bottom: 8px;
  font-weight: 600;
}

.radar-chart {
  height: clamp(320px, 48vh, 520px);
  min-height: 280px;
  border-radius: var(--u-border-radius);
  background: var(--u-body-bg);
  border: 2px solid rgba(51, 50, 46, 0.12);
  padding: 12px;
  box-sizing: border-box;
}

.abilities-radar-echart {
  width: 100%;
  height: 100%;
  min-height: 260px;
}

.radar-grid {
  fill: transparent;
  stroke: rgba(51, 50, 46, 0.14);
  stroke-width: 1;
}

.radar-axis {
  stroke: rgba(51, 50, 46, 0.12);
  stroke-width: 1;
}

.radar-data {
  fill: rgba(140, 212, 203, 0.42);
}

.radar-data-outline {
  fill: transparent;
  stroke: var(--u-black);
  stroke-width: 1.5;
}

.radar-label {
  font-size: 11px;
  fill: rgba(51, 50, 46, 0.82);
}

.radar-placeholder {
  height: clamp(240px, 26vh, 340px);
  border-radius: var(--u-border-radius);
  background: rgba(232, 246, 255, 0.55);
  border: 2px dashed rgba(51, 50, 46, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: clamp(14px, 0.95vw, 16px);
  color: var(--u-placeholder);
  padding: 12px;
  text-align: center;
}

.result-right {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.score-card,
.ability-card,
.suggest-card {
  border-radius: var(--u-border-radius);
  padding: clamp(14px, 1.2vw, 20px);
  border: var(--u-border);
  box-shadow: var(--u-box-shadow);
}

/* 左栏奶黄系信息 / 右栏浅珊瑚能力条 / 薄荷建议 */
.result-right > .score-card {
  background: var(--u-bg-discard);
}

.result-right > .ability-card {
  background: var(--u-bg-normal);
}

.result-right > .suggest-card {
  background: var(--u-bg-completed);
}

.score-card :deep(.el-progress-bar__inner) {
  background-color: var(--u-bg-submit) !important;
}

.score-card :deep(.el-progress-bar__outer) {
  background-color: rgba(51, 50, 46, 0.1);
  border: 1px solid rgba(51, 50, 46, 0.2);
}

.score-label {
  font-size: clamp(16px, 1.05vw, 18px);
  font-weight: 600;
  margin: 0 0 8px;
}

.score-number {
  font-size: clamp(28px, 2vw, 34px);
  font-weight: 700;
}

.score-sub {
  font-size: clamp(14px, 0.95vw, 16px);
  margin-bottom: 6px;
}

.ability-title {
  font-size: clamp(16px, 1.05vw, 18px);
  font-weight: 600;
  margin: 0 0 10px;
}

.ability-item + .ability-item {
  margin-top: 8px;
}

.ability-header {
  display: flex;
  justify-content: space-between;
  font-size: clamp(16px, 1.05vw, 18px);
}

.ability-desc {
  font-size: clamp(15px, 0.95vw, 17px);
  color: #555;
  margin-top: 4px;
  line-height: 1.45;
}

:deep(.ability-progress .el-progress-bar__outer) {
  background-color: rgba(51, 50, 46, 0.1);
  border: 1px solid rgba(51, 50, 46, 0.18);
}

.suggest-title {
  font-size: clamp(17px, 1.1vw, 19px);
  margin-bottom: 6px;
}

.suggest-card ul {
  padding-left: 20px;
  margin: 0;
  font-size: clamp(16px, 1.05vw, 18px);
}

.result-actions {
  position: absolute;
  right: clamp(16px, 2vw, 32px);
  bottom: clamp(16px, 1.5vw, 24px);
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
}

@media (min-width: 1200px) {
  .result-panel {
    padding-left: clamp(24px, 2.2vw, 40px);
    padding-right: clamp(24px, 2.2vw, 40px);
  }

  .result-grid {
    grid-template-columns: minmax(360px, 1fr) minmax(680px, 1.75fr);
    gap: 24px 40px;
  }
}

/* ---------------- 岗位匹配与职业规划报告样式（从 CareerReportView 合并） ---------------- */
.match-panel {
  background: var(--abilities-page-bg);
}

.match-header {
  margin-bottom: 12px;
}

/* 岗位匹配页：标题与个人信息栏同级字重 */
.match-panel .section-title {
  font-size: clamp(16px, 1.05vw, 18px);
  font-weight: 600;
  margin: 0 0 12px;
  color: var(--u-black);
}

.student-tag {
  display: inline-block;
  margin-top: 6px;
  padding: 6px 14px;
  font-size: clamp(15px, 1vw, 17px);
  font-weight: 700;
  color: var(--u-black);
  /* 粉轴：标签条 */
  background: color-mix(in srgb, var(--u-bg-submit) 78%, var(--u-panel));
  border: var(--u-border);
  border-radius: 999px;
  box-shadow: 2px 2px 0 var(--u-black);
}

.recommend-section {
  margin-top: 10px;
  padding: 14px 16px 18px;
  /* 蓝轴：页面主色 body-bg */
  background: color-mix(in srgb, var(--u-body-bg) 70%, var(--u-panel));
  border: var(--u-border);
  border-radius: var(--u-border-radius);
  box-shadow: var(--u-box-shadow);
}

.job-table {
  margin-top: 10px;
  /* 蓝区表格：与推荐卡片同系 */
  --el-table-border-color: rgba(51, 50, 46, 0.42);
  --el-table-bg-color: color-mix(in srgb, var(--u-body-bg) 48%, var(--u-bg-normal));
  --el-table-tr-bg-color: color-mix(in srgb, var(--u-body-bg) 48%, var(--u-bg-normal));
  --el-table-row-hover-bg-color: rgba(140, 212, 203, 0.32);
}

.match-panel .job-table :deep(.el-table) {
  border-radius: calc(var(--u-border-radius) - 4px);
  overflow: hidden;
  border: 2px solid rgba(51, 50, 46, 0.25);
  box-shadow: 3px 3px 0 rgba(51, 50, 46, 0.10);
}

.match-panel .job-table :deep(th.el-table__cell) {
  background: color-mix(in srgb, var(--u-body-bg) 58%, var(--u-panel)) !important;
  color: var(--u-black);
  font-weight: 800;
  border-color: rgba(51, 50, 46, 0.55) !important;
  border-style: solid !important;
  border-width: 2px !important;
  border-right: 2px solid rgba(51, 50, 46, 0.55) !important;
  border-bottom: 2px solid rgba(51, 50, 46, 0.7) !important;
}

.match-panel .job-table :deep(td.el-table__cell) {
  border-color: rgba(51, 50, 46, 0.38) !important;
  background: color-mix(in srgb, var(--u-body-bg) 58%, var(--u-panel)) !important;
  border-style: solid !important;
  border-width: 2px !important;
  border-right: 2px solid rgba(51, 50, 46, 0.38) !important;
  border-bottom: 2px solid rgba(51, 50, 46, 0.7) !important;
}

.match-panel .job-table :deep(.el-table__body tr.el-table__row--striped td.el-table__cell) {
  background: color-mix(in srgb, var(--u-body-bg) 38%, var(--u-bg-normal)) !important;
}

.match-panel .job-table :deep(.el-table__body tr.el-table__row--hover td.el-table__cell) {
  background: rgba(140, 212, 203, 0.34) !important;
}

.other-jobs-collapse {
  margin-top: 14px;
  border: none;
  --el-collapse-border-color: transparent;
}

.match-panel .other-jobs-collapse :deep(.el-collapse-item__header) {
  margin-top: 4px;
  padding: 10px 14px;
  min-height: 48px;
  font-size: clamp(15px, 1vw, 17px);
  font-weight: 800;
  color: var(--u-black);
  /* 绿轴：薄荷 completed */
  background: color-mix(in srgb, var(--u-bg-completed) 74%, var(--u-panel));
  border: var(--u-border);
  border-radius: var(--u-border-radius);
  box-shadow: var(--u-box-shadow-sm);
}

.match-panel .other-jobs-collapse :deep(.el-collapse-item__arrow) {
  font-weight: 800;
}

.match-panel .other-jobs-collapse :deep(.el-collapse-item__wrap) {
  border: none;
  background: color-mix(in srgb, var(--u-body-bg) 70%, var(--u-panel));
}

.match-panel .other-jobs-collapse :deep(.el-collapse-item__content) {
  padding: 12px 0 4px;
  background: color-mix(in srgb, var(--u-body-bg) 70%, var(--u-panel));
}

.current-job-section {
  margin-top: 22px;
}

.match-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 8px 0 12px;
  font-size: clamp(16px, 1.05vw, 18px);
  font-weight: 600;
}

.match-summary :deep(.el-progress-bar__inner) {
  background-color: var(--u-completed) !important;
}

.match-summary :deep(.el-progress-bar__outer) {
  background-color: rgba(51, 50, 46, 0.1);
  border: 1px solid rgba(51, 50, 46, 0.2);
  border-radius: 999px;
}

.match-hint {
  font-size: clamp(15px, 1vw, 17px);
  color: var(--u-black);
  line-height: 1.6;
  margin-bottom: 14px;
  padding: 12px 14px;
  /* 粉轴：说明卡 */
  background: color-mix(in srgb, var(--u-bg-submit) 72%, var(--u-panel));
  border: var(--u-border);
  border-radius: var(--u-border-radius);
  box-shadow: var(--u-box-shadow-sm);
}

.weight-hint {
  font-size: clamp(15px, 0.95vw, 17px);
  color: rgba(51, 50, 46, 0.72);
  margin-top: 8px;
}

.compare-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 14px 20px;
}

.compare-card {
  border-radius: var(--u-border-radius);
  padding: 12px 14px;
  border: var(--u-border);
  box-shadow: var(--u-box-shadow);
  overflow: visible;
}

/* 黄轴：雷达卡 */
.compare-card--radar {
  background: color-mix(in srgb, var(--u-bg-normal) 76%, var(--u-panel));
}

/* 绿轴：四维度列表卡 */
.compare-grid .compare-card:nth-child(2) {
  background: color-mix(in srgb, var(--u-bg-completed) 72%, var(--u-panel));
}

.compare-title {
  font-size: clamp(15px, 1vw, 17px);
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--u-black);
}

.compare-placeholder {
  height: 180px;
  border-radius: var(--u-border-radius);
  background: var(--u-body-bg);
  border: 2px dashed rgba(51, 50, 46, 0.22);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  color: var(--u-placeholder);
  text-align: center;
  padding: 10px;
}

.compare-card--radar .compare-radar-chart {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  min-height: 390px;
}

.compare-radar-echart {
  width: 100%;
  max-width: 100%;
  height: clamp(340px, 44vh, 500px);
  min-height: 320px;
  margin-inline: auto;
}

.match-radar-job {
  fill: rgba(255, 214, 233, 0.55);
  stroke: var(--u-black);
  stroke-width: 1.25;
}

.match-radar-student {
  fill: rgba(140, 212, 203, 0.42);
  stroke: var(--u-black);
  stroke-width: 1.25;
}

.compare-radar-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 14px 20px;
  justify-content: center;
  font-size: clamp(13px, 0.9vw, 15px);
  font-weight: 600;
  color: var(--u-black);
}

.compare-radar-legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.compare-radar-dot {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  border: 1px solid var(--u-black);
}

.compare-radar-dot--job {
  background: rgba(255, 214, 233, 0.85);
}

.compare-radar-dot--student {
  background: rgba(140, 212, 203, 0.85);
}


.compare-list {
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: clamp(16px, 1.05vw, 18px);
}

.compare-list li + li {
  margin-top: 12px;
}

.compare-list-item {
  padding: 10px 12px;
  border-radius: 10px;
  background: color-mix(in srgb, var(--u-body-bg) 55%, var(--u-panel));
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
  font-size: clamp(14px, 0.95vw, 16px);
  color: #555;
}

.dim-requirement {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dim-requirement-label {
  font-size: clamp(12px, 0.82vw, 13px);
  font-weight: 600;
  color: var(--u-placeholder, #888);
  text-transform: none;
}

.dim-requirement-text {
  margin: 0;
  font-size: clamp(14px, 0.92vw, 16px);
  line-height: 1.65;
  color: #444;
}

.dim-requirement-text--empty {
  color: var(--u-placeholder, #888);
}

.dim-requirement-text-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 4px;
}

.analysis-point-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 0 0 12px;
}

.analysis-point {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 12px;
  background: var(--u-bg-normal);
  border-radius: 10px;
  border: 1px solid color-mix(in srgb, var(--u-black) 10%, transparent);
}

.analysis-point--compact {
  padding: 8px 10px;
}

.analysis-point-tag {
  flex-shrink: 0;
  min-width: 1.75rem;
  justify-content: center;
  font-weight: 700;
}

.analysis-point-text {
  margin: 0;
  flex: 1;
  min-width: 0;
  font-size: clamp(14px, 0.92vw, 16px);
  line-height: 1.65;
  color: #444;
}

.match-analysis-block {
  position: relative;
  min-height: 140px;
}

.ai-thinking-loader {
  border: 1px solid rgba(99, 191, 183, 0.35);
  background: linear-gradient(140deg, rgba(236, 253, 245, 0.72), rgba(239, 246, 255, 0.78));
  border-radius: 12px;
  padding: 14px 16px 16px;
  box-shadow: 0 10px 28px rgba(15, 118, 110, 0.08);
}

.ai-thinking-loader__head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.ai-thinking-loader__dot {
  width: 9px;
  height: 9px;
  border-radius: 999px;
  background: #14b8a6;
  box-shadow: 0 0 0 0 rgba(20, 184, 166, 0.45);
  animation: aiThinkingPulse 1.6s ease-out infinite;
}

.ai-thinking-loader__title {
  font-size: clamp(14px, 0.96vw, 16px);
  font-weight: 600;
  color: #0f766e;
  letter-spacing: 0.2px;
}

.ai-thinking-loader__skeleton {
  display: flex;
  flex-direction: column;
}

.analysis-empty {
  margin: 0 0 12px;
  font-size: clamp(14px, 0.92vw, 16px);
  color: var(--u-placeholder, #888);
}

.detail-analysis {
  margin-top: 16px;
  padding: 12px 14px;
  font-size: clamp(16px, 1.05vw, 18px);
  line-height: 1.5;
  /* 蓝轴：与推荐区呼应 */
  background: color-mix(in srgb, var(--u-body-bg) 48%, var(--u-panel));
  border: var(--u-border);
  border-radius: var(--u-border-radius);
  box-shadow: var(--u-box-shadow-sm);
}

.section-subtitle {
  font-weight: 600;
  font-size: clamp(16px, 1.05vw, 18px);
  margin: 8px 0 6px;
  color: var(--u-black);
}

.action-row {
  margin-top: 12px;
  text-align: right;
}

.report-bottom-actions {
  margin-top: 14px;
  display: flex;
  justify-content: center;
}

/* 报告样式：字号与首页 section-title / section-desc、能力页正文对齐 */
.report-panel {
  background: var(--abilities-page-bg);
}

.report-panel .page-title {
  font-size: clamp(28px, 2.2vw, 38px);
  font-weight: 700;
  margin-bottom: 8px;
  line-height: 1.2;
  color: var(--u-black);
}

.report-panel .report-subtitle {
  font-size: clamp(17px, 1.1vw, 20px);
  line-height: 1.6;
  color: var(--u-placeholder);
  margin: 0;
}

/* 卡片内节标题：与个人信息栏 / 对比卡标题同级，避免压过正文 */
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
  /* 黄·绿·粉循环，掺白面板略淡 */
  background: color-mix(in srgb, var(--u-bg-normal) 62%, var(--u-panel));
  border-radius: var(--u-border-radius);
  padding: clamp(14px, 1.2vw, 18px) clamp(14px, 1.2vw, 18px);
  border: var(--u-border);
  box-shadow: var(--u-box-shadow);
}

.report-panel .report-section:nth-of-type(3n + 2) {
  background: color-mix(in srgb, var(--u-bg-completed) 58%, var(--u-panel));
}

.report-panel .report-section:nth-of-type(3n) {
  background: color-mix(in srgb, var(--u-bg-submit) 56%, var(--u-panel));
}

/* 正文：与 .info-line / 首页段落同级 */
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

.report-panel .hint-text {
  font-size: clamp(15px, 0.95vw, 17px);
  color: var(--u-placeholder);
  margin-bottom: 10px;
  line-height: 1.6;
}

.report-panel .path-placeholder {
  margin-top: 8px;
  border-radius: var(--u-border-radius);
  border: 2px dashed color-mix(in srgb, var(--u-black) 26%, transparent);
  padding: 14px 16px;
  font-size: clamp(15px, 0.95vw, 17px);
  color: var(--u-placeholder);
  /* 与「粉」轴一致的浅占位底 */
  background: color-mix(in srgb, var(--u-bg-submit) 22%, var(--u-panel));
  line-height: 1.6;
}

.report-panel .path-figure {
  margin: 10px 0 0;
}

.report-panel .path-img {
  width: 100%;
  max-width: 980px;
  display: block;
  border-radius: var(--u-border-radius);
  border: var(--u-border);
  box-shadow: var(--u-box-shadow-sm);
}

.report-panel .path-caption,
.report-panel .path-text,
.report-panel .empty-text,
.report-panel .multi-line-text {
  margin-top: 8px;
  font-size: clamp(15px, 0.95vw, 17px);
  color: var(--u-placeholder);
  line-height: 1.7;
}

.report-panel .multi-line-text {
  white-space: pre-line;
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
  /* 与岗位匹配页 job-table 同一套 Uiineed 表配色 */
  --el-table-border-color: rgba(51, 50, 46, 0.42);
  --el-table-bg-color: color-mix(in srgb, var(--u-bg-normal) 64%, var(--u-panel));
  --el-table-tr-bg-color: color-mix(in srgb, var(--u-bg-normal) 64%, var(--u-panel));
  --el-table-row-hover-bg-color: rgba(208, 244, 240, 0.18);
}

.report-panel .plan-table :deep(.el-table) {
  border-radius: calc(var(--u-border-radius) - 4px);
  overflow: hidden;
  border: 2px solid rgba(51, 50, 46, 0.25);
  box-shadow: 3px 3px 0 rgba(51, 50, 46, 0.1);
}

.report-panel .plan-table :deep(.el-table th),
.report-panel .plan-table :deep(.el-table td) {
  font-size: inherit;
}

.report-panel .plan-table :deep(th.el-table__cell) {
  background: color-mix(in srgb, var(--u-bg-normal) 64%, var(--u-panel)) !important;
  color: var(--u-black);
  font-weight: 800;
  font-size: clamp(14px, 0.92vw, 16px);
  border-color: rgba(51, 50, 46, 0.55) !important;
  border-style: solid !important;
  border-width: 2px !important;
  border-right: 2px solid rgba(51, 50, 46, 0.55) !important;
  border-bottom: 2px solid rgba(51, 50, 46, 0.7) !important;
}

.report-panel .plan-table :deep(td.el-table__cell) {
  background: color-mix(in srgb, var(--u-bg-normal) 64%, var(--u-panel)) !important;
  border-color: rgba(51, 50, 46, 0.38) !important;
  border-style: solid !important;
  border-width: 2px !important;
  border-right: 2px solid rgba(51, 50, 46, 0.38) !important;
  border-bottom: 2px solid rgba(51, 50, 46, 0.7) !important;
}

.report-panel .plan-table :deep(.el-table__body tr.el-table__row--striped td.el-table__cell) {
  background: rgba(208, 244, 240, 0.12) !important;
}

.report-panel .plan-table :deep(.el-table__body tr.el-table__row--hover td.el-table__cell) {
  background: rgba(208, 244, 240, 0.22) !important;
}

/* 绿卡片内表格：薄荷底 + 条纹 */
.report-panel .report-section:nth-of-type(3n + 2) .plan-table {
  --el-table-bg-color: color-mix(in srgb, var(--u-bg-completed) 60%, var(--u-panel));
  --el-table-tr-bg-color: color-mix(in srgb, var(--u-bg-completed) 60%, var(--u-panel));
  --el-table-row-hover-bg-color: rgba(140, 212, 203, 0.16);
}

.report-panel .report-section:nth-of-type(3n + 2) .plan-table :deep(th.el-table__cell),
.report-panel .report-section:nth-of-type(3n + 2) .plan-table :deep(td.el-table__cell) {
  background: color-mix(in srgb, var(--u-bg-completed) 60%, var(--u-panel)) !important;
}

.report-panel .report-section:nth-of-type(3n + 2) .plan-table :deep(.el-table__body tr.el-table__row--striped td.el-table__cell) {
  background: color-mix(in srgb, var(--u-bg-completed) 42%, var(--u-bg-normal)) !important;
}

.report-panel .report-section:nth-of-type(3n + 2) .plan-table :deep(.el-table__body tr.el-table__row--hover td.el-table__cell) {
  background: rgba(140, 212, 203, 0.2) !important;
}

/* 粉卡片内表格：浅粉底 + 条纹 */
.report-panel .report-section:nth-of-type(3n) .plan-table {
  --el-table-bg-color: color-mix(in srgb, var(--u-bg-submit) 58%, var(--u-panel));
  --el-table-tr-bg-color: color-mix(in srgb, var(--u-bg-submit) 58%, var(--u-panel));
  --el-table-row-hover-bg-color: rgba(255, 214, 233, 0.3);
}

.report-panel .report-section:nth-of-type(3n) .plan-table :deep(th.el-table__cell),
.report-panel .report-section:nth-of-type(3n) .plan-table :deep(td.el-table__cell) {
  background: color-mix(in srgb, var(--u-bg-submit) 58%, var(--u-panel)) !important;
}

.report-panel .report-section:nth-of-type(3n) .plan-table :deep(.el-table__body tr.el-table__row--striped td.el-table__cell) {
  background: color-mix(in srgb, var(--u-bg-submit) 36%, var(--u-panel)) !important;
}

.report-panel .report-section:nth-of-type(3n) .plan-table :deep(.el-table__body tr.el-table__row--hover td.el-table__cell) {
  background: rgba(255, 214, 233, 0.38) !important;
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

.dialog-label {
  margin: 8px 0 4px;
  font-size: clamp(15px, 0.95vw, 17px);
  font-weight: 600;
}

.orig-metric {
  padding: 8px 10px;
  /* Uiineed completed 薄荷底 */
  background: color-mix(in srgb, var(--u-bg-completed) 28%, var(--u-panel));
  border: var(--u-border);
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

.abilities-view.dark .student-tag,
.abilities-view.dark .weight-hint,
.abilities-view.dark .dim-student,
.abilities-view.dark .dim-requirement-text {
  color: var(--dm-text-secondary);
}

.abilities-view.dark .dim-requirement-label {
  color: var(--dm-text-muted, var(--dm-text-secondary));
}

.abilities-view.dark .compare-list-item {
  background: color-mix(in srgb, var(--dm-panel-bg, #1a1d24) 92%, transparent);
  border-color: color-mix(in srgb, var(--dm-border, #333) 70%, transparent);
}

.abilities-view.dark .report-panel .report-subtitle,
.abilities-view.dark .report-panel .hint-text {
  color: var(--dm-text-secondary);
}

.abilities-view.dark .student-tag {
  color: var(--dm-text);
  background: color-mix(in srgb, var(--u-bg-submit) 72%, var(--u-panel));
  border: 2px solid var(--u-black);
  box-shadow: 2px 2px 0 #000000;
}

.abilities-view.dark .match-panel .section-title {
  color: var(--dm-text);
}

.abilities-view.dark .match-hint {
  color: var(--dm-text-secondary);
  background: color-mix(in srgb, var(--u-bg-submit) 68%, var(--u-panel));
  border: 2px solid var(--u-black);
  box-shadow: 2px 2px 0 #000000;
}

.abilities-view.dark .recommend-section {
  background: color-mix(in srgb, var(--u-body-bg) 76%, var(--u-panel));
  border: 2px solid var(--u-black);
  box-shadow: 4px 4px 0 #000000;
}

.abilities-view.dark .match-panel .job-table :deep(th.el-table__cell) {
  background: color-mix(in srgb, var(--u-body-bg) 62%, var(--u-panel)) !important;
  color: var(--dm-text) !important;
  border-color: var(--dm-border) !important;
  border-style: solid !important;
  border-width: 2px !important;
  border-right: 2px solid var(--dm-border) !important;
  border-bottom: 2px solid var(--dm-border) !important;
}

.abilities-view.dark .match-panel .job-table :deep(td.el-table__cell) {
  background: color-mix(in srgb, var(--u-body-bg) 62%, var(--u-panel)) !important;
  border-color: var(--dm-border) !important;
  border-style: solid !important;
  border-width: 2px !important;
  border-right: 2px solid var(--dm-border) !important;
  border-bottom: 2px solid var(--dm-border) !important;
}

.abilities-view.dark .match-panel .job-table :deep(.el-table__body tr.el-table__row--striped td.el-table__cell) {
  background: color-mix(in srgb, var(--u-body-bg) 42%, var(--u-bg-normal)) !important;
}

.abilities-view.dark .match-panel .job-table :deep(.el-table__body tr.el-table__row--hover td.el-table__cell) {
  background: rgba(126, 179, 176, 0.22) !important;
}

.abilities-view.dark .match-panel .other-jobs-collapse :deep(.el-collapse-item__header) {
  background: color-mix(in srgb, var(--u-bg-completed) 72%, var(--u-panel));
  color: var(--dm-text);
  border: 2px solid var(--u-black);
  box-shadow: 2px 2px 0 #000000;
}

.abilities-view.dark .match-panel .other-jobs-collapse :deep(.el-collapse-item__wrap) {
  background: color-mix(in srgb, var(--u-body-bg) 76%, var(--u-panel));
}

.abilities-view.dark .match-panel .other-jobs-collapse :deep(.el-collapse-item__content) {
  background: color-mix(in srgb, var(--u-body-bg) 76%, var(--u-panel));
}

.abilities-view.dark .compare-card {
  border: 2px solid var(--u-black);
  box-shadow: 4px 4px 0 #000000;
}

.abilities-view.dark .compare-card--radar {
  background: color-mix(in srgb, var(--u-bg-normal) 74%, var(--u-panel));
}

.abilities-view.dark .compare-grid .compare-card:nth-child(2) {
  background: color-mix(in srgb, var(--u-bg-completed) 70%, var(--u-panel));
}

.abilities-view.dark .compare-title {
  color: var(--dm-text);
}

.abilities-view.dark .compare-placeholder {
  background: var(--dm-surface);
  color: var(--dm-text-secondary);
  border-color: var(--dm-border);
}

.abilities-view.dark .match-radar-job {
  fill: rgba(236, 72, 153, 0.28);
  stroke: var(--u-black);
}

.abilities-view.dark .match-radar-student {
  fill: rgba(52, 211, 153, 0.28);
  stroke: var(--u-black);
}

.abilities-view.dark .compare-radar-legend {
  color: var(--dm-text);
}

.abilities-view.dark .compare-radar-dot--job {
  background: rgba(236, 72, 153, 0.55);
}

.abilities-view.dark .compare-radar-dot--student {
  background: rgba(52, 211, 153, 0.55);
}

.abilities-view.dark .detail-analysis {
  background: color-mix(in srgb, var(--u-body-bg) 52%, var(--u-panel));
  border: 2px solid var(--u-black);
  box-shadow: 4px 4px 0 #000000;
  color: var(--dm-text-secondary);
}

.abilities-view.dark .section-subtitle {
  color: var(--dm-text);
}

.abilities-view.dark .analysis-point {
  background: color-mix(in srgb, var(--u-bg-normal) 70%, var(--u-panel));
  border-color: var(--dm-border, rgba(255, 255, 255, 0.14));
}

.abilities-view.dark .ai-thinking-loader {
  border-color: color-mix(in srgb, var(--u-completed) 34%, var(--dm-border));
  background: linear-gradient(
    145deg,
    color-mix(in srgb, var(--dm-surface-card) 84%, rgba(15, 118, 110, 0.28)),
    color-mix(in srgb, var(--dm-surface-elevated) 90%, rgba(37, 99, 235, 0.2))
  );
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.28);
}

.abilities-view.dark .ai-thinking-loader__title {
  color: color-mix(in srgb, #99f6e4 72%, var(--dm-text));
}

.abilities-view.dark .analysis-point-text,
.abilities-view.dark .dim-requirement-text {
  color: var(--dm-text, #e8e8e8);
}

.abilities-view.dark .dim-requirement-text--empty,
.abilities-view.dark .analysis-empty {
  color: var(--dm-text-secondary, #a3a3a3);
}

.abilities-view.dark .report-panel {
  background: var(--dm-bg);
}

.abilities-view.dark .report-panel .page-title,
.abilities-view.dark .report-panel .section-title {
  color: var(--dm-text);
}

.abilities-view.dark .report-section {
  border: 2px solid var(--u-black);
  box-shadow: 4px 4px 0 #000000;
}

.abilities-view.dark .report-panel .report-section:nth-of-type(3n + 1) {
  background: color-mix(in srgb, var(--u-bg-normal) 66%, var(--u-panel));
}

.abilities-view.dark .report-panel .report-section:nth-of-type(3n + 2) {
  background: color-mix(in srgb, var(--u-bg-completed) 62%, var(--u-panel));
}

.abilities-view.dark .report-panel .report-section:nth-of-type(3n) {
  background: color-mix(in srgb, var(--u-bg-submit) 60%, var(--u-panel));
}

.abilities-view.dark .report-panel .report-section > p,
.abilities-view.dark .report-panel .report-section li {
  color: var(--dm-text-secondary);
}

@keyframes aiThinkingPulse {
  0% {
    transform: scale(0.94);
    box-shadow: 0 0 0 0 rgba(20, 184, 166, 0.46);
  }
  70% {
    transform: scale(1);
    box-shadow: 0 0 0 11px rgba(20, 184, 166, 0);
  }
  100% {
    transform: scale(0.94);
    box-shadow: 0 0 0 0 rgba(20, 184, 166, 0);
  }
}

.abilities-view.dark .report-panel .path-placeholder {
  background: color-mix(in srgb, var(--u-bg-submit) 22%, var(--u-panel));
  border-color: var(--dm-border);
  color: var(--dm-text-secondary);
}

.abilities-view.dark .report-panel .path-img {
  border-color: var(--dm-border);
}

.abilities-view.dark .report-panel .path-caption,
.abilities-view.dark .report-panel .path-text,
.abilities-view.dark .report-panel .empty-text,
.abilities-view.dark .report-panel .multi-line-text {
  color: var(--dm-text-secondary);
}

.abilities-view.dark .report-panel .subheading {
  color: var(--dm-text);
}

.abilities-view.dark .suggest-list {
  color: var(--dm-text-secondary);
}

.abilities-view.dark .metric-text,
.abilities-view.dark .orig-metric,
.abilities-view.dark .dialog-label {
  color: var(--dm-text);
}

.abilities-view.dark .orig-metric {
  background: color-mix(in srgb, var(--u-bg-completed) 32%, var(--u-panel));
  border-color: var(--dm-border);
}

.abilities-view.dark .report-panel .plan-table :deep(th.el-table__cell) {
  background: var(--dm-surface-elevated) !important;
  color: var(--dm-text) !important;
  border-color: var(--dm-border) !important;
  border-style: solid !important;
  border-width: 2px !important;
  border-right: 2px solid var(--dm-border) !important;
  border-bottom: 2px solid var(--dm-border) !important;
}

.abilities-view.dark .report-panel .plan-table :deep(td.el-table__cell) {
  background: var(--dm-surface) !important;
  border-color: var(--dm-border) !important;
  border-style: solid !important;
  border-width: 2px !important;
  border-right: 2px solid var(--dm-border) !important;
  border-bottom: 2px solid var(--dm-border) !important;
}

.abilities-view.dark .report-panel .plan-table :deep(.el-table__body tr.el-table__row--striped td.el-table__cell) {
  background: rgba(255, 255, 255, 0.04) !important;
}

.abilities-view.dark .report-panel .plan-table {
  --el-table-bg-color: var(--dm-surface);
  --el-table-tr-bg-color: var(--dm-surface);
  --el-table-row-hover-bg-color: rgba(208, 244, 240, 0.08);
}

.abilities-view.dark .report-panel .plan-table :deep(.el-table__body tr.el-table__row--hover td.el-table__cell) {
  background: rgba(208, 244, 240, 0.07) !important;
}

.abilities-view.dark .report-panel .report-section:nth-of-type(3n + 2) .plan-table {
  --el-table-bg-color: color-mix(in srgb, var(--u-bg-completed) 64%, var(--u-panel));
  --el-table-tr-bg-color: color-mix(in srgb, var(--u-bg-completed) 64%, var(--u-panel));
  --el-table-row-hover-bg-color: rgba(126, 179, 176, 0.12);
}

.abilities-view.dark .report-panel .report-section:nth-of-type(3n + 2) .plan-table :deep(th.el-table__cell),
.abilities-view.dark .report-panel .report-section:nth-of-type(3n + 2) .plan-table :deep(td.el-table__cell) {
  background: color-mix(in srgb, var(--u-bg-completed) 64%, var(--u-panel)) !important;
}

.abilities-view.dark .report-panel .report-section:nth-of-type(3n + 2) .plan-table :deep(.el-table__body tr.el-table__row--striped td.el-table__cell) {
  background: color-mix(in srgb, var(--u-bg-completed) 48%, var(--u-panel)) !important;
}

.abilities-view.dark .report-panel .report-section:nth-of-type(3n + 2) .plan-table :deep(.el-table__body tr.el-table__row--hover td.el-table__cell) {
  background: rgba(126, 179, 176, 0.12) !important;
}

.abilities-view.dark .report-panel .report-section:nth-of-type(3n) .plan-table {
  --el-table-bg-color: color-mix(in srgb, var(--u-bg-submit) 62%, var(--u-panel));
  --el-table-tr-bg-color: color-mix(in srgb, var(--u-bg-submit) 62%, var(--u-panel));
  --el-table-row-hover-bg-color: rgba(192, 132, 184, 0.1);
}

.abilities-view.dark .report-panel .report-section:nth-of-type(3n) .plan-table :deep(th.el-table__cell),
.abilities-view.dark .report-panel .report-section:nth-of-type(3n) .plan-table :deep(td.el-table__cell) {
  background: color-mix(in srgb, var(--u-bg-submit) 62%, var(--u-panel)) !important;
}

.abilities-view.dark .report-panel .report-section:nth-of-type(3n) .plan-table :deep(.el-table__body tr.el-table__row--striped td.el-table__cell) {
  background: color-mix(in srgb, var(--u-bg-submit) 44%, var(--u-panel)) !important;
}

.abilities-view.dark .report-panel .report-section:nth-of-type(3n) .plan-table :deep(.el-table__body tr.el-table__row--hover td.el-table__cell) {
  background: rgba(192, 132, 184, 0.1) !important;
}

@media (max-width: 900px) {
  .nav {
    display: none;
  }

  .page-scroll {
    padding-inline: 16px;
  }

  /* 小屏：两张入口卡片改为上下堆叠 */
  .entry-cards {
    grid-template-columns: 1fr;
    gap: 18px;
  }

  .result-grid {
    grid-template-columns: 1fr;
  }

  .compare-card--radar .compare-radar-chart {
    min-height: 330px;
  }

  .compare-radar-echart {
    max-width: 100%;
    height: clamp(300px, 48vh, 420px);
    min-height: 280px;
  }
}
</style>