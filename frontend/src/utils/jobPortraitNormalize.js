/**
 * 解开 { code, data, apiVersion? } 包络；无 data 字段时原样返回（兼容直出数组/对象）。
 * 注意：业务失败应在 jobPortraitApi 层已抛错，到达此处均为成功包络。
 */
export function unwrapData(payload) {
  if (payload && typeof payload === 'object' && 'data' in payload) {
    const inner = payload.data
    if (inner === null || inner === undefined) return {}
    return inner
  }
  return payload ?? {}
}

/** 读取包络上的可选 apiVersion（body）；成功响应由 API 层解析。 */
export function unwrapApiVersion(payload) {
  if (payload && typeof payload === 'object' && typeof payload.apiVersion === 'string') {
    return payload.apiVersion
  }
  return null
}

export function extractJobsArray(payload) {
  const data = unwrapData(payload)
  if (Array.isArray(data)) return data
  if (Array.isArray(data?.jobs)) return data.jobs
  if (Array.isArray(data?.list)) return data.list
  if (Array.isArray(data?.items)) return data.items
  if (Array.isArray(data?.records)) return data.records
  if (Array.isArray(data?.portraits)) return data.portraits
  if (Array.isArray(data?.data) && data.data.length && typeof data.data[0] === 'object') return data.data
  return []
}

/** 分页场景的 total（后端提供 total / count 时用于前端分页） */
export function extractJobsTotal(payload) {
  const data = unwrapData(payload)
  if (data && typeof data === 'object') {
    const t = data.total ?? data.count
    if (typeof t === 'number' && Number.isFinite(t)) return t
    if (typeof t === 'string' && /^\d+$/.test(t)) return Number(t)
  }
  return null
}

export function normalizeText(value, fallback = '') {
  if (typeof value === 'string') return value
  if (typeof value === 'number') return String(value)
  return fallback
}

export function normalizeField(summary, fallbackField) {
  const text = normalizeText(summary)
  if (!text) return fallbackField
  return text.replace(/\s+/g, '').slice(0, 6) || fallbackField
}

export function normalizeStringArray(value) {
  if (!Array.isArray(value)) return []
  return value.map((item) => normalizeText(item)).filter(Boolean)
}

export function normalizeRecommend(raw, jobName) {
  const profileDimsSource = Array.isArray(raw.profileDims)
    ? raw.profileDims
    : Array.isArray(raw.dims)
      ? raw.dims
      : []
  const relationsSource = Array.isArray(raw.relations)
    ? raw.relations
    : Array.isArray(raw.relatedJobs)
      ? raw.relatedJobs
      : []

  return {
    name: normalizeText(raw.name || raw.title, jobName),
    summary: normalizeText(raw.summary || raw.description, ''),
    profileDims: profileDimsSource
      .map((item) => ({
        name: normalizeText(item?.name || item?.label || item?.dimension, ''),
        desc: normalizeText(item?.desc || item?.description || item?.value, '')
      }))
      .filter((item) => item.name && item.desc),
    relations: relationsSource
      .map((item) => ({
        role: normalizeText(item?.role || item?.name || item?.job, ''),
        reason: normalizeText(item?.reason || item?.desc || item?.description, '')
      }))
      .filter((item) => item.role && item.reason)
  }
}

export function normalizePath(raw) {
  const verticalSource = Array.isArray(raw.vertical)
    ? raw.vertical
    : Array.isArray(raw.path)
      ? raw.path
      : Array.isArray(raw.paths)
        ? raw.paths
        : []

  return {
    vertical: verticalSource
      .map((item) => ({
        title: normalizeText(item?.title || item?.name || item?.stage, ''),
        focus: normalizeText(item?.focus || item?.desc || item?.description, '')
      }))
      .filter((item) => item.title && item.focus)
  }
}

function transferCandidatesFromPathGraph(pathGraph) {
  if (!pathGraph) return []
  if (Array.isArray(pathGraph)) return pathGraph
  if (Array.isArray(pathGraph.transfers)) return pathGraph.transfers
  if (Array.isArray(pathGraph.transferPaths)) return pathGraph.transferPaths
  if (Array.isArray(pathGraph.paths)) return pathGraph.paths
  if (Array.isArray(pathGraph.edges) && Array.isArray(pathGraph.nodes)) {
    return pathGraph.edges
      .map((e) => ({
        title: normalizeText(e?.label || e?.name || e?.title, '换岗路径'),
        steps: normalizeStringArray(e?.steps || e?.path || e?.nodes),
        keyGaps: normalizeStringArray(e?.keyGaps || e?.gaps)
      }))
      .filter((item) => item.steps.length >= 1)
  }
  return []
}

