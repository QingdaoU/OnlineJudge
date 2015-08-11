require(["jquery", "avalon", "csrf", "bs_alert", "validation"], function ($, avalon, csrfHeader, bs_alert) {
    avalon.vmodels.group = null;

    // avalon:定义模式 group_list
    avalon.ready(function () {
        var vm = avalon.define({
            $id: "group",
            //通用变量
            group_list: [],                 //  用户列表数据项
            previous_page: 0,                 //  之前的页数
            next_page: 0,                     //   之后的页数
            page: 1,                           //    当前页数
            page_count: 1,                   //    总页数
            keyword: "",

            getNext: function () {
                if (!vm.next_page)
                    return;
                getPageData(vm.page + 1);
            },
            getPrevious: function () {
                if (!vm.previous_page)
                    return;
                getPageData(vm.page - 1);
            },
            getBtnClass: function (btn) {                                                         //上一页/下一页按钮启用禁用逻辑
                if (btn) {
                    return vm.next_page ? "btn btn-primary" : "btn btn-primary disabled";
                }
                else {
                    return vm.previous_page ? "btn btn-primary" : "btn btn-primary disabled";
                }
            },
            getPage: function (page_index) {
                getPageData(page_index);
            },
            getGroupSettingString: function(setting){
                return {0: "允许任何人加入", 1: "提交请求后管理员审核", 2: "不允许任何人加入"}[setting]
            },
            showGroupDetailPage: function(group_id){
                vm.$fire("up!showGroupDetailPage", group_id);
            }
        });

        avalon.scan();
        getPageData(1);   //用户列表初始化
        //Ajax get数据
        function getPageData(page) {
            var url = "/api/admin/group/?paging=true&page=" + page + "&page_size=10";
            if (vm.keyword != "")
                url += "&keyword=" + vm.keyword;
            $.ajax({
                beforeSend: csrfHeader,
                url: url,
                dataType: "json",
                method: "get",
                success: function (data) {
                    if (!data.code) {
                        vm.group_list = data.data.results;
                        vm.page_count = data.data.total_page;
                        vm.previous_page = data.data.previous_page;
                        vm.next_page = data.data.next_page;
                        vm.page = page;
                    }
                    else {
                        bs_alert(data.data);
                    }
                }
            });
        }
    });

});