export function unwrapData(payload) {
  if (payload && typeof payload === 'object' && 'data' in payload) {
    return payload.data || {}
  }
  return payload || {}
}

export function extractJobsArray(payload) {
  const data = unwrapData(payload)
  if (Array.isArray(data)) return data
  if (Array.isArray(data?.jobs)) return data.jobs
  if (Array.isArray(data?.list)) return data.list
  if (Array.isArray(data?.portraits)) return data.portraits
  if (Array.isArray(data?.data) && data.data.length && typeof data.data[0] === 'object') return data.data
  return []
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

export function normalizeTransfer(raw, jobName) {
  const transferSource = Array.isArray(raw.transfers)
    ? raw.transfers
    : Array.isArray(raw.transferPaths)
      ? raw.transferPaths
      : Array.isArray(raw.paths)
        ? raw.paths
        : []

  const transfers = transferSource
    .map((item) => ({
      title: normalizeText(item?.title || item?.name || item?.label, ''),
      steps: normalizeStringArray(item?.steps || item?.path),
      keyGaps: normalizeStringArray(item?.keyGaps || item?.gaps || item?.skillsGap)
    }))
    .filter((item) => item.title && item.steps.length >= 2)

  return {
    name: normalizeText(raw.name || raw.title, jobName),
    transfers
  }
}

export function mergePortraitParts(recommend, path, transfer, jobName) {
  return {
    name: recommend.name || transfer.name || jobName,
    summary: recommend.summary,
    profileDims: recommend.profileDims,
    relations: recommend.relations,
    vertical: path.vertical,
    transfers: transfer.transfers
  }
}

/** 聚合接口单条岗位对象（与原先 recommend/path/transfer 三接口合并结构一致） */
export function portraitFromMergedRaw(raw, jobName) {
  const recommend = normalizeRecommend(raw, jobName)
  const path = normalizePath(raw)
  const transfer = normalizeTransfer(raw, jobName)
  return mergePortraitParts(recommend, path, transfer, jobName)
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
