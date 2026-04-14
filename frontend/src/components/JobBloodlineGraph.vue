<template>
  <div ref="rootRef" class="job-bloodline-graph">
    <svg
      class="graph-svg"
      :viewBox="`0 0 ${graphSize.width} ${graphSize.height}`"
      role="img"
      aria-label="岗位血缘横向图谱"
      preserveAspectRatio="none"
    >
      <defs>
        <filter id="hard-shadow" x="-20%" y="-20%" width="160%" height="180%">
          <feDropShadow dx="4" dy="4" stdDeviation="0" flood-color="#33322e" flood-opacity="1" />
        </filter>
      </defs>

      <rect x="0" y="0" :width="graphSize.width" :height="graphSize.height" class="graph-bg" />

      <g class="links-layer">
        <path
          v-for="link in links"
          :key="`line-${link.id}`"
          :d="link.path"
          class="graph-link"
          :class="{ 'graph-link--active': activeNodeId === link.toId }"
          :style="{ '--dash-speed': `${link.dashSpeed}s` }"
          :stroke-width="link.strokeWidth"
        />

        <path
          v-for="link in links"
          :id="`pulse-${link.id}`"
          :key="`pulse-path-${link.id}`"
          :d="link.path"
          class="pulse-path"
        />

        <g
          v-for="link in links"
          :key="`gap-${link.id}`"
          class="link-gap-tag"
          :transform="`translate(${link.midX}, ${link.midY})`"
        >
          <rect
            x="-72"
            y="-12"
            width="144"
            height="24"
            rx="12"
            ry="12"
            class="gap-tag-bg"
            filter="url(#hard-shadow)"
          />
          <text class="gap-tag-text" text-anchor="middle" dominant-baseline="middle">
            缺口：{{ link.gapSkill }}
          </text>
        </g>

        <g v-for="link in links" :key="`dot-${link.id}`">
          <circle r="6.4" class="flow-dot flow-dot--trail">
            <animateMotion repeatCount="indefinite" :dur="`${link.dotDuration}s`" rotate="auto">
              <mpath :href="`#pulse-${link.id}`" />
            </animateMotion>
          </circle>
          <circle r="3.4" class="flow-dot flow-dot--core">
            <animateMotion repeatCount="indefinite" :dur="`${link.dotDuration}s`" rotate="auto">
              <mpath :href="`#pulse-${link.id}`" />
            </animateMotion>
          </circle>
        </g>
      </g>

      <g class="nodes-layer">
        <g
          v-for="node in placedNodes"
          :key="`node-${node.id}`"
          class="graph-node"
          :class="{ 'graph-node--center': node.center, 'graph-node--active': activeNodeId === node.id }"
          @mouseenter="onNodeHover(node)"
          @mouseleave="onNodeLeave"
          @click.stop="onNodeClick(node)"
        >
          <rect
            :x="node.x - node.width / 2"
            :y="node.y - node.height / 2"
            :width="node.width"
            :height="node.height"
            :rx="node.rx"
            :ry="node.rx"
            class="node-card"
            filter="url(#hard-shadow)"
          />
          <text :x="node.x" :y="node.y - 6" text-anchor="middle" dominant-baseline="middle" class="node-title">
            {{ node.label }}
          </text>
          <text :x="node.x" :y="node.y + 12" text-anchor="middle" dominant-baseline="middle" class="node-sub">
            匹配度: {{ node.matchScore }}%
          </text>
        </g>
      </g>
    </svg>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  nodes: { type: Array, default: () => [] },
  pathPreviewOrder: { type: Array, default: () => [] }
})

const emit = defineEmits(['node-click', 'node-hover'])

const rootRef = ref(null)
const graphSize = ref({ width: 1200, height: 240 })
const placedNodes = ref([])
let resizeObserver = null

const activeNodeId = ref('')

const centerNode = computed(() => placedNodes.value.find((n) => n.center) || placedNodes.value[0] || null)

