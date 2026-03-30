export interface ResponseData {
  code: number
  message: string
  ok: boolean
}
//职位数据类型
export interface RoleItem {
  role_id?: number;
  role_name: string;
  remark: string | null;
  created_time: string;
  updated_time: string;
}

//全部职位的数组的ts类型

//全部职位数据的相应的ts类型
export interface RoleListResponse extends ResponseData {
  data:
  {
    items: RoleItem[];
    total: number;
    page: number;
    limit: number;
  }
}



export interface RoleData {
  role_id?: number
  role_name: string
  remark: string | null

}



//菜单与按钮数据的ts类型
export interface MenuData {
  menu_id?: number
  pid: number
  name: string
  code: string
  toCode: string
  type: number
  status: string
  level: number
  children?: MenuList
  selected: boolean
}
export type MenuList = MenuData[]

//菜单权限与按钮权限数据的ts类型
export interface MenuResponseData extends ResponseData {
  data: MenuList
}
