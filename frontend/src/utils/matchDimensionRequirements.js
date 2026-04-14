import { getJobDetail } from '../api/jobPortraitApi'

/**
 * 人岗匹配「四维」与岗位画像七维字段的对应关系（与后端 career_report_module1 一致）
 */
const FOUR_DIM_COMP_KEYS = {
  base: ['certificate_requirements', 'internship_experience'],
  skill: ['professional_skills'],
  soft: ['stress_resistance', 'communication_skills'],
  potential: ['innovation_capability', 'learning_capability'],
}

const FOUR_KEYS = ['base', 'skill', 'soft', 'potential']
const FOUR_NAMES = ['基础要求', '职业技能', '职业素养', '发展潜力']

function compactForSimilarity(s) {
  return String(s)
    .replace(/\s+/g, '')
    .replace(/……|…|\.{3,}/g, '')
    .replace(/[，,]/g, '')
}

/** 字二元组 Dice 系数，用于识别「措辞略不同」的重复句（如两条实习要求） */
function diceCoefficientBigrams(a, b) {
  const ca = compactForSimilarity(a)
  const cb = compactForSimilarity(b)
  if (ca.length < 2 || cb.length < 2) return 0
  const countBigrams = (str) => {
    const m = new Map()
    for (let i = 0; i < str.length - 1; i++) {
      const bg = str.slice(i, i + 2)
      m.set(bg, (m.get(bg) || 0) + 1)
    }
    return m
  }
  const A = countBigrams(ca)
  const B = countBigrams(cb)
  let inter = 0
  let na = 0
  for (const [k, va] of A) {
    na += va
    const vb = B.get(k) || 0
    inter += Math.min(va, vb)
  }
  let nb = 0
  for (const v of B.values()) nb += v
  return na + nb > 0 ? (2 * inter) / (na + nb) : 0
}

/**
 * 短段是否被长段「实质覆盖」：整段包含、长前缀一致（含一条被 … 截断）、或 Dice 很高。
 */
function isRedundantClause(shorter, longer) {
  if (!shorter || !longer || shorter.length > longer.length) return false
  const MIN = 12
  if (shorter.length < MIN) return false
  if (longer.includes(shorter)) return true
  const cs = compactForSimilarity(shorter)
  const cl = compactForSimilarity(longer)
  if (cs.length >= MIN && cl.includes(cs)) return true
  const probe = Math.min(48, shorter.length)
  if (probe >= MIN && longer.slice(0, probe) === shorter.slice(0, probe)) return true
  const head = shorter.replace(/……|…|\.{3,}\s*$/u, '').trim()
  if (head.length >= MIN && longer.includes(head)) return true
  if (cs.length >= 18) {
    const d = diceCoefficientBigrams(shorter, longer)
    if (d >= 0.44) return true
  }
  return false
}

/**
 * 岗位要求常由多字段拼接，易出现「学历/专业/证书/实习」重复句段。
 * 按分号切句后去重：完全相同、短句被长句包含、以及高相似（Dice / 前缀 / 截断续写）的近重复。
 */
export function dedupeRequirementText(text) {
  if (text == null || typeof text !== 'string') return ''
  const raw = text.replace(/\s+/g, ' ').trim()
  if (!raw) return ''

  const normalize = (s) =>
    String(s)
      .replace(/\s+/g, ' ')
      .replace(/[。．]+$/g, '')
      .trim()

  const chunks = raw
    .split(/[；;\n]+/)
    .map(normalize)
    .filter(Boolean)
  if (chunks.length <= 1) return raw

  const seen = new Set()
  const unique = []
  for (const c of chunks) {
    if (seen.has(c)) continue
    seen.add(c)
    unique.push(c)
  }

  const MIN_SUB = 10
  const afterContain = []
  for (let i = 0; i < unique.length; i++) {
    const a = unique[i]
    let drop = false
    for (let j = 0; j < unique.length; j++) {
      if (i === j) continue
      const b = unique[j]
      if (a.length < b.length && a.length >= MIN_SUB && b.includes(a)) {
        drop = true
        break
      }
    }
    if (!drop) afterContain.push(a)
  }

  const out = []
  for (let i = 0; i < afterContain.length; i++) {
    const a = afterContain[i]
    let drop = false
    for (let j = 0; j < afterContain.length; j++) {
      if (i === j) continue
      const b = afterContain[j]
      if (a.length <= b.length && isRedundantClause(a, b)) {
        drop = true
        break
      }
    }
    if (!drop) out.push(a)
  }

  return out.join('；')
}

