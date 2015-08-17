require(["jquery", "avalon", "csrfToken", "bsAlert", "editor", "validator"],
    function ($, avalon, csrfTokenHeader, bsAlert, editor) {



        avalon.ready(function () {
            avalon.vmodels.announcement = null;

            var createAnnouncementEditor = editor("#create-announcement-editor");
            var editAnnouncementEditor = editor("#edit-announcement-editor");

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
                announcementVisible: 0,
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
                    $("#newTitle").val(announcement.title);
                    editAnnouncementEditor.setValue(announcement.content);
                    vm.announcementVisible = announcement.visible;
                    if (vm.editingAnnouncementId == announcement.id)
                        vm.editingAnnouncementId = 0;
                    else
                        vm.editingAnnouncementId = announcement.id;
                    editAnnouncementEditor.focus();
                },
                cancelEdit: function () {
                    vm.editingAnnouncementId = 0;
                },
                submitChange: function () {
                    var title = $("#newTitle").val();
                    var content = editAnnouncementEditor.getValue();

                    if (content && title) {
                        $.ajax({
                            beforeSend: csrfTokenHeader,
                            url: "/api/admin/announcement/",
                            dataType: "json",
                            method: "put",
                            data: {
                                id: vm.editingAnnouncementId,
                                title: title,
                                content: content,
                                visible: vm.announcementVisible
                            },
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
                    else {
                        bsAlert("标题和公告内容不得为空");
                    }
                }
            });
            vm.$watch("showVisibleOnly", function () {
                getPageData(1);
            });

            getPageData(1);

            function getPageData(page) {
                var url = "/api/announcements/?paging=true&page=" + page + "&page_size=10";
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


            $('form').validator().on('submit', function (e) {
                if (!e.isDefaultPrevented()) {
                    var title = $("#title").val();
                    var content = createAnnouncementEditor.getValue();
                    if (content == "") {
                        bsAlert("请填写公告内容");
                        return false;
                    }
                    $.ajax({
                        beforeSend: csrfTokenHeader,
                        url: "/api/admin/announcement/",
                        data: {title: title, content: content},
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
                    })
                    return false;
                }
            })
        });
        avalon.scan();
    });