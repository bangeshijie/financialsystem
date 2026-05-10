<template>
    <div>
        <!-- 筛选区域 -->
        <el-card class="search-card">
            <el-form ref="formRef" :model="form" label-width="100px" size="default">
                <el-row :gutter="20">
                    <!-- 第一列：日期选择框 (使用子组件) -->
                    <el-col :span="12">
                        <el-form-item label="选择期间">
                            <YearmonthSelect v-model="form.yearmonth" placeholder="请选择期间" @change="chooseChange" />
                        </el-form-item>
                    </el-col>

                    <!-- 第二列：公司选择框 (已有子组件) -->
                    <el-col :span="12">
                        <el-form-item label="所属公司">
                            <CompanySelect v-model="form.company_code" placeholder="点击选择或输入公司名搜索" :default-limit="20"
                                @change="chooseChange" />
                        </el-form-item>
                    </el-col>
                </el-row>
            </el-form>
        </el-card>


        <!-- 数据展示区域 -->
        <el-card class="data-card" style="margin-top: 15px;">
            <template #header>
                <div class="card-header">
                    <div class="button-group">
                        <el-button :type="activeTable === 'table1' ? 'primary' : 'default'"
                            @click="switchTable('table1')" size="small">
                            利润表
                        </el-button>
                        <el-button :type="activeTable === 'table2' ? 'primary' : 'default'"
                            @click="switchTable('table2')" size="small">
                            资产负债表
                        </el-button>
                        <el-button :type="activeTable === 'table3' ? 'primary' : 'default'"
                            @click="switchTable('table3')" size="small">
                            现金流量表
                        </el-button>
                    </div>
                    <div>
                        <el-tag v-if="loading" type="info" effect="plain" size="small">加载中...</el-tag>
                        <el-tag v-else-if="hasData && currentTableData.length > 0" type="success" effect="plain"
                            size="small">已更新 (共 {{ currentTableData.length }} 条)</el-tag>
                        <el-tag v-else-if="!loading && !hasData" type="info" effect="plain" size="small">等待查询</el-tag>
                    </div>
                </div>
            </template>

            <!-- 利润表 -->
            <el-table v-if="activeTable === 'table1'" :data="table1Data" style="width: 100%" border fit
                highlight-current-row empty-text="暂无数据，请选择公司和日期">
                <el-table-column prop="tips" label="序号" width="60" align="center" />
                <el-table-column prop="name" label="项目" min-width="200" />
                <el-table-column prop="currentAmount" label="本月数" width="180" align="right">
                    <template #default="{ row }">
                        {{ formatMoney(row.currentAmount) }}
                    </template>
                </el-table-column>
                <el-table-column prop="totalAmount" label="本年累计数" width="180" align="right">
                    <template #default="{ row }">
                        {{ formatMoney(row.totalAmount) }}
                    </template>
                </el-table-column>
            </el-table>

            <!-- 资产负债表 -->
            <el-table v-else-if="activeTable === 'table2'" :data="table2Data" style="width: 100%" border fit
                highlight-current-row empty-text="暂无数据，请选择公司和日期">
                <el-table-column prop="tips" label="序号" width="60" align="center" />
                <el-table-column prop="assetName" label="资产项目" min-width="200" />
                <el-table-column prop="beginningBalance" label="期初余额" width="180" align="right">
                    <template #default="{ row }">
                        {{ formatMoney(row.beginningBalance) }}
                    </template>
                </el-table-column>
                <el-table-column prop="endingBalance" label="期末余额" width="180" align="right">
                    <template #default="{ row }">
                        {{ formatMoney(row.endingBalance) }}
                    </template>
                </el-table-column>
            </el-table>

            <!-- 现金流量表 -->
            <el-table v-else-if="activeTable === 'table3'" :data="table3Data" style="width: 100%" border fit
                highlight-current-row empty-text="暂无数据，请选择公司和日期">
                <el-table-column prop="tips" label="序号" width="60" align="center" />
                <el-table-column prop="projectName" label="项目" min-width="200" />
                <el-table-column prop="currentPeriod" label="本期金额" width="180" align="right">
                    <template #default="{ row }">
                        {{ formatMoney(row.currentPeriod) }}
                    </template>
                </el-table-column>
                <el-table-column prop="lastPeriod" label="上期金额" width="180" align="right">
                    <template #default="{ row }">
                        {{ formatMoney(row.lastPeriod) }}
                    </template>
                </el-table-column>
            </el-table>

            <!-- 通用的空状态提示 -->
            <div v-if="!loading && !hasData" class="empty-tip">
                <el-empty description="请选择公司和日期后点击按钮查询" :image-size="100" />
            </div>
        </el-card>
    </div>
