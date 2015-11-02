require(["jquery", "avalon", "editor", "uploader", "bsAlert", "csrfToken", "tagEditor", "validator", "editorComponent"],
    function ($, avalon, editor, uploader, bsAlert, csrfTokenHeader) {

        avalon.ready(function () {

            $("#edit-problem-form").validator()
                .on('submit', function (e) {
                    if (!e.isDefaultPrevented()) {
                        e.preventDefault();
                        if (vm.testCaseId == "") {
                            bsAlert("你还没有上传测试数据!");
                            return false;
                        }
                        if (avalon.vmodels.contestProblemDescriptionEditor.content == "") {
                            bsAlert("题目描述不能为空!");
                            return false;
                        }
                        if (vm.timeLimit < 30 || vm.timeLimit > 5000) {
                            bsAlert("保证时间限制是一个30-5000的合法整数");
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
                            description: avalon.vmodels.contestProblemDescriptionEditor.content,
                            time_limit: vm.timeLimit,
                            memory_limit: vm.memoryLimit,
                            samples: [],
                            test_case_id: vm.testCaseId,
                            hint: avalon.vmodels.contestProblemHintEditor.content,
                            visible: vm.visible,
                            contest_id: avalon.vmodels.admin.contestId,
                            input_description: vm.inputDescription,
                            output_description: vm.outputDescription,
                            sort_index: vm.sortIndex
                        };

                        if (avalon.vmodels.admin.contestProblemStatus == "edit") {
                            var method = "put";
                            ajaxData["id"] = avalon.vmodels.admin.problemId;
                            var alertContent = "题目编辑成功";
                        }
                        else {
                            var method = "post";
                            var alertContent = "题目创建成功";
                        }

                        for (var i = 0; i < vm.samples.$model.length; i++) {
                            ajaxData.samples.push({
                                input: vm.samples.$model[i].input,
                                output: vm.samples.$model[i].output
                            });
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
                                    bsAlert(alertContent);
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
                    timeLimit: 1000,
                    memoryLimit: 128,
                    samples: [],
                    hint: "",
                    sortIndex: "",
                    visible: true,
                    inputDescription: "",
                    outputDescription: "",
                    testCaseId: "",
                    testCaseList: [],
                    uploadSuccess: false,

                    contestProblemDescriptionEditor: {
                        editorId: "contest-problem-description-editor",
                        placeholder: "题目描述"
                    },
                    contestProblemHintEditor: {
                        editorId: "contest-problem-hint-editor",
                        placeholder: "提示"
                    },

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

                    goBack: function (check) {
                        avalon.vmodels.admin.template_url = "template/contest/problem_list.html";
                    }
                });
            else {
                var vm = avalon.vmodels.editProblem;
                title = "";
                description = "";
                timeLimit = 1000;
                memoryLimit = 128;
                samples = [];
                hint = "";
                sortIndex = "";
                visible = true;
                inputDescription = "";
                outputDescription = "";
                testCaseId = "";
                testCaseList = [];
                uploadSuccess = false;
            }

            var testCaseUploader = uploader("#testCaseFile", "/api/admin/test_case_upload/", function (file, response) {
                if (response.code)
                    bsAlert(response.data);
                else {
                    vm.testCaseId = response.data.test_case_id;
                    vm.testCaseList = [];
                    for (var key in response.data.file_list) {
                        vm.testCaseList.push({
                            input: response.data.file_list[key].input_name,
                            output: response.data.file_list[key].output_name
                        })
                    }
                    vm.uploadSuccess = true;
                    bsAlert("测试数据添加成功！共添加" + vm.testCaseList.length + "组测试数据");
                }
            });

            if (avalon.vmodels.admin.contestProblemStatus == "edit") {
                $.ajax({
                    url: "/api/admin/contest_problem/?contest_problem_id=" + avalon.vmodels.admin.problemId,
                    method: "get",
                    dataType: "json",
                    success: function (data) {
                        if (data.code) {
                            bsAlert(data.data);
                        }
                        else {
                            var problem = data.data;
                            vm.testCaseList = [];
                            vm.sortIndex = problem.sort_index;
                            vm.title = problem.title;
                            avalon.vmodels.contestProblemDescriptionEditor.content = problem.description;
                            vm.timeLimit = problem.time_limit;
                            vm.memoryLimit = problem.memory_limit;
                            vm.hint = problem.hint;
                            vm.visible = problem.visible;
                            vm.inputDescription = problem.input_description;
                            vm.outputDescription = problem.output_description;
                            vm.score = problem.score;
                            vm.testCaseId = problem.test_case_id;
                            vm.samples = [];
                            for (var i = 0; i < problem.samples.length; i++) {
                                vm.samples.push({
                                    input: problem.samples[i].input,
                                    output: problem.samples[i].output,
                                    visible: false
                                })
                            }
                            avalon.vmodels.contestProblemHintEditor.content = problem.hint;
                            $.ajax({
                                url: "/api/admin/test_case_upload/?test_case_id=" + vm.testCaseId,
                                method: "get",
                                dataType: "json",
                                success: function (response) {
                                    if (response.code) {
                                        bsAlert(response.data);
                                    }
                                    else {
                                        vm.testCaseList = [];
                                        for (var key in response.data.file_list) {
                                            vm.testCaseList.push({
                                                input: response.data.file_list[key].input_name,
                                                output: response.data.file_list[key].output_name
                                            })
                                        }
                                        vm.uploadSuccess = true;
                                    }
                                }
                            })
                        }
                    }
                });


            }
        });
        avalon.scan();

    });
