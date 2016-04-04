define("spj", ["avalon"], function (avalon) {
    avalon.component("ms:spj", {
        $template: '<div class="col-md-6">'+
                    '<label>Special Judge</label>'+
                    '<div class="form-group">'+
                    '<label class="text"><input type="checkbox" ms-duplex-checked="spj">'+
                    '<small> Special Judge用于答案不唯一的情况,需要自己上传判题代码。'+
                    '<a href="#" target="_blank">帮助和示例</a></small>'+
                    '</label></div></div>'+
                    '<div class="col-md-6" ms-if="spj">'+
                    '<label>SPJ代码语言</label>'+
                    '<div class="form-group">'+
                    '<label class="text">'+
                    '<input type="radio" name="spjLanguage" value="1" ms-duplex-string="spjLanguage"> C '+
                    '<input type="radio" name="spjLanguage" value="2" ms-duplex-string="spjLanguage"> C++'+
                    '</label>'+
                    '</div>'+
                    '</div>'+
                    '<div class="col-md-12" ms-if="spj">'+
                    '<label>SPJ代码</label>'+
                    '<textarea class="form-control" rows="5" ms-duplex="spjCode"></textarea>'+
                    '</div>',
        spj: false,
        spjLanguage: 1,
        spjCode: "",
        $ready: function (vm, el) {
            el.msRetain = true;
        }
    })
});
