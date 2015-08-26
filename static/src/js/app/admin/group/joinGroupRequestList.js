require(["jquery", "avalon", "csrfToken", "bsAlert"], function ($, avalon, csrfTokenHeader, bsAlert) {

    // avalon:定义模式 group_list
    avalon.ready(function () {

        if (avalon.vmodels.requestList) {
            var vm = avalon.vmodels.requestList;
        }
        else {

            var vm = avalon.define({
                $id: "requestList",
                //通用变量
                requestList: [],                 //  列表数据项
                previousPage: 0,                 //  之前的页数
                nextPage: 0,                     //   之后的页数
                page: 1,                           //    当前页数
                totalPage: 1,                   //    总页数

                getNext: function () {
                    if (!vm.nextPage)
                        return;
                    getPageData(vm.page + 1);
                },
                getPrevious: function () {
                    if (!vm.previousPage)
                        return;
                    getPageData(vm.page - 1);
                },
                getBtnClass: function (btn) {                                                         //上一页/下一页按钮启用禁用逻辑
                    if (btn == "next") {
                        return vm.nextPage ? "btn btn-primary" : "btn btn-primary disabled";
                    }
                    else {
                        return vm.previousPage ? "btn btn-primary" : "btn btn-primary disabled";
                    }
                },
                getPage: function (page_index) {
                    getPageData(page_index);
                },
                processRequest: function(request, status){
                    $.ajax({
                        beforeSend: csrfTokenHeader,
                        url: "/api/admin/join_group_request/",
                        method: "put",
                        data: {request_id: request.id, status: status},
                        success: function(data){
                            vm.requestList.remove(request);
                            bsAlert(data.data);
                        }
                    })
                }
            });
        }

        avalon.scan();
        getPageData(1);
        //Ajax get数据
        function getPageData(page) {
            var url = "/api/admin/join_group_request/?paging=true&page=" + page + "&page_size=10";
            $.ajax({
                beforeSend: csrfTokenHeader,
                url: url,
                dataType: "json",
                method: "get",
                success: function (data) {
                    if (!data.code) {
                        vm.requestList = data.data.results;
                        vm.totalPage = data.data.total_page;
                        vm.previousPage = data.data.previous_page;
                        vm.nextPage = data.data.next_page;
                        vm.page = page;
                    }
                    else {
                        bsAlert(data.data);
                    }
                }
            });
        }

    });

});