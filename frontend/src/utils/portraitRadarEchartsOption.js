/**
 * ECharts 雷达图布局与岗位详情页（JobDetailView）「岗位核心胜任力分析」一致：
 * legend 位置、半径/中心、splitNumber、网格与坐标样式（含暗色主题）。
 * 数据系列的颜色、线型由调用方在 series.data 中自行指定。
 *
 * @param {object} opts
 * @param {boolean} opts.isDark
 * @param {Array<{ name: string, max?: number }>} opts.indicator
 * @param {string[]} opts.legendData
 * @param {object[]} opts.seriesData radar series 的 data 数组（与 ECharts radar.data 一致）
 * @param {'portrait'|'abilitiesFlat'} [opts.variant='portrait'] — abilitiesFlat：学生能力页「扁平 + 微渐变 + 圆形网格」
 */
export function buildPortraitStyleRadarOption({
  isDark,
  indicator,
  legendData,
  seriesData,
  variant = 'portrait',
}) {
  const legendText = isDark ? 'rgba(238, 238, 238, 0.9)' : 'rgba(51, 50, 46, 0.88)'
  const isAbilitiesFlat = variant === 'abilitiesFlat'

  const gridLine = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
  const axisLine = isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.1)'

  const radarBase = {
    indicator,
    radius: isAbilitiesFlat ? '70%' : '72%',
    center: ['50%', isAbilitiesFlat ? '48%' : '46%'],
    splitNumber: 4,
    shape: isAbilitiesFlat ? 'circle' : 'polygon',
    axisName: isAbilitiesFlat
      ? {
          color: isDark ? 'rgba(238, 238, 238, 0.94)' : '#33322E',
          fontSize: 13,
          fontWeight: 600,
          lineHeight: 18,
        }
      : {
          color: isDark ? 'rgba(238, 238, 238, 0.92)' : 'rgba(51, 50, 46, 0.88)',
          fontSize: 12,
        },
    splitLine: {
      lineStyle: {
        color: isAbilitiesFlat ? gridLine : isDark ? 'rgba(99, 191, 183, 0.28)' : 'rgba(51, 50, 46, 0.12)',
        width: 1,
      },
    },
    splitArea: isAbilitiesFlat
      ? { show: false }
      : {
          show: true,
          areaStyle: {
            color: isDark
              ? ['rgba(99, 191, 183, 0.14)', 'rgba(99, 191, 183, 0.05)']
              : ['rgba(99, 191, 183, 0.09)', 'rgba(99, 191, 183, 0.03)'],
          },
        },
    axisLine: {
      lineStyle: {
        color: isAbilitiesFlat ? axisLine : isDark ? 'rgba(99, 191, 183, 0.4)' : 'rgba(51, 50, 46, 0.14)',
      },
    },
  }

  if (isAbilitiesFlat) {
    radarBase.nameGap = 20
  }

  const animationBlock = isAbilitiesFlat
    ? {
        animation: true,
        animationDuration: 1100,
        animationEasing: 'cubicOut',
        animationDelay: 0,
        animationDurationUpdate: 800,
        animationEasingUpdate: 'cubicOut',
      }
    : {}

  const seriesPayload = isAbilitiesFlat
    ? seriesData.map((item, idx) => ({
        ...item,
        animationDelay: idx * 120,
        animationDuration: 1000,
        animationEasing: 'cubicOut',
      }))
    : seriesData

  return {
    backgroundColor: 'transparent',
    ...animationBlock,
    legend: {
      data: legendData,
      bottom: 4,
      itemGap: 18,
      icon: 'roundRect',
      textStyle: {
        color: legendText,
        fontSize: 11,
      },
    },
    radar: radarBase,
    series: [
      {
        type: 'radar',
        emphasis: isAbilitiesFlat
          ? {
              lineStyle: { width: 2.5 },
              areaStyle: { opacity: 0.45 },
            }
          : {
              lineStyle: { width: 3 },
            },
        data: seriesPayload,
      },
    ],
  }
}

/** 主色 #8cd4cb 微渐变填充（约 0.3 视觉透明度区间） */
export function abilitiesPrimaryAreaGradient() {
  return {
    type: 'linear',
    x: 0,
    y: 0,
    x2: 0,
    y2: 1,
    colorStops: [
      { offset: 0, color: 'rgba(140, 212, 203, 0.36)' },
      { offset: 0.55, color: 'rgba(140, 212, 203, 0.22)' },
      { offset: 1, color: 'rgba(140, 212, 203, 0.08)' },
    ],
  }
}

/** 岗位要求对比色（暖粉）微渐变，与主色区分 */
export function abilitiesJobAreaGradient() {
  return {
    type: 'linear',
    x: 0,
    y: 0,
    x2: 0,
    y2: 1,
    colorStops: [
      { offset: 0, color: 'rgba(232, 160, 175, 0.34)' },
      { offset: 0.55, color: 'rgba(255, 214, 233, 0.22)' },
      { offset: 1, color: 'rgba(255, 214, 233, 0.08)' },
    ],
  }
}
