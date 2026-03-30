<template>

    <div>


        <el-card>
            <el-form :inline="true" class="form">

                <el-form-item class="block">

                    <el-date-picker v-model="yearmonth" type="month" placeholder="请选择期间" format="YYYY-MM"
                        value-format="YYYY-MM" />
                </el-form-item>



                <el-form-item class="block">

                    <el-select v-model="value" placeholder="请选择公司" filterable clearable style="width: 200px">
                        <el-option v-for="item in entitys" :key="item.value" :label="item.label" :value="item.value">
                            <span style="float: left">{{ item.label }}</span>
                            <span style="float: right;">{{ item.value }}</span>
                        </el-option>
                    </el-select>
                </el-form-item>
            </el-form>


        </el-card>

        <el-card style="margin: 10px 0px">




            <el-form>

                <div class="table-wrapper">

                    <!-- 左侧表格：资产 -->
                    <div class="table-side left-side">
                        <el-table :data="leftData" border style="width: 100%" fit highlight-current-row
                            :header-cell-style="{ background: '#f5f7fa', color: '#333', fontWeight: 'bold' }">
                            <el-table-column prop="index" label="序号" width="60" align="center" />
                            <el-table-column prop="subject" label="科目" min-width="180" />
                            <el-table-column prop="endBalance" label="期末余额" align="right" />
                            <el-table-column prop="startBalance" label="年初余额" align="right" />
                        </el-table>
                    </div>



                    <!-- 右侧表格：负债及所有者权益 -->
                    <div class="table-side right-side">
                        <el-table :data="rightData" border style="width: 100%" fit highlight-current-row
                            :header-cell-style="{ background: '#f5f7fa', color: '#333', fontWeight: 'bold' }">
                            <el-table-column prop="index" label="序号" width="60" align="center" />
                            <el-table-column prop="subject" label="科目" min-width="180" />
                            <el-table-column prop="endBalance" label="期末余额" align="right" />
                            <el-table-column prop="startBalance" label="年初余额" align="right" />
                        </el-table>
                    </div>

                </div>


            </el-form>

        </el-card>
    </div>
</template>







<script lang="ts" setup>
import { ref } from 'vue'

const yearmonth = ref<string | null>('')


const value = ref('')
const entitys = [
    {
        value: '101',
        label: '北京公司',
    },
    {
        value: '120',
        label: '广州公司',
    },
    {
        value: '121',
        label: '上海公司',
    },
    {
        value: '0571',
        label: '杭州公司',
    },

]



// 模拟左侧数据（资产）
const leftData = ref([
    { index: 1, subject: '流动资产：', endBalance: '', startBalance: '' },
    { index: 2, subject: '货币资金', endBalance: '1,200,000.00', startBalance: '1,000,000.00' },
    { index: 3, subject: '交易性金融资产', endBalance: '500,000.00', startBalance: '400,000.00' },
    { index: 4, subject: '应收账款', endBalance: '800,000.00', startBalance: '750,000.00' },
    { index: 5, subject: '存货', endBalance: '300,000.00', startBalance: '200,000.00' },
    { index: 6, subject: '非流动资产：', endBalance: '', startBalance: '' },
    { index: 7, subject: '固定资产', endBalance: '2,000,000.00', startBalance: '2,100,000.00' },
    { index: 8, subject: '无形资产', endBalance: '500,000.00', startBalance: '550,000.00' },
    // ... 更多数据，确保行数与右侧对应，如果不对应需补空行对象 { index: '', subject: '', ... }
]);

// 模拟右侧数据（负债及所有者权益）
const rightData = ref([
    { index: 1, subject: '流动负债：', endBalance: '', startBalance: '' },
    { index: 2, subject: '短期借款', endBalance: '600,000.00', startBalance: '500,000.00' },
    { index: 3, subject: '应付账款', endBalance: '400,000.00', startBalance: '350,000.00' },
    { index: 4, subject: '预收账款', endBalance: '100,000.00', startBalance: '80,000.00' },
    { index: 5, subject: '应付职工薪酬', endBalance: '200,000.00', startBalance: '180,000.00' },
    { index: 6, subject: '非流动负债：', endBalance: '', startBalance: '' },
    { index: 7, subject: '长期借款', endBalance: '1,000,000.00', startBalance: '1,200,000.00' },
    { index: 8, subject: '所有者权益：', endBalance: '', startBalance: '' },
    // ... 注意：这里行数最好和左侧保持一致，如果不一致，UI上会出现错位
]);



</script>

<style scoped lang="scss">
.table-wrapper {
    display: flex;
    justify-content: space-between;


}

.table-side {
    flex: 1;
    /* 左右各占一半宽度 */
    min-width: 0;
    /* 防止内容溢出导致 flex 失效 */
}
</style>
