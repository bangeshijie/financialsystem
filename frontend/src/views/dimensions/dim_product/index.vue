<template>
    <div>
        <el-date-picker v-model="selectedMonth" type="month" placeholder="选择月份" format="YYYY-MM" value-format="YYYY-MM"
            @change="handleMonthChange" style="width: 200px; margin-bottom: 20px;" />

        <el-table :data="tableData" border style="width: 100%" show-summary :summary-method="getSummaries">
            <!-- 固定列：产品名称 -->
            <el-table-column prop="productName" label="产品" width="150" fixed="left" />

            <!-- 动态生成的月份列 -->
            <el-table-column v-for="column in dynamicColumns" :key="column.prop" :prop="column.prop"
                :label="column.label" min-width="100">
                <template #default="scope">
                    {{ scope.row[column.prop] || '-' }}
                </template>
            </el-table-column>

            <!-- 合计列 -->
            <el-table-column label="合计" min-width="120" fixed="right" align="right">
                <template #default="scope">
                    {{ calculateRowTotal(scope.row) }}
                </template>
            </el-table-column>
        </el-table>
    </div>
</template>

<script setup lang="ts">

import { ref, computed } from 'vue'

const selectedMonth = ref('2026-04')

const tableData = ref([
    { productName: '产品A', '2026-01': 120, '2026-02': 85, '2026-03': 110, '2026-04': 95 },
    { productName: '产品B', '2026-01': 60, '2026-02': 75, '2026-03': 90, '2026-04': 105 },
    { productName: '产品C', '2026-01': 200, '2026-02': 180, '2026-03': 210, '2026-04': 195 },
])

const dynamicColumns = computed(() => {
    if (!selectedMonth.value) return []
    const parts = selectedMonth.value.split('-')
    const year = Number(parts[0])
    const month = Number(parts[1])

    // 增加有效性校验，防止 NaN 或 undefined
    if (isNaN(year) || isNaN(month) || month < 1 || month > 12) {
        return []
    }
    const columns = []
    for (let i = 1; i <= month; i++) {
        const monthStr = i.toString().padStart(2, '0')
        columns.push({ prop: `${year}-${monthStr}`, label: `${i}月` })
    }
    return columns
})

const calculateRowTotal = (row: any) => {
    let total = 0
    dynamicColumns.value.forEach(column => {
        const value = row[column.prop]
        if (typeof value === 'number') total += value
    })
    return total
}

// 自定义合计行方法
const getSummaries = (param: { columns: any[], data: any[] }) => {
    const { columns, data } = param
    // 修复点：显式声明类型为 (string | number)[]
    const sums: (string | number)[] = []

    columns.forEach((column, index) => {
        if (index === 0) {
            sums[index] = '总计'
            return
        }

        // 处理月份列和合计列
        const values = data.map(item => {
            // 动态月份列
            const monthValue = item[column.property]
            if (typeof monthValue === 'number') return monthValue

            // 合计列
            if (column.label === '合计') {
                return calculateRowTotal(item)
            }

            return 0
        })

        if (values.every(value => value === 0)) {
            sums[index] = '-'
        } else {
            sums[index] = values.reduce((prev, curr) => prev + curr, 0)
        }
    })

    return sums
}

const handleMonthChange = (value: string | null) => {
    console.log('选中的月份:', value)
}
</script>