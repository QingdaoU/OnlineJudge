require(["jquery", "avalon", "csrfToken", "bsAlert", "validator"], function ($, avalon, csrfTokenHeader, bsAlert) {


    // avalon:定义模式 userList
    avalon.ready(function () {

        if (avalon.vmodels.userList) {
            var vm = avalon.vmodels.userList;
            // initialize avalon object
            userList     = []; //previousPage= 0; nextPage= 0;  page         = 1;
            //editingUserId= 0;  totalPage   = 1;  keyword= ""; showAdminOnly= false;
                //user editor fields
            username= "";     realName= "";    email= "";   adminType= 0; id= 0;
        }
        else {
            var vm = avalon.define({
                $id: "userList",
                //通用变量
                userList: [],
                previousPage: 0,
                nextPage: 0,
                page: 1,
                editingUserId: 0,
                totalPage: 1,
                userType: ["一般用户", "管理员", "超级管理员"],
                keyword: "",
                showAdminOnly: false,
                //编辑区域同步变量
                username: "",
                realName: "",
                email: "",
                adminType: 0,
                id: 0,
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
                editUser: function (user) {                                                               //点击编辑按钮的事件,显示/隐藏编辑区
                    vm.username = user.username;
                    vm.realName = user.real_name;
                    vm.adminType = user.admin_type;
                    vm.email = user.email;
                    vm.id = user.id;
                    if (vm.editingUserId == user.id)
                        vm.editingUserId = 0;
                    else
                        vm.editingUserId = user.id;
                },
                search: function () {
                    getPageData(1);
                }
            });
        }
        vm.$watch("showAdminOnly", function () {
            getPageData(1);
        });
        avalon.scan();
        getPageData(1);   //用户列表初始化
        //Ajax get数据
        function getPageData(page) {
            var url = "/api/admin/user/?paging=true&page=" + page + "&page_size=10";
            if (vm.showAdminOnly == true)
                url += "&admin_type=1";
            if (vm.keyword != "")
                url += "&keyword=" + vm.keyword;
            $.ajax({
                beforeSend: csrfTokenHeader,
                url: url,
                dataType: "json",
                method: "get",
                success: function (data) {
                    if (!data.code) {
                        vm.userList = data.data.results;
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

        $("#edit_user-form").validator()
            .on('submit', function (e) {
                if (!e.isDefaultPrevented()) {
                    var data = {
                        username: vm.username,
                        real_name: vm.realName,
                        email: vm.email,
                        id: vm.id,
                        admin_type: vm.adminType
                    };
                    if ($("#password").val() !== "")
                        data.password = $("#password").val();
                    $.ajax({
                        beforeSend: csrfTokenHeader,
                        url: "/api/admin/user/",
                        data: data,
                        dataType: "json",
                        method: "put",
                        success: function (data) {
                            if (!data.code) {
                                bsAlert("编辑成功！");
                                getPageData(1);
                                $("#password").val("");
                            } else {
                                bsAlert(data.data);
                            }
                        }
                    });
                    return false;
                }
            });
    });

})