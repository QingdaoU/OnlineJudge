var require = {
    urlArgs: "v=2.1",
    // RequireJS 通过一个相对的路径 baseUrl来加载所有代码。baseUrl通常被设置成data-main属性指定脚本的同级目录。
    baseUrl: "/static/js/",
    paths: {
        jquery: "lib/jquery/jquery",
        jcountdown: "lib/jcountdown/jcountdown",
        avalon: "lib/avalon/avalon",
        //avalon15: "lib/avalon/avalon15",
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

        // ------ admin web 组件 ----------
        pager: "components/pager",
        editorComponent: "components/editorComponent",
        testCaseUploader: "components/testCaseUploader",
        spj: "components/spj",


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

        // "_datetimePicker": "lib/datetime_picker/bootstrap-datetimepicker",

        //以下都是页面 script 标签引用的js
        //以下都是页面 script 标签引用的js
        announcement_0_pack: "app/admin/announcement/announcement",
        userList_1_pack: "app/admin/user/userList",
        twoFactorAuth_2_pack: "app/oj/account/twoFactorAuth",
        problem_3_pack: "app/oj/problem/problem",
        submissionList_4_pack: "app/admin/problem/submissionList",
        contestCountdown_5_pack: "app/oj/contest/contestCountdown",
        avatar_6_pack: "app/oj/account/avatar",
        addProblem_7_pack: "app/admin/problem/addProblem",
        problem_8_pack: "app/admin/problem/problem",
        contestList_9_pack: "app/admin/contest/contestList",
        admin_10_pack: "app/admin/admin",
        login_11_pack: "app/oj/account/login",
        applyResetPassword_12_pack: "app/oj/account/applyResetPassword",
        addContest_13_pack: "app/admin/contest/addContest",
        contestPassword_14_pack: "app/oj/contest/contestPassword",
        changePassword_15_pack: "app/oj/account/changePassword",
        judges_16_pack: "app/admin/judges/judges",
        editProblem_17_pack: "app/admin/contest/editProblem",
        joinGroupRequestList_18_pack: "app/admin/group/joinGroupRequestList",
        group_19_pack: "app/oj/group/group",
        contestProblemList_20_pack: "app/admin/contest/contestProblemList",
        editProblem_21_pack: "app/admin/problem/editProblem",
        register_22_pack: "app/oj/account/register",
        groupDetail_23_pack: "app/admin/group/groupDetail",
        editContest_24_pack: "app/admin/contest/editContest",
        resetPassword_25_pack: "app/oj/account/resetPassword",
        group_26_pack: "app/admin/group/group",
        settings_27_pack: "app/oj/account/settings"
    },
    shim: {
            avalon: {
                exports: "avalon"
            }
    }
};