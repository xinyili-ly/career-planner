/**
 * 岗位画像 API 统一错误类型（便于页面区分 HTTP 错误、业务码、非 JSON 等）
 */
export function formatJobPortraitApiError(error) {
  if (error instanceof JobPortraitApiError) {
    const parts = [error.message]
    if (error.businessCode !== undefined && error.businessCode !== null && error.businessCode !== '') {
      parts.push(`业务码 ${error.businessCode}`)
    }
    if (error.httpStatus) {
      parts.push(`HTTP ${error.httpStatus}`)
    }
    if (error.kind === 'parse' && error.bodySnippet) {
      parts.push(`片段: ${error.bodySnippet}`)
    }
    if (error.serverApiVersion) {
      parts.push(`服务端版本 ${error.serverApiVersion}`)
    }
    return parts.join(' · ')
  }
  if (error && typeof error.message === 'string') return error.message
  return '接口请求失败'
}

export class JobPortraitApiError extends Error {
  /**
   * @param {string} message
   * @param {{
   *   httpStatus?: number
   *   businessCode?: number | string
   *   businessMessage?: string
   *   contentType?: string | null
   *   bodySnippet?: string
   *   serverApiVersion?: string | null
   *   kind?: 'http' | 'business' | 'parse' | 'network'
   * }} [opts]
   */
  constructor(message, opts = {}) {
    super(message)
    this.name = 'JobPortraitApiError'
    this.httpStatus = opts.httpStatus
    this.businessCode = opts.businessCode
    this.businessMessage = opts.businessMessage
    this.contentType = opts.contentType
    this.bodySnippet = opts.bodySnippet
    this.serverApiVersion = opts.serverApiVersion ?? null
    this.kind = opts.kind || 'http'
  }
}