export function normalizeTransfer(raw, jobName) {
  let transferSource = []
  if (Array.isArray(raw.transfers)) transferSource = raw.transfers
  else if (Array.isArray(raw.transferPaths)) transferSource = raw.transferPaths
  else if (Array.isArray(raw.paths)) transferSource = raw.paths
  else {
    const fromGraph = transferCandidatesFromPathGraph(raw.path_graph)
    if (fromGraph.length) transferSource = fromGraph
  }

  const transfers = transferSource
    .map((item) => ({
      title: normalizeText(item?.title || item?.name || item?.label, ''),
      steps: normalizeStringArray(item?.steps || item?.path || item?.route),
      keyGaps: normalizeStringArray(item?.keyGaps || item?.gaps || item?.skillsGap)
    }))
    .filter((item) => item.title && item.steps.length >= 1)

  return {
    name: normalizeText(raw.name || raw.title, jobName),
    transfers
  }
}

/**
 * 详情页扩展字段：头图、技能/申请条件、path_graph 原样保留给图谱组件。
 * 后端字段名可在此集中扩展映射。
 */
export function normalizeDetailExtras(raw) {
  const hero = normalizeText(
    raw.hero_image || raw.cover_url || raw.heroImage || raw.banner_url || raw.image || '',
    ''
  )

  let skillBullets = normalizeStringArray(raw.skill_requirements || raw.skills || raw.skill_list)
  if (
    typeof raw.skill_requirements === 'string' &&
    !skillBullets.length &&
    raw.skill_requirements.trim()
  ) {
    skillBullets = raw.skill_requirements
      .split(/[\n,，;；]/)
      .map((s) => s.trim())
      .filter(Boolean)
  }
  const skillHtml =
    typeof raw.skills_html === 'string' && raw.skills_html.trim() ? raw.skills_html.trim() : ''

  const conditions = {
    education: normalizeText(
      raw.education_requirement || raw.degree_requirement || raw.education || '',
      ''
    ),
    majors: normalizeText(raw.major_requirement || raw.related_majors || raw.majors || '', ''),
    internship: normalizeText(raw.internship_requirement || raw.experience_requirement || '', ''),
    certificates: normalizeText(raw.certificate_requirement || raw.certificates || '', ''),
    other: normalizeText(raw.other_requirements || raw.conditions_note || '', '')
  }

  let conditionBullets = normalizeStringArray(
    raw.application_conditions || raw.conditions_list || raw.condition_bullets
  )
  if (
    typeof raw.application_conditions === 'string' &&
    !conditionBullets.length &&
    raw.application_conditions.trim()
  ) {
    conditionBullets = raw.application_conditions
      .split(/[\n,，;；]/)
      .map((s) => s.trim())
      .filter(Boolean)
  }

  const pathGraph =
    raw.path_graph && typeof raw.path_graph === 'object' ? raw.path_graph : null

  return {
    heroImage: hero,
    skillBullets,
    skillHtml,
    conditions,
    conditionBullets,
    pathGraph
  }
}

export function mergePortraitParts(recommend, path, transfer, extras, jobName) {
  return {
    name: recommend.name || transfer.name || jobName,
    summary: recommend.summary,
    profileDims: recommend.profileDims,
    relations: recommend.relations,
    vertical: path.vertical,
    transfers: transfer.transfers,
    ...extras
  }
}

/** 聚合接口单条岗位对象（与原先 recommend/path/transfer 三接口合并结构一致） */
export function portraitFromMergedRaw(raw, jobName) {
  const recommend = normalizeRecommend(raw, jobName)
  const path = normalizePath(raw)
  const transfer = normalizeTransfer(raw, jobName)
  const extras = normalizeDetailExtras(raw)
  return mergePortraitParts(recommend, path, transfer, extras, jobName)
}

const JOB_LIST_CACHE_KEY = 'job_portraits_recommend_list_v1'

/** 缓存 /recommend/list 的原始项，供详情页顶栏在首屏展示 title/company */
export function saveJobListCache(list) {
  const byId = {}
  for (const raw of list) {
    const id = raw?.id != null ? String(raw.id) : ''
    if (!id) continue
    byId[id] = raw
  }
  try {
    sessionStorage.setItem(JOB_LIST_CACHE_KEY, JSON.stringify({ ts: Date.now(), byId }))
  } catch {
    /* ignore quota */
  }
}

export function loadJobListItemFromCache(id) {
  if (id == null || id === '') return null
  try {
    const raw = sessionStorage.getItem(JOB_LIST_CACHE_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw)
    return parsed?.byId?.[String(id)] ?? null
  } catch {
    return null
  }
}
