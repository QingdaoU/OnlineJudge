require(["jquery", "avalon", "csrfToken", "bsAlert", "editor", "datetimePicker"], function ($, avalon, csrfTokenHeader, bsAlert, editor) {

    avalon.ready(function () {
        if (avalon.vmodels.contestList) {
            vm = avalon.vmodels.contestList;
            vm.editingContest = 0;
        }
        else {
            var vm = avalon.define({
                $id: "contestList",
                contestList: [],
                previousPage: 0,
                nextPage: 0,
                page: 1,
                totalPage: 1,
                group: "-1",
                groupList: [],
                keyword: "",
                editingContestId: 0,
                editTitle: "",
                editProblemList: [],
                editPassword: "",
                editStartTime: "",
                editEndTime: "",
                editMode: "",
                editShowRank: false,
                editShowSubmission: false,
                editProblemList: [],
                editingProblemId: 0,
                editSamples: [],
                editTestCaseList: [],
                editChoseGroupList: [],
                modelNameList: ["ACM", "AC总数", "分数"],
                contestTypeNameList: ["小组赛", "公开赛", "有密码保护的公开赛"],
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
                    if (contestId == vm.editingContestId)
                        vm.editingContestId = 0;
                    else {
                        vm.editingContestId = contestId;
                        vm.editTitle = vm.contestList[contestId - 1].title;
                        vm.editEndTime = vm.contestList[contestId - 1].end_time;
                        vm.editPassword = vm.contestList[contestId - 1].password;
                        vm.editStartTime = vm.contestList[contestId - 1].start_time;
                        vm.editMode = vm.contestList[contestId - 1].mode;
                        vm.editChoseGroupList = [];
                        //= vm.contestList[contestId-1].group;//
                        /*for (var key in vm.contestList[contestId-1].groups){
                         var id = parseInt(vm.contestList[contestId-1].groups);
                         for ()
                         vm.editChoseGroupList.push({
                         name:vm.groupList[vm.group].name,
                         index:index,
                         id:parseInt(vm.contestList[contestId-1].groups)
                         });
                         }*/
                        vm.editShowRank = vm.contestList[contestId - 1].show_rank;
                        vm.editShowSubmission = vm.contestList[contestId - 1].show_user_submission;
                        //vm.editProblemList    = vm.contestList[contestId-1].problems
                        editor("#editor").setValue(vm.contestList[contestId - 1].description);
                        vm.editingProblemList = vm.contestList[contestId - 1].problemList;
                    }
                }
            });

            getPageData(1);
        }

        function getPageData(page) {

            var url = "/api/admin/contest/?paging=true&page=" + page + "&page_size=10";
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

        var isSuperAdmin = true;

        $.ajax({      //用于获取该用户创建的所有小组的ajax请求

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
    });
    avalon.scan();
});
