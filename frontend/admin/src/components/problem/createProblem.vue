<template>
    <div class="rows">
        <back></back>
        <h3>{{ $t("problem.createProblem") }}</h3>
        <div class="form-group col-md-12">
            <label>{{ $t("adminUtils.title") }}</label>
            <input type="text" class="form-control" maxlength="50" required>
        </div>

        <div class="form-group col-md-12">
            <label>{{ $t("adminUtils.description") }}</label>
            <simditor v-ref:problemdescription></simditor>
        </div>

        <div class="col-md-3">
            <div class="form-group">
                <label>{{ $t("problem.timeLimit") }}</label>
                <help name="timeLimit"></help>
                <input type="number" class="form-control" required>
            </div>
        </div>
        <div class="col-md-3">
            <div class="form-group">
                <label>{{ $t("problem.memoryLimit") }}</label>
                <help name="memoryLimit"></help>
                <input type="number" class="form-control" required>
            </div>
        </div>
        <div class="col-md-3">
            <div class="form-group">
                <label>{{ $t("problem.difficulty") }}</label>
                <select class="form-control" required>
                    <option value="1" selected="selected">{{ $t("problem.easy") }}</option>
                    <option value="2">{{ $t("problem.medium") }}</option>
                    <option value="3">{{ $t("problem.hard") }}</option>
                </select>
            </div>
        </div>
        <div class="col-md-3 form-group">
            <label>{{ $t("adminUtils.isVisible")}}</label><br>
            <input type="checkbox">可见
        </div>
        <div class="col-md-12">
            <label>{{ $t("problem.tag") }}</label>
            <tag-input :tag-list.sync="tagList"></tag-input>
        </div>

        <problem-sample :samples.sync="samples"></problem-sample>
        <test-case-mgnt :mode="mode" :test-case-list="testCaseList"></test-case-mgnt>

        <div class="col-md-12">
            <label>Special Judge</label>
            <code-mirror :selected-language-name="selectedLanguageName" :language-list="languageList"></code-mirror>
        </div>
    </div>
</template>

<script>
    import testCaseMgnt from "../utils/testCaseMgnt.vue"
    import problemSample from "../utils/problemSample.vue"

    import back from "../utils/back.vue"
    import simditor from "../utils/simditor.vue"
    import tagInput from "../utils/tagInput.vue"
    import codeMirror from "../utils/codeMirror.vue"
    import help from "../utils/help.vue"
    import helpLink from "../utils/helpLink.vue"

    export default({
        data() {
            return {
                tagList: ["1234", "呵呵哒"],
                selectedLanguageName: "C",
                languageList: [{name: "C", description: "xxxxxx"}],
                samples: [{input: "", output: "", visible: true}],
                mode: "ACM",
                testCaseList: [{input_name: "1.in", output_name: "1.out"}]
            }
        },
        components: {
            testCaseMgnt,
            problemSample,
            back,
            simditor,
            tagInput,
            codeMirror,
            help,
            helpLink
        }
    })
</script>