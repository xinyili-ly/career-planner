<template>
  <div class="abilities-view" :class="theme">
    <AppHeader />

    <main class="page-scroll">
      <!-- 步骤一：选择入口（上传 or AI 对话） -->
      <section v-if="step === 'entry'" class="panel entry-panel">
        <div class="panel-header">
          <h1 class="page-title">欢迎来到简历智评中心</h1>
          <p class="page-intro">
            学生就业能力来源支持简历上传或对话录入。通过大模型将数据拆解为多维度能力画像，
            并对完整度、竞争力进行评分，为后续人岗匹配与生涯报告提供依据。
          </p>
        </div>

        <div class="entry-cards">
          <button type="button" class="entry-card entry-card--upload" @click="step = 'upload'">
            <div class="entry-card-icon">📄</div>
            <h3 class="entry-card-title">上传解析简历</h3>
            <p class="entry-card-desc">已有简历文件？上传后由系统智能解析，快速生成能力画像与评分。</p>
            <span class="entry-card-link">去上传 →</span>
          </button>
          <button type="button" class="entry-card entry-card--chat" @click="goToChat">
            <div class="entry-card-icon">💬</div>
            <h3 class="entry-card-title">AI 对话获取</h3>
            <p class="entry-card-desc">暂无完整简历？通过多轮对话逐步填写，由 AI 帮你整理成能力画像。</p>
            <span class="entry-card-link">开始对话 →</span>
          </button>
        </div>

        <section class="trust-panel trust-panel--entry">
          <h3 class="trust-title">专业可靠 · 深度理解你的简历</h3>
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
          <a href="javascript:void(0)" class="link-text">查看参考文献</a>
        </section>

      </section>

      <!-- 上传解析简历：仅上传相关 -->
      <section v-else-if="step === 'upload'" class="panel upload-panel">
        <el-button class="step-back u-btn u-btn--text" text @click="step = 'entry'">← 返回选择</el-button>
        <h1 class="page-title">上传解析简历</h1>
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
        <el-button class="step-back u-btn u-btn--text" text @click="step = 'entry'">← 返回选择</el-button>
        <header class="chat-header">
          <h2>AI 对话引导 · 简历录入</h2>
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
          <div class="chat-message bot">
            <div class="avatar">🤖</div>
            <div class="bubble">
              你好！我是你的职业规划助手，让我们一步步完成你的简历信息。
              请问你的姓名是什么？
            </div>
          </div>

          <div class="chat-message user">
            <div class="avatar">👤</div>
            <div class="bubble">张三</div>
          </div>

          <div class="chat-message bot">
            <div class="avatar">🤖</div>
            <div class="bubble">好的，张三。你的专业是什么？</div>
          </div>

          <div class="chat-message user">
            <div class="avatar">👤</div>
            <div class="bubble">计算机科学与技术</div>
          </div>

          <!-- 预留：接入智能体问题模板后，可用 v-for 渲染更多问答 -->
          <div class="chat-placeholder">
            继续回答上方助手的问题，或在此处接入你的 AI 问题模板与答案列表。
          </div>
        </div>

        <div class="chat-input-bar">
          <el-input
            v-model="chatInput"
            placeholder="在这里输入你的回答（后续可替换为真实 AI 对话接口）"
            @keyup.enter="sendChat"
          />
          <el-button class="u-btn u-btn--primary" type="primary" @click="sendChat">发送</el-button>
        </div>

        <div class="chat-footer">
          <div class="progress-wrapper">
            <span>进度条</span>
            <el-progress :percentage="progress" :stroke-width="12" />
            <span class="progress-text">{{ progress }}%（示例 3 / 20 项）</span>
          </div>
          <el-button class="u-btn u-btn--success" type="success" @click="finishChat">
            收集完成，开始构建学生能力画像
          </el-button>
        </div>

      </section>

      <!-- 步骤三：学生就业能力画像（对应第三张图） -->
      <section v-else-if="step === 'result'" class="panel result-panel">
        <header class="result-header">
          <span class="tag">分析完成</span>
        </header>

        <div class="result-grid">
          <aside class="result-left">
            <div class="info-card">
              <p class="info-title">个人信息栏</p>
              <p class="info-line">
                {{ profile.name }} · {{ profile.school }} · {{ profile.major }}
              </p>
              <p class="info-line">
                简历完整度：{{ profile.cvCompletion }}%【{{ profile.cvLabel }}】
              </p>
            </div>

            <div class="radar-card">
              <p class="radar-title">雷达图（n 维度）</p>
              <div class="radar-chart" role="img" aria-label="个人能力雷达图（示例）">
                <svg class="radar-svg" viewBox="0 0 240 240" aria-hidden="true">
                  <g>
                    <polygon
                      v-for="(poly, idx) in radarChart.gridPolygons"
                      :key="idx"
                      :points="poly"
                      class="radar-grid"
                    />
                    <line
                      v-for="(axis, idx) in radarChart.axes"
                      :key="idx"
                      :x1="radarChart.cx"
                      :y1="radarChart.cy"
                      :x2="axis.x"
                      :y2="axis.y"
                      class="radar-axis"
                    />
                    <polygon :points="radarChart.dataPolygon" class="radar-data" />
                    <polygon :points="radarChart.dataPolygon" class="radar-data-outline" />
                    <g>
                      <text
                        v-for="(label, idx) in radarChart.labels"
                        :key="idx"
                        :x="label.x"
                        :y="label.y"
                        text-anchor="middle"
                        dominant-baseline="middle"
                        class="radar-label"
                      >
                        {{ label.text }}
                      </text>
                    </g>
                  </g>
                </svg>
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
                  color="#63bfb7"
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
              <el-button class="u-btn u-btn--primary" type="primary" @click="goToMatch">
                🔍 查看匹配岗位
              </el-button>
              <el-button class="u-btn u-btn--success" type="success" @click="goToMatch">
                📄 生成报告（需先选岗位）
              </el-button>
            </div>
          </section>
        </div>
      </section>

      <!-- 步骤四：岗位匹配与职业探索（原 职业生涯发展页中的人岗匹配部分） -->
      <section v-else-if="step === 'match'" class="panel match-panel">
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

      <!-- 步骤五：职业发展规划报告（原 职业生涯发展页中的报告部分） -->
      <section v-else class="panel report-panel">
        <!-- 报告头部 -->
        <header class="report-header">
          <div>
            <h1 class="page-title">职业发展规划报告</h1>
            <p class="report-subtitle">
              目标岗位：{{ currentJob?.name || baseInfo.targetJob }}
              · 生成时间：{{ reportDate }}
            </p>
          </div>
          <div class="header-actions">
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
          <p>{{ baseInfo.summary }}</p>
        </section>

        <section class="report-section">
          <h2 class="section-title">3. 职业发展路径（阶段性规划示意）</h2>
          <p class="hint-text">
            下面的表格示意了 6 个月内的阶段性成长路径，未来你可以用自动生成的图片替换这部分。
          </p>
          <div class="path-placeholder">
            <span>这里暂时使用第三张图的学习路径表格结构作为占位。</span>
          </div>
        </section>

        <!-- 4. 个人优势与短板 -->
        <section class="report-section">
          <h2 class="section-title">4. 个人优势与短板</h2>
          <div class="two-column">
            <div>
              <h3 class="subheading">优势</h3>
              <ul>
                <li v-for="(a, index) in baseInfo.strengths" :key="index">
                  {{ a }}
                </li>
              </ul>
            </div>
            <div>
              <h3 class="subheading">待提升点</h3>
              <ul>
                <li v-for="(w, index) in baseInfo.weaknesses" :key="index">
                  {{ w }}
                </li>
              </ul>
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
            <el-table-column prop="phase" label="阶段" width="120" />
            <el-table-column prop="time" label="时间节点" width="160" />
            <el-table-column prop="direction" label="核心提升方向" min-width="180" />
            <el-table-column prop="path" label="具体学习路径" min-width="220" />
            <el-table-column prop="practice" label="具体实践安排" min-width="180" />
            <el-table-column label="量化评估指标" min-width="210">
              <template #default="{ row }">
                <div class="metric-cell">
                  <span class="metric-text">{{ row.metric }}</span>
                  <el-button
                    class="u-btn u-btn--text"
                    type="primary"
                    text
                    size="small"
                    @click="openMetricEditor('short', row)"
                  >
                    编辑
                  </el-button>
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
                  <el-button
                    class="u-btn u-btn--text"
                    type="primary"
                    text
                    size="small"
                    @click="openMetricEditor('mid', row)"
                  >
                    编辑
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </section>

        <!-- 7. 阶段性达成标准与评估 -->
        <section class="report-section">
          <h2 class="section-title">7. 阶段性达成标准与评估</h2>
          <p>{{ evaluationSummary }}</p>
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
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTheme } from '../composables/useTheme'
import { ElMessage } from 'element-plus'
import { UploadFilled, ArrowDown } from '@element-plus/icons-vue'
import AppHeader from '../components/AppHeader.vue'

