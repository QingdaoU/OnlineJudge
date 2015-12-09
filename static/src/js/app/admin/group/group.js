require(["jquery", "avalon", "csrfToken", "bsAlert", "validator"], function ($, avalon, csrfTokenHeader, bsAlert) {

    avalon.ready(function () {
        $('#add-group-form').validator().on('submit', function (e) {
        if (!e.isDefaultPrevented()) {
            var name = vm.name;
            var description = vm.description;
            var join_group_setting = vm.group_type;
            $.ajax({
                beforeSend: csrfTokenHeader,
                url: "/api/admin/group/",
                method: "post",
                data: {name: name, description: description, join_group_setting: join_group_setting},
                dataType: "json",
                success: function (data) {
                    if (!data.code) {
                        getPageData(1);
                        bsAlert("添加成功");
                    }
                    else {
                        bsAlert(data.data);
                    }
                }
            });
            return false;
        }
        })
        if (avalon.vmodels.group) {
            var vm = avalon.vmodels.group;
        }
        else {

            var vm = avalon.define({
                $id: "group",
                //通用变量
                groupList: [],                 //  用户列表数据项
                previousPage: 0,                 //  之前的页数
                nextPage: 0,                     //   之后的页数
                page: 1,                           //    当前页数
                totalPage: 1,                   //    总页数
                keyword: "",
                name: "",
                description: "",
                group_type: 0,
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
                getBtnClass: function (btnType) {
                    if (btnType == "next") {
                        return vm.nextPage ? "btn btn-primary" : "btn btn-primary disabled";
                    }
                    else {
                        return vm.previousPage ? "btn btn-primary" : "btn btn-primary disabled";
                    }

                },
                search: function(){
                    getPageData(1);
                },
                getGroupSettingString: function (setting) {
                    return {0: "允许任何人加入", 1: "提交请求后管理员审核", 2: "不允许任何人加入"}[setting]
                },
  
                showGroupDetailPage: function (groupId) {
                    avalon.vmodels.admin.groupId = groupId;
                    avalon.vmodels.admin.template_url = "template/group/group_detail.html";
                }
            });
        }

        getPageData(1);

        function getPageData(page) {
            var url = "/api/admin/group/?paging=true&page=" + page + "&page_size=10";
            if (vm.keyword)
                url += "&keyword=" + vm.keyword;
            $.ajax({
                url: url,
                dataType: "json",
                method: "get",
                success: function (data) {
                    if (!data.code) {
                        vm.groupList = data.data.results;
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

    avalon.scan();

});
