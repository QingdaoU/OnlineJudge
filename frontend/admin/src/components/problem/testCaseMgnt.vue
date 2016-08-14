<template>
    <div class="col-md-12">
        <label>
            {{ $t("problem.testCase") }}
            <a href="https://github.com/QingdaoU/OnlineJudge/wiki/%E6%B5%8B%E8%AF%95%E7%94%A8%E4%BE%8B%E4%B8%8A%E4%BC%A0"
               target="_blank">{{ $t("adminUtils.help") }}
            </a>
            <a v-show="downloadUrl" v-bind:href="downloadUrl">{{ $t("adminUtils.download") }}</a>
        </label>
        <br>
        <input type="checkbox" v-model="OIMode"> {{ $t("problem.OIMode") }}
        <br>
        <label>{{ $t("problem.uploadProgress") }}</label>
        <div class="progress">
            <div class="progress-bar progress-bar-striped" role="progressbar " aria-valuenow="{{ uploadProgress }}"
                 aria-valuemin="0"
                 aria-valuemax="100"
                 v-bind:style="{width: uploadProgress+'%'}">
                {{ uploadProgress }} %
            </div>
        </div>

        <table class="table table-striped" v-if="testCaseList">
            <tr>
                <td>ID</td>
                <td>{{ $t("adminUtils.input") }}</td>
                <td>{{ $t("adminUtils.output") }}</td>
                <td v-if="OIMode">{{ $t("problem.score") }}</td>
            </tr>
            <tr v-for="testCase in testCaseList">
                <td>{{ $index + 1 }}</td>
                <td>{{ testCase.input_name }}</td>
                <td>{{ testCase.output_name }}</td>
                <td v-if="OIMode"><input class="score" v-model="testCase.score" type="number" min="1" required></td>
            </tr>
        </table>
        <div class="form-group">
            <uploader upload-path="/"
                      :accept="{title: 'testcase zip', extensions: 'zip', mimeTypes: 'application/zip'}"
                      :upload-success="uploadSuccess"
                      :upload-error="uploadError"
                      :upload-progress.sync="uploadProgress">
            </uploader>
        </div>
    </div>
</template>

<script>
    import uploader from "../utils/uploader.vue"

    export default({
        data() {
            return {
                downloadUrl: "",
                uploadProgress: 0,
                testCaseList: [],
                OIMode: false
            }
        },
        components: {
            uploader
        },
        methods: {
            uploadSuccess(f, response){
                // todo
            },
            uploadError(f, reason){
                this.uploadProgress = 0;
                alert($t("request.error"));
            },
            setTestCase(mode, testCaseList) {
                this.OIMode = mode == "OI";
                // attr must be set firstly so vue can track it's changes
                if (this.OIMode) {
                    for(let item of testCaseList) {
                        item.score = 0;
                    }
                }
                this.testCaseList = testCaseList;
            },
            getTestCase() {
                var testCaseList = this.testCaseList;
                if (!this.OIMode) {
                    for(let item of testCaseList) {
                        delete item.score;
                    }
                }
                return {testCaseList: testCaseList, mode: this.mode == "OI"};
            }
        }
    })
</script>

<style scoped>
    .score {
        width: 50px;
    }
</style>