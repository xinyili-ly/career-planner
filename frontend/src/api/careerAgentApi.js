/**
 * 职业规划智能体后端（OpenAPI）— 第二 / 三分界面
 * 路径与约定见仓库根目录《前端接入后端接口详细文档.md》
 * Base：`import.meta.env.VITE_CAREER_AGENT_API_BASE`，默认 `http://192.168.31.93:8002`
 */

const DEFAULT_BASE = 'http://192.168.31.93:8002'
const PROFILE_CACHE_ID_STORAGE_KEY = 'profile_cache_id'
const LAST_MATCH_RES_STORAGE_KEY = 'last_match_res'
const CAREER_AGENT_STATUS_EVENT = 'career-agent-status'
const FRIENDLY_AI_FALLBACK_MESSAGE = '当前 AI 逻辑思考中，为您展示本地知识库推荐...'

function dispatchCareerAgentStatus(detail) {
  if (typeof window === 'undefined') return
  window.dispatchEvent(
    new CustomEvent(CAREER_AGENT_STATUS_EVENT, {
      detail: {
        ...detail,
        ts: Date.now(),
      },
    }),
  )
}

function toFriendlyApiError(cause) {
  const err = new Error(FRIENDLY_AI_FALLBACK_MESSAGE)
  err.name = 'CareerAgentApiError'
  if (cause) err.cause = cause
  return err
}

const nativeFetch = globalThis.fetch.bind(globalThis)
async function fetch(input, init) {
  try {
    const response = await nativeFetch(input, init)
    if (response.ok) {
      dispatchCareerAgentStatus({ ok: true })
    } else {
      dispatchCareerAgentStatus({
        ok: false,
        status: response.status,
        url: typeof input === 'string' ? input : String(input?.url || ''),
        message: FRIENDLY_AI_FALLBACK_MESSAGE,
      })
    }
    return response
  } catch (e) {
    dispatchCareerAgentStatus({
      ok: false,
      status: 0,
      url: typeof input === 'string' ? input : String(input?.url || ''),
      message: FRIENDLY_AI_FALLBACK_MESSAGE,
    })
    throw toFriendlyApiError(e)
  }
}

export function getCareerAgentBaseUrl() {
  const u = import.meta.env.VITE_CAREER_AGENT_API_BASE
  if (u && String(u).trim()) return String(u).replace(/\/$/, '')
  return DEFAULT_BASE
}

/** 是否启用真实接口（默认启用，可由环境变量覆盖地址） */
export function isCareerAgentApiEnabled() {
  return Boolean(getCareerAgentBaseUrl())
}

export function saveProfileCacheId(profileCacheId) {
  if (!profileCacheId) return
  const value = String(profileCacheId)
  try {
    localStorage.setItem(PROFILE_CACHE_ID_STORAGE_KEY, value)
  } catch {
    // ignore write errors
  }
  try {
    sessionStorage.setItem(PROFILE_CACHE_ID_STORAGE_KEY, value)
  } catch {
    // ignore write errors
  }
}

export function readProfileCacheId() {
  try {
    const fromLocal = localStorage.getItem(PROFILE_CACHE_ID_STORAGE_KEY)
    if (fromLocal) return fromLocal
  } catch {
    // ignore read errors
  }
  try {
    const fromSession = sessionStorage.getItem(PROFILE_CACHE_ID_STORAGE_KEY)
    if (fromSession) return fromSession
  } catch {
    // ignore read errors
  }
  return ''
}

export function saveLastMatchResult(payload) {
  if (!payload || typeof payload !== 'object') return
  try {
    localStorage.setItem(LAST_MATCH_RES_STORAGE_KEY, JSON.stringify(payload))
  } catch {
    // ignore write errors
  }
}

