require(["jquery", "avalon", "csrfToken", "bsAlert", "validator"], function ($, avalon, csrfTokenHeader, bsAlert) {


    // avalon:定义模式 group_list
    avalon.ready(function () {

        if (avalon.vmodels.groupDetail) {
            var vm = avalon.vmodels.groupDetail;
        }
        else {
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
                        contentType: "application/json;charset=UTF-8",
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
        }

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

        $('form').validator().on('submit', function (e) {
                if (!e.isDefaultPrevented()) {

                    var group_id = avalon.vmodels.admin.groupId;
                    var name = vm.name;
                    var description = vm.description;
                    var join_group_setting = vm.checkedSetting;

                    $.ajax({
                        beforeSend: csrfTokenHeader,
                        url: "/api/admin/group/",
                        method: "put",
                        data: {group_id: group_id, name: name, description: description,
                               join_group_setting: join_group_setting},
                        dataType: "json",
                        success: function (data) {
                            if (!data.code) {
                                bsAlert("修改成功");
                            }
                            else {
                                bsAlert(data.data);
                            }
                        }
                    });
                    return false;
                }
            })
    });

});
