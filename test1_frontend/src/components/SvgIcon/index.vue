<template>
    <svg :style="{ width, height }">
        <use :xlink:href="prefix + name" :fill="color"></use>
    </svg>
</template>

<script setup lang="ts">
// 定义组件名称
defineOptions({
  name: 'SvgIcon'
})

// 解构 props，这样可以直接使用变量名
const { 
  name, 
  prefix = '#icon-', 
  color = '', 
  width = '16px', 
  height = '16px' 
} = defineProps<{
  name: string
  prefix?: string
  color?: string
  width?: string
  height?: string
}>()
</script>

<style scoped></style>