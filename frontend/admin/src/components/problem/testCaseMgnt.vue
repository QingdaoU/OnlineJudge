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
            </tr>
            <tr v-for="testCase in testCaseList">
                <td>{{ $index + 1 }}</td>
                <td>{{ testCase.input }}</td>
                <td>{{ testCase.output }}</td>
            </tr>
        </table>
        <div class="form-group">
            <uploader uploader-id="testCaseUploader"
                      upload-path="/"
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
                testCaseList: []
            }
        },
        components: {
            uploader
        },
        methods: {
            uploadSuccess(f, response){
                alert("success");
            },
            uploadError(f, reason){
                this.uploadProgress = 0;
                alert("error");
            }
        }
    })
</script>