const { theme } = useTheme()
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
    title: '深度理解，而不是关键词匹配',
    desc: '基于大模型深度分析简历与岗位，结合实校招聘场景调试，理解你的经历远不止是扫描关键词。'
  },
  {
    icon: '📈',
    title: '3800+ 官方数据源，每日更新',
    desc: '数据来源官方就业网、企业官网等官方渠道，不推荐过期或虚假岗位。'
  },
  {
    icon: '🧩',
    title: '基于职业心理学理论',
    desc: '匹配结果参考职业兴趣理论等，不是随机推荐，而是根据你本人的特质出发。'
  }
]

// 上传简历 -> 调用解析接口并进入结果页
const handleBeforeUpload = async (file) => {
  const isAllowedType = /pdf|doc|docx$/i.test(file.name)
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isAllowedType) {
    ElMessage.error('仅支持 PDF / DOC / DOCX 格式')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('文件大小不能超过 5MB')
    return false
  }

  ElMessage.success(`已上传：${file.name}，正在解析...`)
  await fetchParseResult()
  step.value = 'result'
  return false // 阻止真实上传，仅演示
}

// 进入 AI 对话录入页面
const goToChat = () => {
  step.value = 'chat'
}

// 对话输入与进度
const chatInput = ref('')
const progress = ref(15)

