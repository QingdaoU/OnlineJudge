require(["jquery", "avalon", "editor", "uploader", "bsAlert",
        "csrfToken", "tagEditor", "validator", "editorComponent", "testCaseUploader", "spj"],
    function ($, avalon, editor, uploader, bsAlert, csrfTokenHeader) {

        avalon.ready(function () {

            $("#edit-problem-form").validator()
                .on('submit', function (e) {
                    if (!e.isDefaultPrevented()) {
                        e.preventDefault();
                        if (!avalon.vmodels.testCaseUploader.uploaded) {
                            bsAlert("你还没有上传测试数据!");
                            return false;
                        }
                        if (avalon.vmodels.contestProblemDescriptionEditor.content == "") {
                            bsAlert("题目描述不能为空!");
                            return false;
                        }
                        if (vm.timeLimit < 1 || vm.timeLimit > 10000) {
                            bsAlert("保证时间限制是一个1-10000的整数");
                            return false;
                        }
                        if (vm.memoryLimit < 16) {
                            bsAlert("最低内存不能低于16M(注意:Java最低需要内存32M)");
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
                        var spjVM = avalon.vmodels.spjConfig;
                        if (spjVM.spj && !spjVM.spjCode){
                            bsAlert("请填写Special Judge的代码");
                            return false;
                        }
                        var ajaxData = {
                            title: vm.title,
                            description: avalon.vmodels.contestProblemDescriptionEditor.content,
                            time_limit: vm.timeLimit,
                            memory_limit: vm.memoryLimit,
                            samples: [],
                            test_case_id: avalon.vmodels.testCaseUploader.testCaseId,
                            hint: avalon.vmodels.contestProblemHintEditor.content,
                            visible: vm.visible,
                            contest_id: avalon.vmodels.admin.contestId,
                            input_description: vm.inputDescription,
                            output_description: vm.outputDescription,
                            sort_index: vm.sortIndex,
                            spj: spjVM.spj
                        };
                        if (spjVM.spj) {
                            ajaxData.spj_language = spjVM.spjLanguage;
                            ajaxData.spj_code = spjVM.spjCode;
                        }

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
                                    avalon.vmodels.admin.template_url = "template/contest/problem_list.html";
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
                    samples: [{input: "", output: "", "visible": true}],
                    hint: "",
                    sortIndex: "",
                    visible: true,
                    inputDescription: "",
                    outputDescription: "",
                    testCaseId: "",
                    testCaseList: [],

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
                vm.title = "";
                vm.description = "";
                vm.timeLimit = 1000;
                vm.memoryLimit = 128;
                vm.samples = [];
                vm.hint = "";
                vm.sortIndex = "";
                vm.visible = true;
                vm.inputDescription = "";
                vm.outputDescription = "";
                vm.testCaseId = "";
                vm.testCaseList = [];
            }

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
                            avalon.vmodels.testCaseUploader.setTestCase(problem.test_case_id);
                            vm.samples = [];
                            for (var i = 0; i < problem.samples.length; i++) {
                                vm.samples.push({
                                    input: problem.samples[i].input,
                                    output: problem.samples[i].output,
                                    visible: false
                                })
                            }
                            avalon.vmodels.contestProblemHintEditor.content = problem.hint;
                            var spjVM = avalon.vmodels.spjConfig;
                            spjVM.spj = problem.spj;
                            // spjLanguage可能是null
                            spjVM.spjLanguage = problem.spj_language=="2"?"2":"1";
                            spjVM.spjCode = problem.spj_code;
                        }
                    }
                });


            }
        });
        avalon.scan();

    });
