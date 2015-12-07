({
	// RequireJS 通过一个相对的路径 baseUrl来加载所有代码。baseUrl通常被设置成data-main属性指定脚本的同级目录。
	baseUrl: "./js",
	// 第三方脚本模块的别名,jquery比libs/jquery-1.11.1.min.js简洁明了；
    paths: {
        jquery: "empty:",
        avalon: "empty:",
        editor: "utils/editor",
        jcountdown: "lib/jcountdown/jcountdown",
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

        // ------ admin web 组件 ----------
        pager: "components/pager",
        editorComponent: "components/editorComponent",
        testCaseUploader: "components/testCaseUploader",

        // ------ 下面写的都不要直接用，而是使用上面的封装版本 ------
        //富文本编辑器simditor -> editor
        simditor: "lib/simditor/simditor",
        "simple-module": "lib/simditor/module",
        "simple-hotkeys": "lib/simditor/hotkeys",
        "simple-uploader": "lib/simditor/uploader",
        "simditor-autosave": "lib/simditor/simditor-autosave",

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
        announcement_0_pack: "app/admin/announcement/announcement",
        userList_1_pack: "app/admin/user/userList",
        problem_2_pack: "app/oj/problem/problem",
        submissionList_3_pack: "app/admin/problem/submissionList",
        contestCountdown_4_pack: "app/oj/contest/contestCountdown",
        avatar_5_pack: "app/oj/account/avatar",
        addProblem_6_pack: "app/admin/problem/addProblem",
        problem_7_pack: "app/admin/problem/problem",
        contestList_8_pack: "app/admin/contest/contestList",
        admin_9_pack: "app/admin/admin",
        login_10_pack: "app/oj/account/login",
        applyResetPassword_11_pack: "app/oj/account/applyResetPassword",
        addContest_12_pack: "app/admin/contest/addContest",
        contestPassword_13_pack: "app/oj/contest/contestPassword",
        changePassword_14_pack: "app/oj/account/changePassword",
        monitor_15_pack: "app/admin/monitor/monitor",
        editProblem_16_pack: "app/admin/contest/editProblem",
        joinGroupRequestList_17_pack: "app/admin/group/joinGroupRequestList",
        group_18_pack: "app/oj/group/group",
        contestProblemList_19_pack: "app/admin/contest/contestProblemList",
        editProblem_20_pack: "app/admin/problem/editProblem",
        register_21_pack: "app/oj/account/register",
        groupDetail_22_pack: "app/admin/group/groupDetail",
        editContest_23_pack: "app/admin/contest/editContest",
        resetPassword_24_pack: "app/oj/account/resetPassword",
        group_25_pack: "app/admin/group/group",
        settings_26_pack: "app/oj/account/settings"
    },
    shim: {
            avalon: {
                exports: "avalon"
            }
    },
    findNestedDependencies: true,
    appDir: "../",
    dir: "../../release/",
    modules: [
        {
            name: "announcement_0_pack"
        },
        {
            name: "userList_1_pack"
        },
        {
            name: "problem_2_pack"
        },
        {
            name: "submissionList_3_pack"
        },
        {
            name: "contestCountdown_4_pack"
        },
        {
            name: "avatar_5_pack"
        },
        {
            name: "addProblem_6_pack"
        },
        {
            name: "problem_7_pack"
        },
        {
            name: "contestList_8_pack"
        },
        {
            name: "admin_9_pack"
        },
        {
            name: "login_10_pack"
        },
        {
            name: "applyResetPassword_11_pack"
        },
        {
            name: "addContest_12_pack"
        },
        {
            name: "contestPassword_13_pack"
        },
        {
            name: "changePassword_14_pack"
        },
        {
            name: "monitor_15_pack"
        },
        {
            name: "editProblem_16_pack"
        },
        {
            name: "joinGroupRequestList_17_pack"
        },
        {
            name: "group_18_pack"
        },
        {
            name: "contestProblemList_19_pack"
        },
        {
            name: "editProblem_20_pack"
        },
        {
            name: "register_21_pack"
        },
        {
            name: "groupDetail_22_pack"
        },
        {
            name: "editContest_23_pack"
        },
        {
            name: "resetPassword_24_pack"
        },
        {
            name: "group_25_pack"
        },
        {
            name: "settings_26_pack"
        }
    ],
    optimizeCss: "standard",
})