// 统一布局配置文件
const LayoutConfig = {
    // 前台菜单配置
    frontMenu: [
        {
            index: '6',
            title: '知识库',
            path: '/front/knowledge.html',
            icon: 'el-icon-document'
        } ,
        {
            index: '4',
            title: '试卷列表',
            path: '/front/paper.html',
            icon: 'el-icon-document-copy'
        },
        {
            index: '5',
            title: '我的考试记录',
            path: '/front/exam_record.html',
            icon: 'el-icon-tickets'
        }
    ],
    
    // 后台菜单配置（按角色划分）
    backendMenu: {
        // 管理员菜单
        admin: [
            {
                index: 'dashboard',
                title: '仪表盘',
                path: '/admin/index.html',
                icon: 'el-icon-s-home'
            },
            {
                index: 'doctors',
                title: '教师管理',
                path: '/admin/users.html?role=doctor',
                icon: 'el-icon-user-solid'
            },
            {
                index: 'patients',
                title: '学生管理',
                path: '/admin/users.html?role=user',
                icon: 'el-icon-user'
            },
            // {
            //     index: 'users',
            //     title: '用户管理',
            //     path: '/admin/users.html',
            //     icon: 'el-icon-user'
            // }, 
            {
                index: 'knowledge',
                title: '知识库管理',
                path: '/admin/knowledge.html',
                icon: 'el-icon-document'
            },
            // {
            //     index: 'question',
            //     title: '题库管理',
            //     path: '/admin/question.html',
            //     icon: 'el-icon-edit-outline'
            // },
            // {
            //     index: 'paper',
            //     title: '试卷管理',
            //     path: '/admin/paper.html',
            //     icon: 'el-icon-document-copy'
            // },
            // {
            //     index: 'exam_record',
            //     title: '考试记录',
            //     path: '/admin/exam_record.html',
            //     icon: 'el-icon-tickets'
            // },
            {
                index: 'exam_statistics',
                title: '考试统计',
                path: '/admin/exam_statistics.html',
                icon: 'el-icon-data-analysis'
            } 
        ],
        // 教师菜单
        doctor: [  
            {
                index: 'question',
                title: '题库管理',
                path: '/admin/question.html',
                icon: 'el-icon-edit-outline'
            },
            {
                index: 'paper',
                title: '试卷管理',
                path: '/admin/paper.html',
                icon: 'el-icon-document-copy'
            },
            {
                index: 'exam_record',
                title: '考试记录',
                path: '/admin/exam_record.html',
                icon: 'el-icon-tickets'
            },
            {
                index: 'exam_statistics',
                title: '考试统计',
                path: '/admin/exam_statistics.html',
                icon: 'el-icon-data-analysis'
            },
        ]
    },

    // 为了向后兼容，保留原 adminMenu 引用（默认指向管理员菜单）
    get adminMenu() {
        return this.backendMenu.admin;
    },
    
    // 系统配置
    system: {
        title: '命题辅助系统',
        logo: '/static/image/logo.png',
        defaultAvatar: '/static/image/profile.png'
    } 
};

// 导出配置
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LayoutConfig;
}
