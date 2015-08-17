require(["jquery", "avalon", "csrfToken", "bsAlert", "formValidation"], function ($, avalon, csrfTokenHeader, bsAlert) {


    // avalon:定义模式 group_list
    avalon.ready(function () {
        avalon.vmodels.groupDetail = null;
        var vm = avalon.define({
            $id: "groupDetail",
            //通用变量
            memberList: [],
            previousPage: 0,
            nextPage: 0,
            page: 1,
            totalPage: 1,
            name: "",
            description: "",
            checkedSetting: "0",

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
            getBtnClass: function (btn) {
                if (btn == "next") {
                    return vm.nextPage ? "btn btn-primary" : "btn btn-primary disabled";
                }
                else {
                    return vm.previousPage ? "btn btn-primary" : "btn btn-primary disabled";
                }
            },

            removeMember: function (relation) {
                $.ajax({
                    beforeSend: csrfTokenHeader,
                    url: "/api/admin/group_member/",
                    method: "put",
                    data: JSON.stringify({group_id: relation.group, members: [relation.user.id]}),
                    contentType: "application/json",
                    success: function (data) {
                        vm.memberList.remove(relation);
                        bsAlert(data.data);
                    }
                })
            },
            showGroupListPage: function () {
                vm.$fire("up!showGroupListPage");
            }
        });

        avalon.scan();
        getPageData(1);
        function getPageData(page) {
            var url = "/api/admin/group_member/?paging=true&page=" + page +
                "&page_size=10&group_id=" + avalon.vmodels.admin.groupId;
            $.ajax({
                url: url,
                dataType: "json",
                method: "get",
                success: function (data) {
                    if (!data.code) {
                        vm.memberList = data.data.results;
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

        $.ajax({
            url: "/api/admin/group/?group_id=" + avalon.vmodels.admin.groupId,
            method: "get",
            dataType: "json",
            success: function (data) {
                if (!data.code) {
                    vm.name = data.data.name;
                    vm.description = data.data.description;
                    vm.checkedSetting = data.data.join_group_setting.toString();
                }
                else {
                    bsAlert(data.data);
                }
            }
        });

        $("#edit_group_form")
            .formValidation({
                framework: "bootstrap",
                fields: {
                    name: {
                        validators: {
                            notEmpty: {
                                message: "请填写小组名"
                            },
                            stringLength: {
                                max: 20,
                                message: '小组名长度必须在20位之内'
                            }
                        }
                    },
                    description: {
                        validators: {
                            notEmpty: {
                                message: "请填写描述"
                            },
                            stringLength: {
                                max: 300,
                                message: '描述长度必须在300位之内'
                            }
                        }
                    }
                }
            }
        ).on('success.form.fv', function (e) {
                e.preventDefault();
                var data = {
                    group_id: avalon.vmodels.admin.groupId,
                    name: vm.name,
                    description: vm.description,
                    join_group_setting: vm.checkedSetting
                };
                $.ajax({
                    beforeSend: csrfTokenHeader,
                    url: "/api/admin/group/",
                    method: "put",
                    data: data,
                    dataType: "json",
                    success: function (data) {
                        if (!data.code) {
                            bsAlert("修改成功");
                        }
                        else {
                            bsAlert(data.data);
                        }
                    }
                })
            });
    });

});