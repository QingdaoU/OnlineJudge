require(["jquery", "avalon", "bsAlert", "csrfToken", "validator"],
    function ($, avalon, bsAlert, csrfTokenHeader) {
        avalon.ready(function () {
            $("#add-vj-problem-form").validator()
                .on('submit', function (e) {
                    if (!e.isDefaultPrevented()) {
                        e.preventDefault();
                        if (!vm.VJProblemUrl) {
                            bsAlert("请输入题目URL");
                            return;
                        }
                        if (!vm.VJName) {
                            bsAlert("请选择一个OJ");
                            return;
                        }
                        function _addVJProblem() {
                            $.ajax({
                                url: "/api/admin/contest_vj_problem/",
                                method: "post",
                                data: {oj: vm.VJName, url: vm.VJProblemUrl, contest_id: avalon.vmodels.admin.contestId},
                                success: function (data) {
                                    if(data.code || data.data.status == 2) {
                                        bsAlert(data.data);
                                        return false;
                                    }
                                    else {
                                        if(data.data.status == 1) {
                                            setTimeout(function(){
                                                _addVJProblem();
                                            }, 1000);
                                        }
                                        else {
                                            bsAlert("题目创建成功");
                                            vm.goBack();
                                        }
                                    }
                                }
                            })
                        }
                        _addVJProblem();
                    }
                    return false;
                });
            var VJConfig = [{name: "Codeforces", value: "codeforces", url: "http://codeforces.com/problemset"},
                {name: "HDUOJ", value: "hduoj", url: "http://acm.hdu.edu.cn/listproblem.php?vol=1"},
                {name: "POJ", value: "poj", url: "http://poj.org/problemlist"},
                {name: "ZOJ", value: "zoj", url: "http://acm.zju.edu.cn/onlinejudge/showProblemsets.do"},
                {name: "PAT", value: "pat", url: "https://www.patest.cn/contests"}];

            var vm = avalon.define({
                $id: "addVJProblem",
                VJConfig: VJConfig,
                VJProblemUrl: "",
                VJName: "",
                goBack: function (check) {
                    avalon.vmodels.admin.template_url = "template/contest/problem_list.html";
                }
            });
        });
        avalon.scan();

    });
