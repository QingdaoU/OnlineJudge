var require = {
    // RequireJS 通过一个相对的路径 baseUrl来加载所有代码。baseUrl通常被设置成data-main属性指定脚本的同级目录。
    baseUrl: "/static/js/",
    paths: {

        jquery: "lib/jquery/jquery",
        avalon: "lib/avalon/avalon",
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
        datetimePicker: "lib/datetime_picker/bootstrap-datetimepicker.zh-CN",
        validator: "lib/validator/validator",


        // ------ 下面写的都不要直接用，而是使用上面的封装版本 ------

        //formValidation -> utils/validation
        base: "lib/formValidation/base",
        helper: "lib/formValidation/helper",
        "language/zh_CN": "lib/formValidation/language/zh_CN",
        "framework/bootstrap": "lib/formValidation/framework/bootstrap",
        "validator/notEmpty": "lib/formValidation/validator/notEmpty",
        "validator/stringLength": "lib/formValidation/validator/stringLength",
        "validator/date": "lib/formValidation/validator/date",
        "validator/integer": "lib/formValidation/validator/integer",
        "validator/between": "lib/formValidation/validator/between",
        "validator/confirm":"lib/formValidation/validator/confirm",
        "validator/remote":"lib/formValidation/validator/remote",
        "validator/emailAddress":"lib/formValidation/validator/emailAddress",

        //富文本编辑器simditor -> editor
        simditor: "lib/simditor/simditor",
        "simple-module": "lib/simditor/module",
        "simple-hotkeys": "lib/simditor/hotkeys",
        "simple-uploader": "lib/simditor/uploader",

        //code mirror 代码编辑器 ->codeMirror
        _codeMirror: "lib/codeMirror/codemirror",
        codeMirrorClang: "lib/codeMirror/language/clike",

        //百度webuploader -> uploader
        webUploader: "lib/webuploader/webuploader",

        "_datetimePicker": "lib/datetime_picker/bootstrap-datetimepicker"
    },
    shim: {
        bootstrap: {deps: ["jquery"]},
        _datetimePicker: {dep: ["jquery"]},
        datetimePicker: {deps: ["_datetimePicker"]},
        validator: ["jquery"]
    }
};