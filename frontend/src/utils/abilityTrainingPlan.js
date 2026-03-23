function pickFirstMatching(text, patterns) {
  for (const p of patterns) {
    if (p.test(text)) return true
  }
  return false
}

function normalizeInputText(inputText) {
  return String(inputText || '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 8000)
}

function detectGaps(text) {
  const t = text.toLowerCase()

  const hasProject = pickFirstMatching(t, [
    /project/,
    /项目/,
    /实战/,
    /实习/,
    /intern/,
    /github/,
    /gitlab/,
    /作品集/,
  ])

  const hasQuant = pickFirstMatching(t, [
    /\d+%/,
    /\d+\s*(k|w|万|千)/,
    /提升/,
    /降低/,
    /优化/,
    /指标/,
    /结果/,
    /impact/,
  ])

  const hasBasics = pickFirstMatching(t, [
    /数据结构/,
    /算法/,
    /操作系统/,
    /计算机网络/,
    /数据库/,
    /os\b/,
    /\bnetwork/,
    /\bdb/,
  ])

  const hasInterview = pickFirstMatching(t, [
    /面试/,
    /笔试/,
    /简历投递/,
    /项目讲解/,
    /mock/,
    /behavior/,
    /star/,
  ])

  const hasCommunication = pickFirstMatching(t, [
    /沟通/,
    /协作/,
    /跨部门/,
    /复盘/,
    /总结/,
    /汇报/,
    /沟通能力/,
  ])

  return {
    needProjectDepth: !hasProject,
    needQuantification: !hasQuant,
    needBasicsSystem: !hasBasics,
    needInterviewReadiness: !hasInterview,
    needCommunication: !hasCommunication,
  }
}

function buildRoadmap(gaps) {
  const rows = []

  rows.push({
    label: '基础能力补齐',
    items: [
      {
        title: gaps.needBasicsSystem ? '核心基础系统化补齐' : '核心基础巩固与查漏补缺',
        start: 1,
        end: 2,
        tone: 'blue',
      },
      {
        title: '面向岗位的专题串讲与总结',
        start: 2,
        end: 3,
        tone: 'blueDeep',
      },
    ],
  })

  rows.push({
    label: '项目与作品集',
    items: [
      {
        title: gaps.needProjectDepth ? '完成 1 个可展示项目（含部署/文档）' : '打磨现有项目到可面试叙述',
        start: 1,
        end: 2,
        tone: 'indigo',
      },
      {
        title: gaps.needQuantification ? '补齐量化成果与对比数据' : '补强技术亮点与可解释指标',
        start: 2,
        end: 3,
        tone: 'indigoDeep',
      },
    ],
  })

  rows.push({
    label: '求职与表达',
    items: [
      {
        title: gaps.needCommunication ? '输出可复用的项目讲解脚本（STAR/拆解）' : '形成稳定的项目表达与复盘机制',
        start: 1,
        end: 2,
        tone: 'teal',
      },
      {
        title: gaps.needInterviewReadiness ? '完成多轮模拟面试并迭代简历' : '建立投递-复盘-迭代闭环',
        start: 2,
        end: 3,
        tone: 'tealDeep',
      },
    ],
  })

  const months = [
    { key: 1, label: 'Month 1' },
    { key: 2, label: 'Month 2' },
    { key: 3, label: 'Month 3' },
  ]

  return { months, rows }
}

function buildTodoText(gaps) {
  const weekGoal =
    (gaps.needProjectDepth ? '补齐项目闭环与可展示成果' : '将现有经历转化为可面试叙述') +
    '，并形成一版可投递的简历/发展报告摘要'

  const weekTasks = []

  weekTasks.push(
    gaps.needProjectDepth
      ? '产出 1 份「项目选型 + 需求范围 + 里程碑」方案，并确定可在 2 周内交付的 MVP'
      : '完成 1 版「项目故事线」梳理（背景-目标-方案-结果-反思）并可在 3 分钟内讲清'
  )

  weekTasks.push(
    gaps.needBasicsSystem
      ? '完成 1 轮「基础四件套」系统复盘（数据结构/算法、计网、操作系统、数据库），输出一份可复习的知识图谱'
      : '完成 1 轮「高频薄弱点」查漏补缺，输出错题/薄弱点清单并闭环修复'
  )

  weekTasks.push(
    gaps.needQuantification
      ? '为简历/报告补齐不少于 6 条量化成果（前后对比、指标、规模、约束），并在文档中可被直接引用'
      : '为核心经历补强技术亮点不少于 4 条（难点、权衡、取舍、验证方式），形成可追问的证据链'
  )

  weekTasks.push(
    gaps.needInterviewReadiness
      ? '完成 2 次模拟面试（技术面 + 项目面），并形成可复用的复盘模板与改进清单'
      : '建立 1 套投递与复盘看板（投递-反馈-原因-改进），并完成首轮投递与复盘闭环'
  )

  if (gaps.needCommunication) {
    weekTasks.push('完成 1 版「自我介绍 + 项目介绍 + 亮点总结」脚本，并录制 1 次自测音频用于迭代')
  }

  const month1Achievement = gaps.needProjectDepth
    ? '交付 1 个可线上访问/可演示的 MVP 项目，并在简历中可完整呈现'
    : '将 1-2 段核心经历打磨为可面试追问的项目叙述，并形成稳定表达'
  const month1Logic = '先建立“可展示成果”，再把学习内容绑定到成果的交付与复盘中'

  const month2Achievement = gaps.needQuantification
    ? '简历/报告中每段核心经历都具备可解释的量化成果与验证方式'
    : '形成可追问的技术证据链（难点-方案-权衡-验证），面试表达更有说服力'
  const month2Logic = '用数据与证据把能力“坐实”，让面试官能够快速判断你解决问题的深度'

  const month3Achievement = gaps.needInterviewReadiness
    ? '完成多轮模拟面试与真实投递迭代，面试表现与反馈明显提升'
    : '形成投递-复盘-迭代闭环，稳定获得面试机会并提升通过率'
  const month3Logic = '把“准备”变成“迭代系统”，用反馈驱动持续优化而不是一次性冲刺'

  const lines = []
  lines.push('短期计划（本周）：')
  lines.push(`本周核心目标：${weekGoal}`)
  lines.push('本周总任务：')
  for (const task of weekTasks.slice(0, 5)) {
    lines.push(`- ${task}`)
  }
  lines.push('')
  lines.push('长期计划（三个月）：')
  lines.push('Month 1：')
  lines.push(`阶段性成就：${month1Achievement}`)
  lines.push(`核心成长逻辑：${month1Logic}`)
  lines.push('Month 2：')
  lines.push(`阶段性成就：${month2Achievement}`)
  lines.push(`核心成长逻辑：${month2Logic}`)
  lines.push('Month 3：')
  lines.push(`阶段性成就：${month3Achievement}`)
  lines.push(`核心成长逻辑：${month3Logic}`)

  return lines.join('\n')
}

export function generateAbilityTrainingPlan(input) {
  const sourceText = normalizeInputText(input?.text)
  const gaps = detectGaps(sourceText)
  const roadmap = buildRoadmap(gaps)
  const todoText = buildTodoText(gaps)

  const helpIntro = [
    '本页会基于你的简历缺陷项或职业发展报告内容，自动生成一份由浅入深的能力培养计划：',
    '1）时间轴式的三个月计划表（Month 1-3）',
    '2）严格格式的 To Do List（本周 + 三个月阶段）',
  ]

  return {
    helpIntro,
    gaps,
    roadmap,
    todoText,
  }
}

