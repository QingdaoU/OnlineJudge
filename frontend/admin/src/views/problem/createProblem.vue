<template>
    <div class="rows">
        <back></back>
        <h3>{{ $t("problem.createProblem") }}</h3>
        <form v-on:submit="submit">
            <div class="form-group col-md-12">
                <label>{{ $t("adminUtils.title") }}</label>
                <input type="text" class="form-control" maxlength="50" v-model="title" required>
            </div>

            <div class="form-group col-md-12">
                <label>{{ $t("adminUtils.description") }}</label>
                <simditor v-ref:problem-description></simditor>
            </div>

            <div class="col-md-3">
                <div class="form-group">
                    <label>{{ $t("problem.timeLimit") }}</label>
                    <help name="timeLimit"></help>
                    <input type="number" class="form-control" v-model="timeLimit" required>
                </div>
            </div>
            <div class="col-md-3">
                <div class="form-group">
                    <label>{{ $t("problem.memoryLimit") }}</label>
                    <help name="memoryLimit"></help>
                    <input type="number" class="form-control" v-model="memoryLimit" required>
                </div>
            </div>
            <div class="col-md-3">
                <div class="form-group">
                    <label>{{ $t("problem.difficulty") }}</label>
                    <select class="form-control" required v-model="difficulty">
                        <option value="1" selected="selected">{{ $t("problem.easy") }}</option>
                        <option value="2">{{ $t("problem.medium") }}</option>
                        <option value="3">{{ $t("problem.hard") }}</option>
                    </select>
                </div>
            </div>
            <div class="col-md-3 form-group">
                <label>{{ $t("adminUtils.isVisible")}}</label><br>
                <input type="checkbox" checked v-model="visible">可见
            </div>
            <div class="col-md-12">
                <label>{{ $t("problem.tag") }}</label>
                <tag-input :tag-list.sync="tagList"></tag-input>
            </div>

            <problem-sample :sample-list.sync="sampleList"></problem-sample>
            <test-case-mgnt :mode="mode" :test-case-list="testCaseList" :special-judge="specialJudge"></test-case-mgnt>

            <div class="col-md-12">
                <special-judge :special-judge.sync="specialJudge" :language-list="languageList"
                               :selected-language.sync="specialJudgeLanguage"></special-judge>
            </div>
            <div class="col-md-12">
                <label>{{ $t("problem.hint") }}</label>
                <simditor></simditor>
            </div>
            <div class="col-md-12">
                <label>{{ $t("problem.source") }}</label>
                <div class="form-group">
                    <input type="text" class="form-control" list="problemSourceAutoCompleteList" v-model="source">
                    <datalist id="problemSourceAutoCompleteList">
                        <option value="{{ item }}" v-for="item in problemSourceAutoCompleteList"></option>
                    </datalist>
                </div>
            </div>

            <div class="col-md-12">
                <input type="submit" class="btn btn-primary btn-lg" value='{{ $t("adminUtils.submit") }}'>
            </div>
        </form>
    </div>
</template>

<script>
    import testCaseMgnt from "../../components/testCaseMgnt.vue"
    import problemSample from "../../components/problemSample.vue"
    import specialJudge from "./specialJudge.vue"

    import back from "../../components/back.vue"
    import simditor from "../../components/simditor.vue"
    import tagInput from "../../components/tagInput.vue"
    import codeMirror from "../../components/codeMirror.vue"
    import help from "../../components/help.vue"
    import helpLink from "../../components/helpLink.vue"

    export default({
        data() {
            return {
                title: "",
                timeLimit: 100,
                memoryLimit: 128,
                difficulty: "1",
                visible: true,
                tagList: ["1234", "呵呵哒"],
                sampleList: [{input: "", output: "", visible: true}],
                mode: "ACM",
                testCaseList: [{input_name: "1.in", output_name: "1.out", score: 0}],
                specialJudge: true,
                languageList: [{name: "C", description: "xxxxxx"}],
                specialJudgeLanguage: "C",
                source: "",
                problemSourceAutoCompleteList: []
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
            helpLink,
            specialJudge
        },
        methods: {
            submit() {
                if (!this.$refs.problemDescription.getContent().trim()) {
                    alert(this.$t("problem.problemDescriptionIsRequired"));
                    return false;
                }
                if (!this.tagList) {
                    alert(this.$t(""));
                    return false;
                }
                if (!this.testCaseList) {

                }
                if (this.specialJudge && !this.$refs.specialJudgeCode.getCode().trim()) {

                }
                var submitData = {
                    title: this.title,
                    description: this.$refs.problemDescription.getContent(),
                    timeLimit: this.timeLimit,
                    memoryLimit: this.memoryLimit,
                    difficulty: this.difficulty,
                    visible: this.visible,
                    sample_list: this.sample_list,
                    mode: this.mode,

                };
                return false;
            }
        }
    })
</script>