require(["jquery", "avalon", "editor", "uploader", "bsAlert", "csrfToken", "datetimePicker",
        "validator"],
    function ($, avalon, editor, uploader, bsAlert, csrfTokenHeader) {

        //avalon.vmodels.add_contest = null;
        $("#add-contest-form").validator().on('submit', function (e) {
            if (!e.isDefaultPrevented()){
                e.preventDefault();
                var ajaxData = {
                    title: vm.title,
                    description: vm.description,
                    mode: vm.mode,
                    contest_type: 0,
                    show_rank: vm.showRank,
                    show_user_submission: vm.showSubmission,
                    start_time: vm.startTime,
                    end_time: vm.endTime,
                    visible: false
                };
                if (vm.choseGroupList.length == 0) {
                   bsAlert("你没有选择参赛用户!");
                   return false;
                }
                if (vm.choseGroupList[0].id == 0) { //everyone | public contest
                    if (vm.password) {
                        ajaxData.password = vm.password;
                        ajaxData.contest_type = 2;
                    }
                    else{
                        ajaxData.contest_type = 1;
                    }
                }
                else { // Add groups info
                    ajaxData.groups = [];
                    for (var i = 0; vm.choseGroupList[i]; i++)
                        ajaxData.groups.push(parseInt(vm.choseGroupList[i].id))
                }

                console.log(ajaxData);
                $.ajax({                                  // Add contest
                    beforeSend: csrfTokenHeader,
                    url: "/api/admin/contest/",
                    dataType: "json",
                    contentType: "application/json",
                    data: JSON.stringify(ajaxData),
                    method: "post",
                    contentType: "application/json",
                    success: function (data) {
                        if (!data.code) {
                                bsAlert("添加成功！将转到比赛列表页以便为比赛添加问题(注意比赛当前状态为:隐藏)");
                                vm.title          = "";
                                vm.description    = "";
                                vm.startTime      = "";
                                vm.endTime        = "";
                                vm.password       = "";
                                vm.mode           = "";
                                vm.showRank       = false;
                                vm.showSubmission = false;
                                vm.group          = "-1";
                                vm.groupList      = [];
                                vm.choseGroupList = [];
                                vm.passwordUsable = false;
                                location.hash = "#contest/contest_list";
                        }
                        else {
                            bsAlert(data.data);
                            console.log(data);
                        }
                    }
                });
                console.log(JSON.stringify(ajaxData));
            }
            return false;
        });

        editor("#editor");
    if (avalon.vmodels.add_contest)
        var vm = avalon.vmodels.add_contest;
    else
        var vm = avalon.define({
            $id: "add_contest",
            title: "",
            description: "",
            startTime: "",
            endTime: "",
            password: "",
            mode: "",
            showRank: false,
            showSubmission: false,
            group: "-1",
            groupList: [],
            choseGroupList: [],
            passwordUsable: false,
            addGroup: function() {
                if (vm.group == -1) return;
                if (vm.groupList[vm.group].id == 0){
                    vm.passwordUsable = true;
                    vm.choseGroupList = [];
                    for (var key in vm.groupList){
                        vm.groupList[key].chose = true;
                    }
                }
                vm.groupList[vm.group]. chose = true;
                vm.choseGroupList.push({name:vm.groupList[vm.group].name, index:vm.group, id:vm.groupList[vm.group].id});
                vm.group = -1;
            },
            removeGroup: function(groupIndex){
                if (vm.groupList[vm.choseGroupList[groupIndex].index].id == 0){
                    vm.passwordUsable = false;
                    for (key in vm.groupList){
                        vm.groupList[key].chose = false;
                    }
                }
                vm.groupList[vm.choseGroupList[groupIndex].index].chose = false;
                vm.choseGroupList.remove(vm.choseGroupList[groupIndex]);
            }
        });

        $.ajax({  // Get current user type
            url: "/api/user/",
            method: "get",
            dataType: "json",
            success: function (data) {
                if (!data.code) {
                    if (data.data.admin_type == 2) { // Is super user
                        vm.isGlobal = true;
                        vm.groupList.push({id:0,name:"所有人",chose:false});
                    }
                    $.ajax({      // Get the group list of current user
                        beforeSend: csrfTokenHeader,
                        url: "/api/admin/group/",
                        method: "get",
                        dataType: "json",
                        success: function (data) {
                            if (!data.code) {
                                if (!data.data.length) {
                                    bsAlert("您的用户权限只能创建组内比赛，但是您还没有创建过小组");
                                    return;
                                }
                                for (var i = 0; i < data.data.length; i++) {
                                    var item = data.data[i];
                                    item["chose"] = false;
                                    vm.groupList.push(item);
                                }
                            }
                            else {
                                bsAlert(data.data);
                            }
                        }
                    });
                }
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