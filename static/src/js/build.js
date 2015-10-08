({
	// RequireJS 通过一个相对的路径 baseUrl来加载所有代码。baseUrl通常被设置成data-main属性指定脚本的同级目录。
	baseUrl: "./js",
	// 第三方脚本模块的别名,jquery比libs/jquery-1.11.1.min.js简洁明了；
    paths: {
        jquery: "empty:",
        avalon: "empty:",
        editor: "utils/editor",
        uploader: "utils/uploader",
        formValidation: "utils/formValidation",
        codeMirror: "utils/codeMirror",
        bsAlert: "utils/bsAlert",
        problem: "app/oj/problem/problem",
        contest: "app/admin/contest/contest",
        csrfToken: "utils/csrfToken",
        admin: "app/admin/admin",
        chart: "lib/chart/Chart",
        tagEditor: "lib/tagEditor/jquery.tag-editor.min",
        jqueryUI: "lib/jqueryUI/jquery-ui",
        bootstrap: "lib/bootstrap/bootstrap",
        datetimePicker: "lib/datetime_picker/bootstrap-datetimepicker",
        validator: "lib/validator/validator",
        ZeroClipboard: "lib/ZeroClipboard/ZeroClipboard",

        // ------ 下面写的都不要直接用，而是使用上面的封装版本 ------
        //富文本编辑器simditor -> editor
        simditor: "lib/simditor/simditor",
        "simple-module": "lib/simditor/module",
        "simple-hotkeys": "lib/simditor/hotkeys",
        "simple-uploader": "lib/simditor/uploader",

        //code mirror 代码编辑器 ->codeMirror
        _codeMirror: "lib/codeMirror/codemirror",
        codeMirrorClang: "lib/codeMirror/language/clike",

        // bootstrap组件
        modal: "lib/bootstrap/modal",
        dropdown: "lib/bootstrap/dropdown",
        transition: "lib/bootstrap/transition",
        collapse: "lib/bootstrap/collapse",

        //百度webuploader -> uploader
        webUploader: "lib/webuploader/webuploader",

        //"_datetimePicker": "lib/datetime_picker/bootstrap-datetimepicker",

        //以下都是页面 script 标签引用的js
        addProblem_0_pack: "app/admin/problem/addProblem",
        addContest_1_pack: "app/admin/contest/addContest",
        problem_2_pack: "app/admin/problem/problem",
        register_3_pack: "app/oj/account/register",
        contestList_4_pack: "app/admin/contest/contestList",
        group_5_pack: "app/oj/group/group",
        editProblem_6_pack: "app/admin/problem/editProblem",
        announcement_7_pack: "app/admin/announcement/announcement",
        monitor_8_pack: "app/admin/monitor/monitor",
        groupDetail_9_pack: "app/admin/group/groupDetail",
        admin_10_pack: "app/admin/admin",
        problem_11_pack: "app/oj/problem/problem",
        submissionList_12_pack: "app/admin/problem/submissionList",
        editProblem_13_pack: "app/admin/contest/editProblem",
        joinGroupRequestList_14_pack: "app/admin/group/joinGroupRequestList",
        changePassword_15_pack: "app/oj/account/changePassword",
        group_16_pack: "app/admin/group/group",
        submissionList_17_pack: "app/admin/contest/submissionList",
        login_18_pack: "app/oj/account/login",
        contestPassword_19_pack: "app/oj/contest/contestPassword",
        userList_20_pack: "app/admin/user/userList"
    },
    findNestedDependencies: true,
    appDir: "../",
    dir: "../../release/",
    modules: [
        {
            name: "bootstrap",
        },
        {
            name: "addProblem_0_pack"
        },
        {
            name: "addContest_1_pack"
        },
        {
            name: "problem_2_pack"
        },
        {
            name: "register_3_pack"
        },
        {
            name: "contestList_4_pack"
        },
        {
            name: "group_5_pack"
        },
        {
            name: "editProblem_6_pack"
        },
        {
            name: "announcement_7_pack"
        },
        {
            name: "monitor_8_pack"
        },
        {
            name: "groupDetail_9_pack"
        },
        {
            name: "admin_10_pack"
        },
        {
            name: "problem_11_pack"
        },
        {
            name: "submissionList_12_pack"
        },
        {
            name: "editProblem_13_pack"
        },
        {
            name: "joinGroupRequestList_14_pack"
        },
        {
            name: "changePassword_15_pack"
        },
        {
            name: "group_16_pack"
        },
        {
            name: "submissionList_17_pack"
        },
        {
            name: "login_18_pack"
        },
        {
            name: "contestPassword_19_pack"
        },
        {
            name: "userList_20_pack"
        }
    ],
    optimizeCss: "standard",
})