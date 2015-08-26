require(["jquery", "avalon", "csrfToken", "bsAlert", "editor", "datetimePicker", "validator"], function ($, avalon, csrfTokenHeader, bsAlert, editor) {

    avalon.ready(function () {

        $("#edit-contest-form").validator().on('submit', function (e) {
            if (!e.isDefaultPrevented()){
                e.preventDefault();
                var ajaxData = {
                    id:                   vm.contestList[vm.editingContestId-1].id,
                    title:                vm.editTitle,
                    description:          vm.editDescription,
                    mode:                 vm.editMode,
                    contest_type:         0,
                    show_rank:            vm.editShowRank,
                    show_user_submission: vm.editShowSubmission,
                    start_time:           vm.editStartTime,
                    end_time:             vm.editEndTime,
                    visible:              vm.editVisible
                };
                if (vm.choseGroupList.length == 0) {
                    bsAlert("你没有选择参赛用户!");
                    return false;
                }
                if (vm.editDescription == "") {
                    bsAlert("比赛描述不能为空!");
                    return false;
                }
                if (vm.choseGroupList[0].id == 0) { //everyone | public contest
                    if (vm.editPassword) {
                        ajaxData.password = vm.editPassword;
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

                $.ajax({                                  // Add contest
                    beforeSend: csrfTokenHeader,
                    url: "/api/admin/contest/",
                    dataType: "json",
                    contentType: "application/json",
                    data: JSON.stringify(ajaxData),
                    method: "put",
                    contentType: "application/json",
                    success: function (data) {
                        if (!data.code) {
                            bsAlert("修改成功!");
                            vm.editingContestId = 0; // Hide the editor
							vm.getPage(1);           // Refresh the contest list
                        }
                        else {
                            bsAlert(data.data);
                        }
                    }
                });
            }
            return false;
        });

    if(avalon.vmodels.contestList){
        // this page has been loaded before, so set the default value
        var vm = avalon.vmodels.contestList;
        vm.contestList= [];
        vm.previousPage= 0;
        vm.nextPage= 0;
        vm.page= 1;
        vm.totalPage= 1;
        vm.group= "-1";
        vm.groupList= [];
        vm.choseGroupList= [];
        vm.passwordUsable= false;
        vm.keyword= "";
        vm.editingContestId= 0;
        vm.editTitle= "";
        vm.editDescription= "";
        vm.editProblemList= [];
        vm.editPassword= "";
        vm.editStartTime= "";
        vm.editEndTime= "";
        vm.editMode= "";
        vm.editShowRank= false;
        vm.editShowSubmission= false;
        vm.editProblemList= [];
        vm.editVisible= false;
        vm.editChoseGroupList= [];
        vm.editingProblemContestIndex= 0;
    }
    else {
        var vm = avalon.define({
            $id: "contestList",
            contestList: [],
            previousPage: 0,
            nextPage: 0,
            page: 1,
            totalPage: 1,
            showVisibleOnly: false,
            group: "-1",
            groupList: [],
            choseGroupList: [],
            passwordUsable: false,
            keyword: "",
            editingContestId: 0,
            editTitle: "",
            editDescription: "",
            editProblemList: [],
            editPassword: "",
            editStartTime: "",
            editEndTime: "",
            editMode: "",
            editShowRank: false,
            editShowSubmission: false,
            editProblemList: [],
            editVisible: false,
            editChoseGroupList: [],
            editingProblemContestIndex: 0,
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
            getPage: function (page_index) {
                getPageData(page_index);
            },
            showEditContestArea: function (contestId) {
                if (vm.editingContestId && !confirm("如果继续将丢失未保存的信息,是否继续?"))
                    return;
                if (contestId == vm.editingContestId)
                    vm.editingContestId = 0;
                else {
                    vm.editingContestId = contestId;
                    vm.editTitle     = vm.contestList[contestId-1].title;
                    vm.editPassword  = vm.contestList[contestId-1].password;
                    vm.editStartTime = vm.contestList[contestId-1].start_time.substring(0,16).replace("T"," ");
                    vm.editEndTime   = vm.contestList[contestId-1].end_time.substring(0,16).replace("T"," ");
                    vm.editMode      = vm.contestList[contestId-1].mode;
                    vm.editVisible      = vm.contestList[contestId-1].visible;
                    if (vm.contestList[contestId-1].contest_type == 0) { //contest type == 0, contest in group
                        //Clear the choseGroupList
                        while (vm.choseGroupList.length) {
                            vm.removeGroup(0);
                        }

                        for (var i = 0; i < vm.contestList[contestId-1].groups.length; i++){
                            var id = parseInt(vm.contestList[contestId-1].groups[i]);
                            var index = 0;
                            for (; vm.groupList[index]; index++) {
                                if (vm.groupList[index].id == id)
                                    break;
                            }
                            vm.groupList[index].chose = true;
                            vm.choseGroupList.push({
                                name:vm.groupList[index].name,
                                index:index,
                                id:id
                            });
                        }
                    }
                    else{
                        vm.group = "0";
                        vm.addGroup()//vm.editChoseGroupList = [0]; id 0 is for the group of everyone~
                    }
                    vm.editShowRank = vm.contestList[contestId-1].show_rank;
                    vm.editShowSubmission = vm.contestList[contestId-1].show_user_submission;
                    editor("#editor").setValue(vm.contestList[contestId-1].description);
                    vm.editingProblemContestIndex = 0;
                }
            },
            showEditProblemArea: function(contestId) {
                if (vm.editingProblemContestIndex == contestId) {
                    vm.editingProblemContestIndex = 0;
                    return;
                }
                if (vm.editingContestId&&!confirm("如果继续将丢失未保存的信息,是否继续?")){
                    return;
                }
                $.ajax({      // Get the problem list of current contest
                        beforeSend: csrfTokenHeader,
                        url: "/api/admin/contest_problem/?contest_id=" + vm.contestList[contestId-1].id,
                        method: "get",
                        dataType: "json",
                        success: function (data) {
                            if (!data.code) {
                                vm.editProblemList = data.data;
                            }
                            else {
                                bsAlert(data.data);
                            }
                        }
                    });
                vm.editingContestId = 0;
                vm.editingProblemContestIndex = contestId;
                vm.editMode = vm.contestList[contestId-1].mode;
            },
            addGroup: function() {
                    if (vm.group == -1) return;
                    if (vm.groupList[vm.group].id == 0){
                        vm.passwordUsable = true;
                        vm.choseGroupList = [];
                        for (var i = 0; i < vm.groupList.length; i++) {
                            vm.groupList[i].chose = true;
                        }
                    }
                    vm.groupList[vm.group]. chose = true;
                    // index of the group is relative. It is related to user
                    vm.choseGroupList.push({name:vm.groupList[vm.group].name, index:vm.group, id:vm.groupList[vm.group].id});
                    vm.group = -1;
            },
            removeGroup: function(groupIndex){
                    if (vm.groupList[vm.choseGroupList[groupIndex].index].id == 0){
                        vm.passwordUsable = false;
                        for (var i = 0; i < vm.groupList.length; i++) {
                            vm.groupList[i].chose = false;
                        }
                    }
                    vm.groupList[vm.choseGroupList[groupIndex].index].chose = false;
                    vm.choseGroupList.remove(vm.choseGroupList[groupIndex]);
                },
            addProblem: function () {
                vm.$fire("up!showContestProblemPage", 0, vm.contestList[vm.editingProblemContestIndex-1].id, vm.editMode);
            },
            showProblemEditor: function(el) {
                vm.$fire("up!showContestProblemPage", el.id, vm.contestList[vm.editingProblemContestIndex-1].id, vm.editMode);
            },
            showSubmissionPage: function() {
                vm.$fire("up!showContestSubmissionPage", el.id, vm.contestList[vm.editingProblemContestIndex-1].id, vm.editMode);
            },
            getYesOrNo: function(yORn) {
                if (yORn) return "是";
                return "否";
            }
        });
        vm.$watch("showVisibleOnly", function() {
            getPageData(1);
        })
    }
        getPageData(1);

        //init time picker
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

        function getPageData(page) {
            var url = "/api/admin/contest/?paging=true&page=" + page + "&page_size=10";
            if (vm.showVisibleOnly)
                url += "&visible=true"
            if (vm.keyword != "")
                url += "&keyword=" + vm.keyword;
            $.ajax({
                url: url,
                dataType: "json",
                method: "get",
                success: function (data) {
                    if (!data.code) {
                        vm.contestList = data.data.results;
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
        // Get group list
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
                                    //this user have no group can use
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

    });
    avalon.scan();
});
