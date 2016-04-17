define("spj", ["avalon", "bsAlert"], function (avalon, bsAlert) {
    avalon.component("ms:spj", {
        $template: '<div class="col-md-6">' +
        '<label>Special Judge</label>' +
        '<div class="form-group">' +
        '<label class="text"><input type="checkbox" ms-duplex-checked="spj" ms-attr-disabled="checkboxDisabled">' +
        '<small> Special Judge用于答案不唯一的情况,需要自己上传判题代码。上传测试用后如需要修改, 必须重新上传对应类型的新测试用例。' +
        '<a href="https://github.com/QingdaoU/OnlineJudge/wiki/SpecialJudge" target="_blank">帮助和示例</a></small>' +
        '</label></div></div>' +
        '<div class="col-md-6" ms-if="spj">' +
        '<label>SPJ代码语言</label>' +
        '<div class="form-group">' +
        '<label class="text">' +
        '<input type="radio" name="spjLanguage" value="1" ms-duplex-string="spjLanguage"> C ' +
        '<input type="radio" name="spjLanguage" value="2" ms-duplex-string="spjLanguage"> C++' +
        '</label>' +
        '</div>' +
        '</div>' +
        '<div class="col-md-12" ms-if="spj">' +
        '<label>SPJ代码</label>' +
        '<textarea class="form-control" rows="5" ms-duplex="spjCode"></textarea>' +
        '</div>',
        spj: false,
        spjLanguage: 1,
        spjCode: "",
        checkboxDisabled: false,
        $init: function(vm, el) {
            vm.$watch("testCaseUploadFinished", function (spj) {
                vm.spj = spj;
                vm.checkboxDisabled = true;
            });
        },
        $ready: function (vm, el) {
            el.msRetain = true;

        }
    })
});
