require(["jquery", "avalon", "csrfToken", "bsAlert", "pager"], function ($, avalon, csrfTokenHeader, bsAlert) {

    avalon.ready(function () {

        if (avalon.vmodels.submissionList) {
            var vm = avalon.vmodels.submissionList;
        }
        else {
            var vm = avalon.define({
                $id: "submissionList",
                submissionList: [],
                previousPage: 0,
                nextPage: 0,
                page: 1,
                totalPage: 1,
                results: {
                    0: "Accepted",
                    1: "Runtime Error",
                    2: "Time Limit Exceeded",
                    3: "Memory Limit Exceeded",
                    4: "Compile Error",
                    5: "Format Error",
                    6: "Wrong Answer",
                    7: "System Error",
                    8: "Waiting"
                },
                pager: {
                    getPage: function (page) {
                        getPage(page);
                    }
                },
                showProblemListPage: function () {
                    avalon.vmodels.admin.template_url = "template/problem/problem_list.html";
                },

                rejudge: function (submission_id) {
                    $.ajax({
                        url: "/api/admin/rejudge/",
                        method: "post",
                        data: {"submission_id": submission_id},
                        success: function (data) {
                            if (!data.code) {
                                bsAlert("重判任务提交成功");
                            }
                        }
                    })
                }
            });
        }

        function getPage(page) {
            var url = "/api/admin/submission/?paging=true&page=" + page + "&page_size=20&problem_id=" + avalon.vmodels.admin.problemId;
            $.ajax({
                url: url,
                dataType: "json",
                method: "get",
                success: function (data) {
                    if (!data.code) {
                        vm.submissionList = data.data.results;
                        vm.totalPage = data.data.total_page;
                        vm.previousPage = data.data.previous_page;
                        vm.nextPage = data.data.next_page;
                        vm.page = page;
                        avalon.vmodels.submissionsListPager.totalPage = data.data.total_page;
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