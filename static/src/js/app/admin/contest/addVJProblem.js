require(["jquery", "avalon", "bsAlert", "csrfToken"],
    function ($, avalon, bsAlert, csrfTokenHeader) {
        avalon.ready(function () {
            var VJConfig = [{name: "Codeforces", value: "codeforces", url: "http://codeforces.com/problemset"},
                {name: "HDUOJ", value: "hduoj", url: "http://acm.hdu.edu.cn/listproblem.php?vol=1"},
                {name: "POJ", value: "poj", url: "http://poj.org/problemlist"},
                {name: "ZOJ", value: "zoj", url: "http://acm.zju.edu.cn/onlinejudge/showProblemsets.do"},
                {name: "PAT", value: "pat", url: "https://www.patest.cn/contests"}]

            var vm = avalon.define({
                $id: "addVJProblem",
                VJConfig: VJConfig,
                goBack: function (check) {
                    avalon.vmodels.admin.template_url = "template/contest/problem_list.html";
                }
            });
        });
        avalon.scan();

    });
