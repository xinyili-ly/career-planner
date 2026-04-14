<template>
  <div class="career-template-view" :class="theme">
    <AppHeader />

    <main class="page-scroll">
      <section class="panel">
        <header class="panel-head">
          <div>
            <h1 class="page-title">职业发展报告模板</h1>
            <p class="subtitle">
              学生：{{ payload.studentName || '（未读取到数据）' }} · 目标岗位：{{ payload.targetJob || '—' }} · 生成时间：{{
                payload.reportDate || '—'
              }}
            </p>
          </div>
          <div class="actions">
            <el-button class="u-btn u-btn--ghost" @click="applyStudentAutoEdit">学生自动编辑</el-button>
            <el-button class="u-btn u-btn--primary" type="primary" @click="applySmartPolish">智能润色</el-button>
            <el-dropdown @command="exportDoc">
              <el-button class="u-btn u-btn--primary" type="primary" plain>
                导出
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

        <div class="tip">
          这个页面会把我们已知的学生关键信息填入统一模板。你可以先选择「学生自动编辑」生成一版更直白的报告，
          或选择「智能润色」：将按《API_DOC.md》先请求报告预览再调用 finalize，拉取 module_4 的 Markdown 全文（生成可能需数秒至数十秒）。
        </div>
      </section>

      <section class="panel">
        <h2 class="section-title">报告正文（可继续手动改）</h2>
        <el-input v-model="reportText" type="textarea" :rows="20" class="report-editor" />
      </section>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElLoading, ElMessage } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import { useTheme } from '../composables/useTheme'
import AppHeader from '../components/AppHeader.vue'
import {
  postCareerReportPolishFromPreview,
  readLastMatchResult,
  readProfileCacheId,
} from '../api/careerAgentApi'

const { theme } = useTheme()

const payload = ref({
  studentName: '',
  reportDate: '',
  targetJob: '',
  baseInfo: { major: '', summary: '', strengths: [], weaknesses: [] },
  pathNote: '',
  shortTermPlan: [],
  midTermPlan: [],
  evaluationSummary: '',
})

const reportText = ref('')

const esc = (s) => String(s ?? '').replace(/\s+/g, ' ').trim()

function loadPayload() {
  try {
    const raw = sessionStorage.getItem('career_report_payload_v1')
    if (!raw) return false
    const obj = JSON.parse(raw)
    if (!obj) return false
    payload.value = obj
    return true
  } catch (e) {
    return false
  }
}