const sendChat = () => {
  if (!chatInput.value.trim()) return
  // 这里只做示意，后续你可以替换为真正的对话列表追加逻辑
  ElMessage.success('已记录你的回答（示意），后续可接入真实 AI 对话。')
  chatInput.value = ''
  progress.value = Math.min(progress.value + 5, 100)
}

const finishChat = async () => {
  await fetchParseResult()
  step.value = 'result'
}

// API 响应数据
const studentProfile = ref(null)
const analysisSummary = ref(null)
const recommendedJobsApi = ref([])
const otherJobsApi = ref([])
const matchReport = ref(null)

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

const radarDimensions = computed(() => {
  const comp = studentProfile.value?.competencies || {}
  return [
    { name: '专业技能', score: Number(comp.professional_skills?.score ?? 0) },
    { name: '学习能力', score: Number(comp.learning_capability?.score ?? 0) },
    { name: '抗压能力', score: Number(comp.stress_resistance?.score ?? 0) },
    { name: '沟通能力', score: Number(comp.communication_skills?.score ?? 0) },
    { name: '创新能力', score: Number(comp.innovation_capability?.score ?? 0) },
    { name: '实习能力', score: Number(comp.internship_experience?.score ?? 0) }
  ].map((d) => ({ ...d, score: clamp(d.score, 0, 10) }))
})