export function readLastMatchResult() {
  try {
    const raw = localStorage.getItem(LAST_MATCH_RES_STORAGE_KEY)
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

function baseUrlOrDefault() {
  return getCareerAgentBaseUrl() || DEFAULT_BASE
}

async function parseJsonResponse(response) {
  const text = await response.text()
  let json
  try {
    json = text ? JSON.parse(text) : null
  } catch {
    json = null
  }
  if (!response.ok) {
    json = {
      ...(json && typeof json === 'object' ? json : {}),
      message: FRIENDLY_AI_FALLBACK_MESSAGE,
      detail: FRIENDLY_AI_FALLBACK_MESSAGE,
    }
  }
  return { json, text, response }
}

function unwrapData(json) {
  if (json == null) return null
  if (typeof json === 'object' && 'data' in json) {
    const code = json.code
    if (code !== undefined && code !== 0 && code !== '0') {
      dispatchCareerAgentStatus({ ok: false, status: 200, message: FRIENDLY_AI_FALLBACK_MESSAGE })
      throw toFriendlyApiError(json?.message || json?.msg || '业务错误')
    }
    return json.data
  }
  return json
}

export async function checkCareerAgentConnection() {
  const url = new URL('/recommend/list', baseUrlOrDefault())
  const res = await fetch(url.toString(), {
    method: 'GET',
    headers: { Accept: 'application/json' },
  })
  if (!res.ok) {
    throw toFriendlyApiError(`HTTP ${res.status}`)
  }
  dispatchCareerAgentStatus({ ok: true })
  return true
}

/**
 * GET /recommend/list
 * @returns {Promise<Array>}
 */
export async function fetchRecommendJobList() {
  const url = new URL('/recommend/list', baseUrlOrDefault())
  const res = await fetch(url.toString(), {
    method: 'GET',
    headers: { Accept: 'application/json' },
  })
  const { json } = await parseJsonResponse(res)
  if (!res.ok) {
    throw new Error(json?.detail?.[0]?.msg || json?.message || `HTTP ${res.status}`)
  }
  const data = unwrapData(json)
  return Array.isArray(data) ? data : []
}

/**
 * POST /api/v1/student/parse（multipart 文件）
 * @param {File} file
 */
export async function parseResumeFile(file) {
  const url = new URL('/api/v1/student/parse', baseUrlOrDefault())
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(url.toString(), {
    method: 'POST',
    body: form,
  })
  const { json } = await parseJsonResponse(res)
  if (!res.ok) {
    throw new Error(
      typeof json?.detail === 'string'
        ? json.detail
        : json?.detail?.[0]?.msg || json?.message || `HTTP ${res.status}`
    )
  }
  return unwrapData(json) ?? json
}

/**
 * POST /api/v1/student/parse/manual
 * @param {string} resumeText
 */
export async function parseResumeText(resumeText) {
  const url = new URL('/api/v1/student/parse/manual', baseUrlOrDefault())
  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ resume_text: resumeText }),
  })
  const { json } = await parseJsonResponse(res)
  if (!res.ok) {
    throw new Error(
      typeof json?.detail === 'string'
        ? json.detail
        : json?.detail?.[0]?.msg || json?.message || `HTTP ${res.status}`
    )
  }
  return unwrapData(json) ?? json
}

/**
 * POST /api/v1/match/report
 * @param {{ job_id: string, student_profile?: object, profile_cache_id?: string, plan_preferences?: object }} body
 */
export async function postMatchReport(body) {
  const url = new URL('/api/v1/match/report', baseUrlOrDefault())
  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })
  const { json } = await parseJsonResponse(res)
  if (!res.ok) {
    const msg =
      typeof json?.detail === 'string'
        ? json.detail
        : json?.detail?.[0]?.msg || json?.message || `HTTP ${res.status}`
    throw new Error(msg)
  }
  return unwrapData(json) ?? json
}

/**
 * 按《后端接口文档_生成职业报告.md》构建请求体：
 * - 必传 job_id
 * - student_profile 与 profile_cache_id 支持二选一（若同时传，后端优先 student_profile）
 * - precomputed_module_1 可选（用于跳过 module_1 LLM 调用）
 */
export function buildMatchReportPayload(params) {
  const payload = {}
  const jobId = String(params?.job_id ?? '').trim()
  if (!jobId) {
    throw new Error('缺少 job_id')
  }
  payload.job_id = jobId

  const studentProfile = params?.student_profile
  if (studentProfile && typeof studentProfile === 'object') {
    payload.student_profile = studentProfile
  }

  const profileCacheId = params?.profile_cache_id != null ? String(params.profile_cache_id).trim() : ''
  if (profileCacheId) {
    payload.profile_cache_id = profileCacheId
  }

  const precomputedModule1 = params?.precomputed_module_1
  if (precomputedModule1 && typeof precomputedModule1 === 'object') {
    payload.precomputed_module_1 = precomputedModule1
  }

  if (!payload.student_profile && !payload.profile_cache_id) {
    throw new Error('缺少 profile_cache_id 或 student_profile')
  }
  return payload
}

/**
 * POST /api/v1/match/report-preview（仅 module_1~3，文档 3.4）
 * @param {{ job_id: string, student_profile?: object, profile_cache_id?: string, plan_preferences?: object }} body
 */
export async function postMatchReportPreview(body) {
  const url = new URL('/api/v1/match/report-preview', baseUrlOrDefault())
  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })
  const { json } = await parseJsonResponse(res)
  if (!res.ok) {
    const msg =
      typeof json?.detail === 'string'
        ? json.detail
        : json?.detail?.[0]?.msg || json?.message || `HTTP ${res.status}`
    throw new Error(msg)
  }
  return unwrapData(json) ?? json
}

/**
 * POST /api/v1/match/report/finalize（仅 module_4，文档 3.5）
 * @param {{ job_id: string, preview_data: object, profile_cache_id?: string, student_profile?: object }} body
 */
export async function postMatchReportFinalize(body) {
  const url = new URL('/api/v1/match/report/finalize', baseUrlOrDefault())
  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })
  const { json } = await parseJsonResponse(res)
  if (!res.ok) {
    const msg =
      typeof json?.detail === 'string'
        ? json.detail
        : json?.detail?.[0]?.msg || json?.message || `HTTP ${res.status}`
    throw new Error(msg)
  }
  return unwrapData(json) ?? json
}

/**
 * 职业规划报告「智能润色」——与仓库根目录《API_DOC.md》一致：
 * 1) POST /api/v1/match/report-preview
 * 2) POST /api/v1/match/report/finalize（body.preview_data 为步骤 1 完整返回）
 *
 * @param {{
 *   job_id: string,
 *   profile_cache_id?: string,
 *   student_profile?: object
 * }} params profile_cache_id 与 student_profile 至少其一（与后端约定一致）
 * @returns {Promise<{ module_4: object | null, polished_markdown: string }>}
 */