function buildTemplateText(style) {
  const p = payload.value
  const lines = []
  lines.push('职业发展规划报告')
  lines.push(`学生：${esc(p.studentName)}`)
  lines.push(`专业：${esc(p.baseInfo?.major)}`)
  lines.push(`目标岗位：${esc(p.targetJob)}`)
  lines.push(`生成时间：${esc(p.reportDate)}`)
  lines.push('')

  lines.push('一、学生画像摘要')
  if (style === 'polish') {
    lines.push(`综合评估：${esc(p.baseInfo?.summary)}`)
  } else {
    lines.push(`现状概述：${esc(p.baseInfo?.summary)}`)
  }
  lines.push('')

  lines.push('二、优势与短板')
  lines.push('优势：')
  for (const s of p.baseInfo?.strengths || []) {
    lines.push(`- ${esc(s)}`)
  }
  lines.push('待提升点：')
  for (const w of p.baseInfo?.weaknesses || []) {
    lines.push(`- ${esc(w)}`)
  }
  lines.push('')

  lines.push('三、发展路径与节奏建议')
  lines.push(esc(p.pathNote || '（此处可补充阶段性发展路径图/文字说明）'))
  lines.push('')

  lines.push('四、短期计划（0 ~ 6 个月）')
  for (const r of p.shortTermPlan || []) {
    if (style === 'polish') {
      lines.push(`- ${esc(r.phase)}（${esc(r.time)}）：聚焦「${esc(r.direction)}」，以可量化指标验证学习成果。`)
    } else {
      lines.push(`- ${esc(r.phase)}（${esc(r.time)}）：${esc(r.direction)}`)
    }
    lines.push(`  - 学习路径：${esc(r.path)}`)
    lines.push(`  - 实践安排：${esc(r.practice)}`)
    lines.push(`  - 量化指标：${esc(r.metric)}`)
  }
  lines.push('')

  lines.push('五、中期计划（6 ~ 18 个月）')
  for (const r of p.midTermPlan || []) {
    if (style === 'polish') {
      lines.push(`- ${esc(r.phase)}（${esc(r.time)}）：在「${esc(r.direction)}」上形成稳定能力闭环。`)
    } else {
      lines.push(`- ${esc(r.phase)}（${esc(r.time)}）：${esc(r.direction)}`)
    }
    lines.push(`  - 学习路径：${esc(r.path)}`)
    lines.push(`  - 实践安排：${esc(r.practice)}`)
    lines.push(`  - 量化指标：${esc(r.metric)}`)
  }
  lines.push('')

  lines.push('六、阶段性评估与迭代机制')
  lines.push(esc(p.evaluationSummary || '每阶段结束对照量化指标复盘，根据达成情况调整后续计划。'))
  lines.push('')

  if (style === 'polish') {
    lines.push('结语')
    lines.push('建议你以“可展示成果”为牵引，把学习、实践、复盘固化为节奏，持续迭代并稳定提升面试竞争力。')
  }

  return lines.join('\n')
}

const applyStudentAutoEdit = () => {
  reportText.value = buildTemplateText('student')
  ElMessage.success('已生成「学生自动编辑」版本（示意）。')
}

const applySmartPolish = async () => {
  const jobId = String(payload.value.jobId || readLastMatchResult()?.job_info?.job_id || '').trim()
  const profileCacheId = String(
    payload.value.profile_cache_id || readProfileCacheId() || ''
  ).trim()
  const last = readLastMatchResult()
  const studentProfile =
    last?.student_profile ??
    last?.studentProfile ??
    payload.value.student_profile ??
    undefined

  if (!jobId) {
    ElMessage.warning('缺少岗位 ID：请先在「职业发展规划报告」页选择岗位并生成报告，再进入本页润色。')
    return
  }
  if (!profileCacheId && (!studentProfile || typeof studentProfile !== 'object')) {
    ElMessage.warning('缺少画像缓存或学生画像：请先完成简历解析或能力画像流程。')
    return
  }

  const loading = ElLoading.service({
    lock: true,
    text: '正在生成润色报告（预览 → 定稿），请稍候…',
    background: 'rgba(255,255,255,0.65)',
  })
  try {
    const { module_4, polished_markdown } = await postCareerReportPolishFromPreview({
      job_id: jobId,
      profile_cache_id: profileCacheId || undefined,
      student_profile: profileCacheId ? undefined : studentProfile,
    })
    const text = String(polished_markdown || '').trim()
    if (module_4?.llm_status === 'error') {
      ElMessage.warning(
        module_4?.validation?.warnings?.length
          ? `润色返回异常：${module_4.validation.warnings.join('；')}`
          : '润色接口返回 llm_status=error，请稍后重试或查看后端日志。'
      )
    }
    if (text) {
      reportText.value = text
      ElMessage.success('润色成功！')
      return
    }
    reportText.value = buildTemplateText('polish')
    ElMessage.success('未返回 Markdown 正文，已使用本地模板润色稿。')
  } catch (e) {
    ElMessage.error(`润色失败：${e?.message || '请检查后端接口（需先 preview 再 finalize）'}`)
  } finally {
    loading.close()
  }
}

function buildMarkdown() {
  return reportText.value || buildTemplateText('student')
}

