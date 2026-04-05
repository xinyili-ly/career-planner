/**
 * 岗位画像 OpenAPI 契约（前端侧约定，供与后端对齐）
 *
 * 列表：GET /recommend/list
 * 详情：GET /job_detail/{id}
 *
 * --- 响应包络（推荐，便于错误码与版本）---
 * {
 *   "code": 0,                    // 业务码：0 / 200 表示成功（见 JOB_PORTRAIT_SUCCESS_CODES）
 *   "message": "ok",             // 失败时人类可读原因
 *   "apiVersion": "1",           // 可选，接口版本（也可由响应头 X-API-Version 返回）
 *   "data": ...                  // 成功载荷：列表为数组，详情为对象
 * }
 *
 * 兼容：无 code 字段时，视为成功（直出数组或对象的历史格式）。
 *
 * --- 空数据 ---
 * 列表：{ "code": 0, "data": [] } 表示合法空列表，非 HTTP 错误。
 * 详情：{ "code": 0, "data": null } 或 data 缺少 id/title 时，前端可走兜底或提示「详情为空」。
 */

/** 前端声明的契约版本（请求头携带，便于后端做兼容分支） */
export const JOB_PORTRAIT_CLIENT_CONTRACT_VERSION = '1'

/** 请求头：客户端契约版本 */
export const HEADER_CLIENT_CONTRACT = 'X-Client-Contract-Version'

/** 响应头：服务端 API 版本（若后端未设置则忽略） */
export const HEADER_SERVER_API_VERSION = 'X-API-Version'

/** 判定为「业务成功」的.code 取值（number 与 string 均兼容） */
export const JOB_PORTRAIT_SUCCESS_CODES = new Set([0, 200, '0', '200', 'OK'])

/** 非 JSON/HTML 占位页等业务上需单独提示的场景 */
export const JOB_PORTRAIT_ERROR_HINT = {
  NON_JSON: '响应不是 JSON（多为 HTML 页面）。请确认 VITE_API_BASE_URL 指向提供 /recommend/list 与 /job_detail/{id} 的 API 服务，而不是纯前端站点。',
  EMPTY_BODY: '响应体为空，无法解析岗位数据。',
  INVALID_JSON: '响应不是合法的 JSON。',
}
