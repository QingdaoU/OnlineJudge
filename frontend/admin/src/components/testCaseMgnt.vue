<template>
    <div class="col-md-12">
        <label>
            {{ $t("problem.testCase") }}
            <help-link link="https://github.com/QingdaoU/OnlineJudge/wiki/%E6%B5%8B%E8%AF%95%E7%94%A8%E4%BE%8B%E4%B8%8A%E4%BC%A0"></help-link>
            <a v-show="downloadURL" v-bind:href="downloadURL">{{ $t("adminUtils.download") }}</a>
        </label>

        <div>
            <div class="form-group">
                <p class="sub-label">{{ $t("problem.mode") }}</p>
                <div>
                    <span class="radio-inline"><input type="radio" name="mode" value="ACM" v-model="mode" checked>{{ $t("problem.ACMMode") }}</span>
                    <span class="radio-inline"><input type="radio" name="mode" value="OI"  v-model="mode">{{ $t("problem.OIMode") }}</span>
                </div>
            </div>
        </div>

        <div>
            <p class="sub-label">{{ $t("problem.uploadProgress") }}</p>
            <div class="progress">
                <div class="progress-bar progress-bar-striped" role="progressbar " aria-valuenow="{{ uploadProgress }}"
                     aria-valuemin="0"
                     aria-valuemax="100"
                     v-bind:style="{width: uploadProgress+'%'}">
                    {{ uploadProgress }} %
                </div>
            </div>
        </div>

        <table class="table table-striped" v-if="testCaseList">
            <tr>
                <td>ID</td>
                <td>{{ $t("adminUtils.input") }}</td>
                <td v-if="!specialJudge">{{ $t("adminUtils.output") }}</td>
                <td v-if="mode == 'OI'">{{ $t("problem.score") }}</td>
            </tr>
            <tr v-for="testCase in testCaseList">
                <td>{{ $index + 1 }}</td>
                <td>{{ testCase.input_name }}</td>
                <td v-if="!specialJudge">{{ testCase.output_name }}</td>
                <td v-if="mode == 'OI'"><input class="score" v-model="testCase.score" type="number" min="1" required></td>
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
    import helpLink from "../utils/helpLink.vue"

    export default({
        props: {
            downloadURL: {
                type: String,
                required: false,
                default() {
                    return ""
                }
            },
            testCaseList: {
                type: Array,
                required: true
            },
            mode: {
                type: String,
                required: true
            },
            specialJudge: {
                type: Boolean,
                required: true
            }
        },
        data() {
            return {
                uploadProgress: 0,
            }
        },
        components: {
            uploader,
            helpLink
        },
        methods: {
            uploadSuccess(f, response){
                // todo
            },
            uploadError(f, reason){
                this.uploadProgress = 0;
                alert(this.$t("request.error"));
            }
        }
    })
</script>

<style scoped>
    .score {
        width: 50px;
    }
</style>