const radarChart = computed(() => {
  const dims = radarDimensions.value.length ? radarDimensions.value : []
  const cx = 120
  const cy = 120
  const radius = 82
  const levels = 5

  const toPoint = (angleRad, r) => ({
    x: cx + Math.cos(angleRad) * r,
    y: cy + Math.sin(angleRad) * r
  })

  const count = Math.max(3, dims.length || 6)
  const step = (Math.PI * 2) / count
  const start = -Math.PI / 2

  const angles = Array.from({ length: count }, (_, i) => start + step * i)

  const gridPolygons = Array.from({ length: levels }, (_, levelIdx) => {
    const r = (radius * (levelIdx + 1)) / levels
    return angles.map((a) => {
      const p = toPoint(a, r)
      return `${p.x.toFixed(2)},${p.y.toFixed(2)}`
    }).join(' ')
  })

  const axes = angles.map((a) => toPoint(a, radius))

  const labels = angles.map((a, idx) => {
    const p = toPoint(a, radius + 12)
    const text = dims[idx]?.name ?? `维度${idx + 1}`
    return { x: p.x, y: p.y, text }
  })

  const dataPolygon = angles.map((a, idx) => {
    const score = dims[idx]?.score ?? 0
    const r = (radius * clamp(score, 0, 10)) / 10
    const p = toPoint(a, r)
    return `${p.x.toFixed(2)},${p.y.toFixed(2)}`
  }).join(' ')

  return { cx, cy, gridPolygons, axes, labels, dataPolygon }
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

const currentJob = computed(() => {
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

const baseInfo = computed(() => {
  return {
    major: studentProfile.value?.basic_info?.major || '-',
    targetJob: currentJob.value?.title || currentJob.value?.name || '-',
    summary:
      matchReport.value?.career_report?.gap_analysis ||
      analysisSummary.value?.overall_comment ||
      '暂无分析摘要',
    strengths: matchReport.value?.match_analysis?.details?.reasons || [],
    weaknesses: matchReport.value?.match_analysis?.details?.warnings || []
  }
})

// 解析简历并获取推荐岗位（阶段一接口）
const fetchParseResult = async () => {
  try {
    const data = MOCK_PARSE_RESPONSE
    studentProfile.value = data.student_profile
    analysisSummary.value = data.analysis_summary
    recommendedJobsApi.value = data.recommended_jobs || []
    otherJobsApi.value = data.other_jobs || []

    // 默认选中首个推荐岗位
    if (recommendedJobsApi.value.length > 0) {
      selectedJobId.value = recommendedJobsApi.value[0].job_id
    }
  } catch (err) {
    ElMessage.error(`解析失败：${err.message}`)
  }
}

// 生成岗位匹配报告（阶段二接口）
const fetchMatchReport = async () => {
  if (!selectedJobId.value || !studentProfile.value) return

  try {
    const data =
      MOCK_MATCH_REPORTS[selectedJobId.value] || buildFallbackMatchReport(selectedJobId.value)

    if (!data) {
      throw new Error('未找到匹配报告 mock 数据')
    }

    matchReport.value = data

    // 更新匹配详情展示
    const dims = data.match_analysis?.details?.dimensions || {}
    compareDimensions.value = [
      { name: '基础要求', student: dims.base ?? '-', job: '-' },
      { name: '职业技能', student: dims.skill ?? '-', job: '-' },
      { name: '职业素养', student: dims.soft ?? '-', job: '-' },
      { name: '发展潜力', student: dims.potential ?? '-', job: '-' }
    ]

    gapDetails.value = data.match_analysis?.details?.reasons || []
    improveSuggestions.value = data.match_analysis?.details?.warnings || []
  } catch (err) {
    ElMessage.error(`获取匹配报告失败：${err.message}`)
  }
}

// 查看匹配岗位 / 生成报告 -> 切换到「岗位匹配与职业探索」步骤
const goToMatch = async () => {
  step.value = 'match'
  await fetchMatchReport()
}

// ----------------- 以下为岗位匹配与职业规划报告相关逻辑（原 CareerReportView） -----------------

// 选中岗位详情
const viewJobDetail = async (row) => {
  selectedJobId.value = row.id
  ElMessage.success(`已切换到岗位「${row.name}」的匹配详情`)
  await fetchMatchReport()
}

// 从匹配页生成报告
const generateReport = () => {
  step.value = 'report'
  ElMessage.success('已根据当前岗位生成职业发展规划报告（示意）')
}

const goGenerateTrainingPlan = () => {
  router.push('/ability-training-plan/generated')
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

const evaluationSummary = ref(
  '在每个阶段结束时，对照量化指标进行自评与导师评估，根据达成情况适当调整后续学习与实践计划。'
)

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

  width: 100vw;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--u-body-bg);
  color: var(--u-black);
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI',
    sans-serif;
}

.abilities-view.dark {
  background: var(--dm-bg);
  color: var(--dm-text);
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
  background: #f0f2f8;
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
  background: #111827;
  color: #fff;
}

.page-scroll {
  padding: 28px 6vw 56px 64px;
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
  background: rgba(255, 255, 255, 0.6);
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
  background: rgba(255, 255, 255, 0.55);
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

.panel-header {
  margin-bottom: 16px;
}

.page-title {
  font-size: clamp(28px, 2.2vw, 38px);
  margin-bottom: 10px;
}

.page-intro {
  font-size: clamp(17px, 1.1vw, 20px);
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
  background: rgba(255, 255, 255, 0.55);
  border-radius: 16px;
  padding: 16px 18px 18px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(148, 163, 184, 0.22);
  box-shadow: 0 18px 40px rgba(16, 24, 40, 0.08);
}

.abilities-view.dark .trust-panel {
  background: rgba(28, 33, 40, 0.62);
  border: 1px solid var(--dm-border);
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.35);
}

.trust-panel--entry {
  /* 入口页：该区域本身也作为卡片展示（黑色边框） */
  background: rgba(255, 255, 255, 0.55);
  border-radius: 16px;
  padding: 16px 18px 35px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(148, 163, 184, 0.22);
  box-shadow: 0 18px 40px rgba(16, 24, 40, 0.08);
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

.abilities-view.dark .link-text {
  color: var(--dm-accent);
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
}

.trust-item-desc {
  font-size: clamp(16px, 1.05vw, 18px);
  color: rgba(51, 50, 46, 0.78);
  line-height: 1.5;
}

.link-text {
  display: inline-block;
  /* 让“查看参考文献”与上下内容保持一致垂直间距 */
  margin-top: 30px;
  font-size: clamp(15px, 0.95vw, 17px);
  color: var(--u-black);
  background: var(--u-bg-submit);
  border: var(--u-border);
  box-shadow: 2px 2px 0px var(--u-black);
  padding: 4px 10px;
  border-radius: 999px;
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
  box-shadow: none;
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
  color: var(--dm-text-secondary);
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
.upload-panel .page-title {
  margin-bottom: 12px;
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
  background: linear-gradient(180deg, #fdf8ef 0%, #fff7f5 100%);
  padding: 22px 18px;
  transition:
    border-color 0.2s ease,
    background-color 0.2s ease,
    transform 0.2s ease;
}

.upload-area-wrap :deep(.el-upload-dragger:hover) {
  border-color: rgba(51, 50, 46, 0.62);
  background: linear-gradient(180deg, #fff9f1 0%, #fff4f0 100%);
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

.chat-header h2 {
  font-size: clamp(20px, 1.4vw, 26px);
  margin-bottom: 10px;
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
  border: 1px solid var(--dm-border);
  color: var(--dm-text);
}

.abilities-view.dark .info-title,
.abilities-view.dark .radar-title {
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
}

.abilities-view.dark .radar-grid {
  stroke: rgba(255, 255, 255, 0.18);
}

.abilities-view.dark .radar-axis {
  stroke: rgba(255, 255, 255, 0.14);
}

.abilities-view.dark .radar-data {
  fill: rgba(99, 191, 183, 0.26);
}

.abilities-view.dark .radar-data-outline {
  stroke: rgba(255, 255, 255, 0.7);
}

.abilities-view.dark .radar-label {
  fill: rgba(255, 255, 255, 0.82);
}

.abilities-view.dark .tag {
  background: var(--dm-warm-soft);
  color: var(--dm-warm);
  border: 1px solid rgba(251, 191, 36, 0.3);
}

.chat-window {
  background: #ffffff;
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
  background: #f3f4ff;
}

.chat-message.user .bubble {
  background: #e0f7fa;
}

.chat-placeholder {
  margin-top: 8px;
  padding: 8px 10px;
  border-radius: 8px;
  font-size: 12px;
  background: #f9fafb;
  color: #666;
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

/* 结果面板 */
.result-panel {
  background: #f0fbff;
}

.result-header {
  margin-bottom: 8px;
}

.tag {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 999px;
  background: #00bfa5;
  color: #fff;
  font-size: clamp(13px, 0.95vw, 15px);
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

.info-card,
.radar-card {
  background: #ffffff;
  border-radius: 12px;
  padding: clamp(14px, 1.2vw, 20px);
  box-shadow: 0 4px 10px rgba(15, 23, 42, 0.04);
}

.info-title {
  font-size: clamp(16px, 1.05vw, 18px);
  margin-bottom: 6px;
  font-weight: 600;
}

.info-line {
  font-size: clamp(15px, 0.95vw, 17px);
  line-height: 1.55;
}

.radar-title {
  font-size: clamp(16px, 1.05vw, 18px);
  margin-bottom: 8px;
  font-weight: 600;
}

.radar-chart {
  height: clamp(500px, 62vh, 600px);
  border-radius: 12px;
  background: #f5f7fb;
  display: grid;
  place-items: center;
  padding: 12px;
}

.radar-svg {
  width: 100%;
  height: 100%;
  max-width: 360px;
  max-height: 360px;
  overflow: visible;
}

.radar-grid {
  fill: transparent;
  stroke: rgba(15, 23, 42, 0.12);
  stroke-width: 1;
}

.radar-axis {
  stroke: rgba(15, 23, 42, 0.1);
  stroke-width: 1;
}

.radar-data {
  fill: rgba(99, 191, 183, 0.32);
}

.radar-data-outline {
  fill: transparent;
  stroke: rgba(15, 23, 42, 0.6);
  stroke-width: 1.5;
}

.radar-label {
  font-size: 11px;
  fill: rgba(15, 23, 42, 0.78);
}

.radar-placeholder {
  height: clamp(240px, 26vh, 340px);
  border-radius: 12px;
  background: #f5f7fb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: clamp(14px, 0.95vw, 16px);
  color: #777;
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
  /* 移除波点底纹：保留线性渐变的轻盈卡片背景 */
  background: linear-gradient(135deg, var(--u-bg-normal), var(--u-gradient-fade));
  border-radius: 12px;
  padding: clamp(14px, 1.2vw, 20px);
  border: 1px solid rgba(148, 163, 184, 0.25);
  box-shadow: 0 14px 34px rgba(16, 24, 40, 0.08);
}

/* 混搭：结果区三张卡片交替底色 */
.result-right > :nth-child(2) {
  background: linear-gradient(135deg, var(--u-bg-submit), var(--u-gradient-fade));
}

.result-right > :nth-child(3) {
  background: linear-gradient(135deg, var(--u-bg-completed), var(--u-gradient-fade));
}

.score-label {
  font-size: clamp(15px, 1vw, 17px);
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
  font-size: clamp(17px, 1.1vw, 19px);
  margin-bottom: 8px;
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
  background-color: rgba(51, 50, 46, 0.12);
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
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 4px;
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
  background: #f5fbff;
}

.match-header {
  margin-bottom: 12px;
}

.student-tag {
  font-size: clamp(17px, 1.1vw, 19px);
  color: #555;
}

.recommend-section {
  margin-top: 8px;
}

.job-table {
  margin-top: 8px;
}

.current-job-section {
  margin-top: 18px;
}

.match-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 8px 0 12px;
  font-size: clamp(16px, 1.05vw, 18px);
}

.match-hint {
  font-size: clamp(16px, 1.05vw, 18px);
  color: #555;
  line-height: 1.6;
  margin-bottom: 14px;
  padding: 10px 12px;
  background: #f0f9ff;
  border-radius: 10px;
}

.weight-hint {
  font-size: clamp(15px, 0.95vw, 17px);
  color: #666;
  margin-top: 8px;
}

.compare-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 14px 20px;
}

.compare-card {
  background: linear-gradient(135deg, var(--u-bg-normal), var(--u-gradient-fade));
  border-radius: 12px;
  padding: 12px 14px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  box-shadow: 0 14px 34px rgba(16, 24, 40, 0.08);
}

.compare-grid .compare-card:nth-child(2) {
  background: linear-gradient(135deg, var(--u-body-bg), var(--u-gradient-fade));
}

.compare-title {
  font-size: clamp(17px, 1.1vw, 19px);
  margin-bottom: 8px;
}

.compare-placeholder {
  height: 180px;
  border-radius: 10px;
  background: #f5f7fb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  color: #777;
  text-align: center;
}

.compare-list {
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: clamp(16px, 1.05vw, 18px);
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
  font-size: clamp(16px, 1.05vw, 18px);
  line-height: 1.5;
}

.section-subtitle {
  font-weight: 600;
  font-size: clamp(17px, 1.1vw, 19px);
  margin: 8px 0 6px;
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

/* 报告样式 */
.report-panel {
  background: #f0fbff;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.header-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.report-subtitle {
  font-size: clamp(16px, 1.05vw, 18px);
  color: #555;
  line-height: 1.5;
}

.report-section {
  margin-top: 14px;
  background: linear-gradient(135deg, var(--u-bg-normal), var(--u-gradient-fade));
  border-radius: 14px;
  padding: 12px 14px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  box-shadow: 0 14px 34px rgba(16, 24, 40, 0.08);
}

/* 混搭：报告分段卡片交替底色 */
.report-panel .report-section:nth-of-type(4n + 2) {
  background: linear-gradient(135deg, var(--u-bg-submit), var(--u-gradient-fade));
}

.report-panel .report-section:nth-of-type(4n + 3) {
  background: linear-gradient(135deg, var(--u-bg-completed), var(--u-gradient-fade));
}

.report-panel .report-section:nth-of-type(4n) {
  background: linear-gradient(135deg, var(--u-bg-discard), var(--u-gradient-fade));
}

.hint-text {
  font-size: clamp(15px, 0.95vw, 17px);
  color: #666;
  margin-bottom: 8px;
  line-height: 1.5;
}

.path-placeholder {
  margin-top: 6px;
  border-radius: 12px;
  border: 1px dashed #cbd5e1;
  padding: 16px;
  font-size: clamp(16px, 1.05vw, 18px);
  color: #555;
  background: #f8fafc;
}

.two-column {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px 24px;
  font-size: clamp(16px, 1.05vw, 18px);
  line-height: 1.5;
}

.subheading {
  font-size: clamp(17px, 1.1vw, 19px);
  margin-bottom: 6px;
}

.plan-table {
  margin-top: 8px;
  font-size: clamp(16px, 1.05vw, 18px);
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
  font-size: clamp(16px, 1.05vw, 18px);
  font-weight: 600;
}

.orig-metric {
  padding: 8px 10px;
  background: #f5f7fb;
  border-radius: 8px;
  font-size: clamp(16px, 1.05vw, 18px);
}

.suggest-group {
  margin: 4px 0 6px;
}

.suggest-list {
  font-size: clamp(16px, 1.05vw, 18px);
  padding-left: 18px;
  margin: 0 0 8px;
  line-height: 1.5;
}

.reason-block {
  margin-top: 6px;
}

.abilities-view.dark .student-tag,
.abilities-view.dark .match-hint,
.abilities-view.dark .weight-hint,
.abilities-view.dark .report-subtitle,
.abilities-view.dark .hint-text,
.abilities-view.dark .dim-score {
  color: var(--dm-text-secondary);
}

.abilities-view.dark .match-hint {
  background: var(--dm-accent-soft);
}

.abilities-view.dark .compare-card {
  background: var(--dm-surface-card);
  border: 1px solid var(--dm-border);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.abilities-view.dark .compare-placeholder {
  background: var(--dm-surface);
  color: var(--dm-text-secondary);
}

.abilities-view.dark .report-panel {
  background: var(--dm-bg);
}

.abilities-view.dark .report-section {
  background: var(--dm-surface-card);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  border: 1px solid var(--dm-border);
}

.abilities-view.dark .path-placeholder {
  background: var(--dm-surface);
  border-color: var(--dm-border);
  color: var(--dm-text-secondary);
}

.abilities-view.dark .subheading {
  color: var(--dm-text);
}

.abilities-view.dark .detail-analysis {
  color: var(--dm-text-secondary);
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
  background: var(--dm-surface-elevated);
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
}
</style>