export async function postCareerReportPolishFromPreview(params) {
  const job_id = String(params?.job_id ?? '').trim()
  if (!job_id) throw new Error('缺少 job_id')
  const cacheId = params.profile_cache_id != null ? String(params.profile_cache_id).trim() : ''
  const studentProfile = params.student_profile
  if (!cacheId && (!studentProfile || typeof studentProfile !== 'object')) {
    throw new Error('缺少 profile_cache_id 或 student_profile')
  }

  const previewBody = { job_id }
  if (cacheId) previewBody.profile_cache_id = cacheId
  else previewBody.student_profile = studentProfile

  const previewData = await postMatchReportPreview(previewBody)

  const finalizeBody = { job_id, preview_data: previewData }
  if (cacheId) finalizeBody.profile_cache_id = cacheId
  if (!cacheId && studentProfile) finalizeBody.student_profile = studentProfile

  const finalized = await postMatchReportFinalize(finalizeBody)
  const module4 = finalized?.module_4 ?? finalized?.module4 ?? null
  const polished_markdown =
    module4?.polished_markdown ?? module4?.polishedMarkdown ?? ''
  return { module_4: module4, polished_markdown }
}

/**
 * （可选）旧版或扩展后端：POST /api/v1/match/polish
 * 当前《API_DOC.md》推荐流程见 {@link postCareerReportPolishFromPreview}
 */
export async function postSmartPolish(data) {
  const body = { ...(data && typeof data === 'object' ? data : {}) }
  if (body.content != null && body.original_content == null) {
    body.original_content = body.content
    delete body.content
  }
  if (body.target_job_id == null && body.job_id != null) {
    body.target_job_id = body.job_id
    delete body.job_id
  }
  const url = new URL('/api/v1/match/polish', baseUrlOrDefault())
  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })
  const { json } = await parseJsonResponse(res)
  if (!res.ok) {
    const msg =
      typeof json?.detail === 'string'
        ? json.detail
        : json?.detail?.[0]?.msg || json?.message || `HTTP ${res.status}`
    throw new Error(msg)
  }
  return unwrapData(json) ?? json
}

/**
 * POST /api/v1/match/detail
 * @param {{ job_id: string, student_profile?: object, profile_cache_id?: string }} body
 */
export async function postMatchDetail(body) {
  const url = new URL('/api/v1/match/detail', baseUrlOrDefault())
  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })
  const { json } = await parseJsonResponse(res)
  if (!res.ok) {
    const msg =
      typeof json?.detail === 'string'
        ? json.detail
        : json?.detail?.[0]?.msg || json?.message || `HTTP ${res.status}`
    throw new Error(msg)
  }
  return unwrapData(json) ?? json
}

/**
 * POST /api/v1/student/intake/start
 */
export async function intakeStart() {
  const url = new URL('/api/v1/student/intake/start', baseUrlOrDefault())
  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: { Accept: 'application/json' },
  })
  const { json } = await parseJsonResponse(res)
  if (!res.ok) {
    throw new Error(
      typeof json?.detail === 'string'
        ? json.detail
        : json?.detail?.[0]?.msg || json?.message || `HTTP ${res.status}`
    )
  }
  return unwrapData(json) ?? json
}

/**
 * POST /api/v1/student/intake/answer
 * @param {{ session_id: string, answer: string }} body
 */
export async function intakeAnswer(body) {
  const url = new URL('/api/v1/student/intake/answer', baseUrlOrDefault())
  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })
  const { json } = await parseJsonResponse(res)
  if (!res.ok) {
    throw new Error(
      typeof json?.detail === 'string'
        ? json.detail
        : json?.detail?.[0]?.msg || json?.message || `HTTP ${res.status}`
    )
  }
  return unwrapData(json) ?? json
}

/**
 * POST /api/v1/student/intake/finish
 * @param {{ session_id: string }} body
 */
export async function intakeFinish(body) {
  const url = new URL('/api/v1/student/intake/finish', baseUrlOrDefault())
  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })
  const { json } = await parseJsonResponse(res)
  if (!res.ok) {
    throw new Error(
      typeof json?.detail === 'string'
        ? json.detail
        : json?.detail?.[0]?.msg || json?.message || `HTTP ${res.status}`
    )
  }
  return unwrapData(json) ?? json
}

/**
 * GET /api/v1/action-plan/check-pending
 * @param {string} studentId
 */
export async function getActionPlanCheckPending(studentId) {
  const url = new URL('/api/v1/action-plan/check-pending', baseUrlOrDefault())
  url.searchParams.set('student_id', String(studentId))
  const res = await fetch(url.toString(), {
    method: 'GET',
    headers: { Accept: 'application/json' },
  })
  const { json } = await parseJsonResponse(res)
  if (!res.ok) {
    throw new Error(
      typeof json?.detail === 'string'
        ? json.detail
        : json?.detail?.[0]?.msg || json?.message || `HTTP ${res.status}`
    )
  }
  return unwrapData(json) ?? json
}

