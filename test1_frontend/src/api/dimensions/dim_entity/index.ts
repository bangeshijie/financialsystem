//这里书写商品属性相关的接口
import request from '@/utils/request';
import type { CompanyCreateRequest, CompanyUpdateRequest, CompanyBaseResponse, CompanyDetailResponse, CompanyListResponse, CompanyOptionsRequest, CompanyOptionsResponse } from './type';

// 获取已有属性接口
export const API = {
    ADD_COMPANY_URL: "/company/add",
    DELETE_COMPANY_URL: "/company/delete/",
    UPDATE_COMPANY_URL: "/company/update",
    GET_COMPANY_URL: "/company/info/",
    GET_COMPANY_LIST_URL: "/company/list",

    GET_COMPANY_TOTAL_URL: "/company/total",
    GET_COMPANY_PAGE_URL: "/company/page",
    GET_COMPANY_PAGE_LIST_URL: "/company/page/list",
    GET_COMPANY_OPTIONS_URL: "/company/options",
    



} as const;




// 获取已有公司列表接口方法


export const reqCompanyList = (page: number, limit: number, searchKeyword: string) => {
    return request.get<any, CompanyListResponse>(API.GET_COMPANY_LIST_URL, {
        params: {
            page,
            limit,
            keyword: searchKeyword || undefined // 如果为空字符串，传 undefined 让后端忽略该参数
        }
    });
};

// 获取某个已有公司信息接口方法
export const reqCompany = (companyId: number | string) => request.get<any, CompanyDetailResponse>(API.GET_COMPANY_URL + companyId);


// 添加公司接口方法
export const reqAddCompany = (data: CompanyCreateRequest) => request.post<any, CompanyBaseResponse>(API.ADD_COMPANY_URL, data);

// 更新公司接口方法

export const reqUpdateCompany = (id: number, data: CompanyUpdateRequest) => request.put<any, CompanyBaseResponse>(`${API.UPDATE_COMPANY_URL}/${id}`, data);

// 删除某个已有公司接口方法
export const reqDeleteCompany = (companyId: number | string) => request.delete<any, any>(API.DELETE_COMPANY_URL + companyId);


//获取公司下拉选项列表

export const reqCompanyOptions = (data: CompanyOptionsRequest) => request.get<any, CompanyOptionsResponse>(API.GET_COMPANY_OPTIONS_URL, { params: data });
