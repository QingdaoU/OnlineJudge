define("pager", ["avalon"], function (avalon) {
    var _interface = function () {
    };
    avalon.component("ms:pager", {
        $template: "页数: {{ currentPage }}/{{ totalPage }} " +
        "<button ms-class=\"{{ currentPage==1?'btn btn-primary disabled':'btn btn-primary' }}\" ms-click=\"_getPrevPage\">上一页</button> " +
        " <button ms-class=\"{{ currentPage==totalPage?'btn btn-primary disabled':'btn btn-primary' }}\" ms-click=\"_getNextPage\">下一页</button>",
        currentPage: 1,
        totalPage: 1,
        _getPrevPage: _interface,
        _getNextPage: _interface,
        $init: function (vm, el) {
            vm._getPrevPage = function () {
                if (vm.currentPage > 1) {
                    vm.currentPage--;
                    vm.getPage(vm.currentPage);
                }
            };
            vm._getNextPage = function () {
                if (vm.currentPage < vm.totalPage) {
                    vm.currentPage++;
                    vm.getPage(vm.currentPage);
                }
            };
        },
        $ready: function(vm, el){
            el.msRetain = true;
            vm.getPage(1);

        }
    })
});