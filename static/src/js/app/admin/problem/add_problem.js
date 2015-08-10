require(["jquery", "avalon", "editor", "uploader", "tagEditor", "validation"],
    function ($, avalon, editor, uploader) {
        avalon.vmodels.add_problem = null;
        $("#add-problem-form")
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
                    description:{
                        validators: {
                            notEmpty: {
                                message: "请输入描述"
                            }
                        }
                    },
                    cpu: {
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
                    memory: {
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
                var ajaxData = {
                    title: vm.title,
                    description: vm.description,
                    cpu: vm.cpu,
                    memory: vm.memory,
                    samples: []
                };

                for (var i = 0; i < vm.samples.length; i++) {
                    ajaxData.samples.push({input: vm.samples[i].input, output: vm.samples[i].output});
                }
                console.log(ajaxData);
            });
        var problemDiscription = editor("#problemDescription");
        var testCaseUploader = uploader("#testCaseFile", "/admin/api/testCase");//{
        var hinteditor = editor("#hint");
        /*auto: true,
         swf: '/static/js/lib/webuploader/Uploader.swf',
         server: 'http://webuploader.duapp.com/server/fileupload.php',
         multiple:false,
         accept: {
         title: 'Zip',
         extensions: 'zip',
         mimeTypes: 'zip/*'
         }*/
        // });
        $("#tags").tagEditor();
        var vm = avalon.define({
            $id: "add_problem",
            title: "",
            description: "",
            cpu: 0,
            memory: 0,
            samples: [],
            hint: "",
            visible: false,
            difficulty: 0,
            tags: [],
            tag: "",
            checkTag: function () {
                alert("11");
                if (event.keyCode == 13)
                {
                    alert("You press the enter key!");
                    return false;
                }
            },
            add_sample: function () {
                vm.samples.push({input: "", output: "", "visible": true});
            },
            del_sample: function (sample) {
                if (confirm("你确定要删除么?")) {
                    vm.samples.remove(sample);
                }
            },
            toggle_sample: function (sample) {
                sample.visible = !sample.visible;
            },
            getBtnContent: function (item) {
                if (item.visible)
                    return "折叠";
                return "展开";
            }
        });
        function checkTags(e)
        {
            e.preventDefault();
        }
        //$("#tag").bind("keydown", checkTags(evevt));
        avalon.scan();
    });