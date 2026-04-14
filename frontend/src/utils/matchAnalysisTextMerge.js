/**
 * 岗位匹配「详细差距 / 提升建议」：统一数据来源与 Markdown 清洗，供 StudentAbilitiesView、CareerReportView 共用。
 */

function flattenAnalysisInput(value) {
  if (value == null) return []
  if (typeof value === 'string') {
    const t = value.trim()
    return t ? [t] : []
  }
  if (Array.isArray(value)) {
    return value.flatMap((x) => flattenAnalysisInput(x))
  }
  return []
}

export function stripMarkdownNoiseChars(s) {
  let t = String(s ?? '')
    .replace(/\*/g, '')
    .replace(/#/g, '')
  t = t.replace(/\r\n/g, '\n')
  t = t
    .split('\n')
    .map((line) => {
      const trimmed = line.trim()
      if (/^-{3,}$/.test(trimmed)) return ''
      return line
        .replace(/^#{1,6}\s+/g, '')
        .replace(/^\s*[-*+]\s+/g, '')
        .replace(/`+/g, '')
        .trim()
    })
    .filter(Boolean)
    .join('\n')
  return t.trim()
}

function collapseInnerWhitespace(s) {
  return String(s).replace(/\s+/g, ' ').trim()
}

/**
 * 按序号切分：支持「换行 + 1.」与同一行内的「1. xxx 2. yyy」
 */
function splitNumberedSegments(text) {
  const t = String(text).trim()
  if (!t) return []

  const stripLeadNum = (s) =>
    String(s)
      .replace(/^\d+(?:[\.\、．)]|）)\s*/, '')
      .trim()

  const inlinePieces = t
    .split(/\s+(?=\d+(?:[\.\、．)]|）)\s+)/)
    .map(stripLeadNum)
    .filter(Boolean)
  if (inlinePieces.length > 1) return inlinePieces

  const re = /(?:^|\n)\s*(\d+)[\.\、．)]\s*/g
  const hits = []
  let m
  while ((m = re.exec(t)) !== null) {
    hits.push({ index: m.index, len: m[0].length })
  }
  if (!hits.length) return [t]
  const out = []
  if (hits[0].index > 0) {
    const head = collapseInnerWhitespace(t.slice(0, hits[0].index))
    if (head) out.push(head)
  }
  for (let i = 0; i < hits.length; i++) {
    const from = hits[i].index + hits[i].len
    const to = i + 1 < hits.length ? hits[i + 1].index : t.length
    const seg = collapseInnerWhitespace(t.slice(from, to))
    if (seg) out.push(seg)
  }
  return out.length ? out : [t]
}

/**
 * 将 Markdown 长文按「编号块」切成多条（每块内多行、多句保留在同一条，不逐行拆卡片）。
 * 无显式编号时整段为一条。
 */
function rawListFromNumberedMarkdown(mdText) {
  if (mdText == null || mdText === '') return []
  const text = typeof mdText === 'string' ? mdText : String(mdText)
  const t = stripMarkdownNoiseChars(text)
  if (!t.trim()) return []
  return splitNumberedSegments(t)
    .map((p) => collapseInnerWhitespace(p))
    .filter(Boolean)
}

/**
 * 单条字符串内若出现 2 个及以上四维起点，则拆成多条卡片；前置总述（如「详细差距分析：」）单独成条。
 * 匹配：「维度：」或「维度得分…」「维度为…」（避免无冒号粘连在一坨无法拆）
 */
function splitGapMergedBlobToCards(s) {
  const t = String(s).trim()
  if (!t) return []
  const re =
    /(?:基础要求|职业技能|职业素养|发展潜力)(?:[：:]\s*|(?=得分)|(?=为))/g
  const matches = [...t.matchAll(re)]
  if (matches.length <= 1) return [t]
  const parts = []
  for (let i = 0; i < matches.length; i++) {
    const start = matches[i].index
    const end = i + 1 < matches.length ? matches[i + 1].index : t.length
    parts.push(t.slice(start, end).trim())
  }
  if (matches[0].index > 0) {
    const pre = t.slice(0, matches[0].index).trim()
    if (pre) parts.unshift(pre)
  }
  return parts.filter(Boolean)
}

const GAP_DIMENSION_NAMES = ['基础要求', '职业技能', '职业素养', '发展潜力']

function stripLeadingOrderMark(s) {
  return String(s ?? '')
    .trim()
    .replace(/^\d+(?:[\.\、．)]|）)\s*/, '')
    .trim()
}

function extractLeadingGapDimension(text) {
  const t = stripLeadingOrderMark(text)
  for (const name of GAP_DIMENSION_NAMES) {
    if (t.startsWith(name)) return name
  }
  return null
}

/** 下一段是否为「同维度的得分/量化摘要」行（常与上一段长叙述拆成两条） */
function isGapScoreSummarySegment(dim, strippedNext) {
  const n = String(strippedNext || '').trim()
  if (!dim || !n.startsWith(dim)) return false
  if (n.startsWith(dim + '得分')) return true
  if (n.startsWith(dim + '为')) return /\d/.test(n.slice((dim + '为').length))
  const rest = n.slice(dim.length).trim().replace(/^[：:]+/u, '').trim()
  return rest.startsWith('得分') || rest.startsWith('为')
}

/**
 * 叙述段以「，」收束、下接「维度得分…」时，合并后把句末逗号收成句号，避免「悬逗号」观感。
 */
function joinMergedGapPair(first, second) {
  let a = String(first).trimEnd()
  const b = String(second).trim()
  const dim = extractLeadingGapDimension(stripLeadingOrderMark(b))
  if (dim && /[，,]\s*$/u.test(a) && isGapScoreSummarySegment(dim, stripLeadingOrderMark(b))) {
    a = a.replace(/[，,]\s*$/u, '。')
  }
  return `${a}\n${b}`
}

/**
 * 模型/接口常把「维度：」与「维度得分…」拆成相邻两条（或编号列表相邻两项），
 * 展示层应合并为一条卡片，避免标题与正文各占一个序号。
 * 亦合并「同维度长叙述（常以逗号结尾）」+「维度得分…」拆行。
 */
function shouldMergeGapHeaderWithNext(prev, next) {
  if (next == null) return false
  const p = stripLeadingOrderMark(prev)
  const n = stripLeadingOrderMark(next)
  if (!p || !n) return false
  const dim = extractLeadingGapDimension(p)
  if (!dim) return false
  const afterDim = p.slice(dim.length).trim().replace(/^[：:]+/u, '').trim()
  if (!afterDim) return true
  if (/^[，,。.…、；;：:\s]+$/u.test(afterDim)) return true
  if (afterDim.length <= 8) {
    if (n.startsWith(dim)) return true
    return extractLeadingGapDimension(n) === dim
  }
  if (isGapScoreSummarySegment(dim, n)) return true
  return false
}

function coalesceGapSegmentCards(parts) {
  const list = Array.isArray(parts) ? parts.map((x) => String(x ?? '').trim()).filter(Boolean) : []
  const out = []
  for (let i = 0; i < list.length; ) {
    const cur = list[i]
    const nxt = list[i + 1]
    if (nxt !== undefined && shouldMergeGapHeaderWithNext(cur, nxt)) {
      out.push(joinMergedGapPair(cur, nxt))
      i += 2
    } else {
      out.push(cur)
      i += 1
    }
  }
  return out
}

/** 提升建议：优先保留编号切分；否则按分号拆成多条（避免整段一坨） */
function splitSuggestMergedBlob(s) {
  const t = String(s).trim()
  if (!t) return []
  const numbered = splitNumberedSegments(t)
  if (numbered.length > 1) {
    return numbered.map((p) => collapseInnerWhitespace(p)).filter(Boolean)
  }
  const semi = t
    .split(/[；;]+/)
    .map((p) => collapseInnerWhitespace(p))
    .filter(Boolean)
  if (semi.length > 1) return semi
  return [collapseInnerWhitespace(t)]
}

/**
 * @param {string|string[]|null|undefined} raw
 * @param {{ splitNumbered?: boolean }} [options] splitNumbered 为 false 时，数组中每一项仅输出一张卡片（不拆项内编号/子句）
 * @returns {{ order: number, text: string }[]}
 */
export function cleanAndFormatText(raw, options = {}) {
  const splitNumbered = options.splitNumbered !== false
  const chunks = flattenAnalysisInput(raw)
  const segments = []
  for (const chunk of chunks) {
    const tidied = stripMarkdownNoiseChars(chunk)
    if (!tidied) continue
    if (splitNumbered) {
      for (const part of splitNumberedSegments(tidied)) {
        const text = collapseInnerWhitespace(part)
        if (text) segments.push(text)
      }
    } else {
      const text = collapseInnerWhitespace(tidied)
      if (text) segments.push(text)
    }
  }
  return segments.map((text, i) => ({ order: i + 1, text }))
}

const safeArr = (value) => (Array.isArray(value) ? value : [])

function toTextList(value, fallback = []) {
  const list = safeArr(value)
    .map((x) => String(x || '').trim())
    .filter(Boolean)
  return list.length ? list : fallback
}

function pickSectionList(text, sectionTitle) {
  const src = String(text || '')
  if (!src.trim()) return []
  const escaped = sectionTitle.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const reg = new RegExp(`(?:^|\\n)#{0,6}\\s*${escaped}[：:\\s]*\\n([\\s\\S]*?)(?=\\n#{1,6}\\s*|$)`, 'i')
  const match = src.match(reg)
  if (!match) return []
  return rawListFromNumberedMarkdown(match[1])
}

function pickFirstSectionList(text, titles) {
  const narr = String(text || '')
  if (!narr.trim()) return []
  for (const t of titles) {
    const list = pickSectionList(narr, t)
    if (list.length) return list
  }
  return []
}

const GAP_SECTION_TITLES = ['详细差距分析', '差距分析', '人岗差距', '匹配差距分析']
const SUGGEST_SECTION_TITLES = ['提升建议', '改进建议', '行动建议', '优化建议', '学习与发展建议', '发展建议']

function buildFallbackAnalysis(dims) {
  const num = (v) => (Number.isFinite(Number(v)) ? Number(v) : 0)
  const rows = [
    { key: '基础要求', score: num(dims?.base) },
    { key: '职业技能', score: num(dims?.skill) },
    { key: '职业素养', score: num(dims?.soft) },
    { key: '发展潜力', score: num(dims?.potential) },
  ]
  const sorted = [...rows].sort((a, b) => a.score - b.score)
  const weak = sorted.slice(0, 2)
  const strong = sorted.slice(2).sort((a, b) => b.score - a.score)
  const gap = [
    `${weak[0]?.key || '关键维度'}相对薄弱，当前得分 ${weak[0]?.score ?? 0}，建议优先补齐。`,
    `${weak[1]?.key || '次要维度'}仍有提升空间，建议通过项目实践和复盘提升稳定性。`,
    `${strong[0]?.key || '优势维度'}是当前优势项，可作为岗位竞争力展示重点。`,
  ]
  const suggest = [
    `优先提升 ${weak[0]?.key || '薄弱维度'}：制定 2-4 周专项训练任务并量化验收指标。`,
    `围绕目标岗位补齐 ${weak[1]?.key || '能力短板'}：每周至少完成 1 次实战任务 + 1 次复盘。`,
    `保持 ${strong[0]?.key || '优势维度'}优势：沉淀可展示成果（项目、文档、指标）用于面试表达。`,
  ]
  return { gap, suggest }
}

/** 兼容：match_analysis.details（mock）与顶层 details（当前 Python match/detail 响应） */
function detailBuckets(d) {
  if (!d || typeof d !== 'object') return []
  const nested = d.match_analysis?.details ?? d.matchAnalysis?.details
  const root = d.details && typeof d.details === 'object' && !Array.isArray(d.details) ? d.details : null
  const out = []
  if (nested && typeof nested === 'object') out.push(nested)
  if (root && root !== nested) out.push(root)
  return out
}

function firstNonEmptyReasonsList(buckets) {
  for (const b of buckets) {
    const arr = b.reasons
    if (Array.isArray(arr) && arr.some((x) => String(x || '').trim())) {
      return arr.map((x) => String(x ?? '').trim()).filter(Boolean)
    }
  }
  return null
}

const SUGGEST_ARRAY_KEYS = [
  'warnings',
  'gaps',
  'suggestions',
  'improvement_items',
  'improvement_list',
  'recommendations',
]

function firstNonEmptySuggestList(buckets) {
  for (const b of buckets) {
    for (const k of SUGGEST_ARRAY_KEYS) {
      const arr = b[k]
      if (Array.isArray(arr) && arr.some((x) => String(x || '').trim())) {
        return arr.map((x) => String(x ?? '').trim()).filter(Boolean)
      }
    }
  }
  return null
}

/**
 * 详细差距：details.reasons[]（多路径）→ gap_analysis → narrative 章节 → fallback
 */
export function mergeGapDetailStrings(detail, narrative, dimScores) {
  const d = detail && typeof detail === 'object' ? detail : {}
  const buckets = detailBuckets(d)
  let rawList = firstNonEmptyReasonsList(buckets) || []
  const gapStr = d.gap_analysis ?? d.gapAnalysis ?? ''
  if (!rawList.length && gapStr) {
    rawList = rawListFromNumberedMarkdown(gapStr)
  }
  const narr = String(narrative ?? '')
  if (!rawList.length && narr) {
    rawList = pickFirstSectionList(narr, GAP_SECTION_TITLES)
  }
  const fallback = buildFallbackAnalysis(dimScores).gap
  rawList = toTextList(rawList, fallback)
  rawList = rawList.flatMap((item) => splitGapMergedBlobToCards(item))
  rawList = coalesceGapSegmentCards(rawList)
  return rawList.map((s) => stripMarkdownNoiseChars(s)).filter(Boolean)
}

/**
 * 提升建议：warnings / 别名字段[] → improvement_suggestions → narrative → fallback
 */
export function mergeSuggestDetailStrings(detail, narrative, dimScores) {
  const d = detail && typeof detail === 'object' ? detail : {}
  const buckets = detailBuckets(d)
  let rawList = firstNonEmptySuggestList(buckets) || []
  const sStr = d.improvement_suggestions ?? d.improvementSuggestions ?? ''
  if (!rawList.length && sStr) {
    rawList = rawListFromNumberedMarkdown(sStr)
  }
  const narr = String(narrative ?? '')
  if (!rawList.length && narr) {
    rawList = pickFirstSectionList(narr, SUGGEST_SECTION_TITLES)
  }
  const fallback = buildFallbackAnalysis(dimScores).suggest
  rawList = toTextList(rawList, fallback)
  rawList = rawList.flatMap((item) => splitSuggestMergedBlob(item))
  return rawList.map((s) => stripMarkdownNoiseChars(s)).filter(Boolean)
}
