require(["jquery", "avalon", "csrf", "bs_alert", "validation"], function ($, avalon, csrfHeader, bs_alert) {
    avalon.vmodels.group_detail = null;

    // avalon:定义模式 group_list
    avalon.ready(function () {
        var vm = avalon.define({
            $id: "group_detail",
            //通用变量
            member_list: [],
            previous_page: 0,
            next_page: 0,
            page: 1,
            page_count: 1,
            name: "",
            description: "",
            join_group_setting: {0: false, 1: false, 2: false},
            checked_setting: "0",

            updateGroupInfo: function () {
                $.ajax({
                    beforeSend: csrfHeader,
                    url: "/api/admin/group/",
                    method: "put",
                    data: {group_id: avalon.vmodels.admin.group_id, name: vm.name,
                        description: vm.description, join_group_setting: vm.checked_setting},
                    dataType: "json",
                    success: function (data) {
                        if (!data.code) {
                            bs_alert("修改成功");
                        }
                        else {
                            bs_alert(data.data);
                        }
                    }
                })
            },

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
            getBtnClass: function (btn) {
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
            removeMember: function (relation) {
                $.ajax({
                    beforeSend: csrfHeader,
                    url: "/api/admin/group_member/",
                    method: "put",
                    data: JSON.stringify({group_id: relation.group, members: [relation.user.id]}),
                    contentType: "application/json",
                    success: function (data) {
                        vm.member_list.remove(relation);
                        bs_alert(data.data);
                    }
                })
            }
        });

        avalon.scan();
        getPageData(1);
        function getPageData(page) {
            var url = "/api/admin/group_member/?paging=true&page=" + page +
                "&page_size=10&group_id=" + avalon.vmodels.admin.group_id;
            $.ajax({
                url: url,
                dataType: "json",
                method: "get",
                success: function (data) {
                    if (!data.code) {
                        vm.member_list = data.data.results;
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

        $.ajax({
            url: "/api/admin/group/?group_id=" + avalon.vmodels.admin.group_id,
            method: "get",
            dataType: "json",
            success: function (data) {
                if (!data.code) {
                    vm.name = data.data.name;
                    vm.description = data.data.description;
                    vm.checked_setting = data.data.join_group_setting.toString();
                }
                else {
                    bs_alert(data.data);
                }
            }
        })
    });

});