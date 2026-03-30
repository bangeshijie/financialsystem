//数据类型定义
export interface ResponseData {
  code: number
  message: string
  ok: boolean
}
//菜单数据与按钮数据的ts类型
export interface Permisstion {
  menu_id?: number
  createTime?: string
  updateTime?: string
  pid: number
  name: string
  code: null
  toCode: null
  type: number
  status: null
  level: number
  children?: Permisstion[]
  selected: boolean
}

//菜单接口返回的数据类型
export interface PermisstionResponseData extends ResponseData {
  data: Permisstion[]
}

//添加与修改菜单携带的参数的ts类型
export interface MenuParams {
  menu_id?: number //ID
  pid: number //上级菜单的ID
  name: string //菜单的名字
  code: string //权限数值
  to_code: string
  type: number
  status: string | null

  level: number //几级菜单
  selected?: false


}
