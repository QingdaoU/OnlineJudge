require(["jquery", "avalon", "csrf", "bs_alert", "editor", "validation"], function ($, avalon, csrfHeader, bs_alert, editor) {
    announcementEditor = editor("#editor");                                               //创建新建公告的内容编辑器
    editAnnouncementEditor = null;

    if (!avalon.vmodels.announcement)                                                   // 防止模式重新定义
    {
        // avalon:定义模式 announcement
        vm = avalon.define({
            $id: "announcement",
            announcement: [], //  公告列表数据项
            previous_page: 0, //  之前的页数
            next_page: 0,     //   之后的页数
            page: 1,          //    当前页数
            isEditing: 0,    //    正在编辑的公告的ID， 为零说明未在编辑
            getState: function (el) {   //获取公告当前状态，显示
                if (el.visible)
                    return "可见";
                else
                    return "隐藏";
            },
            getNext: function (el) {
                if (!vm.next_page)
                    return;
                getPageData(++(vm.page));
            },
            getPrevious: function (el) {
                if (!vm.previous_page)
                    return;
                getPageData(--(vm.page));
            },
            getBtnClass: function (btn) {
                if (btn) {
                    return vm.next_page ? "btn btn-primary" : "btn btn-primary disabled";
                }
                else {
                    return vm.previous_page ? "btn btn-primary" : "btn btn-primary disabled";
                }

            },
            enEdit: function (el) {   //点击编辑按钮的事件,显示/隐藏编辑区
                $("#newTitle").val(el.title);
                if (!editAnnouncementEditor)  //初始化编辑器
                    editAnnouncementEditor = editor("#editAnnouncementEditor");
                editAnnouncementEditor.setValue(el.content);
                if (el.visible == false)
                    $("#hidden").attr("checked", true);
                if (vm.isEditing == el.id)
                    vm.isEditing = 0;
                else
                    vm.isEditing = el.id;
                editAnnouncementEditor.focus();
            },
            disEdit: function () {                                                                 //收起编辑框
                vm.isEditing = 0;
            },
            submitChange: function () {                                                          // 处理编辑公告提交事件，顺便验证字段为空
                var title = $("#newTitle").val(), content = editAnnouncementEditor.getValue(), visible = true;
                if ($("#hidden").attr("checked") == true)
                    visible = false;
                if (title != "") {
                    if (content != "") {
                        $.ajax({                                                                      //发送修改公告请求
                            beforeSend: csrfHeader,
                            url: "/api/edit_announcements/",
                            dataType: "json",
                            method: "post",
                            data: {id: vm.isEditing, title: title, content: content, visible: visible},
                            success: function (data) {
                                if (!data.code) {
                                    bs_alert("修改成功");
                                    vm.isEditing = 0;
                                }
                                else {
                                    bs_alert(data.data);
                                }
                            }
                        });
                    }
                    else
                        bs_alert("公告内容不得为空");
                }
                else
                    bs_alert("公告标题不能为空");
            }
        });
    }

    avalon.scan();
    getPageData(1);   //公告列表初始化
    vm.page = 1;
    vm.isEditing = 0;
    //Ajax get数据
    function getPageData(page) {
        $.ajax({
            beforeSend: csrfHeader,
            url: "/api/announcements/?paging=true&page=" + page + "&page_size=10",
            dataType: "json",
            method: "get",
            success: function (data) {
                if (!data.code) {
                    vm.announcement = data.data.results;
                    vm.previous_page = data.data.previous_page;
                    vm.next_page = data.data.next_page;
                }
                else {
                    bs_alert(data.data);
                }
            }
        });
    }

    //新建公告表单验证与数据提交
    $("#announcement-form")
        .formValidation({
            framework: "bootstrap",
            fields: {
                title: {
                    validators: {
                        notEmpty: {
                            message: "请填写公告标题"
                        }
                    }
                }
            }
        }
    ).on('success.form.fv', function (e) {
            e.preventDefault();
            var title = $("#title").val();
            var content = announcementEditor.getValue();
            if (content == "") {
                bs_alert("请填写公告内容");
                return;
            }
            $.ajax({
                beforeSend: csrfHeader,
                url: "/api/admin/announcement/",
                data: {title: title, content: content},
                dataType: "json",
                method: "post",
                success: function (data) {
                    if (!data.code) {
                        bs_alert("提交成功！");
                        $("#title").val("");
                        announcementEditor.setValue("");
                        getPageData(1, function (data) {
                        });
                    } else {
                        bs_alert(data.data);
                    }
                }
            })
        });

});