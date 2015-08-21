require(["jquery", "avalon", "csrfToken", "bsAlert", "editor", "datetimePicker"], function ($, avalon, csrfTokenHeader, bsAlert, editor) {

    avalon.ready(function () {
        if(avalon.vmodels.contestList){
            vm = avalon.vmodels.contestList;
	    vm.editingContest = 0;
        }
        else {
            var vm = avalon.define({
                $id: "contestList",
                contestList: [],
                previousPage: 0,
                nextPage: 0,
                page: 1,
                totalPage: 1,
                keyword: "",
				editingContestId: 0,
				editTitle: "",
				editingProblemList: [],
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
                showEditContestArea: function (contestId) {
					if (contestId == vm.editingContestId)
						vm.editingContestId = 0;
					else {
						vm.editingContestId = contestId;
						vm.editTitle = vm.contestList[contestId-1].title;
						editor("#editor").setValue(vm.contestList[contestId-1].description);
						vm.editingProblemList = vm.contestList[contestId-1].problemList;
					}
                }
            });

            getPageData(1);
        }

        function getPageData(page) {
/*
            var url = "/api/admin/contest/?paging=true&page=" + page + "&page_size=10";
            if (vm.keyword != "")
                url += "&keyword=" + vm.keyword;
            $.ajax({
                url: url,
                dataType: "json",
                method: "get",
                success: function (data) {
                    if (!data.code) {
                        vm.contestList = data.data.results;
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
*/
                        vm.contestList =[{
							id: 1, title:"The first contest",
							created_by: {username:"owen"},
							description:"<p>this contest is just for<h1>fun</h1></p>",
							problemList:[{title:"A+B problem", id:1, testCaseList:[1,2], samples:[1,2]}]
							}]; 
                        vm.totalPage = 1;
                        vm.previousPage = false;
                        vm.nextPage = false;
                        vm.page = 1;
        }


    });
    avalon.scan();
});
