<template>
    <h3>{{ $t("problem.problemList") }}</h3>
    <div>
            <form class="form-inline" onsubmit="return false;">
                <div class="form-group-sm">
                    <label>{{ $t("adminUtils.search") }}</label>
                    <input name="keyword" class="form-control" placeholder='{{ $t("adminUtils.inputKeyword") }}'
                           v-model="keyword">
                    <button type="button" class="btn btn-primary" v-on:click="search">{{ $t("adminUtils.search") }}
                    </button>
                </div>
            </form>
            <br>
        </div>
    <table class="table table-striped">
        <tr>
            <th>ID</th>
            <th>{{ $t("adminUtils.title") }}</th>
            <th>{{ $t("adminUtils.createTime") }}</th>
            <th>{{ $t("adminUtils.createdBy") }}</th>
            <th>{{ $t("adminUtils.isVisible") }}</th>
            <th>{{ $t("adminUtils.management") }}</th>
        </tr>
        <tr v-for="problem in problemList">
            <td>{{ problem.id }}</td>
            <td>{{ problem.title }}</td>
            <td>{{ problem.create_time }}</td>
            <td>{{ problem.created_by.username }}</td>
            <td>{{ $t(problemStatus[problem.visible?1:0]) }}</td>
            <td>
                <button type="button" class="btn-sm btn-info" v-on:click="edit(problem.id)">{{ $t("adminUtils.edit") }}</button>
            </td>
        </tr>
    </table>
    <pager :pagination="pagination" :callback="loadData"></pager>

</template>

<script>
    import pager from "../../components/pager.vue"

    export default({
        data() {
            return {
                keyword: "",
                problemStatus: ["adminUtils.visible", "adminUtils.invisible"],
                problemList: [],
                pagination: {
                    currentPage: 1,
                    totalPages: 10
                }
            }
        },
        methods: {
            loadData() {
                var url = "/api/admin/problem/?paging=true&page_size=2&page=" + this.pagination.currentPage;
                if (this.keyword) {
                    url += ("&keyword=" + this.keyword)
                }
                this.request({
                    url: url,
                    method: "GET",
                    success: (data)=> {
                        this.problemList = data.data.results;
                        this.pagination.totalPages = data.data.total_page;
                    }
                })
            },
            edit(problemId){
                this.$router.go("/problem/edit/" + problemId)
            },
            search() {
                sessionStorage.problemListSearchKeyword = this.keyword;
                this.$router.go({path: "/problem/1", query: {_: (new Date()).getTime()}});
            },
        },
        route: {
            data(){
                if (sessionStorage.problemListSearchKeyword) {
                    this.keyword = sessionStorage.problemListSearchKeyword;
                }
                this.loadData();
            }
        },
        components: {
            pager
        }
    })
</script>

<style>

</style>