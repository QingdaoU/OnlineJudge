require(["jquery", "avalon", "csrfToken", "bsAlert", "editor", "validator"],
    function ($, avalon, csrfTokenHeader, bsAlert, editor) {
        avalon.ready(function () {

            var createAnnouncementEditor = editor("#create-announcement-editor");
            var editAnnouncementEditor = editor("#edit-announcement-editor");
            if (avalon.vmodels.announcement){
                var vm = avalon.vmodels.announcement;
                announcementList = [];
            }
            else {

                var vm = avalon.define({
                    $id: "announcement",
                    //通用变量
                    announcementList: [],                 //  公告列表数据项
                    previousPage: 0,                 //  之前的页数
                    nextPage: 0,                     //   之后的页数
                    page: 1,                           //    当前页数
                    editingAnnouncementId: 0,                     //    正在编辑的公告的ID， 为零说明未在编辑
                    totalPage: 1,                   //    总页数
                    showVisibleOnly: false,            //仅显示可见公告
                    // 编辑
                    newTitle: "",
                    announcementVisible: 0,
                    showGlobalViewRadio: true,
                    isGlobal: true,
                    allGroups: [],
                    getState: function (el) {   //获取公告当前状态，显示
                        if (el.visible)
                            return "可见";
                        else
                            return "隐藏";
                    },
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
                    editAnnouncement: function (announcement) {
                        vm.newTitle = announcement.title;
                        editAnnouncementEditor.setValue(announcement.content);
                        vm.announcementVisible = announcement.visible;
                        if (vm.editingAnnouncementId == announcement.id)
                            vm.editingAnnouncementId = 0;
                        else
                            vm.editingAnnouncementId = announcement.id;
                        vm.isGlobal = announcement.is_global;
                        for (var i = 0; i < announcement.groups.length; i++) {
                            for (var j = 0; j < vm.allGroups.length; j++) {
                                if (announcement.groups[i] == vm.allGroups[j].id) {
                                    vm.allGroups[j].isSelected = true;
                                }
                            }
                        }
                        editAnnouncementEditor.focus();
                    },
                    cancelEdit: function () {
                        vm.editingAnnouncementId = 0;
                    },
                    submitChange: function () {
                        var title = vm.newTitle;
                        var content = editAnnouncementEditor.getValue();

                        if (content == "" || title == "") {
                            bsAlert("标题和内容都不能为空");
                            return false;
                        }

                        var selectedGroups = [];
                        if (!vm.isGlobal) {
                            for (var i = 0; i < vm.allGroups.length; i++) {
                                if (vm.allGroups[i].isSelected) {
                                    selectedGroups.push(vm.allGroups[i].id);
                                }
                            }
                        }

                        if (!vm.isGlobal && !selectedGroups.length) {
                            bsAlert("请至少选择一个小组");
                            return false;
                        }

                        $.ajax({
                            beforeSend: csrfTokenHeader,
                            url: "/api/admin/announcement/",
                            contentType: "application/json",
                            dataType: "json",
                            method: "put",
                            data: JSON.stringify({
                                id: vm.editingAnnouncementId,
                                title: title,
                                content: content,
                                visible: vm.announcementVisible,
                                is_global: vm.isGlobal,
                                groups: selectedGroups
                            }),
                            success: function (data) {
                                if (!data.code) {
                                    bsAlert("修改成功");
                                    vm.editingAnnouncementId = 0;
                                    getPageData(1);
                                }
                                else {
                                    bsAlert(data.data);
                                }
                            }
                        });

                    }
                });
                vm.$watch("showVisibleOnly", function () {
                    getPageData(1);
                });
            }

            getPageData(1);

            $.ajax({
                url: "/api/admin/group/",
                method: "get",
                dataType: "json",
                success: function (data) {
                    if (!data.code) {
                        if (!data.data.length) {
                            bsAlert("您的用户权限只能创建组内公告，但是您还没有创建过小组");
                            return;
                        }
                        for (var i = 0; i < data.data.length; i++) {
                            var item = data.data[i];
                            item["isSelected"] = false;
                            vm.allGroups.push(item);
                        }
                    }
                    else {
                        bsAlert(data.data);
                    }
                }
            });

            $.ajax({
                url: "/api/user/",
                method: "get",
                dataType: "json",
                success: function (data) {
                    if (!data.code) {
                        if (data.data.admin_type == 1) {
                            vm.isGlobal = false;
                            vm.showGlobalViewRadio = false;
                        }
                    }
                }
            });

            function getPageData(page) {
                var url = "/api/admin/announcement/?paging=true&page=" + page + "&page_size=10";
                if (vm.showVisibleOnly)
                    url += "&visible=true";
                $.ajax({
                    url: url,
                    dataType: "json",
                    method: "get",
                    success: function (data) {
                        if (!data.code) {
                            vm.announcementList = data.data.results;
                            vm.totalPage = data.data.total_page;
                            vm.previousPage = data.data.previous_page;
                            vm.nextPage = data.data.next_page;
                            vm.page = page;
                        }
                        else {
                            bs_alert(data.data);
                        }
                    }
                });
            }

            //新建公告表单验证与数据提交
            $("#announcement-form").validator().on('submit', function (e) {
                if (!e.isDefaultPrevented()) {
                    var title = $("#title").val();
                    var content = createAnnouncementEditor.getValue();
                    if (content == "") {
                        bsAlert("请填写公告内容");
                        return false;
                    }
                    var selectedGroups = [];
                    if (!vm.isGlobal) {
                        for (var i = 0; i < vm.allGroups.length; i++) {
                            if (vm.allGroups[i].isSelected) {
                                selectedGroups.push(vm.allGroups[i].id);
                            }
                        }
                    }

                    if (!vm.isGlobal && !selectedGroups.length) {
                        bsAlert("请至少选择一个小组");
                        return false;
                    }
                    $.ajax({
                        beforeSend: csrfTokenHeader,
                        url: "/api/admin/announcement/",
                        contentType: "application/json",
                        data: JSON.stringify({
                            title: title,
                            content: content,
                            is_global: vm.isGlobal,
                            groups: selectedGroups
                        }),
                        dataType: "json",
                        method: "post",
                        success: function (data) {
                            if (!data.code) {
                                bsAlert("提交成功！");
                                $("#title").val("");
                                createAnnouncementEditor.setValue("");
                                getPageData(1);
                            } else {
                                bsAlert(data.data);
                            }
                        }
                    });
                    return false;
                }
            })
        });
        avalon.scan();
    });