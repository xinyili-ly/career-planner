<template>
  <div class="job-path-chart">
    <p class="chart-desc"> draggable · 可放大查看岗位间衔接关系（数据来自 path_graph 或由换岗路径自动生成）。</p>
    <div ref="chartEl" class="chart-el" />
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  pathGraph: { type: Object, default: null },
  transferPaths: { type: Array, default: () => [] },
  theme: { type: String, default: '' },
})

const chartEl = ref(null)
let chart

function normalizeEdgeList(pg) {
  if (!pg || typeof pg !== 'object') return []
  if (Array.isArray(pg.edges)) return pg.edges
  if (Array.isArray(pg.links)) return pg.links
  return []
}

function normalizeNodeList(pg) {
  if (!pg || typeof pg !== 'object') return []
  if (Array.isArray(pg.nodes)) return pg.nodes
  return []
}

function buildFromPathGraph(pg) {
  const rawNodes = normalizeNodeList(pg)
  const rawEdges = normalizeEdgeList(pg)
  if (!rawNodes.length) return null

  const data = rawNodes.map((n, i) => ({
    id: String(n.id ?? n.name ?? n.label ?? `node_${i}`),
    name: String(n.name ?? n.label ?? n.id ?? `节点${i}`),
    symbolSize: typeof n.symbolSize === 'number' ? n.symbolSize : 44,
    category: typeof n.category === 'number' ? n.category : 0,
  }))

  const idSet = new Set(data.map((d) => d.id))
  const links = rawEdges
    .map((e) => ({
      source: String(e.source ?? e.from ?? e.sourceId ?? ''),
      target: String(e.target ?? e.to ?? e.targetId ?? ''),
    }))
    .filter((l) => l.source && l.target && idSet.has(l.source) && idSet.has(l.target))

  return { data, links }
}

function buildFromTransfers(paths) {
  const nameToId = new Map()
  let counter = 0
  function idFor(label) {
    const key = String(label)
    if (!nameToId.has(key)) nameToId.set(key, `n_${counter++}`)
    return nameToId.get(key)
  }

  const links = []
  for (const p of paths || []) {
    const steps = Array.isArray(p?.steps) ? p.steps : []
    for (let i = 0; i < steps.length - 1; i++) {
      const s = String(steps[i])
      const t = String(steps[i + 1])
      links.push({ source: idFor(s), target: idFor(t) })
    }
  }

  const data = [...nameToId.entries()].map(([name, id]) => ({
    id,
    name,
    symbolSize: 42,
    category: 0,
  }))

  if (!data.length) return null
  return { data, links }
}

function buildOption() {
  let pack = buildFromPathGraph(props.pathGraph)
  if (!pack || !pack.data.length) {
    pack = buildFromTransfers(props.transferPaths)
  }
  if (!pack || !pack.data.length) return null

  const lineColor =
    props.theme === 'dark' ? 'rgba(255,255,255,0.45)' : 'rgba(51,50,46,0.55)'

  return {
    tooltip: { trigger: 'item' },
    series: [
      {
        type: 'graph',
        layout: 'force',
        roam: true,
        draggable: true,
        label: {
          show: true,
          position: 'right',
          formatter: '{b}',
          color: props.theme === 'dark' ? '#e5e7eb' : '#33322e',
        },
        lineStyle: { color: lineColor, curveness: 0.12, width: 1.2 },
        emphasis: { focus: 'adjacency', lineStyle: { width: 2 } },
        force: {
          repulsion: 320,
          edgeLength: 88,
          gravity: 0.12,
        },
        data: pack.data,
        links: pack.links,
      },
    ],
  }
}

function render() {
  if (!chartEl.value) return
  const opt = buildOption()
  if (!opt) {
    chart?.clear()
    return
  }
  if (!chart) chart = echarts.init(chartEl.value)
  chart.setOption(opt, true)
}

function onResize() {
  chart?.resize()
}

watch(
  () => [props.pathGraph, props.transferPaths, props.theme],
  () => nextTick(render),
  { deep: true },
)

onMounted(() => {
  nextTick(render)
  window.addEventListener('resize', onResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  chart?.dispose()
  chart = null
})

defineExpose({
  resize() {
    chart?.resize()
  },
})
</script>

<style scoped>
.job-path-chart {
  margin-top: 8px;
}

.chart-desc {
  font-size: clamp(13px, 0.9vw, 15px);
  color: rgba(51, 50, 46, 0.72);
  margin: 0 0 10px;
}

.chart-el {
  width: 100%;
  height: min(420px, 48vh);
  border-radius: 12px;
  border: 2px solid var(--u-black, #33322e);
  background: rgba(255, 255, 255, 0.6);
}

:global(.job-detail-view.dark) .chart-desc {
  color: var(--dm-text-secondary, rgba(255, 255, 255, 0.65));
}

:global(.job-detail-view.dark) .chart-el {
  background: var(--dm-surface-elevated, rgba(28, 33, 40, 0.72));
  border-color: var(--dm-border, #3d4450);
}
</style>
