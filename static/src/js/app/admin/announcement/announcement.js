require(["jquery", "avalon", "csrfToken", "bsAlert", "editor", "validator", "pager"],
    function ($, avalon, csrfTokenHeader, bsAlert, editor) {
        avalon.ready(function () {

            var createAnnouncementEditor = editor("#create-announcement-editor");
            var editAnnouncementEditor = editor("#edit-announcement-editor");

            if (avalon.vmodels.announcement){
                var vm = avalon.vmodels.announcement;
            }
            else {
                var vm = avalon.define({
                    $id: "announcement",
                    announcementList: [],
                    pager: {
                        getPage: function(page){
                            getPage(page);
                        }
                    },
                    isEditing: false,
                    announcementId: -1,
                    showVisibleOnly: false,
                    newTitle: "",
                    announcementVisible: 0,

                    editAnnouncement: function (announcement) {
                        vm.newTitle = announcement.title;
                        vm.announcementId = announcement.id;
                        editAnnouncementEditor.setValue(announcement.content);
                        vm.announcementVisible = announcement.visible;
                        vm.isEditing = !vm.isEditing;
                        editAnnouncementEditor.focus();
                    },
                    cancelEdit: function () {
                        vm.isEditing = false;
                    },
                    submitChange: function () {
                        var title = vm.newTitle;
                        var content = editAnnouncementEditor.getValue();

                        if (content == "" || title == "") {
                            bsAlert("标题和内容都不能为空");
                            return false;
                        }

                        $.ajax({
                            url: "/api/admin/announcement/",
                            contentType: "application/json;charset=UTF-8",
                            dataType: "json",
                            method: "put",
                            data: JSON.stringify({
                                id: vm.announcementId,
                                title: title,
                                content: content,
                                visible: vm.announcementVisible
                            }),
                            success: function (data) {
                                if (!data.code) {
                                    bsAlert("修改成功");
                                    vm.isEditing = false;
                                    getPage(1);
                                }
                                else {
                                    bsAlert(data.data);
                                }
                            }
                        });

                    }
                });

                vm.$watch("showVisibleOnly", function () {
                    getPage(1);
                    avalon.vmodels.announcementPager.currentPage = 1;
                });
            }

            function getPage(page) {
                var url = "/api/admin/announcement/?paging=true&page=" + page + "&page_size=2";
                if (vm.showVisibleOnly)
                    url += "&visible=true";
                $.ajax({
                    url: url,
                    method: "get",
                    success: function (data) {
                        if (!data.code) {
                            vm.announcementList = data.data.results;
                            avalon.vmodels.announcementPager.totalPage = data.data.total_page;
                        }
                        else {
                            bsAlert(data.data);
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
                    $.ajax({
                        url: "/api/admin/announcement/",
                        contentType: "application/json",
                        data: JSON.stringify({
                            title: title,
                            content: content
                        }),
                        dataType: "json",
                        method: "post",
                        success: function (data) {
                            if (!data.code) {
                                bsAlert("提交成功！");
                                $("#title").val("");
                                createAnnouncementEditor.setValue("");
                                getPage(1);
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