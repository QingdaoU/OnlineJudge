define("testCaseUploader", ["avalon", "uploader", "bsAlert", "jquery"], function(avalon, uploader, bsAlert, $){
    avalon.component("ms:testcaseuploader", {
        $template: '<div class="col-md-12">' +
        '<br> ' +
        '<label>测试数据</label><br> ' +
        '<small class="text-info">' +
        '请将所有测试用例打包在一个文件中上传，' +
        '所有文件要在压缩包的根目录，' +
        '且输入输出文件名要以从1开始连续数字标识要对应例如：' +
        '<br>1.in 1.out 2.in 2.out </small> ' +
        '<p>上传进度<span ms-text="uploadProgress"></span>%</p> ' +
        '<table class="table table-striped" ms-visible="uploaded"> ' +
        '<tr> <td>编号</td> <td>输入文件名</td> <td>输出文件名</td> </tr> ' +
        '<tr ms-repeat="testCaseList"> ' +
        '<td>{{ $index + 1 }}</td> ' +
        '<td>{{ el.input }}</td> ' +
        '<td>{{ el.output }}</td> </tr> ' +
        '</table> ' +
        '</div> ' +
        '<div class="col-md-12"> ' +
        '<div class="form-group">' +
        ' <div id="testCaseFileSelector">选择文件</div> ' +
        '</div> ' +
        '</div>',
        testCaseId: "",
        testCaseList: [],
        uploaded: false,
        uploadProgress: 0,

        setTestCaseId: function(){},

        $init: function(vm, el){
            vm.setTestCase = function(testCaseId){
                vm.testCaseId = testCaseId;
                $.ajax({
                    url: "/api/admin/test_case_upload/?test_case_id=" + testCaseId,
                    method: "get",
                    success: function(data){
                        if(data.code){
                            bsAlert("获取测试用例列表失败");
                        }
                        else{
                            for(var key in data.data.file_list){
                                vm.testCaseList.push({
                                    input: data.data.file_list[key].input_name,
                                    output: data.data.file_list[key].output_name
                                })
                            }
                            vm.uploaded = true;
                            vm.uploadProgress = 100;
                        }
                    }
                });

            }
        },

        $ready: function(vm, el){
            el.msRetain = true;
            var testCaseUploader = uploader("#testCaseFileSelector", "/api/admin/test_case_upload/",
                function (file, response) {
                    if (response.code) {
                        bsAlert(response.data);
                    }
                    else {
                        vm.testCaseId = response.data.test_case_id;
                        vm.uploaded = true;
                        vm.testCaseList = [];
                        for(var key in response.data.file_list){
                            vm.testCaseList.push({
                                input: response.data.file_list[key].input_name,
                                output: response.data.file_list[key].output_name
                            })
                        }
                        bsAlert("测试数据添加成功！共添加" + vm.testCaseList.length + "组测试数据");
                    }
                },
                function (file, percentage) {
                    vm.uploadProgress = parseInt(percentage * 100);
                });
        }
    })
});