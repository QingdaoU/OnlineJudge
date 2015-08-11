require(["jquery", "avalon", "csrf", "bs_alert", "validation"], function ($, avalon, csrfHeader, bs_alert) {
    avalon.vmodels.request_list = null;

    // avalon:定义模式 group_list
    avalon.ready(function () {
        var vm = avalon.define({
            $id: "request_list",
            //通用变量
            request_list: [],                 //  列表数据项
            previous_page: 0,                 //  之前的页数
            next_page: 0,                     //   之后的页数
            page: 1,                           //    当前页数
            page_count: 1,                   //    总页数

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
            processRequest: function(request_id, status){
                $.ajax({
                    beforeSend: csrfHeader,
                    url: "/api/admin/join_group_request/",
                    method: "put",
                    data: {request_id: request_id, status: status},
                    success: function(data){
                        bs_alert(data.data);
                    }
                })
            }
        });

        avalon.scan();
        getPageData(1);
        //Ajax get数据
        function getPageData(page) {
            var url = "/api/admin/join_group_request/?paging=true&page=" + page + "&page_size=10";
            $.ajax({
                beforeSend: csrfHeader,
                url: url,
                dataType: "json",
                method: "get",
                success: function (data) {
                    if (!data.code) {
                        vm.request_list = data.data.results;
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

        /*$("#edit_user-form")
            .formValidation({
                framework: "bootstrap",
                fields: {
                    username: {
                        validators: {
                            notEmpty: {
                                message: "请填写用户名"
                            },
                            stringLength: {
                                min: 3,
                                max: 30,
                                message: '用户名长度必须在3到30位之间'
                            }
                        }
                    },
                    real_name: {
                        validators: {
                            notEmpty: {
                                message: "请填写真实姓名"
                            }
                        }
                    },
                    email: {
                        validators: {
                            notEmpty: {
                                message: "请填写电子邮箱邮箱地址"
                            },
                            emailAddress: {
                                message: "请填写有效的邮箱地址"
                            }
                        }
                    },
                    password: {
                        validators: {
                            stringLength: {
                                min: 6,
                                max: 30,
                                message: '密码长度必须在6到30位之间'
                            }
                        }
                    }
                }
            }
        ).on('success.form.fv', function (e) {
                e.preventDefault();
                var data = {
                    username: vm.username,
                    real_name: vm.real_name,
                    email: vm.email,
                    id: vm.id,
                    admin_type: vm.admin_type
                };
                if ($("#password").val() !== "")
                    data.password = $("#password").val();
                $.ajax({
                    beforeSend: csrfHeader,
                    url: "/api/admin/user/",
                    data: data,
                    dataType: "json",
                    method: "put",
                    success: function (data) {
                        if (!data.code) {
                            bs_alert("提交成功！");
                            getPageData(1);
                            $("#password").val("");
                        } else {
                            bs_alert(data.data);
                        }
                    }
                })
            });*/
    });

});