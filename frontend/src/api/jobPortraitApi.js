import {
  HEADER_CLIENT_CONTRACT,
  HEADER_SERVER_API_VERSION,
  JOB_PORTRAIT_CLIENT_CONTRACT_VERSION,
  JOB_PORTRAIT_ERROR_HINT,
  JOB_PORTRAIT_SUCCESS_CODES,
} from './jobPortraitContract'
import { JobPortraitApiError } from './jobPortraitErrors'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'https://career-planner--3144682663.replit.app'

/** 最近一次成功响应中记录的服务端版本（响应头 X-API-Version 或 body.apiVersion） */
let lastServerApiVersion = null

export function getLastJobPortraitServerApiVersion() {
  return lastServerApiVersion
}

function looksLikeHtml(text) {
  const t = String(text).trim().slice(0, 400).toLowerCase()
  return t.startsWith('<!doctype') || t.startsWith('<html') || t.includes('<head')
}

function isJsonContentType(ct) {
  if (!ct) return false
  const s = String(ct).toLowerCase()
  return s.includes('application/json') || s.includes('+json')
}

function parseJsonText(text) {
  const trimmed = String(text).trim()
  if (!trimmed) {
    throw new JobPortraitApiError(JOB_PORTRAIT_ERROR_HINT.EMPTY_BODY, {
      kind: 'parse',
    })
  }
  try {
    return JSON.parse(text)
  } catch {
    if (looksLikeHtml(text)) {
      throw new JobPortraitApiError(JOB_PORTRAIT_ERROR_HINT.NON_JSON, {
        kind: 'parse',
        contentType: 'text/html',
        bodySnippet: trimmed.slice(0, 200),
      })
    }
    throw new JobPortraitApiError(JOB_PORTRAIT_ERROR_HINT.INVALID_JSON, {
      kind: 'parse',
      bodySnippet: trimmed.slice(0, 120),
    })
  }
}

/**
 * 若存在业务字段 code，则必须为约定成功码；否则抛 JobPortraitApiError。
 * 无 code 字段时视为历史兼容格式，原样返回。
 */
function assertBusinessSuccess(json, serverApiVersionHeader) {
  if (json == null || typeof json !== 'object' || !('code' in json)) {
    return json
  }
  const code = json.code
  if (JOB_PORTRAIT_SUCCESS_CODES.has(code)) {
    return json
  }
  const msg =
    typeof json.message === 'string'
      ? json.message
      : typeof json.msg === 'string'
        ? json.msg
        : `业务错误（code=${String(code)}）`
  throw new JobPortraitApiError(msg, {
    kind: 'business',
    businessCode: code,
    businessMessage: msg,
    serverApiVersion: serverApiVersionHeader,
  })
}

function networkMessage(error) {
  if (error && typeof error.message === 'string') return error.message
  return '网络请求失败'
}

function maxRetries() {
  const n = Number(import.meta.env.VITE_API_RETRY_COUNT)
  if (Number.isFinite(n) && n >= 0) return Math.min(5, Math.floor(n))
  return 1
}

function shouldRetry(error, attempt, max) {
  if (attempt >= max) return false
  if (!(error instanceof JobPortraitApiError)) return false
  if (error.kind === 'network') return true
  if (error.kind === 'http' && error.httpStatus === 503) return true
  return false
}

async function requestApiOnce(path, params = {}) {
  const url = new URL(path, API_BASE_URL)
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.set(key, String(value))
    }
  })

  let response
  try {
    response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        [HEADER_CLIENT_CONTRACT]: JOB_PORTRAIT_CLIENT_CONTRACT_VERSION,
      },
    })
  } catch (e) {
    throw new JobPortraitApiError(networkMessage(e), { kind: 'network' })
  }

  const serverVerHeader = response.headers.get(HEADER_SERVER_API_VERSION)
  if (serverVerHeader) lastServerApiVersion = serverVerHeader

  const contentType = response.headers.get('content-type')
  const text = await response.text()

  if (!response.ok) {
    let bizCode
    let bizMsg
    if (contentType && isJsonContentType(contentType)) {
      try {
        const errJson = parseJsonText(text)
        if (errJson && typeof errJson === 'object') {
          bizCode = errJson.code
          bizMsg =
            typeof errJson.message === 'string'
              ? errJson.message
              : typeof errJson.msg === 'string'
                ? errJson.msg
                : undefined
        }
      } catch (e) {
        if (e instanceof JobPortraitApiError) {
          /* 仍用 HTTP 错误主因 */
        }
      }
    }
    throw new JobPortraitApiError(
      bizMsg || `HTTP ${response.status}: ${response.statusText}`,
      {
        kind: 'http',
        httpStatus: response.status,
        businessCode: bizCode,
        businessMessage: bizMsg,
        contentType,
        bodySnippet: text.trim().slice(0, 200),
        serverApiVersion: serverVerHeader,
      }
    )
  }

  let json
  if (contentType && isJsonContentType(contentType)) {
    json = parseJsonText(text)
  } else {
    try {
      json = JSON.parse(String(text).trim())
    } catch {
      throw new JobPortraitApiError(JOB_PORTRAIT_ERROR_HINT.NON_JSON, {
        kind: 'parse',
        contentType,
        bodySnippet: text.trim().slice(0, 200),
        serverApiVersion: serverVerHeader,
      })
    }
  }

  json = assertBusinessSuccess(json, serverVerHeader)

  if (json && typeof json === 'object' && typeof json.apiVersion === 'string' && json.apiVersion) {
    lastServerApiVersion = json.apiVersion
  }

  return json
}

async function requestApi(path, params = {}) {
  const max = maxRetries()
  let lastErr
  for (let attempt = 0; attempt <= max; attempt++) {
    try {
      return await requestApiOnce(path, params)
    } catch (e) {
      lastErr = e
      if (shouldRetry(e, attempt, max)) {
        await new Promise((r) => setTimeout(r, 320 * (attempt + 1)))
        continue
      }
      throw e
    }
  }
  throw lastErr
}

/**
 * OpenAPI: GET /recommend/list
 * 成功时约定：{ code: 0, data: JobItem[] } 或直接返回数组（无 code）
 * @param {Record<string, string | number>} [params] 可选查询：keyword、page、page_size、sort 等（后端支持时生效）
 */
export function getRecommendJobList(params = {}) {
  return requestApi('/recommend/list', params)
}

/**
 * OpenAPI: GET /job_detail/{id}
 * 成功时约定：{ code: 0, data: JobDetail } 或直接返回对象（无 code）
 */
export function getJobDetail(id) {
  const path = `/job_detail/${encodeURIComponent(String(id))}`
  return requestApi(path)
}