/**
 * GET /api/v1/action-plan/current
 * @param {string} studentId
 */
export async function getCurrentActionPlan(studentId) {
  const url = new URL('/api/v1/action-plan/current', baseUrlOrDefault())
  url.searchParams.set('student_id', String(studentId))
  const res = await fetch(url.toString(), {
    method: 'GET',
    headers: { Accept: 'application/json' },
  })
  const { json } = await parseJsonResponse(res)
  if (!res.ok) {
    throw new Error(
      typeof json?.detail === 'string'
        ? json.detail
        : json?.detail?.[0]?.msg || json?.message || `HTTP ${res.status}`
    )
  }
  return unwrapData(json) ?? json
}

/**
 * POST /api/v1/action-plan/items/{item_id}/update
 * @param {string} itemId
 * @param {{ student_id: string, status: string, evidence?: string }} body
 */
export async function updateActionPlanItemStatus(itemId, body) {
  const url = new URL(`/api/v1/action-plan/items/${encodeURIComponent(itemId)}/update`, baseUrlOrDefault())
  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })
  const { json } = await parseJsonResponse(res)
  if (!res.ok) {
    throw new Error(
      typeof json?.detail === 'string'
        ? json.detail
        : json?.detail?.[0]?.msg || json?.message || `HTTP ${res.status}`
    )
  }
  return unwrapData(json) ?? json
}

/**
 * GET /api/v1/profile/fluctuation（文档 3.9）
 * @param {string} studentId
 * @param {string} [month] YYYY-MM
 */
export async function getProfileFluctuation(studentId, month) {
  const url = new URL('/api/v1/profile/fluctuation', baseUrlOrDefault())
  url.searchParams.set('student_id', String(studentId))
  if (month) url.searchParams.set('month', String(month))
  const res = await fetch(url.toString(), {
    method: 'GET',
    headers: { Accept: 'application/json' },
  })
  const { json } = await parseJsonResponse(res)
  if (!res.ok) {
    throw new Error(
      typeof json?.detail === 'string'
        ? json.detail
        : json?.detail?.[0]?.msg || json?.message || `HTTP ${res.status}`
    )
  }
  return unwrapData(json) ?? json
}

/**
 * POST /api/v1/action-plan/evaluate（文档 3.10）
 */
export async function triggerMonthlyEvaluation(body) {
  const url = new URL('/api/v1/action-plan/evaluate', baseUrlOrDefault())
  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })
  const { json } = await parseJsonResponse(res)
  if (!res.ok) {
    throw new Error(
      typeof json?.detail === 'string'
        ? json.detail
        : json?.detail?.[0]?.msg || json?.message || `HTTP ${res.status}`
    )
  }
  return unwrapData(json) ?? json
}

/**
 * GET /api/v1/reports/quarterly（文档 3.11）
 * @param {string} studentId
 * @param {number} [months]
 */
export async function getQuarterlyReport(studentId, months = 3) {
  const url = new URL('/api/v1/reports/quarterly', baseUrlOrDefault())
  url.searchParams.set('student_id', String(studentId))
  url.searchParams.set('months', String(months))
  const res = await fetch(url.toString(), {
    method: 'GET',
    headers: { Accept: 'application/json' },
  })
  const { json } = await parseJsonResponse(res)
  if (!res.ok) {
    throw new Error(
      typeof json?.detail === 'string'
        ? json.detail
        : json?.detail?.[0]?.msg || json?.message || `HTTP ${res.status}`
    )
  }
  return unwrapData(json) ?? json
}

/** 与《前端接入后端接口详细文档》命名一致：更新任务状态 */
export const updateActionItemStatus = updateActionPlanItemStatus

/**
 * POST /api/v1/report/polish
 * @param {{ content: string, student_id?: string, profile_cache_id?: string }} body
 */
export async function postReportPolish(body) {
  const url = new URL('/api/v1/report/polish', baseUrlOrDefault())
  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })
  const { json } = await parseJsonResponse(res)
  if (!res.ok) {
    throw new Error(
      typeof json?.detail === 'string'
        ? json.detail
        : json?.detail?.[0]?.msg || json?.message || `HTTP ${res.status}`
    )
  }
  return unwrapData(json) ?? json
}

/**
 * GET /api/v1/profile/snapshots?student_id={student_id}&limit={limit}
 */
export async function getProfileSnapshots(studentId, limit = 12) {
  const url = new URL('/api/v1/profile/snapshots', baseUrlOrDefault())
  url.searchParams.set('student_id', String(studentId))
  url.searchParams.set('limit', String(limit))
  const res = await fetch(url.toString(), {
    method: 'GET',
    headers: { Accept: 'application/json' },
  })
  const { json } = await parseJsonResponse(res)
  if (!res.ok) {
    throw new Error(
      typeof json?.detail === 'string'
        ? json.detail
        : json?.detail?.[0]?.msg || json?.message || `HTTP ${res.status}`
    )
  }
  const data = unwrapData(json) ?? json
  return Array.isArray(data?.snapshots) ? data.snapshots : []
}

/**
 * GET /api/v1/profile/snapshots/latest?student_id={student_id}
 */
