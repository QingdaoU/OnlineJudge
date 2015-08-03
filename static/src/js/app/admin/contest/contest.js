require(["jquery", "avalon", "editor", "uploader", "datetimepicker",
        "validation"
    ],
    function ($, avalon, editor, uploader) {
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
                alert("1111");
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
            problems: [],
            add_problem: function () {
                var problem = {};
                var problem_id = make_id();
                problem["id"] = problem_id;
                problem["samples"] = [];
                problem["webuploader"] = {};
                problem["toggle_string"] = "折叠";
                vm.problems.push(problem);
                uploader("#problem-" + problem_id + "-uploader");
                console.log(vm.problems);
                $("#add-contest-form").formValidation('addField', $('[name="problem_name[]"]'));
                $("#add-contest-form").formValidation('addField', $('[name="cpu[]"]'));
                $("#add-contest-form").formValidation('addField', $('[name="memory[]"]'));
            },
            del_problem: function (problem) {
                if (confirm("你确定要删除么?")) {
                    vm.problems.remove(problem);
                }
            },
            toggle_problem: function (problem) {
                $("#" + "problem-" + problem.id + "-body").toggle();
                if (problem["toggle_string"] == "展开") {
                    problem["toggle_string"] = "折叠";
                }
                else {
                    problem["toggle_string"] = "展开";
                }
            },
            add_sample: function (problem) {
                problem["samples"].push({"id": make_id(), "toggle_string": "折叠"});
            },
            del_sample: function (problem, sample) {
                if (confirm("你确定要删除么?")) {
                    problem["samples"].remove(sample);
                }
            },
            toggle_sample: function (problem, sample) {
                $("#" + "problem-" + problem.id + "-sampleio-" + sample.id + "-body").toggle();
                if (sample["toggle_string"] == "展开") {
                    sample["toggle_string"] = "折叠";
                }
                else {
                    sample["toggle_string"] = "展开";
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