function buildHtml() {
  const content = (reportText.value || buildTemplateText('student'))
    .split('\n')
    .map((l) => `<p style="margin:0 0 8px;line-height:1.6;">${l.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')}</p>`)
    .join('')

  return `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>职业发展规划报告</title>
  <style>
    body{font-family:'Source Han Sans SC','Source Han Sans CN','Source Han Sans','Noto Sans CJK SC','Noto Sans SC',Roboto,'Helvetica Neue',Helvetica,Arial,sans-serif;padding:24px;color:#111827;}
    .meta{color:#475569;margin:0 0 14px;}
  </style>
</head>
<body>
  <div class="meta">学生：${payload.value.studentName} · 目标岗位：${payload.value.targetJob} · 生成时间：${payload.value.reportDate}</div>
  ${content}
</body>
</html>`
}

function openPrint() {
  const html = buildHtml()
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

function downloadWord(filename) {
  const html = buildHtml()
  const blob = new Blob([html], { type: 'application/msword;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

function exportDoc(format) {
  if (format === 'markdown') {
    const content = buildMarkdown()
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'career-report-template.md'
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('已导出 Markdown。')
  } else if (format === 'pdf') {
    openPrint()
    ElMessage.success('已打开打印窗口：可选择“另存为 PDF”。')
  } else if (format === 'word') {
    downloadWord('career-report-template.doc')
    ElMessage.success('已导出 Word（.doc）。')
  }
}

onMounted(() => {
  const ok = loadPayload()
  if (!ok) {
    ElMessage.warning('未读取到报告数据，请从“职业发展规划报告”页点击“智能润色”进入。')
  } else {
    reportText.value = buildTemplateText('student')
  }
})
</script>

<style scoped>
.career-template-view {
  width: 100vw;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fb;
  color: #222;
  font-family: var(--font-family-sans);
}

.career-template-view.dark {
  background: var(--dm-bg);
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
  border-bottom: 1px solid #edf0f5;
}

.career-template-view.dark .header {
  background: var(--dm-header-bg);
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

.career-template-view.dark .nav-item {
  color: var(--dm-text);
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

.career-template-view.dark .theme-toggle {
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

.career-template-view.dark .theme-option.active {
  background: var(--dm-surface-elevated);
  color: var(--dm-text);
}

.page-scroll {
  padding: 28px 6vw 56px 64px;
  flex: 1;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.panel {
  background:
    radial-gradient(circle at 12px 12px, rgba(51, 50, 46, 0.08) 1.6px, transparent 2.3px)
      0 0 / 28px 28px,
    linear-gradient(135deg, var(--u-bg-normal), var(--u-gradient-fade));
  border-radius: 18px;
  padding: 24px 24px 28px;
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.08);
}

/* 混搭：两个面板交替底色 */
.panel:nth-of-type(2) {
  background:
    radial-gradient(circle at 12px 12px, rgba(51, 50, 46, 0.08) 1.6px, transparent 2.3px)
      0 0 / 28px 28px,
    linear-gradient(135deg, var(--u-bg-submit), var(--u-gradient-fade));
}

.career-template-view.dark .panel {
  background: var(--dm-gradient-card);
  border: 1px solid var(--dm-border);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.page-title {
  font-size: clamp(26px, 2vw, 36px);
  margin: 0 0 6px;
}

.subtitle {
  margin: 0;
  color: #64748b;
}

.career-template-view.dark .subtitle {
  color: var(--dm-text-secondary);
}

.tip {
  margin-top: 14px;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(2, 132, 199, 0.06);
  border: 1px solid rgba(2, 132, 199, 0.14);
  color: #0f172a;
  line-height: 1.65;
}

.career-template-view.dark .tip {
  background: rgba(255, 255, 255, 0.06);
  border-color: var(--dm-border);
  color: var(--dm-text);
}

.section-title {
  margin: 0 0 12px;
  font-size: clamp(18px, 1.35vw, 24px);
}

.report-editor {
  margin-top: 6px;
}
</style>

