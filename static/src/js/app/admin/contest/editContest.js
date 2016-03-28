require(["jquery", "avalon", "editor", "uploader", "bsAlert", "csrfToken", "datetimePicker",
        "validator", "editorComponent"],
    function ($, avalon, editor, uploader, bsAlert, csrfTokenHeader) {

        $("#edit-contest-form").validator().on('submit', function (e) {
            if (!e.isDefaultPrevented()) {
                e.preventDefault();
                var ajaxData = {
                    id: avalon.vmodels.admin.contestId,
                    title: vm.title,
                    description: avalon.vmodels.contestDescriptionEditor.content,
                    contest_type: 0,
                    real_time_rank: vm.realTimeRank,
                    start_time: vm.startTime,
                    end_time: vm.endTime,
                    visible: vm.visible
                };

                var selectedGroups = [];
                if (!vm.isGlobal) {
                    for (var i = 0; i < vm.allGroups.length; i++) {
                        if (vm.allGroups[i].isSelected) {
                            selectedGroups.push(vm.allGroups[i].id);
                        }
                    }
                    if (vm.password) {
                        ajaxData.password = vm.password;
                        ajaxData.contest_type = 3;
                    }
                    ajaxData.groups = selectedGroups;
                }
                else {
                    if (vm.password) {
                        ajaxData.password = vm.password;
                        ajaxData.contest_type = 2;
                    }
                    else
                        ajaxData.contest_type = 1;
                }
                if (!vm.isGlobal && !selectedGroups.length) {
                    bsAlert("你没有选择参赛用户!");
                    return false;
                }
                if (ajaxData.description.trim() == "") {
                    bsAlert("比赛描述不能为空!");
                    return false;
                }
                $.ajax({
                    url: "/api/admin/contest/",
                    dataType: "json",
                    contentType: "application/json;charset=UTF-8",
                    data: JSON.stringify(ajaxData),
                    method: "put",
                    success: function (data) {
                        if (!data.code) {
                            bsAlert("修改成功！");
                            vm.showContestListPage();
                        }
                        else {
                            bsAlert(data.data);
                        }
                    }
                });
            }
            return false;
        });

        if (avalon.vmodels.edit_contest)
            var vm = avalon.vmodels.edit_contest;
        else
            var vm = avalon.define({
                $id: "edit_contest",
                title: "",
                startTime: "",
                endTime: "",
                password: "",
                isGlobal: true,
                allGroups: [],
                showGlobalViewRadio: true,
                realTimeRank: true,
                visible: false,
                showContestListPage: function () {
                    avalon.vmodels.admin.template_url = "template/contest/contest_list.html";
                },

                contestDescriptionEditor: {
                    editorId: "contest-description-editor",
                    placeholder: "比赛介绍内容"
                }
            });
        avalon.scan();
        $.ajax({
            url: "/api/user/",
            method: "get",
            dataType: "json",
            success: function (data) {
                if (!data.code) {
                    var admin_type = data.data.admin_type;
                    if (data.data.admin_type == 1) {
                        vm.isGlobal = false;
                        vm.showGlobalViewRadio = false;
                    }
                }
                $.ajax({
                    url: "/api/admin/group/",
                    method: "get",
                    dataType: "json",
                    success: function (data) {
                        if (!data.code) {
                            if (!data.data.length) {
                                if (admin_type == 1) {
                                    bsAlert("您的用户权限只能创建小组内比赛，但是您还没有创建过小组");
                                    return;
                                }
                                else if(admin_type == 2) {
                                    bsAlert("当前系统中没有小组，创建或编辑小组赛功能将不可用。");
                                }
                            }
                            vm.allGroups = [];
                            for (var i = 0; i < data.data.length; i++) {
                                var item = data.data[i];
                                item.isSelected = false;
                                vm.allGroups.push(item);
                            }
                            $.ajax({
                                url: "/api/admin/contest/?contest_id=" + avalon.vmodels.admin.contestId,
                                method: "get",
                                dataType: "json",
                                success: function (data) {
                                    if (data.code) {
                                        bsAlert(data.data);
                                    }
                                    else {
                                        var contest = data.data;
                                        vm.title = contest.title;
                                        avalon.vmodels.contestDescriptionEditor.content = contest.description;
                                        vm.visible = contest.visible;
                                        vm.realTimeRank = contest.real_time_rank;
                                        vm.startTime = contest.start_time.substring(0, 16).replace("T", " ");
                                        vm.endTime = contest.end_time.substring(0, 16).replace("T", " ");
                                        vm.password = contest.password;
                                        if (contest.contest_type == 0 || contest.contest_type == 3) { //contest_type == 0, 小组内比赛
                                            vm.isGlobal = false;
                                            for (var i = 0; i < vm.allGroups.length; i++) {
                                                vm.allGroups[i].isSelected = false;
                                            }
                                            for (var i = 0; i < contest.groups.length; i++) {
                                                var id = contest.groups[i];
                                                for (var index = 0; vm.allGroups[index]; index++) {
                                                    if (vm.allGroups[index].id == id) {
                                                        vm.allGroups[index].isSelected = true;
                                                        break;
                                                    }
                                                }
                                            }
                                        }
                                        else {
                                            vm.isGlobal = true;
                                        }
                                    }
                                }
                            });
                        }
                        else {
                            bsAlert(data.data);
                        }
                    }
                });
            }
        });

        $("#contest_start_time").datetimepicker({
            format: "yyyy-mm-dd hh:ii",
            minuteStep: 5,
            weekStart: 1,
            language: "zh-CN"
        });
        $("#contest_end_time").datetimepicker({
            format: "yyyy-mm-dd hh:ii",
            minuteStep: 5,
            weekStart: 1,
            language: "zh-CN"
        });
    });