</template>

<script lang="ts" setup>
import { ref, reactive, computed } from 'vue'
import CompanySelect from '@/components/selectcomponents/CompanySelect.vue';
import YearmonthSelect from '@/components/selectcomponents/YearmonthSelect.vue';

// --- 状态定义 ---
const loading = ref(false);
const hasData = ref(false);
const activeTable = ref('table1'); // 当前激活的表格：table1, table2, table3

// 统一的表单数据对象
const form = reactive({
    yearmonth: '' as string | null,
    company_code: '' as string | undefined,
});

// 三个表格的数据
const table1Data = ref<any[]>([]); // 利润表
const table2Data = ref<any[]>([]); // 资产负债表
const table3Data = ref<any[]>([]); // 现金流量表

// 当前显示的表格数据
const currentTableData = computed(() => {
    if (activeTable.value === 'table1') return table1Data.value;
    if (activeTable.value === 'table2') return table2Data.value;
    return table3Data.value;
});

// --- 核心逻辑 ---

const formatMoney = (val: any) => {
    if (val === null || val === undefined || val === '') return '-';
    const num = Number(val);
    if (isNaN(num)) return String(val);
    return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

/**
 * 切换表格
 */
const switchTable = (table: string) => {
    activeTable.value = table;
    // 如果已经有数据，不需要重新加载，只是切换显示
    // 如果当前没有数据且条件满足，可以重新查询
    if (hasData.value && form.yearmonth && form.company_code) {
        // 已经有数据，不需要操作
        console.log('切换到表格:', table);
    } else if (form.yearmonth && form.company_code) {
        // 没有数据但条件满足，执行查询
        performFetch();
    }
};

/**
 * 统一触发查询逻辑
 * 规则：只要任意筛选条件变动，立即检查并更新表格
 */
const triggerSearch = () => {
    const hasDate = !!form.yearmonth;
    const hasCode = !!form.company_code;

    console.log('🔍 触发查询检查', { date: form.yearmonth, company: form.company_code });

    // 如果条件不完整
    if (!hasDate || !hasCode) {
        // 条件不全时，清空所有表格数据
        if (table1Data.value.length > 0 || table2Data.value.length > 0 || table3Data.value.length > 0) {
            table1Data.value = [];
            table2Data.value = [];
            table3Data.value = [];
            hasData.value = false;
            loading.value = false;
            console.log('⚠️ 条件缺失，已清空所有表格数据');
        }
        return;
    }

    // 条件完整，执行请求
    performFetch();
};

/**
 * 执行实际的数据获取逻辑
 */
const performFetch = async () => {
    loading.value = true;

    console.log('📊 执行查询，参数：', {
        公司: form.company_code,
        日期: form.yearmonth,
        时间戳: new Date().toLocaleString()
    });

    // 模拟网络延迟
    setTimeout(() => {
        const code = form.company_code || 'DEFAULT';
        const monthStr = form.yearmonth ? form.yearmonth.substring(5) : '01';
        const yearStr = form.yearmonth ? form.yearmonth.substring(0, 4) : '2024';

        // 计算系数（用于所有表格）
        let companyFactor = 1.0;
        if (String(code).endsWith('01')) companyFactor = 1.2;
        else if (String(code).endsWith('02')) companyFactor = 0.8;
        else companyFactor = 1.0;

        const month = parseInt(monthStr);
        let monthFactor = 1.0;
        if (month >= 3 && month <= 5) monthFactor = 1.3;
        else if (month >= 6 && month <= 8) monthFactor = 1.1;
        else if (month >= 9 && month <= 11) monthFactor = 1.2;
        else monthFactor = 0.9;

        const year = parseInt(yearStr);
        let yearFactor = 1.0;
        if (year === 2024) yearFactor = 0.8;
        else if (year === 2025) yearFactor = 1.0;
        else if (year === 2026) yearFactor = 1.2;

        const totalFactor = companyFactor * monthFactor * yearFactor;

        // 1. 利润表数据（保持原有逻辑）
        let profitData;
        if (month >= 1 && month <= 3) {
            profitData = [
                { tips: '1', name: '一、营业收入', currentAmount: 1000 * totalFactor, totalAmount: 3000 * totalFactor },
                { tips: '2', name: '二、营业总成本', currentAmount: 800 * totalFactor, totalAmount: 2400 * totalFactor },
                { tips: '3', name: '其中：营业成本', currentAmount: 500 * totalFactor, totalAmount: 1500 * totalFactor },
                { tips: '4', name: '税金及附加', currentAmount: 50 * totalFactor, totalAmount: 150 * totalFactor },
                { tips: '5', name: '销售费用', currentAmount: 100 * totalFactor, totalAmount: 300 * totalFactor },
                { tips: '6', name: '管理费用', currentAmount: 120 * totalFactor, totalAmount: 360 * totalFactor },
                { tips: '7', name: '财务费用', currentAmount: 20 * totalFactor, totalAmount: 60 * totalFactor },
                { tips: '8', name: '三、营业利润', currentAmount: 200 * totalFactor, totalAmount: 600 * totalFactor },
            ];
        } else if (month >= 4 && month <= 6) {
            profitData = [
                { tips: '1', name: '一、营业收入', currentAmount: 1200 * totalFactor, totalAmount: 5200 * totalFactor },
                { tips: '2', name: '二、营业总成本', currentAmount: 950 * totalFactor, totalAmount: 4150 * totalFactor },
                { tips: '3', name: '其中：营业成本', currentAmount: 580 * totalFactor, totalAmount: 2580 * totalFactor },
                { tips: '4', name: '税金及附加', currentAmount: 60 * totalFactor, totalAmount: 270 * totalFactor },
                { tips: '5', name: '销售费用', currentAmount: 150 * totalFactor, totalAmount: 600 * totalFactor },
                { tips: '6', name: '管理费用', currentAmount: 130 * totalFactor, totalAmount: 550 * totalFactor },
                { tips: '7', name: '财务费用', currentAmount: 30 * totalFactor, totalAmount: 150 * totalFactor },
                { tips: '8', name: '三、营业利润', currentAmount: 250 * totalFactor, totalAmount: 1050 * totalFactor },
            ];
        } else if (month >= 7 && month <= 9) {
            profitData = [
                { tips: '1', name: '一、营业收入', currentAmount: 1500 * totalFactor, totalAmount: 8200 * totalFactor },
                { tips: '2', name: '二、营业总成本', currentAmount: 1150 * totalFactor, totalAmount: 6400 * totalFactor },
                { tips: '3', name: '其中：营业成本', currentAmount: 700 * totalFactor, totalAmount: 3900 * totalFactor },
                { tips: '4', name: '税金及附加', currentAmount: 80 * totalFactor, totalAmount: 450 * totalFactor },
                { tips: '5', name: '销售费用', currentAmount: 180 * totalFactor, totalAmount: 980 * totalFactor },
                { tips: '6', name: '管理费用', currentAmount: 150 * totalFactor, totalAmount: 850 * totalFactor },
                { tips: '7', name: '财务费用', currentAmount: 40 * totalFactor, totalAmount: 220 * totalFactor },
                { tips: '8', name: '三、营业利润', currentAmount: 350 * totalFactor, totalAmount: 1800 * totalFactor },
            ];
        } else {
            profitData = [
                { tips: '1', name: '一、营业收入', currentAmount: 1100 * totalFactor, totalAmount: 11000 * totalFactor },
                { tips: '2', name: '二、营业总成本', currentAmount: 880 * totalFactor, totalAmount: 8700 * totalFactor },
                { tips: '3', name: '其中：营业成本', currentAmount: 530 * totalFactor, totalAmount: 5300 * totalFactor },
                { tips: '4', name: '税金及附加', currentAmount: 55 * totalFactor, totalAmount: 600 * totalFactor },
                { tips: '5', name: '销售费用', currentAmount: 120 * totalFactor, totalAmount: 1200 * totalFactor },
                { tips: '6', name: '管理费用', currentAmount: 130 * totalFactor, totalAmount: 1300 * totalFactor },
                { tips: '7', name: '财务费用', currentAmount: 45 * totalFactor, totalAmount: 300 * totalFactor },
                { tips: '8', name: '三、营业利润', currentAmount: 220 * totalFactor, totalAmount: 2300 * totalFactor },
            ];
        }

        // 2. 资产负债表数据
        const balanceData = [
            { tips: '1', assetName: '流动资产：', beginningBalance: 5000 * totalFactor, endingBalance: 5500 * totalFactor },
            { tips: '2', assetName: '  货币资金', beginningBalance: 2000 * totalFactor, endingBalance: 2200 * totalFactor },
            { tips: '3', assetName: '  应收账款', beginningBalance: 1500 * totalFactor, endingBalance: 1650 * totalFactor },
            { tips: '4', assetName: '  存货', beginningBalance: 1000 * totalFactor, endingBalance: 1100 * totalFactor },
            { tips: '5', assetName: '非流动资产：', beginningBalance: 3000 * totalFactor, endingBalance: 3500 * totalFactor },
            { tips: '6', assetName: '  固定资产', beginningBalance: 2000 * totalFactor, endingBalance: 2300 * totalFactor },
            { tips: '7', assetName: '  无形资产', beginningBalance: 800 * totalFactor, endingBalance: 900 * totalFactor },
            { tips: '8', assetName: '资产总计', beginningBalance: 8000 * totalFactor, endingBalance: 9000 * totalFactor },
        ];

        // 3. 现金流量表数据
        const cashFlowData = [
            { tips: '1', projectName: '一、经营活动产生的现金流量：', currentPeriod: 1500 * totalFactor, lastPeriod: 1200 * totalFactor },
            { tips: '2', projectName: '  销售商品、提供劳务收到的现金', currentPeriod: 3000 * totalFactor, lastPeriod: 2500 * totalFactor },
            { tips: '3', projectName: '  购买商品、接受劳务支付的现金', currentPeriod: -1800 * totalFactor, lastPeriod: -1500 * totalFactor },
            { tips: '4', projectName: '  支付给职工以及为职工支付的现金', currentPeriod: -500 * totalFactor, lastPeriod: -450 * totalFactor },
            { tips: '5', projectName: '  经营活动产生的现金流量净额', currentPeriod: 700 * totalFactor, lastPeriod: 550 * totalFactor },
            { tips: '6', projectName: '二、投资活动产生的现金流量：', currentPeriod: -300 * totalFactor, lastPeriod: -200 * totalFactor },
            { tips: '7', projectName: '  购建固定资产、无形资产支付的现金', currentPeriod: -400 * totalFactor, lastPeriod: -300 * totalFactor },
            { tips: '8', projectName: '  投资活动产生的现金流量净额', currentPeriod: -400 * totalFactor, lastPeriod: -300 * totalFactor },
            { tips: '9', projectName: '三、筹资活动产生的现金流量：', currentPeriod: 200 * totalFactor, lastPeriod: 100 * totalFactor },
            { tips: '10', projectName: '  筹资活动产生的现金流量净额', currentPeriod: 200 * totalFactor, lastPeriod: 100 * totalFactor },
            { tips: '11', projectName: '四、现金及现金等价物净增加额', currentPeriod: 500 * totalFactor, lastPeriod: 350 * totalFactor },
        ];

        table1Data.value = profitData;
        table2Data.value = balanceData;
        table3Data.value = cashFlowData;
        hasData.value = true;
        loading.value = false;

        console.log('✅ 所有表格数据生成完成', {
            公司: code,
            日期: `${yearStr}年${monthStr}月`,
            利润表条数: profitData.length,
            资产负债表条数: balanceData.length,
            现金流量表条数: cashFlowData.length
        });

    }, 600);
};

// --- 事件绑定 ---
const chooseChange = () => {
    triggerSearch();
};

</script>

<style scoped lang="scss">
.search-card {
    margin-bottom: 0;
    border-radius: 4px;
}

.data-card {
    border-radius: 4px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .button-group {
        display: flex;
        gap: 10px;
    }
}

.empty-tip {
    padding: 40px 0;
    text-align: center;
}
</style>