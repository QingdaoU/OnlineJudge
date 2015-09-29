require(["jquery", "avalon", "editor", "uploader", "bsAlert", "csrfToken", "tagEditor", "validator", "jqueryUI"],
    function ($, avalon, editor, uploader, bsAlert, csrfTokenHeader) {

        avalon.ready(function () {

            $("#edit-problem-form").validator()
                .on('submit', function (e) {
                    if (!e.isDefaultPrevented()){
                        e.preventDefault();
                        if (vm.testCaseId == "") {
                            bsAlert("你还没有上传测试数据!");
                            return false;
                        }
                        if (vm.description == "") {
                            bsAlert("题目描述不能为空!");
                            return false;
                        }
                        if (vm.timeLimit < 1000 || vm.timeLimit > 5000) {
                            bsAlert("保证时间限制是一个1000-5000的合法整数");
                            return false;
                        }
                        if (vm.samples.length == 0) {
                            bsAlert("请至少添加一组样例!");
                            return false;
                        }
                        for (var i = 0; i < vm.samples.length; i++) {
                            if (vm.samples[i].input == "" || vm.samples[i].output == "") {
                                bsAlert("样例输入与样例输出不能为空！");
                                return false;
                            }
                        }
                        var ajaxData = {
                            title: vm.title,
                            description: vm.description,
                            time_limit: vm.timeLimit,
                            memory_limit: vm.memoryLimit,
                            samples: [],
                            test_case_id: vm.testCaseId,
                            hint: vm.hint,
                            visible:            vm.visible,
                            contest_id:         avalon.vmodels.admin.$contestId,
                            input_description:  vm.inputDescription,
                            output_description: vm.outputDescription,
                            sort_index:         vm.sortIndex,
                        };
                        if (vm.contestMode == '2') {
                            if (!vm.score) {
                                bsAlert("请输入有效的分值!")
                                return false;
                            }
                            ajaxData.score = vm.score;
                        }
                        var method = "post";
                        if (avalon.vmodels.admin.$problemId) {
                            method = "put";
                            ajaxData.id = avalon.vmodels.admin.$problemId;
                        }

                        for (var i = 0; i < vm.samples.$model.length; i++) {
                            ajaxData.samples.push({input: vm.samples.$model[i].input, output: vm.samples.$model[i].output});
                        }

                        $.ajax({
                            beforeSend: csrfTokenHeader,
                            url: "/api/admin/contest_problem/",
                            dataType: "json",
                            data: JSON.stringify(ajaxData),
                            method: method,
                            contentType: "application/json;charset=UTF-8",
                            success: function (data) {
                                if (!data.code) {
                                    bsAlert("题目编辑成功！");
                                    vm.goBack(true);
                                }
                                else {
                                    bsAlert(data.data);
                                }
                            }

                        });
                        return false;
                    }
                });

        if (!avalon.vmodels.editProblem)
            var vm = avalon.define({
                $id: "editProblem",
                title: "",
                description: "",
                timeLimit: 0,
                memoryLimit: 0,
                samples: [],
                hint: "",
                sortIndex: "",
                visible: true,
                inputDescription: "",
                outputDescription: "",
                testCaseIdd: "",
                contestMode: 0,
                score: 1,
                uploadSuccess: false,
                testCaseList: [],
                addSample: function () {
                    vm.samples.push({input: "", output: "", "visible": true});
                },
                delSample: function (sample) {
                    if (confirm("你确定要删除么?")) {
                        vm.samples.remove(sample);
                    }
                },
                toggleSample: function (sample) {
                    sample.visible = !sample.visible;
                },
                getBtnContent: function (item) {
                    if (item.visible)
                        return "折叠";
                    return "展开";
                },
                goBack: function(check){
                    if (check||confirm("这将丢失所有的改动,确定要继续么?")) {
                        vm.$fire("up!showContestListPage");
                    }
                }
            });
        else
            vm = avalon.vmodels.editProblem;

            var hintEditor = editor("#hint");
            var descriptionEditor = editor("#problemDescription");
            var testCaseUploader = uploader("#testCaseFile", "/api/admin/test_case_upload/", function (file, response) {
                if (response.code)
                    bsAlert(response.data);
                else {
                    vm.testCaseId = response.data.test_case_id;
                    vm.uploadSuccess = true;
                    vm.testCaseList = [];
                    for (var i = 0; i < response.data.file_list.input.length; i++) {
                        vm.testCaseList.push({
                            input: response.data.file_list.input[i],
                            output: response.data.file_list.output[i]
                        });
                    }
                    bsAlert("测试数据添加成功！共添加" + vm.testCaseList.length + "组测试数据");
                }
            });

            vm.contestMode = avalon.vmodels.admin.$contestMode;
            if (avalon.vmodels.admin.$problemId){
                $.ajax({
                    url: "/api/admin/contest_problem/?contest_problem_id=" + avalon.vmodels.admin.$problemId,
                    method: "get",
                    dataType: "json",
                    success: function (data) {
                        if (data.code) {
                            bsAlert(data.data);
                        }
                        else {  // Edit mode    load the problem data
                            var problem = data.data;
                            vm.testCaseList      = [];
                            vm.sortIndex         = problem.sort_index;
                            vm.title             = problem.title;
                            vm.description       = problem.description;
                            vm.timeLimit         = problem.time_limit;
                            vm.memoryLimit       = problem.memory_limit;
                            vm.hint              = problem.hint;
                            vm.visible           = problem.visible;
                            vm.inputDescription  = problem.input_description;
                            vm.outputDescription = problem.output_description;
                            vm.score             = problem.score;
                            vm.samples           = [];
                            vm.testCaseId        = problem.test_case_id;
                            for (var i = 0; i < problem.samples.length; i++) {
                                vm.samples.push({
                                    input: problem.samples[i].input,
                                    output: problem.samples[i].output,
                                    visible: false
                                })
                            }
                            hintEditor.setValue(vm.hint);
                            descriptionEditor.setValue(vm.description);
                        }
                    }
                });
            }
            else {   //Create new problem    Set default values
                vm.testCaseList      = [];
                vm.title             = "";
                vm.timeLimit         = 1000;
                vm.memoryLimit       = 256;
                vm.samples           = [];
                vm.visible           = true;
                vm.inputDescription  = "";
                vm.outputDescription = "";
                vm.testCaseId        = "";
                vm.sortIndex         = "";
                vm.score             = 0;
                hintEditor.setValue("");
                descriptionEditor.setValue("");
            }
        });
        avalon.scan();

    });
