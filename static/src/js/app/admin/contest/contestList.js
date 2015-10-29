require(["jquery", "avalon", "csrfToken", "bsAlert", "editor", "datetimePicker", "validator", "pager"], function ($, avalon, csrfTokenHeader, bsAlert, editor) {

    avalon.ready(function () {
        if (avalon.vmodels.contestList) {
            var vm = avalon.vmodels.contestList;
            vm.contestList = [];
        }
        else {
            var vm = avalon.define({
                $id: "contestList",
                contestList: [],
                keyword: "",
                showVisibleOnly: false,
                pager: {
                    getPage: function(page){
                        getPage(page);
                    }
                },

                search: function () {
                    getPage(1);
                    avalon.vmodels.contestListPager.currentPage = 1;
                },

                editContest: function(contestId){
                    avalon.vmodels.admin.contestId = contestId;
                    avalon.vmodels.admin.template_url = "template/contest/edit_contest.html";
                },
                showContestProblems: function(contestId){
                    avalon.vmodels.admin.contestId = contestId;
                    avalon.vmodels.admin.template_url = "template/contest/problem_list.html";
                }
            })
        }

        vm.$watch("showVisibleOnly", function () {
            getPage(1);
            avalon.vmodels.contestListPager.currentPage = 1;
        });

        function getPage(page) {
            var url = "/api/admin/contest/?paging=true&page=" + page + "&page_size=20";
            if (vm.showVisibleOnly)
                url += "&visible=true";
            if (vm.keyword != "")
                url += "&keyword=" + vm.keyword;
            $.ajax({
                url: url,
                dataType: "json",
                method: "get",
                success: function (data) {
                    if (!data.code) {
                        vm.contestList = data.data.results;
                        avalon.vmodels.contestListPager.totalPage = data.data.total_page;
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