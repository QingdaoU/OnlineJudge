require(["jquery", "avalon", "editor", "uploader", "bsAlert", "csrfToken", "datetimePicker",
        "validator"],
    function ($, avalon, editor, uploader, bsAlert, csrfTokenHeader) {
        avalon.vmodels.add_contest = null;
        $("#add-contest-form").validator().on('submit', function (e) {
                if (!e.isDefaultPrevented()){
					alert("smoething went wrong!");
				}
				else{	
					var data = {
						title: vm.title, 
							 description: vm.description, 
							 start_time: vm.startTime, 
						end_time: vm.endTime,
						password: vm.password, 
						mode: vm.model, 
						show_rank: vm.openRank
					};
					$.ajax({
								beforeSend: csrfTokenHeader,
								url: "/api/admin/contest/",
								dataType: "json",
								data: data,
								method: "post",
								contentType: "application/json",
								success: function (data) {
									if (!data.code) {
										bsAlert("添加成功！");
												console.log(data);
									}
									else {
										bsAlert(data.data);
										console.log(data);
									}
								}
							});
					console.log(data);
				}
                return false;
        })
        editor("#editor");
        editor("#problemDescriptionEditor");
        editor("#problemHintEditor");
		
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
            problems: [],
            editingProblemId: 0,
            editSamples: [],
            editTestCaseList: [],
            group: "-1",
            groupList: [{name:"Every one", id:1, choosed: false},{name:"Group one", id :3, choosed: false},{name:"Group two", id:5,  choosed: false}],
            choosedGroupList: [],
            showProblemEditArea: function (problemIndex) {
                if (vm.editingProblemId == problemIndex){
                    vm.problems[vm.editingProblemId-1].samples = vm.editSamples;
                    vm.editingProblemId = 0;
                }
                else {
					if (vm.editingProblemId)
					{
						vm.problems[vm.editingProblemId-1].samples = vm.editSamples;
						vm.problems[vm.editingProblemId-1].testCaseList = vm.editTestCaseList;
					}
					vm.editingProblemId = problemIndex;
                    vm.editSamples = [];
                    vm.editSamples = vm.problems[vm.editingProblemId-1].samples;
                    vm.editTestCaseList = [];
                    vm.editTestCaseList = vm.problems[vm.editingProblemId-1].testCaseList;
                }
            },
            passwordUsable: false,
            add_problem: function () {
                var problem = {
                    title: "",
                    timeLimit: 1000,
                    memoryLimit: 256,
                    description: "",
                    samples: [],
                    visible: true,
                    test_case_id: "",
                    testCaseList: [],
                    hint: "",
                    score: 0,
					uploadSuccess: false,
                };
                vm.problems.push(problem);
                vm.showProblemEditArea(vm.problems.length);
            },
            del_problem: function (problemIndex) {
                if (confirm("你确定要删除么?")) {
                    vm.editingProblemId = 0;
                    vm.problems.remove(vm.problems[problemIndex-1]);
                }
            },
            hidden: function () {
                vm.problems[vm.editingProblemId-1].samples = editSamples;
                vm.problems[vm.editingProblemId-1].testCaseList = editTestCaseList;
                vm.editingProblemId = 0;
            },
            toggle: function (item) {
                item.visible = !item.visible;
            },
            add_sample: function () {
                vm.editSamples.push({visible: true, input: "", output: ""});
            },
            del_sample: function (sample) {
                if (confirm("你确定要删除么?")) {
                    editSamples.remove(sample);
                }
            },
            getBtnContent: function (item) {
                if (item.visible)
                    return "折叠";
                return "展开";
            },
            addGroup: function() {
				if (vm.group == -1) return;
				if (vm.groupList[vm.group].id == 1){
					vm.passwordUsable = true;
					vm.choosedGroupList = [];
					for (var key in vm.groupList){
						vm.groupList[key].choosed = true;
					}
				}
				vm.groupList[vm.group]. choosed = true;
				vm.choosedGroupList .push({name:vm.groupList[vm.group].name, index:vm.group, id:vm.groupList[vm.group].id});
			},
			unchoosed: function(groupIndex){
				if (vm.groupList[vm.choosedGroupList[groupIndex].index].id == 1){
					vm.passwordUsable = false;
					for (key in vm.groupList){
						vm.groupList[key].choosed = false;
					}
				}
				vm.groupList[vm.choosedGroupList[groupIndex].index].choosed = false;
				vm.choosedGroupList.remove(vm.choosedGroupList[groupIndex]);
			}
        });
		
		uploader("#uploader", "/api/admin/test_case_upload/", function (file, respond) {
			if (respond.code)
				bsAlert(respond.data);
			else {
					vm.problems[vm.editingProblemId-1].test_case_id = respond.data.test_case_id;
					vm.problems[vm.editingProblemId-1].uploadSuccess = true;
					vm.editTestCaseList = [];
					for (var i = 0; i < respond.data.file_list.input.length; i++) {
						vm.editTestCaseList.push({
							input: respond.data.file_list.input[i],
							output: respond.data.file_list.output[i]
						});
					}
                    vm.problems[vm.editingProblemId-1].testCaseList = vm.editTestCaseList;
					bsAlert("测试数据添加成功！共添加"+vm.editTestCaseList.length +"组测试数据");
			}
		},
		function(){
			if (vm.editingProblemId == 0)
			{
				bsAlert("你还未指定一道题目！");
				return false;
			}
		}
		);
	
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