export async function getLatestProfileSnapshot(studentId) {
  const url = new URL('/api/v1/profile/snapshots/latest', baseUrlOrDefault())
  url.searchParams.set('student_id', String(studentId))
  const res = await fetch(url.toString(), {
    method: 'GET',
    headers: { Accept: 'application/json' },
  })
  const { json } = await parseJsonResponse(res)
  if (!res.ok) {
    throw new Error(
      typeof json?.detail === 'string'
        ? json.detail
        : json?.detail?.[0]?.msg || json?.message || `HTTP ${res.status}`
    )
  }
  return unwrapData(json) ?? json
}

/** 与文档一致：获取最新画像快照 */
export const getLatestSnapshot = getLatestProfileSnapshot

/**
 * 规范岗位列表项（文档 2.1 normalizeJobRow）
 * @param {object} item
 * @returns {{ id: string, title: string, category: string, summary: string, company: string, salary_range: string, hot_index: number } | null}
 */
export function normalizeJobRow(item) {
  if (!item || typeof item !== 'object') return null
  const id = item.id ?? item.job_id
  if (id == null || id === '') return null
  const tags = item.field_tags ?? item.tags ?? []
  return {
    id: String(id),
    title: item.title || item.name || '',
    category: Array.isArray(tags) ? tags.slice(0, 3).join('/') : '',
    summary: item.summary || item.title || item.name || '',
    company: item.company || '',
    salary_range: item.salary_range || item.salaryRange || '',
    hot_index: Number(item.hot_index ?? item.match_score ?? item.match ?? 0) || 0,
  }
}

/**
 * 将后端返回的岗位列表项映射为 StudentAbilitiesView 使用的结构
 */
export function mapRecommendListItemToJob(row) {
  const n = normalizeJobRow(row)
  if (!n) return null
  const tags = row.field_tags ?? row.tags ?? []
  return {
    job_id: n.id,
    title: n.title || '岗位',
    match_score: Number.isFinite(n.hot_index) ? n.hot_index : 0,
    tags: Array.isArray(tags) ? tags : [],
  }
}

/**
 * 将阶段一解析响应映射为视图状态（尽量兼容多种字段名）
 */
export function mapParseResponseToState(raw) {
  const o = raw && typeof raw === 'object' ? raw : {}
  const profile =
    o.student_profile ??
    o.studentProfile ??
    o.profile ??
    o.parsed_profile ??
    o.resume_profile ??
    null
  const analysis =
    o.analysis_summary ??
    o.analysisSummary ??
    o.summary ??
    o.parse_summary ??
    null
  return {
    student_profile: profile,
    analysis_summary: analysis,
    recommended_jobs: o.recommended_jobs ?? o.recommendedJobs ?? [],
    other_jobs: o.other_jobs ?? o.otherJobs ?? [],
    profile_cache_id: o.profile_cache_id ?? o.profileCacheId ?? null,
  }
}

/**
 * 从岗位匹配详情或含 match_analysis 的片段中提取四维学生得分（兼容嵌套路径与别名字段）
 * @param {object} [o] 常为 postMatchDetail 响应，或 normalize 后的报告根对象
 * @returns {{ base?: number, skill?: number, soft?: number, potential?: number }}
 */
export function extractFourDimensionScoresFromMatchPayload(o) {
  if (!o || typeof o !== 'object') return {}
  const matchAnalysis = o.match_analysis ?? o.matchAnalysis
  const details = matchAnalysis?.details ?? {}
  const rootDetails = o.details && typeof o.details === 'object' ? o.details : {}
  const matchSummary = o.match_summary ?? o.matchSummary ?? {}
  let dims =
    o.dimensions ??
    details.dimensions ??
    rootDetails.dimensions ??
    rootDetails.dimension_scores ??
    details.dimension_scores ??
    matchSummary.dimensions ??
    {}

  if (Array.isArray(dims)) {
    const acc = {}
    for (const row of dims) {
      if (!row || typeof row !== 'object') continue
      const rawKey = String(row.dimension_key ?? row.key ?? row.dimension ?? '').toLowerCase()
      const val =
        row.student_score ??
        row.student_score_100 ??
        row.score ??
        row.value ??
        row.point
      const n = Number(val)
      if (!Number.isFinite(n)) continue
      if (rawKey === 'base' || rawKey === 'skill' || rawKey === 'soft' || rawKey === 'potential') {
        acc[rawKey] = n
      } else if (rawKey === 'basic') acc.base = n
      else if (rawKey === 'professional') acc.skill = n
      else if (rawKey === 'quality') acc.soft = n
      else if (rawKey === 'growth') acc.potential = n
    }
    dims = acc
  }

  if (!dims || typeof dims !== 'object' || Array.isArray(dims)) return {}

  const num = (v) => {
    const x = Number(v)
    return Number.isFinite(x) ? x : NaN
  }
  const base = num(dims.base ?? dims.basic ?? dims['基础要求'])
  const skill = num(dims.skill ?? dims.professional ?? dims['职业技能'])
  const soft = num(dims.soft ?? dims.quality ?? dims['职业素养'])
  const potential = num(dims.potential ?? dims.growth ?? dims['发展潜力'])
  const out = {}
  if (Number.isFinite(base)) out.base = base
  if (Number.isFinite(skill)) out.skill = skill
  if (Number.isFinite(soft)) out.soft = soft
  if (Number.isFinite(potential)) out.potential = potential
  return out
}

