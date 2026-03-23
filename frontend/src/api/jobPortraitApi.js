const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://192.168.31.94:8000'

async function requestJSON(path, params = {}) {
  const url = new URL(path, API_BASE_URL)
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.set(key, String(value))
    }
  })

  const response = await fetch(url.toString(), {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    let detail = ''
    try {
      detail = await response.text()
    } catch {
      detail = ''
    }
    throw new Error(`HTTP ${response.status}: ${detail || response.statusText}`)
  }

  return response.json()
}

/**
 * OpenAPI: GET /recommend/list — 获取系统中所有岗位的列表（含 id、title、field_tags、company 等）
 * @returns {Promise<{ code?: number, message?: string, data: object[] }>}
 */
export function getRecommendJobList() {
  return requestJSON('/recommend/list')
}

/**
 * OpenAPI: GET /job_detail/{id} — 单岗位完整画像（profileDims、vertical、transfers、path_graph 等）
 * @param {string} id 岗位 ID，如 JOB_001
 */
export function getJobDetail(id) {
  const path = `/job_detail/${encodeURIComponent(String(id))}`
  return requestJSON(path)
}
