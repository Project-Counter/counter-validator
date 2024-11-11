<template>
  <svg
    class="pie"
    xmlns="http://www.w3.org/2000/svg"
    :height="size"
    :width="size"
    viewBox="-1 -1 2 2"
  >
    <g transform="rotate(-90)">
      <path
        v-for="(path, index) in paths"
        :key="index"
        :d="`M ${path.startX} ${path.startY} A 1 1 0 ${path.longArc} 1 ${path.endX} ${path.endY} L 0 0`"
        :fill="path.color"
      ></path>
    </g>
  </svg>
</template>

<script setup lang="ts">
type Part = {
  size: number
  color: string
}

let props = withDefaults(
  defineProps<{
    parts: Part[]
    size?: number
  }>(),
  {
    size: 32,
  },
)

// let sizeSum: number = computed(() => props.parts.map((item) => item.size).reduce((x, y) => x + y))

type Chunk = {
  startX: number
  startY: number
  endX: number
  endY: number
  longArc: number
  color: string
}

let paths = computed(() => {
  let out: Chunk[] = []
  if (props.parts.length === 0) {
    return out
  }
  let i = 0
  let startSize = 0
  let sizeSum = props.parts.map((item) => item.size).reduce((x, y) => x + y, 0)
  const sizeToRel = (size: number) => (size / sizeSum) * Math.PI * 2
  for (let item of props.parts) {
    let startX = Math.cos(sizeToRel(startSize))
    let startY = Math.sin(sizeToRel(startSize))
    let x = Math.cos(sizeToRel(startSize + item.size))
    let y = Math.sin(sizeToRel(startSize + item.size))
    out.push({
      startX: startX,
      startY: startY,
      endX: x,
      endY: y,
      longArc: item.size > 0.5 * sizeSum ? 1 : 0,
      color: item.color,
    })
    i++
    startX = x
    startY = y
    startSize += item.size
  }
  return out
})
</script>
