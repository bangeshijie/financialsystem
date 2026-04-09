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
                    <span>数据明细</span>
                    <div>
                        <el-tag v-if="loading" type="info" effect="plain" size="small">加载中...</el-tag>
                        <el-tag v-else-if="hasData && liquidData.length > 0" type="success" effect="plain"
                            size="small">已更新 (共 {{ liquidData.length }} 条)</el-tag>
                        <el-tag v-else-if="!loading && !hasData" type="info" effect="plain" size="small">等待查询</el-tag>
                    </div>
                </div>
            </template>

            <el-table :data="liquidData" style="width: 100%" border fit highlight-current-row
                empty-text="暂无数据，请选择公司和日期">
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


        </el-card>

    </div>
</template>

<script lang="ts" setup>
import { ref, reactive } from 'vue'

import CompanySelect from '@/components/selectcomponents/CompanySelect.vue';
import YearmonthSelect from '@/components/selectcomponents/YearmonthSelect.vue';

// --- 状态定义 ---
const loading = ref(false);
const hasData = ref(false);

// 统一的表单数据对象
const form = reactive({
    yearmonth: '' as string | null,
    company_code: '' as string | undefined,
});

// 表格数据 
const liquidData = ref<any[]>([]);

// --- 核心逻辑 ---

const formatMoney = (val: any) => {
    if (val === null || val === undefined || val === '') return '-';
    const num = Number(val);
    if (isNaN(num)) return String(val);
    return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
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
        // 【关键修改】：条件不全时，必须清空数据，防止展示过期的旧数据
        // 这样用户能明确感知到“当前选择无效”
        if (liquidData.value.length > 0) {
            liquidData.value = [];
            hasData.value = false;
            loading.value = false;
            console.log('⚠️ 条件缺失，已清空表格数据');
        }
        // 如果本来就是空的，什么都不做，或者可以给个轻微提示（可选）
        // if(!hasDate && !hasCode) ElMessage.info('请选择日期和公司'); 
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
        const monthStr = form.yearmonth ? form.yearmonth.substring(5) : '01'; // 获取月份，如 '2024-03' -> '03'
        const yearStr = form.yearmonth ? form.yearmonth.substring(0, 4) : '2024'; // 获取年份

        // 1. 公司系数：不同公司数据不同
        let companyFactor = 1.0;
        if (String(code).endsWith('01')) companyFactor = 1.2;  // 公司01：数据较大
        else if (String(code).endsWith('02')) companyFactor = 0.8; // 公司02：数据较小
        else companyFactor = 1.0; // 其他公司：中等

        // 2. 月份系数：不同月份数据不同（模拟季节性波动）
        const month = parseInt(monthStr);
        let monthFactor = 1.0;

        // 让数据随月份变化：1-12月有规律地波动
        if (month >= 3 && month <= 5) monthFactor = 1.3;  // 春季（3-5月）：旺季
        else if (month >= 6 && month <= 8) monthFactor = 1.1;  // 夏季（6-8月）：次旺
        else if (month >= 9 && month <= 11) monthFactor = 1.2;  // 秋季（9-11月）：次旺
        else monthFactor = 0.9;  // 冬季（12-2月）：淡季

        // 3. 年份趋势：逐年增长（假设是2024年）
        const year = parseInt(yearStr);
        let yearFactor = 1.0;
        if (year === 2024) yearFactor = 0.8;  // 2023年：基数较低
        else if (year === 2025) yearFactor = 1.0;  // 2024年：正常
        else if (year === 2026) yearFactor = 1.2;  // 2025年：预期增长

        // 综合因子 = 公司系数 × 月份系数 × 年份系数
        const totalFactor = companyFactor * monthFactor * yearFactor;

        // 根据不同的月份生成不同的数据明细
        let mockData;

        if (month >= 1 && month <= 3) {
            // 第一季度：传统业务为主
            mockData = [
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
            // 第二季度：促销活动多，销售费用增加
            mockData = [
                { tips: '1', name: '一、营业收入', currentAmount: 1200 * totalFactor, totalAmount: 5200 * totalFactor },
                { tips: '2', name: '二、营业总成本', currentAmount: 950 * totalFactor, totalAmount: 4150 * totalFactor },
                { tips: '3', name: '其中：营业成本', currentAmount: 580 * totalFactor, totalAmount: 2580 * totalFactor },
                { tips: '4', name: '税金及附加', currentAmount: 60 * totalFactor, totalAmount: 270 * totalFactor },
                { tips: '5', name: '销售费用', currentAmount: 150 * totalFactor, totalAmount: 600 * totalFactor }, // 促销费增加
                { tips: '6', name: '管理费用', currentAmount: 130 * totalFactor, totalAmount: 550 * totalFactor },
                { tips: '7', name: '财务费用', currentAmount: 30 * totalFactor, totalAmount: 150 * totalFactor },
                { tips: '8', name: '三、营业利润', currentAmount: 250 * totalFactor, totalAmount: 1050 * totalFactor },
            ];
        } else if (month >= 7 && month <= 9) {
            // 第三季度：旺季，各项指标都高
            mockData = [
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
            // 第四季度：年底结算，财务费用增加
            mockData = [
                { tips: '1', name: '一、营业收入', currentAmount: 1100 * totalFactor, totalAmount: 11000 * totalFactor },
                { tips: '2', name: '二、营业总成本', currentAmount: 880 * totalFactor, totalAmount: 8700 * totalFactor },
                { tips: '3', name: '其中：营业成本', currentAmount: 530 * totalFactor, totalAmount: 5300 * totalFactor },
                { tips: '4', name: '税金及附加', currentAmount: 55 * totalFactor, totalAmount: 600 * totalFactor },
                { tips: '5', name: '销售费用', currentAmount: 120 * totalFactor, totalAmount: 1200 * totalFactor },
                { tips: '6', name: '管理费用', currentAmount: 130 * totalFactor, totalAmount: 1300 * totalFactor },
                { tips: '7', name: '财务费用', currentAmount: 45 * totalFactor, totalAmount: 300 * totalFactor }, // 年底财务费用增加
                { tips: '8', name: '三、营业利润', currentAmount: 220 * totalFactor, totalAmount: 2300 * totalFactor },
            ];
        }

        // 添加累计值的说明（让数据更真实）
        mockData = mockData.map(item => {
            if (item.tips === '1') {
                item.name = `一、营业收入 (${yearStr}年${monthStr}月)`;
            }
            return item;
        });

        liquidData.value = mockData;
        hasData.value = true;
        loading.value = false;

        // 打印详细的计算信息，方便观察变化
        console.log('✅ 数据生成完成', {
            公司: code,
            日期: `${yearStr}年${monthStr}月`,
            公司系数: companyFactor.toFixed(2),
            月份系数: monthFactor.toFixed(2),
            年份系数: yearFactor.toFixed(2),
            综合因子: totalFactor.toFixed(2),
            本月收入: mockData[0]?.currentAmount.toFixed(2),
            季度类型: month >= 1 && month <= 3 ? 'Q1' : month >= 4 && month <= 6 ? 'Q2' : month >= 7 && month <= 9 ? 'Q3' : 'Q4'
        });

    }, 600);
};

// --- 事件绑定 ---

const chooseChange = () => {
    // 公司或日期变动
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

    span {
        font-weight: bold;
        font-size: 16px;
    }
}
</style>