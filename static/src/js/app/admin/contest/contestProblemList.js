require(["jquery", "avalon", "csrfToken", "bsAlert"], function ($, avalon, csrfTokenHeader, bsAlert) {

    avalon.ready(function () {
        if (avalon.vmodels.contestProblemList) {
            vm = avalon.vmodels.contestProblemList;
        }
        else {
            var vm = avalon.define({
                $id: "contestProblemList",
                problemList: [],
                showEditProblemPage: function (problemId) {
                    avalon.vmodels.admin.contestProblemStatus = "edit";
                    avalon.vmodels.admin.problemId = problemId;
                    avalon.vmodels.admin.template_url = "template/contest/edit_problem.html";
                },
                addProblem: function(){
                    avalon.vmodels.admin.contestProblemStatus = "add";
                    avalon.vmodels.admin.template_url = "template/contest/edit_problem.html";
                },
                goBack: function(){
                    avalon.vmodels.admin.template_url = "template/contest/contest_list.html"
                }
            });
        }

        $.ajax({
            url: "/api/admin/contest_problem/?contest_id=" + avalon.vmodels.admin.contestId,
            dataType: "json",
            method: "get",
            success: function (data) {
                if (!data.code) {
                    vm.problemList = data.data;
                }
                else {
                    bsAlert(data.data);
                }
            }
        });

        avalon.scan();
    });

});