function formatSevenDimSlice(item) {
  if (!item || typeof item !== 'object') return ''
  const kw = Array.isArray(item.keywords) ? item.keywords.filter(Boolean) : []
  const kwStr = kw.length ? kw.slice(0, 14).join('、') : ''
  const desc = String(item.description || '').trim()
  if (desc && kwStr) return `${desc} 相关要点：${kwStr}。`
  if (desc) return desc
  if (kwStr) return `侧重：${kwStr}。`
  return ''
}

/**
 * 从职业规划报告 module_1.target_job.seven_dimensions 生成四维要求文案
 * @param {object} [targetJob]
 * @returns {Record<'base'|'skill'|'soft'|'potential', string>|null}
 */
export function buildFourDimensionRequirementsFromModule1TargetJob(targetJob) {
  const seven = targetJob?.seven_dimensions
  if (!Array.isArray(seven) || seven.length === 0) return null
  const byKey = {}
  for (const x of seven) {
    const k = x?.dimension_key
    if (k) byKey[k] = x
  }
  const pick = (keys) =>
    keys.map((k) => formatSevenDimSlice(byKey[k])).filter(Boolean).join(' ').trim()
  const out = {
    base: pick(FOUR_DIM_COMP_KEYS.base),
    skill: pick(FOUR_DIM_COMP_KEYS.skill),
    soft: pick(FOUR_DIM_COMP_KEYS.soft),
    potential: pick(FOUR_DIM_COMP_KEYS.potential),
  }
  return Object.values(out).some(Boolean) ? out : null
}

/**
 * 从岗位画像 GET /job_detail/{id} 的 data 对象生成四维要求文案
 * @param {object} [data] JobDetailResponseData
 * @returns {Record<'base'|'skill'|'soft'|'potential', string>|null}
 */
export function buildFourDimensionRequirementsFromJobDetailApiData(data) {
  if (!data || typeof data !== 'object') return null
  const dims = Array.isArray(data.profileDims) ? data.profileDims : []
  const descByName = {}
  for (const d of dims) {
    const n = d?.name
    if (n) descByName[n] = String(d?.desc || '').trim()
  }
  /** 用分号串联，便于与 dedupeRequirementText（按 [；;\n] 切句去重）配合 */
  const pick = (names) => names.map((n) => descByName[n]).filter(Boolean).join('；').trim()

  const baseParts = []
  const edu = String(data.education_requirement || '').trim()
  const maj = String(data.major_requirement || '').trim()
  if (edu) baseParts.push(`学历：${edu}`)
  if (maj) baseParts.push(`专业：${maj}`)
  if (Array.isArray(data.application_conditions)) {
    baseParts.push(...data.application_conditions.map(String).filter(Boolean))
  }
  const cert = String(data.certificate_requirement || '').trim()
  const intern = String(data.internship_requirement || '').trim()
  if (cert) baseParts.push(cert)
  if (intern) baseParts.push(`实习：${intern}`)

  const baseText = [baseParts.filter(Boolean).join('；'), pick(['证书要求', '实习能力'])]
    .filter(Boolean)
    .join('；')
    .trim()

  const skillList = Array.isArray(data.skill_requirements) ? data.skill_requirements.filter(Boolean) : []
  const skillText = [skillList.join('；'), descByName['专业技能']].filter(Boolean).join('；').trim()

  const softText = [pick(['抗压能力', '沟通能力']), String(data.other_requirements || '').trim()]
    .filter(Boolean)
    .join('；')
    .trim()

  const potText = pick(['创新能力', '学习能力']).trim()

  const out = {
    base: baseText,
    skill: skillText,
    soft: softText,
    potential: potText,
  }
  return Object.values(out).some(Boolean) ? out : null
}

