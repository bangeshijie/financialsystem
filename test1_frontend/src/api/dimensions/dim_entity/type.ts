/**
 * 公司模块类型定义
 * 对应后端 Pydantic 模型
 */



// 分类相关数据类型
export interface ResponseData {
    code: number;
    message: string;
    ok: boolean;
}



// --- 通用基础字段 (用于 Request 和 Response 的共有部分) ---
export interface CompanyBaseFields {
    name: string;
    company_code: string;
    address?: string | null;
    contact_person?: string | null;
    contact_phone?: string | null;
    contact_email?: string | null;
    industry?: string | null;
    scale?: string; // 创建时有默认值 'small'，更新时可选
    description?: string | null;
}

// --- 请求模型 (Request) ---

/**
 * 创建公司请求
 * 对应: CompanyCreateRequest
 */
export interface CompanyCreateRequest extends CompanyBaseFields {
    // name, company_code 等在 BaseFields 中已定义为必填或根据需求调整
    // 注意：Python 中 scale 有默认值 'small'，TS 中设为可选，由后端处理默认值，或者前端显式传 'small'
    scale?: string;
}

/**
 * 更新公司请求
 * 对应: CompanyUpdateRequest
 * 所有字段均为可选 (Partial)
 */
export interface CompanyUpdateRequest {
    name?: string | null;
    address?: string | null;
    contact_person?: string | null;
    contact_phone?: string | null;
    contact_email?: string | null;
    industry?: string | null;
    scale?: string | null;
    description?: string | null;
    status?: number | null; // 0 或 1
}

// --- 响应模型 (Response) ---

/**
 * 公司基础响应 (用于创建/更新后的返回)
 * 对应: CompanyBaseResponse
 * 特点：不包含 creator_name/updater_name
 */
export interface CompanyBaseObj {
    id: number;
    company_id: number;
    name: string;
    company_code: string;
    address: string | null;
    contact_person: string | null;
    contact_phone: string | null;
    contact_email: string | null;
    industry: string | null;
    scale: string | null;
    description: string | null;
    status: number;
    created_time: string; // ISO Date String
    updated_time: string; // ISO Date String
}


export interface CompanyBaseResponse extends ResponseData {
    data: CompanyBaseObj[]

}








/**
 * 公司详细响应 (用于详情/列表)
 * 对应: CompanyDetailResponse
 * 特点：包含 creator_name, updater_name
 */
export interface CompanyDetailObj extends CompanyBaseObj {
    // 重写 scale，根据 Python 模型 DetailResponse 中 scale: str (非 Optional)，但在实际 JSON 中可能仍为 null
    // 如果后端保证 detail 接口 scale 永不为空，这里可以去掉 | null
    scale: string;

    creator_name: string | null;
    updater_name: string | null;
}



export interface CompanyDetailResponse extends ResponseData {
    data: CompanyDetailObj[];
}



/**
 * 公司列表响应包装器
 * 对应: CompanyListResponse
 */
export interface CompanyListResponse extends ResponseData {
    data: {
        total: number;
        items: CompanyDetailObj[];
    }
}

// --- 辅助类型 (可选) ---

/**
 * 表单数据类型 (用于 Vue Form 绑定)
 * 通常将 null 转换为 空字符串 '' 以便 v-model 绑定
 */
export type CompanyFormState = Omit<CompanyCreateRequest, 'scale'> & {
    scale: string;
};





// 简单的公司选项调用 用于各个页面的筛选

/**
 * 公司选项对象
 * 对应后端 CompanyOption Schema
 */
export interface CompanyOptions {
    company_code: string;
    name: string;
}
/** 
* 查询参数接口
* 对应后端 Query 参数
*/
export interface CompanyOptionsRequest {
    keyword?: string; // 搜索关键字
    limit?: number;   // 限制返回数量，默认 100
}

/** 
* 简短短公司详情接口

*/
export interface CompanyOptionsResponse extends ResponseData {
    data: CompanyOptions[];
}
