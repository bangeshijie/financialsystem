<script setup lang="ts">

import { onMounted } from 'vue'
import { reqCompanyList, reqCompanyOptions } from '@/api/dimensions/dim_entity'

onMounted(() => {
    reqCompanyOptions({
        keyword: ''
    })
    reqCompanyList(1, 2, "")

})





</script>

<template>
    <div>
        <h1>我是现金流量表</h1>

    </div>

</template>

<style scoped lang="scss"></style>
