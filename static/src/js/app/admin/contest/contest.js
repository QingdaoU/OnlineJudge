require(["jquery", "avalon", "editor", "uploader", "datetimepicker",
        "validation","tagEditor"],
    function ($, avalon, editor, uploader) {
        avalon.vmodels.add_contest = null;
        $("#add-contest-form")
            .formValidation({
                framework: "bootstrap",
                fields: {
                    name: {
                        validators: {
                            notEmpty: {
                                message: "请填写比赛名称"
                            },
                            stringLength: {
                                min: 1,
                                max: 30,
                                message: "名称不能超过30个字"
                            }
                        }
                    },
                    description: {
                        validators: {
                            notEmpty: {
                                message: "请输入描述"
                            }
                        }
                    },
                    start_time: {
                        validators: {
                            notEmpty: {
                                message: "请填写开始时间"

                            },
                            date: {
                                format: "YYYY-MM-DD h:m",
                                message: "请输入一个正确的日期格式"
                            }
                        }
                    },
                    end_time: {
                        validators: {
                            notEmpty: {
                                message: "请填写结束时间"
                            },
                            date: {
                                format: "YYYY-MM-DD h:m",
                                message: "请输入一个正确的日期格式"
                            }
                        }
                    },
                    password: {
                        validators: {
                            stringLength: {
                                min: 0,
                                max: 30,
                                message: "密码不能超过10个字符"
                            }
                        }
                    },
                    "problem_name[]": {
                        validators: {
                            notEmpty: {
                                message: "请输入题目名称"
                            },
                            stringLength: {
                                min: 1,
                                max: 30,
                                message: "题目不能超过30个字符"
                            }
                        }
                    },
                    "cpu[]": {
                        validators: {
                            notEmpty: {
                                message: "请输入cpu时间"
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
                    "memory[]": {
                        validators: {
                            notEmpty: {
                                message: "请输入内存"
                            },
                            integer: {
                                message: "请输入一个合法的数字"
                            }
                        }
                    }
                }
            })
            .on("success.form.fv", function (e) {
                e.preventDefault();
                var data = {
                    title: vm.title, description: vm.description, start_time: vm.startTime, end_time: vm.endTime,
                    password: vm.password, model: vm.model, open_rank: vm.openRank, problems: []
                };
                for (var i = 0; i < vm.problems.length; i++) {
                    var problem = {
                        title: vm.problems[i].title, description: vm.problems[i].description,
                        cpu: vm.problems[i].cpu, memory: vm.problems[i].memory, samples: []
                    };
                    for (var j = 0; j < vm.problems[i].samples.length; j++) {
                        problem.samples.push({
                            input: vm.problems[i].samples[j].input,
                            output: vm.problems[i].samples[j].output
                        })
                    }
                    data.problems.push(problem);
                }
                console.log(data);
            });
        function make_id() {
            var text = "";
            var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
            for (var i = 0; i < 5; i++)
                text += possible.charAt(Math.floor(Math.random() * possible.length));
            return text;
        }


        var editor1 = editor("#editor");

        var vm = avalon.define({
            $id: "add_contest",
            title: "",
            description: "",
            startTime: "",
            endTime: "",
            password: "",
            model: "",
            openRank: false,
            problems: [],
            add_problem: function () {
                var problem_id = make_id();
                var problem = {
                    id: problem_id,
                    title: "",
                    cpu: "",
                    memory: "",
                    description: "",
                    samples: [],
                    visible: true,
                    test_case_id: "",
                    testCaseList: [],
                    hint: "",
                    isVisible: false,
                    difficulty: 0,
                    tags: [],
                    tag: ""
                };
                vm.problems.push(problem);
                var id = vm.problems.length - 1;
                editor("#problem-" + problem_id + "-description");
                var hinteditor = editor("#problem-" + problem_id +"-hint");
                $("#problem-" + problem_id +"-tags").tagEditor();
                uploader("#problem-" + problem_id + "-uploader", "/api/admin/test_case_upload/", function (file, respond) {
                    console.log(respond);
                    if (respond.code)
                        bs_alert(respond.data);
                    else {
                        vm.problems[id].test_case_id = respond.data.test_case_id;
                        vm.problems[id].uploadSuccess = true;
                        vm.problems[id].testCaseList = [];
                        for (var i = 0; i < respond.data.file_list.input.length; i++) {
                            vm.problems[id].push({
                                input: respond.data.file_list.input[i],
                                output: respond.data.file_list.output[i]
                            });
                        }
                    }
                });
                $("#add-contest-form").formValidation('addField', $('[name="problem_name[]"]'));
                $("#add-contest-form").formValidation('addField', $('[name="cpu[]"]'));
                $("#add-contest-form").formValidation('addField', $('[name="memory[]"]'));
            },
            del_problem: function (problem) {
                if (confirm("你确定要删除么?")) {
                    vm.problems.remove(problem);
                }
            },
            toggle: function (item) {
                item.visible = !item.visible;
            },
            add_sample: function (problem) {
                problem.samples.push({id: make_id(), visible: true, input: "", output: ""});
            },
            del_sample: function (problem, sample) {
                if (confirm("你确定要删除么?")) {
                    problem.samples.remove(sample);
                }
            },
            getBtnContent: function (item) {
                if (item.visible)
                    return "折叠";
                return "展开";
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
        $("#contest_start_time").datetimepicker()
            .on("hide", function (ev) {
                $("#add-contest-form")
                    .formValidation("revalidateField", "start_time");
            });
        $("#contest_end_time").datetimepicker()
            .on("hide", function (ev) {
                $("#add-contest-form")
                    .formValidation("revalidateField", "end_time");
            });
    });