const links = computed(() => {
  const center = centerNode.value
  if (!center) return []
  return placedNodes.value
    .filter((n) => !n.center)
    .map((node, idx) => {
      const difficulty = Math.max(0, Math.min(100, Number(node.transitionDifficulty ?? 50)))
      const strokeWidth = 0.9 + ((100 - difficulty) / 100) * 2.2
      const dotDuration = 1.2 + (difficulty / 100) * 2.8
      const dashSpeed = 1.8 + (difficulty / 100) * 2.6
      const cx = center.x + (node.x - center.x) * 0.52
      const cy = center.y + (node.y - center.y) * 0.5 + (idx % 2 === 0 ? -18 : 18)
      const path = `M ${center.x} ${center.y} C ${center.x + 160} ${center.y}, ${cx} ${cy}, ${node.x} ${node.y}`
      const t = 0.55
      const midX =
        Math.pow(1 - t, 3) * center.x +
        3 * Math.pow(1 - t, 2) * t * (center.x + 160) +
        3 * (1 - t) * Math.pow(t, 2) * cx +
        Math.pow(t, 3) * node.x
      const midY =
        Math.pow(1 - t, 3) * center.y +
        3 * Math.pow(1 - t, 2) * t * center.y +
        3 * (1 - t) * Math.pow(t, 2) * cy +
        Math.pow(t, 3) * node.y
      return {
        id: `${center.id}-${node.id}`,
        toId: node.id,
        path,
        strokeWidth,
        dotDuration,
        dashSpeed,
        midX,
        midY,
        gapSkill: node.gapSkill || '核心技能补齐'
      }
    })
})

function estimateWidth(text, isCenter) {
  const chars = Math.max(String(text || '').length, 4)
  const base = (isCenter ? 18 : 14) * chars + (isCenter ? 72 : 56)
  return Math.min(Math.max(base, isCenter ? 240 : 180), isCenter ? 360 : 280)
}

function placeNodes() {
  const source = Array.isArray(props.nodes) ? props.nodes.slice(0, 9) : []
  if (!source.length) {
    placedNodes.value = []
    return
  }
  const width = graphSize.value.width
  const height = graphSize.value.height

  const centerRaw = source.find((n) => n?.center) || source[0]
  const targets = source.filter((n) => n && n.id !== centerRaw.id)
  const leftX = Math.max(140, width * 0.16)
  const rightX = Math.min(width - 170, width * 0.84)
  const centerY = height / 2
  const minGapY = 72
  const totalH = (targets.length - 1) * minGapY
  const startY = centerY - totalH / 2

  const arranged = []
  arranged.push({
    id: centerRaw.id || 'center',
    label: centerRaw.label || '当前岗位',
    center: true,
    x: leftX,
    y: centerY,
    width: estimateWidth(centerRaw.label, true),
    height: 70,
    rx: 34,
    matchScore: Math.round(Number(centerRaw.matchScore ?? 100)),
    transitionDifficulty: 0,
    gapSkill: ''
  })

  targets.forEach((raw, index) => {
    const gapList = Array.isArray(raw.gapSkills) ? raw.gapSkills.filter(Boolean) : []
    arranged.push({
      id: raw.id || `node-${index}`,
      label: raw.label || `关联岗位${index + 1}`,
      center: false,
      x: rightX,
      y: startY + index * minGapY,
      width: estimateWidth(raw.label, false),
      height: 62,
      rx: 30,
      matchScore: Math.round(Number(raw.matchScore ?? 75)),
      transitionDifficulty: Math.round(Number(raw.transitionDifficulty ?? 50)),
      gapSkill: gapList.length ? gapList[0] : raw.gapSkill || '技能迁移',
      gapSkills: gapList.length ? [...gapList] : [],
      diffFromCenter: Array.isArray(raw.diffFromCenter) ? raw.diffFromCenter.filter(Boolean) : [],
      reusableSkills: Array.isArray(raw.reusableSkills) ? raw.reusableSkills.filter(Boolean) : [],
      skillOverlap: raw.skillOverlap,
      salaryDeltaPct: raw.salaryDeltaPct
    })
  })

  placedNodes.value = arranged
  if (!placedNodes.value.find((n) => n.id === activeNodeId.value)) {
    activeNodeId.value = ''
  }
}

function onNodeHover(node) {
  if (!node || node.center) return
  activeNodeId.value = node.id
  emit('node-hover', node)
}

function onNodeLeave() {
  activeNodeId.value = ''
  emit('node-hover', null)
}

