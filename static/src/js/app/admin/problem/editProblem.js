require(["jquery", "avalon", "editor", "uploader", "bsAlert", "csrfToken", "tagEditor", "validator", "jqueryUI"],
    function ($, avalon, editor, uploader, bsAlert, csrfTokenHeader) {

        avalon.ready(function () {

            $("#edit-problem-form").validator()
                .on('submit', function (e) {
                    if (!e.isDefaultPrevented()) {
                        if (vm.testCaseId == "") {
                            bsAlert("你还没有上传测试数据!");
                            return false;
                        }
                        if (vm.description == "") {
                            bsAlert("题目描述不能为空!");
                            return false;
                        }
                        if (vm.timeLimit < 100 || vm.timeLimit > 5000) {
                            bsAlert("保证时间限制是一个100-5000的合法整数");
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
                        var tags = $("#tags").tagEditor("getTags")[0].tags;
                        if (tags.length == 0) {
                            bsAlert("请至少添加一个标签，这将有利于用户发现你的题目!");
                            return false;
                        }
                        var ajaxData = {
                            id: avalon.vmodels.admin.problemId,
                            title: vm.title,
                            description: vm.description,
                            time_limit: vm.timeLimit,
                            memory_limit: vm.memoryLimit,
                            samples: [],
                            test_case_id: vm.testCaseId,
                            hint: vm.hint,
                            source: vm.source,
                            visible: vm.visible,
                            tags: tags,
                            input_description: vm.inputDescription,
                            output_description: vm.outputDescription,
                            difficulty: vm.difficulty
                        };

                        for (var i = 0; i < vm.samples.$model.length; i++) {
                            ajaxData.samples.push({
                                input: vm.samples.$model[i].input,
                                output: vm.samples.$model[i].output
                            });
                        }

                        $.ajax({
                            beforeSend: csrfTokenHeader,
                            url: "/api/admin/problem/",
                            dataType: "json",
                            data: JSON.stringify(ajaxData),
                            method: "put",
                            contentType: "application/json;charset=UTF-8",
                            success: function (data) {
                                if (!data.code) {
                                    bsAlert("题目编辑成功！");
                                    vm.showProblemListPage();
                                }
                                else {
                                    bsAlert(data.data);
                                }
                            }

                        });
                        return false;
                    }
                });
            if (avalon.vmodels.editProblem) {
                var vm = avalon.vmodels.editProblem;
            }
            else
                var vm = avalon.define({
                    $id: "editProblem",
                    title: "",
                    description: "",
                    timeLimit: -1,
                    memoryLimit: -1,
                    samples: [],
                    hint: "",
                    visible: true,
                    difficulty: 0,
                    inputDescription: "",
                    outputDescription: "",
                    testCaseIdd: "",
                    uploadSuccess: false,
                    source: "",
                    testCaseList: [],
                    uploadProgress: 0,
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
                    showProblemListPage: function () {
                        avalon.vmodels.admin.template_url = "template/problem/problem_list.html";
                    }
                });
            var hintEditor = editor("#hint");
            var descriptionEditor = editor("#problemDescription");
            var testCaseUploader = uploader("#testCaseFile", "/api/admin/test_case_upload/",
                function (file, response) {
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
                },
                function (file, percentage) {
                    vm.uploadProgress = percentage;
                }
            );

            $.ajax({
                url: "/api/admin/problem/?problem_id=" + avalon.vmodels.admin.problemId,
                method: "get",
                dataType: "json",
                success: function (data) {
                    if (data.code) {
                        bsAlert(data.data);
                    }
                    else {
                        var problem = data.data;
                        vm.title = problem.title;
                        vm.description = problem.description;
                        vm.timeLimit = problem.time_limit;
                        vm.memoryLimit = problem.memory_limit;
                        for (var i = 0; i < problem.samples.length; i++) {
                            vm.samples.push({
                                input: problem.samples[i].input,
                                output: problem.samples[i].output,
                                visible: false
                            })
                        }
                        vm.hint = problem.hint;
                        vm.visible = problem.visible;
                        vm.difficulty = problem.difficulty;
                        vm.inputDescription = problem.input_description;
                        vm.outputDescription = problem.output_description;
                        vm.testCaseId = problem.test_case_id;
                        vm.source = problem.source;
                        var problemTags = problem.tags;
                        hintEditor.setValue(vm.hint);
                        descriptionEditor.setValue(vm.description);
                        $.ajax({
                            url: "/api/admin/tag/",
                            dataType: "json",
                            method: "get",
                            success: function (data) {
                                if (!data.code) {
                                    var tagAutoCompleteList = [], tags = [];
                                    for (var i = 0; i < data.data.length; i++) {
                                        tagAutoCompleteList.push(data.data[i].name);
                                    }
                                    for (var j = 0; j < problem.tags.length; j++) {
                                        tags.push(problemTags[j].name);
                                    }
                                    $("#tags").tagEditor({
                                        initialTags: tags,
                                        autocomplete: {
                                            delay: 0,
                                            position: {collision: 'flip'},
                                            source: tagAutoCompleteList
                                        }
                                    });
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