<template>
    <div class="demo-date-picker">


        <div class="container">

            <div class="block">
                <span class="demonstration">期间</span>
                <el-date-picker v-model="yearmonths" type="month" placeholder="请选择期间" format="YYYY-MM"
                    value-format="YYYY-MM" />
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'

const yearmonths = ref<string | null>('') 
</script>

<style scoped lang="scss">
.demo-date-picker {
    display: flex;
    width: 100%;
    padding: 0;
    flex-wrap: wrap;
}

.demo-date-picker .container {
    flex: 1;
    min-width: 300px;
    border-right: solid 1px var(--el-border-color);
}

.demo-date-picker .container:last-child {
    border-right: none;
}

.demo-date-picker .block {
    display: flex;
    align-items: center;
    padding: 1.5rem 0;
    gap: 12px;

}

.demo-date-picker .container .block:last-child {
    border-top: solid 1px var(--el-border-color);
}

.demo-date-picker .demonstration {
    display: inline-block;
    color: var(--el-text-color-secondary);
    font-size: 14px;

}

@media screen and (max-width: 768px) {
    .demo-date-picker .container {
        flex: 0 0 100%;
        min-width: auto;
        border-right: none;
        border-bottom: solid 1px var(--el-border-color);
    }

    .demo-date-picker .container:last-child {
        border-bottom: none;
    }

    .demo-date-picker .block {
        padding: 1rem 0;
    }

    .demo-date-picker .container .block:last-child {
        border-top: solid 1px var(--el-border-color);
    }
}
</style>