function onNodeClick(node) {
  if (!node || node.center) return
  activeNodeId.value = node.id
  emit('node-click', { ...node })
}

onMounted(() => {
  if (!rootRef.value) return
  resizeObserver = new ResizeObserver((entries) => {
    const entry = entries[0]
    if (!entry?.contentRect) return
    graphSize.value = {
      width: Math.max(780, entry.contentRect.width),
      height: Math.max(180, entry.contentRect.height)
    }
    placeNodes()
  })
  resizeObserver.observe(rootRef.value)
})

watch(
  () => props.nodes,
  () => placeNodes(),
  { deep: true, immediate: true }
)

onBeforeUnmount(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
})
</script>

<style scoped>
.job-bloodline-graph {
  width: 100%;
  min-height: 180px;
  border-radius: 20px;
  overflow: hidden;
  background: var(--u-bg-normal);
}

.graph-svg {
  width: 100%;
  height: 100%;
  min-height: 180px;
  display: block;
}

.graph-bg {
  fill: var(--u-bg-normal);
}

.graph-link {
  fill: none;
  stroke: rgba(51, 50, 46, 0.16);
  stroke-linecap: round;
  stroke-dasharray: 5 7;
  animation: dashMove var(--dash-speed, 2.8s) linear infinite;
  transition: stroke 0.2s ease, stroke-width 0.2s ease;
}

.graph-link--active {
  stroke: rgba(99, 191, 183, 0.94);
}

.pulse-path {
  fill: none;
  stroke: transparent;
}

.flow-dot--trail {
  fill: rgba(99, 191, 183, 0.36);
  filter: blur(1px);
}

.flow-dot--core {
  fill: #63bfb7;
  filter: drop-shadow(0 0 5px #63bfb7);
}

.link-gap-tag {
  pointer-events: none;
}

.gap-tag-bg {
  fill: rgba(255, 255, 255, 0.78);
  stroke: rgba(51, 50, 46, 0.34);
  stroke-width: 1.2;
}

.gap-tag-text {
  font-size: 11px;
  font-weight: 700;
  fill: rgba(51, 50, 46, 0.78);
}

.graph-node {
  cursor: pointer;
}

.graph-node--center {
  cursor: default;
}

.node-card {
  fill: var(--u-bg-submit);
  stroke: var(--u-black);
  stroke-width: 2;
}

.graph-node--active .node-card {
  fill: color-mix(in srgb, var(--u-bg-submit) 78%, #ffffff);
}

.node-title {
  font-size: 14px;
  font-weight: 800;
  fill: var(--u-black);
  user-select: none;
  pointer-events: none;
}

.node-sub {
  font-size: 11px;
  font-weight: 600;
  fill: rgba(51, 50, 46, 0.72);
  user-select: none;
  pointer-events: none;
}

@keyframes dashMove {
  to {
    stroke-dashoffset: -30;
  }
}

:deep(.job-detail-view.dark) .job-bloodline-graph {
  background: var(--dm-surface-card);
  border: 2px solid var(--dm-border);
}

:deep(.job-detail-view.dark) .graph-bg {
  fill: var(--dm-surface-card);
}

:deep(.job-detail-view.dark) .graph-link {
  stroke: rgba(255, 255, 255, 0.18);
}

:deep(.job-detail-view.dark) .graph-link--active {
  stroke: color-mix(in srgb, var(--u-bg-submit) 78%, #d8fff9);
}

:deep(.job-detail-view.dark) .node-card {
  fill: color-mix(in srgb, var(--dm-surface-elevated) 82%, var(--u-bg-submit));
  stroke: var(--dm-text);
}

:deep(.job-detail-view.dark) .graph-node--active .node-card {
  fill: color-mix(in srgb, var(--dm-surface-elevated) 68%, #cffff6);
}

:deep(.job-detail-view.dark) .node-title {
  fill: var(--dm-text);
}

:deep(.job-detail-view.dark) .node-sub {
  fill: var(--dm-text-secondary);
}

:deep(.job-detail-view.dark) .gap-tag-bg {
  fill: rgba(28, 31, 38, 0.92);
  stroke: var(--dm-border);
}

:deep(.job-detail-view.dark) .gap-tag-text {
  fill: var(--dm-text-secondary);
}
</style>
