require.config({
    // RequireJS 通过一个相对的路径 baseUrl来加载所有代码。baseUrl通常被设置成data-main属性指定脚本的同级目录。
    baseUrl: "/static/js/lib/",
    paths: {
        //百度webuploader
        webuploader: "webuploader/webuploader",

        jquery: "jquery/jquery",
        avalon: "avalon/avalon",
        editor: "../utils/editor",
        uploader: "../utils/uploader",
        validation: "../utils/validation",
        code_mirror: "../utils/code_mirror",
        login: "../app/account/login",
        oj: "../app/oj",

        //formValidation 不要在代码中单独使用，而是使用和修改utils/validation
        base: "formValidation/base",
        helper: "formValidation/helper",
        "language/zh_CN": "formValidation/language/zh_CN",
        "framework/bootstrap": "formValidation/framework/bootstrap",
        "validator/notEmpty": "formValidation/validator/notEmpty",
        "validator/stringLength": "formValidation/validator/stringLength",
        "validator/date": "formValidation/validator/date",
        "validator/integer": "formValidation/validator/integer",
        "validator/between": "formValidation/validator/between",

        //富文本编辑器 不要直接使用，而是使用上面的editor
        simditor: "simditor/simditor",
        "simple-module": "simditor/module",
        "simple-hotkeys": "simditor/hotkeys",
        "simple-uploader": "simditor/uploader",

        //code mirroe 代码编辑器
        _code_mirror: "codeMirror/codemirror",
        code_mirror_clang: "codeMirror/language/clike"

    }
});