const RADAR_FOUR_KEYS = ['base', 'skill', 'soft', 'potential']

function normalizeFourDimKey(raw) {
  const k = String(raw || '')
    .toLowerCase()
    .trim()
  if (k === 'basic' || k === '基础要求') return 'base'
  if (k === 'professional' || k === '职业技能') return 'skill'
  if (k === 'quality' || k === '职业素养') return 'soft'
  if (k === 'growth' || k === '发展潜力') return 'potential'
  if (RADAR_FOUR_KEYS.includes(k)) return k
  return ''
}

function toRadarScore100(v) {
  const x = Number(v)
  if (!Number.isFinite(x)) return null
  if (x <= 10 && x >= 0) return Math.max(0, Math.min(100, Math.round(x * 10)))
  return Math.max(0, Math.min(100, Math.round(x)))
}

/**
 * 解析 POST /api/v1/match/detail（及同类结构）的四维雷达：学生 vs 岗位要求，0–100。
 * 兼容：① 顶层 dimensions[]（student_score / job_required_score）；
 * ② 元素字段 student_score_100 / job_required_score_100（module_1 four_dimensions）；
 * ③ details.dimensions 对象（calculate_match 仅学生四维分）；
 * ④ match_analysis.details.dimensions（本地 mock）。
 */
export function parseMatchRadarFourDimensionValues(detail) {
  const z = (n) => (typeof n === 'number' && Number.isFinite(n) ? n : 0)
  const fallbackJob = () => [75, 75, 75, 75]

  if (!detail || typeof detail !== 'object') {
    return { student: [0, 0, 0, 0], job: fallbackJob() }
  }

  let dims = detail.dimensions
  const rootDetails = detail.details && typeof detail.details === 'object' ? detail.details : {}
  if (dims === undefined || dims === null) {
    dims = rootDetails.dimensions ?? rootDetails.dimension_scores
  }

  if (Array.isArray(dims)) {
    const stud = { base: null, skill: null, soft: null, potential: null }
    const job = { base: null, skill: null, soft: null, potential: null }
    for (const row of dims) {
      if (!row || typeof row !== 'object') continue
      const dk = normalizeFourDimKey(row.dimension_key ?? row.key ?? row.dimension)
      if (!dk) continue
      const sv = toRadarScore100(
        row.student_score ??
          row.student_score_100 ??
          row.score ??
          row.student ??
          row.value
      )
      const jv = toRadarScore100(
        row.job_required_score ??
          row.job_required_score_100 ??
          row.job_score ??
          row.required_score
      )
      if (sv !== null) stud[dk] = sv
      if (jv !== null) job[dk] = jv
    }
    const student = RADAR_FOUR_KEYS.map((k) => (stud[k] !== null ? z(stud[k]) : 0))
    const hasAnyJob = RADAR_FOUR_KEYS.some((k) => job[k] !== null)
    const jobArr = hasAnyJob
      ? RADAR_FOUR_KEYS.map((k) => (job[k] !== null ? z(job[k]) : 70))
      : fallbackJob()
    return { student, job: jobArr }
  }

  if (dims && typeof dims === 'object') {
    const student = RADAR_FOUR_KEYS.map((k) => {
      const v = toRadarScore100(dims[k])
      return v === null ? 0 : v
    })
    const jobObj =
      detail.job_required_dimensions ??
      detail.job_required_dimensions_100 ??
      rootDetails.job_required_dimensions ??
      detail.target_job?.required_dimensions
    if (jobObj && typeof jobObj === 'object' && !Array.isArray(jobObj)) {
      const job = RADAR_FOUR_KEYS.map((k) => {
        const v = toRadarScore100(jobObj[k])
        return v === null ? 75 : v
      })
      return { student, job }
    }
    return { student, job: fallbackJob() }
  }

  const fromExtract = extractFourDimensionScoresFromMatchPayload(detail)
  const student = RADAR_FOUR_KEYS.map((k) => {
    const v = toRadarScore100(fromExtract[k])
    return v === null ? 0 : v
  })
  const hasStudent = RADAR_FOUR_KEYS.some((k) => fromExtract[k] !== undefined)
  if (hasStudent) {
    return { student, job: fallbackJob() }
  }

  return { student: [0, 0, 0, 0], job: fallbackJob() }
}

/**
 * 供 buildCompareDimensionRows 第二参数：四维得分展示为「xx.x 分」
 */
export function formatFourDimensionScoresForCompareRows(scores) {
  const s = scores && typeof scores === 'object' ? scores : {}
  const fmt = (k) => {
    const n = Number(s[k])
    return Number.isFinite(n) ? `${n.toFixed(1)} 分` : '—'
  }
  return {
    base: fmt('base'),
    skill: fmt('skill'),
    soft: fmt('soft'),
    potential: fmt('potential'),
  }
}

/**
 * 将阶段二匹配报告规范为视图使用的结构
 */