/**
 * 匹配详情接口若返回 dimension_requirements 则优先使用
 */
export function dimensionRequirementsFromMatchDetail(detail) {
  const dr = detail?.dimension_requirements ?? detail?.dimensionRequirements
  if (!dr || typeof dr !== 'object') return null
  const pick = (a, b) => String(dr[a] ?? dr[b] ?? '').trim()
  const out = {
    base: pick('base', '基础要求'),
    skill: pick('skill', '职业技能'),
    soft: pick('soft', '职业素养'),
    potential: pick('potential', '发展潜力'),
  }
  return Object.values(out).some(Boolean) ? out : null
}

/**
 * 按层合并：每层只填补仍为空的维度，靠前层优先
 * @param {Array<Record<string, string>|null|undefined>} layers
 */
export function mergeDimensionRequirementTexts(layers) {
  const out = { base: '', skill: '', soft: '', potential: '' }
  for (const layer of layers) {
    if (!layer || typeof layer !== 'object') continue
    for (const k of FOUR_KEYS) {
      const v = layer[k]
      if (!out[k] && typeof v === 'string' && v.trim()) out[k] = v.trim()
    }
  }
  return out
}

export function fallbackRequirementTexts(jobTitle) {
  const t = jobTitle && String(jobTitle).trim() ? String(jobTitle).trim() : '目标岗位'
  return {
    base: `${t}：需满足岗位基本条件（学历/专业）、相关证书及实习或项目经历等，具体以岗位画像与 JD 为准。`,
    skill: `${t}：需掌握岗位核心技术栈与工程实践要求，并能独立完成职责范围内的开发或交付任务。`,
    soft: `${t}：需具备岗位所需的沟通协作、承压与执行力，能稳定参与团队协作与迭代交付。`,
    potential: `${t}：需体现持续学习与技术/业务创新能力，能适应工具链与需求变化并保持成长。`,
  }
}

/**
 * @param {Record<string, string>} merged
 * @param {Record<string, string>} fallback
 */
export function withFallbackRequirementTexts(merged, fallback) {
  const out = {}
  for (const k of FOUR_KEYS) {
    out[k] = (merged[k] && merged[k].trim()) ? merged[k].trim() : (fallback[k] || '')
  }
  return out
}

/**
 * @param {Record<string, string>} textsByKey
 * @param {Record<string, string|number>} studentByKey
 */
export function buildCompareDimensionRows(textsByKey, studentByKey) {
  return FOUR_KEYS.map((key, i) => ({
    name: FOUR_NAMES[i],
    student: studentByKey[key],
    requirementText: textsByKey[key] || '',
  }))
}

/**
 * 合并匹配详情、岗位画像接口、报告 module_1 中的要求说明（依次补全空缺维度）
 * @param {object} [detail] postMatchDetail 原始响应
 * @param {string} jobId
 * @param {string} [jobTitle]
 * @param {object} [module1TargetJob] career_report.module_1.target_job
 */
export async function resolveMatchDimensionRequirementTexts(
  detail,
  jobId,
  jobTitle,
  module1TargetJob
) {
  let jobDetailData = null
  if (jobId != null && String(jobId).trim()) {
    try {
      const raw = await getJobDetail(String(jobId).trim())
      const data = raw?.data ?? raw
      jobDetailData = data && typeof data === 'object' ? data : null
    } catch {
      jobDetailData = null
    }
  }

  const merged = mergeDimensionRequirementTexts([
    dimensionRequirementsFromMatchDetail(detail),
    buildFourDimensionRequirementsFromJobDetailApiData(jobDetailData),
    module1TargetJob ? buildFourDimensionRequirementsFromModule1TargetJob(module1TargetJob) : null,
  ])
  const withFb = withFallbackRequirementTexts(merged, fallbackRequirementTexts(jobTitle))
  const out = {}
  for (const k of FOUR_KEYS) {
    out[k] = dedupeRequirementText(withFb[k] || '')
  }
  return out
}
