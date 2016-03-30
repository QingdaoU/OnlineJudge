require(["jquery", "avalon", "csrfToken", "bsAlert", "validator", "pager"],
    function ($, avalon, csrfTokenHeader, bsAlert, editor) {
        avalon.ready(function () {

            if (avalon.vmodels.judges) {
                var vm = avalon.vmodels.judges;
            }
            else {
                var vm = avalon.define({
                    $id: "judges",
                    judgesList: [],
                    isEditing: false,
                    showEnableOnly: false,

                    //编辑器同步变量
                    max_instance_number: 0,
                    ipAddress: "",
                    port: 0,
                    status: true,
                    judgesId: -1,
                    name: "",
                    token: "",
                    id: 0,
                    pager: {
                        getPage: function (page) {
                            getPage(page);
                        }
                    },
                    editJudges: function (judges) {
                        vm.id = judges.id;
                        vm.name = judges.name;
                        vm.judgesId = judges.id;
                        vm.status = judges.status;
                        vm.port = judges.port;
                        vm.ipAddress = judges.ip;
                        vm.max_instance_number = judges.max_instance_number;
                        vm.token = judges.token;
                        vm.isEditing = true;
                    },
                    cancelEdit: function () {
                        vm.isEditing = false;
                    }
                });
                vm.$watch("showEnableOnly", function () {
                    getPage(1);
                    avalon.vmodels.judgesPager.currentPage = 1;
                });
            }

            function getPage(page) {
                var url = "/api/admin/judges/?paging=true&page=" + page + "&page_size=20";
                if (vm.showEnableNnly)
                    url += "&status=true";
                $.ajax({
                    url: url,
                    method: "get",
                    success: function (data) {
                        if (!data.code) {
                            vm.judgesList = data.data.results;
                            avalon.vmodels.judgesPager.totalPage = data.data.total_page;
                        }
                        else {
                            bsAlert(data.data);
                        }
                    }
                });
            }

            $("#judges-form").validator().on('submit', function (e) {
                if (!e.isDefaultPrevented()) {
                    var name = $("#name").val();
                    var max_instance_number = $("#max_instance_number").val();
                    var ip = $("#ipAddress").val();
                    var port = $("#port").val();
                    var token = $("#token").val();
                    $.ajax({
                        url: "/api/admin/judges/",
                        contentType: "application/json",
                        data: JSON.stringify({
                            name: name,
                            ip: ip,
                            port: port,
                            token: token,
                            max_instance_number: max_instance_number
                        }),
                        dataType: "json",
                        method: "post",
                        success: function (data) {
                            if (!data.code) {
                                bsAlert("提交成功！");
                                $("#name").val("");
                                $("#max_instance_number").val("");
                                $("#ipAddress").val("");
                                $("#port").val("");
                                $("#token").val("");
                                getPage(1);
                            } else {
                                bsAlert(data.data);
                            }
                        }
                    });
                    return false;
                }
            });

            $("#edit-judges-form").validator().on('submit', function (e) {
                if (!e.isDefaultPrevented()) {
                    var name = vm.name;
                    var max_instance_number = vm.max_instance_number;
                    var ip = vm.ipAddress;
                    var port = vm.port;
                    var token = vm.token;
                    var status = vm.status;
                    var id = vm.id;
                    $.ajax({
                        url: "/api/admin/judges/",
                        contentType: "application/json",
                        data: JSON.stringify({
                            id: id,
                            name: name,
                            ip: ip,
                            port: port,
                            token: token,
                            max_instance_number: max_instance_number,
                            status: status
                        }),
                        dataType: "json",
                        method: "put",
                        success: function (data) {
                            if (!data.code) {
                                bsAlert("提交成功！");
                                getPage(1);
                            } else {
                                bsAlert(data.data);
                            }
                        }
                    });
                    return false;
                }
            });
        });
        avalon.scan();
    });