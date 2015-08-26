require(["jquery", "avalon", "csrfToken", "bsAlert"], function ($, avalon, csrfTokenHeader, bsAlert) {

    avalon.ready(function () {

        if (avalon.vmodels.contestSubmissionList){
            var vm = avalon.vmodels.contestSubmissionList;
        }
        else {

            var vm = avalon.define({
                $id: "contestSubmissionList",
                submissionList: [],
                previousPage: 0,
                nextPage: 0,
                page: 1,
                totalPage: 1,
                results : {
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
                getNext: function () {
                    if (!vm.nextPage)
                        return;
                    getPageData(vm.page + 1);
                },
                getPrevious: function () {
                    if (!vm.previousPage)
                        return;
                    getPageData(vm.page - 1);
                },
                getBtnClass: function (btn) {
                    if (btn == "next") {
                        return vm.nextPage ? "btn btn-primary" : "btn btn-primary disabled";
                    }
                    else {
                        return vm.previousPage ? "btn btn-primary" : "btn btn-primary disabled";
                    }
                },
                getPage: function (page_index) {
                    getPageData(page_index);
                },
                showSubmissionDetailPage: function (submissionId) {

                },
                showProblemListPage: function(){
                    vm.$fire("up!showProblemListPage");
                }
            });
        }

        getPageData(1);

        function getPageData(page) {
            var url = "/api/admin/submission/?paging=true&page=" + page + "&page_size=10&problem_id=" + avalon.vmodels.admin.problemId;
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