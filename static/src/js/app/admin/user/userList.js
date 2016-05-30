require(["jquery", "avalon", "csrfToken", "bsAlert", "pager", "validator"],
    function ($, avalon, csrfTokenHeader, bsAlert) {
        avalon.ready(function () {
            if (avalon.vmodels.userList) {
                var vm = avalon.vmodels.userList;
            }
            else {
                var vm = avalon.define({
                    $id: "userList",

                    userList: [],
                    userType: ["一般用户", "管理员", "超级管理员"],

                    keyword: "",
                    showAdminOnly: false,
                    isEditing: false,

                    username: "",
                    realName: "",
                    email: "",
                    adminType: 0,
                    userId: -1,
                    openAPI: false,
                    tfa_auth: false,
                    is_forbidden: false,
                    password: "",

                    pager: {
                        getPage: function (page) {
                            getPage(page);
                        }
                    },
                    editUser: function (user) {
                        vm.username = user.username;
                        vm.realName = user.real_name;
                        vm.adminType = user.admin_type;
                        vm.email = user.email;
                        vm.userId = user.id;
                        vm.tfa_auth = user.two_factor_auth;
                        vm.openAPI = user.openapi_appkey ? true: false;
                        vm.is_forbidden = user.is_forbidden ? true: false;

                        vm.isEditing = true;
                    },
                    search: function () {
                        getPage(1);
                        avalon.vmodels.userPager.currentPage = 1;
                    }
                });
            }

            vm.$watch("showAdminOnly", function () {
                getPage(1);
                avalon.vmodels.userPager.currentPage = 1;
            });

            function getPage(page) {
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
                            avalon.vmodels.userPager.totalPage = data.data.total_page;
                        }
                        else {
                            bsAlert(data.data);
                        }
                    }
                });
            }

            $("#edit-user-form").validator()
                .on('submit', function (e) {
                    if (!e.isDefaultPrevented()) {
                        var data = {
                            username: vm.username,
                            real_name: vm.realName,
                            email: vm.email,
                            id: vm.userId,
                            admin_type: vm.adminType,
                            openapi: vm.openAPI,
                            tfa_auth: vm.tfa_auth,
                            is_forbidden : vm.is_forbidden
                        };
                        if (vm.password != "")
                            data.password = vm.password;
                        $.ajax({
                            url: "/api/admin/user/",
                            data: data,
                            dataType: "json",
                            method: "put",
                            success: function (data) {
                                if (!data.code) {
                                    bsAlert("编辑成功！");
                                    getPage(avalon.vmodels.userPager.currentPage);
                                    vm.password = "";
                                    vm.isEditing = false;
                                } else {
                                    bsAlert(data.data);
                                }
                            }
                        });
                        return false;
                    }
                });
        });
        avalon.scan();

    });
