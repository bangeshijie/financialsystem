
// ---------------------------------------------科目-----------------------------------------------------

export interface ResponseData {
    code: number;

    message: string;
    ok: boolean
}


export const BalanceDirection = {
    DEBIT: 'debit',
    CREDIT: 'credit'
} as const

export type BalanceDirectionType = typeof BalanceDirection[keyof typeof BalanceDirection]

// 会计科目
export interface AccountingSubject {
    id: number
    code: string
    name: string
    display_name: string | null
    parent_id: number | null
    level: number
    is_leaf: boolean
    balance_direction: BalanceDirectionType
    is_active: boolean
    full_name: string | null
    account_version_id: number
    children?: AccountingSubject[]
    version?: number
}

export interface AccountingSubjectCreate {
    code: string
    name: string
    display_name?: string
    parent_id?: number | null
    level?: number
    is_leaf?: boolean
    balance_direction?: BalanceDirectionType
    is_active?: boolean
    full_name?: string
    account_version_id: number
}

export interface AccountingSubjectUpdate {
    code?: string
    name?: string
    display_name?: string
    parent_id?: number | null
    level?: number
    is_leaf?: boolean
    balance_direction?: BalanceDirectionType
    is_active?: boolean
    full_name?: string
    account_version_id?: number
}

// API 响应
export interface PageResponse<T> extends ResponseData {
    total: number
    items: T[]
}


// ---------------------------------------------科目版本-----------------------------------------------------
export interface ResponseData {
    code: number;

    message: string;
    ok: boolean
}

// 科目版本
export interface AccountVersion {
    id: number
    version_code: string
    version_name: string
    description: string | null
    is_default: boolean
    is_active: boolean
    effective_date: string | null
    remark: string | null
}

export interface AccountVersionCreate {
    version_code: string
    version_name: string
    description?: string
    is_default?: boolean
    is_active?: boolean
    effective_date?: string
    remark?: string
}

export interface AccountVersionUpdate {
    version_code?: string
    version_name?: string
    description?: string
    is_default?: boolean
    is_active?: boolean
    effective_date?: string
    remark?: string
}


// API 响应
export interface PageResponse<T> extends ResponseData {

    total: number
    items: T[]
}