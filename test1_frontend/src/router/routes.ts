
//1对外暴漏配置路由  常量路由!!!
export const constantRoutes = [
    {
        path: '/login',
        component: () => import('@/views/login/index.vue'),
        name: 'login',
        meta: {
            title: '登录',
            hidden: true,
            icon: 'Promotion',

        },
    },



    {
        // 登录成功后展示数据的路由
        path: '/',
        component: () => import('@/layout/index.vue'),
        name: 'layout',
        meta: {
            title: '',
            hidden: false,
            icon: ''


        },
        redirect: '/home',
        children: [{
            path: '/home',
            component: () => import('@/views/home/index.vue'),
            meta: {
                title: '首页',
                hidden: false,
                icon: 'Avatar',


            },

        },

        ]
    },
    {
        path: '/screen',
        component: () => import('@/views/screen/index.vue'),
        name: 'Screen',
        meta: {
            title: '数据大屏',
            hidden: false,
            icon: 'TrendCharts'

        }
    },

    // {
    //     path: '/about',
    //     component: () => import('@/views/about/index.vue'),
    //     name: 'About',
    //     meta: {
    //         title: '关于我们',
    //         hidden: false,
    //         icon: 'Reading',

    //     },
    // },


    {
        path: '/about',
        component: () => import('@/layout/index.vue'),
        name: 'About',
        redirect: '/about/project',
        meta: {
            title: '关于',
            hidden: false,
            icon: 'Reading',


        },
        children: [
            {
                path: '/about/project',
                component: () => import('@/views/about/index.vue'),
                name: 'AboutProject',
                meta: {
                    title: '关于项目',
                    hidden: false,
                    icon: 'Memo',
                }

            },
        ],
    },



    {
        path: '/404',
        component: () => import('@/views/404/index.vue'),
        name: '404',
        meta: {
            title: '丢失界面',
            hidden: true,
            icon: 'Platform'

        }
    },





]

// 2异步路由
export const asyncRoutes = [

    {
        path: '/acl',
        component: () => import('@/layout/index.vue'),
        name: 'Acl',
        redirect: '/acl/user',
        meta: {
            title: '权限管理',
            hidden: false,
            icon: 'Lock',


        },
        children: [
            {
                path: '/acl/user',
                component: () => import('@/views/acl/user/index.vue'),
                name: 'User',
                meta: {
                    title: '用户管理',
                    hidden: false,
                    icon: 'User',
                }

            },

            {
                path: '/acl/role',
                component: () => import('@/views/acl/role/index.vue'),
                name: 'Role',
                meta: {
                    title: '角色管理',
                    hidden: false,
                    icon: 'UserFilled',
                }

            },
            {
                path: '/acl/permission',
                component: () => import('@/views/acl/permission/index.vue'),
                name: 'Permission',
                meta: {
                    title: '菜单管理',
                    hidden: false,
                    icon: 'Monitor',
                }

            }
        ],
    },








    {

        path: '/dimensions',
        component: () => import('@/layout/index.vue'),
        name: 'Dimensions',
        redirect: '/dimensions/date',
        meta: {
            title: '主数据管理',
            hidden: false,
            icon: 'Goods',
        },
        children: [{
            path: '/dimensions/date',
            component: () => import('@/views/dimensions/dim_date/index.vue'),
            name: 'Date',
            meta: {
                title: '日期管理',
                hidden: false,
                icon: 'ShoppingCartFull',
            },



        },
        {
            path: '/dimensions/account',
            component: () => import('@/views/dimensions/dim_account/index.vue'),
            name: 'Account',
            meta: {
                title: '科目管理',
                hidden: false,
                icon: 'ChromeFilled',
            },



        },
        {
            path: '/dimensions/bp',
            component: () => import('@/views/dimensions/dim_bp/index.vue'),
            name: 'BP',
            meta: {
                title: '客商管理',
                hidden: false,
                icon: 'Calendar',
            },



        },
        {
            path: '/dimensions/entity',
            component: () => import('@/views/dimensions/dim_entity/index.vue'),
            name: 'Entity',
            meta: {
                title: '组织管理',
                hidden: false,
                icon: 'Calendar',
            },



        },
        {
            path: '/dimensions/product',
            component: () => import('@/views/dimensions/dim_product/index.vue'),
            name: 'Product',
            meta: {
                title: '产品管理',
                hidden: false,
                icon: 'Calendar',
            },



        },
        {
            path: '/dimensions/category',
            component: () => import('@/views/dimensions/dim_category/index.vue'),
            name: 'Category',
            meta: {
                title: '版本管理',
                hidden: false,
                icon: 'GobletFull',
            },



        }],
    },
    {

        path: '/reports',
        component: () => import('@/layout/index.vue'),
        name: 'Reports',
        redirect: '/reports/income',
        meta: {
            title: '报表管理',
            hidden: false,
            icon: 'Postcard',
        },
        children: [{
            path: '/reports/income',
            component: () => import('@/views/reports/income/index.vue'),
            name: 'Income',
            meta: {
                title: '利润表',
                hidden: false,
                icon: 'Coin',
            },
        },
        {
            path: '/reports/balance',
            component: () => import('@/views/reports/balance/index.vue'),
            name: 'Balance',
            meta: {
                title: '资产负债表',
                hidden: false,
                icon: 'Magnet',
            },



        },
        {
            path: '/reports/cashflow',
            component: () => import('@/views/reports/cashflow/index.vue'),
            name: 'Cashflow',
            meta: {
                title: '现金流表',
                hidden: false,
                icon: 'Money',
            },
        },
        ]
    },



]


// 3任意路由
export const anyRoutes = [
    {
        path: '/:pathMatch(.*)*',
        redirect: '/404',
        name: 'any',
        meta: {
            title: '其他跳转',
            hidden: true,

        }
    },
]