export function normalizeMatchReportPayload(raw) {
  if (!raw || typeof raw !== 'object') return null
  const summary = raw.summary ?? {}
  const matchSummary = raw.match_summary ?? raw.matchSummary ?? {}
  const jobInfo = raw.job_info ?? raw.jobInfo ?? {}
  const matchDetail = raw.match_detail ?? raw.matchDetail ?? {}
  const matchAnalysis =
    raw.match_analysis ??
    raw.matchAnalysis ?? {
      match_score: raw.match_score ?? summary.match_score ?? matchSummary.match_score,
      details: {
        dimensions: matchSummary.dimensions ?? matchDetail.dimensions ?? {},
      },
    }
  const details = matchAnalysis.details ?? {}
  const dims = details.dimensions ?? details.dimension_scores ?? {}

  const base = dims.base ?? dims.basic ?? dims['基础要求']
  const skill = dims.skill ?? dims.professional ?? dims['职业技能']
  const soft = dims.soft ?? dims.quality ?? dims['职业素养']
  const potential = dims.potential ?? dims.growth ?? dims['发展潜力']

  const careerReport = raw.career_report ?? raw.careerReport ?? {}
  const module1 = careerReport.module_1 ?? careerReport.module1 ?? {}
  const module2 = careerReport.module_2 ?? careerReport.module2 ?? {}
  const module3 = careerReport.module_3 ?? careerReport.module3 ?? {}
  const module4 = careerReport.module_4 ?? careerReport.module4 ?? {}
  const selectedPlan = module3.selected_plan ?? module3.selectedPlan ?? {}
  const gapAnalysisObj = selectedPlan.gap_analysis ?? selectedPlan.gapAnalysis ?? {}
  const dimRows = Array.isArray(gapAnalysisObj.dimensions) ? gapAnalysisObj.dimensions : []
  const dimReasons = dimRows
    .map((d) => d?.strategy || d?.dimension_label || d?.dimension_key)
    .filter(Boolean)
  const dimWarnings = Array.isArray(gapAnalysisObj.action_sequence)
    ? gapAnalysisObj.action_sequence
        .map((x) => x?.strategy || x?.dimension_label || x?.quadrant_label)
        .filter(Boolean)
    : []
  const module1Summary =
    module1?.student_info?.summary || module1?.overall_summary || module1?.llm_commentary?.overall_summary
  const reportGapText =
    careerReport.gap_analysis ??
    careerReport.gapAnalysis ??
    selectedPlan?.llm_commentary?.overall_summary ??
    module1Summary ??
    ''
  const reportActionPlan =
    careerReport.action_plan ??
    careerReport.actionPlan ??
    selectedPlan?.llm_commentary?.risk_and_opportunity?.join('；') ??
    ''
  const reportLearningPath =
    careerReport.learning_path ??
    careerReport.learningPath ??
    selectedPlan.timeline ??
    module2?.career_paths?.recommended_path?.timeline ??
    (Array.isArray(module3?.path_candidates)
      ? module3.path_candidates.map((p) => p?.title).filter(Boolean).join(' -> ')
      : '')
  const reportLearningPathImage =
    careerReport.learning_path_image ??
    careerReport.learningPathImage ??
    careerReport.path_image ??
    careerReport.pathImage ??
    selectedPlan.path_image ??
    selectedPlan.pathImage ??
    selectedPlan.roadmap_image ??
    selectedPlan.roadmapImage

  const module1Strengths = Array.isArray(module1?.strengths)
    ? module1.strengths
        .map((x) => x?.dimension_label ?? x?.label ?? x?.dimension_key ?? x?.name)
        .filter(Boolean)
    : []
  const module1Gaps = Array.isArray(module1?.gaps)
    ? module1.gaps
        .map((x) => x?.dimension_label ?? x?.label ?? x?.dimension_key ?? x?.name)
        .filter(Boolean)
    : []

  const reportStrengths =
    careerReport.strengths ??
    careerReport.advantages ??
    module1Strengths
  const reportWeaknesses =
    careerReport.weaknesses ??
    careerReport.gaps ??
    module1Gaps

  const module3Evaluation =
    selectedPlan?.evaluation?.summary ??
    (Array.isArray(selectedPlan?.evaluation?.metrics)
      ? selectedPlan.evaluation.metrics
          .map((m) => m?.description ?? m?.metric ?? m?.text ?? m?.name)
          .filter(Boolean)
          .join('；')
      : '')
  const module4Polished =
    module4?.polished_markdown ?? module4?.polishedMarkdown ?? ''
  const reportEvaluationSummary =
    careerReport.evaluation_summary ??
    careerReport.evaluationSummary ??
    careerReport.stage_evaluation ??
    careerReport.stageEvaluation ??
    module3Evaluation ??
    module4Polished

  const shortPlan =
    careerReport.short_term_plan ??
    careerReport.shortTermPlan ??
    selectedPlan?.short_term?.skills ??
    selectedPlan?.shortTerm?.skills
  const midPlan =
    careerReport.mid_term_plan ??
    careerReport.midTermPlan ??
    selectedPlan?.mid_term?.skills ??
    selectedPlan?.midTerm?.skills
  const planTableRows = selectedPlan?.plan_table?.rows ?? selectedPlan?.planTable?.rows
  const modulePlanItems = module3?.plan_items ?? module3?.planItems
  const planItemsRows = Array.isArray(modulePlanItems) ? modulePlanItems : null

  const normalizePlanRows = (rows) => {
    if (!Array.isArray(rows)) return undefined
    return rows
      .map((r) => {
        if (!r || typeof r !== 'object') return null
        return {
          phase: r.phase ?? r.stage ?? r.skill ?? r.skill_theme ?? r.theme ?? '',
          time: r.time ?? r.timeline ?? r.period ?? selectedPlan?.short_term?.timeline ?? '',
          direction: r.direction ?? r.focus ?? r.core ?? r.goal ?? '',
          path:
            r.path ??
            r.learning_path ??
            r.learningPath ??
            r.criteria ??
            '',
          practice:
            r.practice ??
            r.practice_plan ??
            `预估工时：${r.hours ?? r.estimated_hours ?? '-'}h；优先级：${r.priority ?? '-'}`,
          metric: r.metric ?? r.metrics ?? r.evaluation ?? r.criteria ?? '',
        }
      })
      .filter(Boolean)
  }

  const normalizedFromPlanItems = normalizePlanRows(planItemsRows)
  const normalizedShortPlan =
    normalizePlanRows(shortPlan) ??
    normalizePlanRows(planTableRows)?.slice(0, 3) ??
    (normalizedFromPlanItems?.length ? normalizedFromPlanItems.slice(0, 3) : undefined)
  const normalizedMidPlan =
    normalizePlanRows(midPlan) ??
    normalizePlanRows(planTableRows)?.slice(3) ??
    (normalizedFromPlanItems?.length > 3 ? normalizedFromPlanItems.slice(3) : undefined)

  return {
    job_info: {
      job_id: jobInfo.job_id ?? jobInfo.id ?? raw.job_id ?? summary?.target_job?.job_id,
      title: jobInfo.title ?? jobInfo.name ?? summary?.target_job?.title ?? summary?.target_job_title,
      company: jobInfo.company,
      description: jobInfo.description,
      salary_range: jobInfo.salary_range ?? jobInfo.salaryRange,
      location: jobInfo.location,
    },
    match_analysis: {
      match_score: Number(
        matchAnalysis.match_score ??
          matchAnalysis.score ??
          summary.match_score ??
          matchSummary.match_score ??
          0
      ),
      details: {
        dimensions: {
          base: base != null ? Number(base) : undefined,
          skill: skill != null ? Number(skill) : undefined,
          soft: soft != null ? Number(soft) : undefined,
          potential: potential != null ? Number(potential) : undefined,
        },
        reasons: Array.isArray(details.reasons)
          ? details.reasons
          : Array.isArray(details.strengths)
            ? details.strengths
            : Array.isArray(summary.top_strengths)
              ? summary.top_strengths
              : dimReasons.length
                ? dimReasons
            : [],
        warnings: Array.isArray(details.warnings)
          ? details.warnings
          : Array.isArray(details.gaps)
            ? details.gaps
            : Array.isArray(summary.key_gaps)
              ? summary.key_gaps
              : dimWarnings.length
                ? dimWarnings
            : [],
      },
    },
    career_report: {
      gap_analysis: reportGapText,
      action_plan: reportActionPlan,
      learning_path: reportLearningPath,
      learning_path_image: reportLearningPathImage,
      strengths: reportStrengths,
      weaknesses: reportWeaknesses,
      evaluation_summary: reportEvaluationSummary,
      short_term_plan: normalizedShortPlan,
      mid_term_plan: normalizedMidPlan,
      module_1: module1,
      module_2: module2,
      module_3: module3,
      module_4: module4,
    },
  }
}

