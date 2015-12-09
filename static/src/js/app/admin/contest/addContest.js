require(["jquery", "avalon", "editor", "uploader", "bsAlert", "csrfToken", "datetimePicker",
        "validator", "editorComponent"],
    function ($, avalon, editor, uploader, bsAlert, csrfTokenHeader) {

        $("#add-contest-form").validator().on('submit', function (e) {
            if (!e.isDefaultPrevented()) {
                e.preventDefault();
                var ajaxData = {
                    title: vm.title,
                    description: avalon.vmodels.contestDescriptionEditor.content,
                    contest_type: 0,
                    real_time_rank: vm.realTimeRank,
                    start_time: vm.startTime,
                    end_time: vm.endTime,
                    visible: false
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
                    method: "post",
                    success: function (data) {
                        if (!data.code) {
                            bsAlert("添加成功！接下来下需要为比赛添加问题(注意比赛当前状态为:隐藏)");
                            location.hash = "#contest/contest_list";
                        }
                        else {
                            bsAlert(data.data);
                        }
                    }
                });
            }
            return false;
        });

        //editor("#editor");
        if (avalon.vmodels.add_contest) {
            var vm = avalon.vmodels.add_contest;
            vm.title = "";
            vm.startTime = "";
            vm.endTime = "";
            vm.password = "";
            vm.isGlobal = true;
            vm.allGroups = [];
            vm.showGlobalViewRadio = true;
            vm.realTimeRank = true;
            avalon.vmodels.contestDescriptionEditor.content = "";

        }
        else
            var vm = avalon.define({
                $id: "add_contest",
                title: "",
                startTime: "",
                endTime: "",
                password: "",
                isGlobal: true,
                allGroups: [],
                showGlobalViewRadio: true,
                realTimeRank: true,

                contestDescriptionEditor: {
                    editorId: "contest-description-editor",
                    placeholder: "比赛介绍内容"
                }
            });

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
                                if (admin_type != 2)
                                    bsAlert("您的用户权限只能创建小组内比赛，但是您还没有创建过小组");
                                return;
                            }
                            vm.allGroups = [];
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
            }
        });

        avalon.scan();

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