require(["jquery", "avalon", "csrf", "bs_alert", "editor", "validation"], function ($, avalon, csrfHeader, bs_alert, editor) {
    annoumcementEditor = editor("#editor");
    editAnnoumcementEditor = null;
    if (!avalon.vmodels.announcement)
        avalon.vmodels.announcement = null;
    vm = avalon.define({
        $id: "announcement",
        announcement: [],
        previous_page: 0,
        next_page: 0,
        page: 1,
        isEditing: false,
        getState: function (el) {
            if (el.visible)
                return "可见";
            else
                return "隐藏";
        },
        getNext: function (el) {
            getPageData(++(vm.page), function (data) {
            });
        },
        getPrevious: function (el) {
            getPageData(--(vm.page), function (data) {
            });
        },
        getBtnClass: function (btn) {
            if (btn) {
                return vm.next_page ? "btn btn-primary" : "btn btn-primary disabled";
            }
            else {
                return vm.previous_page ? "btn btn-primary" : "btn btn-primary disabled";
            }

        },
        enEdit: function(el){
            $("#newTitle").val(el.title);
            if (!editAnnoumcementEditor)
                editAnnoumcementEditor = editor("#editAnnoumcementEditor");
            editAnnoumcementEditor.setValue(el.content);
            vm.isEditing = true;
            editAnnoumcementEditor.focus();
        }
    });

    getPageData(1, function (data) {
        avalon.scan();
    });

    function getPageData(page, callback) {
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
                    callback(data);
                }
                else {
                    bs_alert(data.data);
                }
            }
        });
    }


    $("#announcement-edit-form")
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
            var title = $("#newTitle").val();
            var content = editor1.getValue();
            if (content == "") {
                bs_alert("请填写公告内容")
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
                        editor1.setValue("");
                        getPageData(1, function (data) {});
                    } else {
                        bs_alert(data.data);
                    }
                }

            })
        });

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
            var content = editor1.getValue();
            if (content == "") {
                bs_alert("请填写公告内容")
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
                        editor1.setValue("");
                        getPageData(1, function (data) {});
                    } else {
                        bs_alert(data.data);
                    }
                }

            })
        });

});