require(["jquery", "avalon", "csrfToken", "bsAlert", "pager"], function ($, avalon, csrfTokenHeader, bsAlert) {

    avalon.ready(function () {
        if(avalon.vmodels.problemList){
            vm = avalon.vmodels.problemList;
        }
        else {
            var vm = avalon.define({
                $id: "problemList",
                problemList: [],

                keyword: "",
                showVisibleOnly: false,

                pager: {
                    getPage: function (page) {
                        getPage(page);
                    }
                },

                showEditProblemPage: function (problemId) {
                    avalon.vmodels.admin.problemId = problemId;
                    avalon.vmodels.admin.template_url = "template/problem/edit_problem.html";
                },
                showProblemSubmissionPage: function(problemId){
                    avalon.vmodels.admin.problemId = problemId;
                    avalon.vmodels.admin.template_url = "template/problem/submission_list.html";
                },

                search: function(){
                    getPage(1);
                    avalon.vmodels.problemPager.currentPage = 1;
                }
            });
            vm.$watch("showVisibleOnly", function () {
                getPage(1);
                avalon.vmodels.problemPager.currentPage = 1;
            });
        }

        function getPage(page) {
            var url = "/api/admin/problem/?paging=true&page=" + page + "&page_size=10";
            if (vm.keyword != "")
                url += "&keyword=" + vm.keyword;
            if (vm.showVisibleOnly)
                url += "&visible=true";
            $.ajax({
                url: url,
                dataType: "json",
                method: "get",
                success: function (data) {
                    if (!data.code) {
                        vm.problemList = data.data.results;
                        avalon.vmodels.problemPager.totalPage = data.data.total_page;
                    }
                    else {
                        bsAlert(data.data);
                    }
                }
            });
        }


    });
    avalon.scan();
});
