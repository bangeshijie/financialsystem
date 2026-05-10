import request from '@/utils/request';

import type {

    AccountingSubject,
    AccountingSubjectCreate,
    AccountingSubjectUpdate,
    AccountVersion,
    AccountVersionCreate,
    AccountVersionUpdate,
    PageResponse
} from './type'





// ---------------------------------------科目------------------------------------------------





const ACCOUNT_BASE_URL = '/account'

// ============ 科目管理 API ============
export const accountApi = {
    // 创建科目
    create: (data: AccountingSubjectCreate) =>
        request.post<AccountingSubject>(`${ACCOUNT_BASE_URL}/add`, data),

    // 获取科目列表
    getList: (params: {
        skip?: number
        limit?: number
        account_version_id?: number
        parent_id?: number
        level?: number
        is_active?: boolean
        is_leaf?: boolean
        search?: string
    }) => request.get<PageResponse<AccountingSubject>>(`${ACCOUNT_BASE_URL}/list`, { params }),

    // 获取科目树
    getTree: (account_version_id: number) =>
        request.get<AccountingSubject[]>(`${ACCOUNT_BASE_URL}/tree`, { params: { account_version_id } }),

    // 获取科目详情
    getById: (id: number) =>
        request.get<AccountingSubject>(`${ACCOUNT_BASE_URL}/info/${id}`),

    // 更新科目
    update: (id: number, data: AccountingSubjectUpdate) =>
        request.put<AccountingSubject>(`${ACCOUNT_BASE_URL}/update/${id}`, data),

    // 删除科目
    delete: (id: number) =>
        request.delete(`${ACCOUNT_BASE_URL}/delete/${id}`),

    // 批量创建
    batchCreate: (data: AccountingSubjectCreate[]) =>
        request.post<AccountingSubject[]>(`${ACCOUNT_BASE_URL}/add/batch`, data),

    // 导出科目
    export: (account_version_id: number) =>
        request.get(`${ACCOUNT_BASE_URL}/export/${account_version_id}`)
}


// --------------------------------------版本管理------------------------------------------------


const VERSION_BASE_URL = '/account_version'

export const versionApi = {
    // 创建版本
    create: (data: AccountVersionCreate) =>
        request.post<AccountVersion>(`${VERSION_BASE_URL}/add`, data),

    // 获取版本列表
    getList: (params: { skip?: number; limit?: number; is_active?: boolean; search?: string }) =>
        request.get<PageResponse<AccountVersion>>(`${VERSION_BASE_URL}/list`, { params }),

    // 获取版本详情
    getById: (id: number) =>
        request.get<AccountVersion>(`${VERSION_BASE_URL}/info/${id}`),

    // 更新版本
    update: (id: number, data: AccountVersionUpdate) =>
        request.put<AccountVersion>(`${VERSION_BASE_URL}/update/${id}`, data),

    // 删除版本
    delete: (id: number) =>
        request.delete(`${VERSION_BASE_URL}/delete/${id}`),

    // 设置默认版本
    setDefault: (id: number) =>
        request.post<AccountVersion>(`${VERSION_BASE_URL}/set-default/${id}`)
}