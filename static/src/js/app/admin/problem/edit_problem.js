require(["jquery", "avalon", "editor", "uploader", "bsAlert", "csrfToken", "tagEditor", "formValidation", "jqueryUI"],
    function ($, avalon, editor, uploader, bsAlert, csrfTokenHeader) {

        avalon.ready(function () {
            avalon.vmodels.editProblem = null;

            $("#edit-problem-form")
                .formValidation({
                    framework: "bootstrap",
                    fields: {
                        title: {
                            validators: {
                                notEmpty: {
                                    message: "请填写题目名称"
                                },
                                stringLength: {
                                    min: 1,
                                    max: 30,
                                    message: "名称不能超过30个字"
                                }
                            }
                        },
                        cpu: {
                            validators: {
                                notEmpty: {
                                    message: "请输入时间限制"
                                },
                                integer: {
                                    message: "请输入一个合法的数字"
                                },
                                between: {
                                    inclusive: true,
                                    min: 1,
                                    max: 5000,
                                    message: "只能在1-5000之间"
                                }
                            }
                        },
                        memory: {
                            validators: {
                                notEmpty: {
                                    message: "请输入内存限制"
                                },
                                integer: {
                                    message: "请输入一个合法的数字"
                                }
                            }
                        },
                        difficulty: {
                            validators: {
                                notEmpty: {
                                    message: "请输入难度"
                                },
                                integer: {
                                    message: "难度用一个整数表示"
                                }
                            }
                        },
                        input_description: {
                            validators: {
                                notEmpty: {
                                    message: "请填写输入描述"
                                }
                            }
                        },
                        output_description: {
                            validators: {
                                notEmpty: {
                                    message: "请填写输出描述"
                                }
                            }
                        }
                    }
                })
                .on("success.form.fv", function (e) {
                    e.preventDefault();
                    if (vm.testCaseId == "") {
                        bsAlert("你还没有上传测试数据!");
                        return;
                    }
                    if (vm.description == "") {
                        bsAlert("题目描述不能为空!");
                        return;
                    }
                    if (vm.samples.length == 0) {
                        bsAlert("请至少添加一组样例!");
                        return;
                    }
                    for (var i = 0; i < vm.samples.length; i++) {
                        if (vm.samples[i].input == "" || vm.samples[i].output == "") {
                            bsAlert("样例输入与样例输出不能为空！");
                            return;
                        }
                    }
                    if (tags.length == 0) {
                        bsAlert("请至少添加一个标签，这将有利于用户发现你的题目!");
                        return;
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
                        tags: $("#tags").tagEditor("getTags")[0].tags,
                        input_description: vm.inputDescription,
                        output_description: vm.outputDescription,
                        difficulty: vm.difficulty
                    };

                    for (var i = 0; i < vm.samples.$model.length; i++) {
                        ajaxData.samples.push({input: vm.samples.$model[i].input, output: vm.samples.$model[i].output});
                    }

                    $.ajax({
                        beforeSend: csrfTokenHeader,
                        url: "/api/admin/problem/",
                        dataType: "json",
                        data: JSON.stringify(ajaxData),
                        method: "put",
                        contentType: "application/json",
                        success: function (data) {
                            if (!data.code) {
                                bsAlert("题目编辑成功！");
                            }
                            else {
                                bsAlert(data.data);
                            }
                        }

                    })
                });

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
                showProblemListPage: function(){
                    vm.$fire("up!showProblemListPage");
                }
            });
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
                        console.log(problem);
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