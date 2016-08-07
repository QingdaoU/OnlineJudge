<template>
    <div>
        <div class="col-md-12">
            <label>{{ $t("problem.testCase") }}
                <a v-show="downloadUrl" v-bind:href="downloadUrl">{{ $t("adminUtils.download") }}</a>
            </label>
            <small class="text-info">
                请将所有测试用例打包在一个zip文件中上传，所有文件要在压缩包的根目录，且输入输出文件名要以从1开始连续数字标识要对应例如：
                <br>1.in 1.out 2.in 2.out(普通题目)或者1.in 2.in 3.in(Special Judge)
                <a href="https://github.com/QingdaoU/OnlineJudge/wiki/%E6%B5%8B%E8%AF%95%E7%94%A8%E4%BE%8B%E4%B8%8A%E4%BC%A0"
                   target="_blank">{{ $t("adminUtils.help") }}
                </a>
            </small>
            <p>{{ $t("problem.uploadProgress") }}<span v-text="uploadProgress"></span>%</p>
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
        </div>
        <div class="col-md-12">
            <div class="form-group">
                <uploader uploader-id="testCaseUploader"
                          upload-path="/"
                          :accept="{title: 'testcase zip', extensions: 'zip', mimeTypes: 'application/zip'}"
                          :upload-success="uploadSuccess"
                          :upload-error="uploadError"
                          :upload-progress="uploadProgress">
                </uploader>
            </div>
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
            uploadSuccess: (f, response)=> {
                alert("success");
            },
            uploadError: (f, reason)=> {
                alert("error");
            },
            uploadProgress: (file, percentage)=> {
                console.log(percentage);
            }
        }
    })
</script>