/**
 * 将 API 返回的成长计划行映射为表格行（若字段名不一致）
 */
export function mapPlanRow(row) {
  if (!row || typeof row !== 'object') return null
  return {
    phase: row.phase ?? row.stage ?? row.title ?? '',
    time: row.time ?? row.timeline ?? row.period ?? '',
    direction: row.direction ?? row.focus ?? row.core ?? '',
    path: row.path ?? row.learning_path ?? row.learningPath ?? '',
    practice: row.practice ?? row.practice_plan ?? '',
    metric: row.metric ?? row.metrics ?? row.evaluation ?? '',
  }
}

/**
 * 行动计划 API 单项映射（文档 2.1 `mapPlanRow` 中面向 Todo 项的结构；勿与上方学习路径表格 `mapPlanRow` 混淆）
 */
export function mapActionPlanItemFromApi(item) {
  if (!item || typeof item !== 'object') return null
  return {
    id: item.id || item.item_id,
    title: item.title || item.skill || '',
    description: item.description || '',
    target_dimension: item.target_dimension || '',
    target_dimension_label: item.target_dimension_label || '',
    skill_keywords: item.skill_keywords || [],
    completion_criteria: item.completion_criteria || item.criteria || '',
    estimated_hours: item.estimated_hours || 0,
    difficulty: item.difficulty || 'standard',
    milestone_checkpoints: item.milestone_checkpoints || item.milestones || [],
    status: item.status || 'pending',
    is_rolled_over: item.is_rolled_over || false,
    completed_at: item.completed_at || null,
    progress_percent: item.progress_percent || 0,
  }
}
