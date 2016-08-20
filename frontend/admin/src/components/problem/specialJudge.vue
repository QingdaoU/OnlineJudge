<template>
    <div>
        <label>Special Judge</label>
        <div @click="switchSpecialJudge($event)">
            <input type="checkbox" v-model="specialJudge"> <span class="sub-label">{{ $t("problem.turnOnSpecialJudge") }}</span>
        </div>
        <div v-if="specialJudge">
            <code-mirror :selected-language="selectedLanguage" :language-list="languageList"></code-mirror>
        </div>
        <div class="col-md-12 test-special-judge">
            <div class="form-group" v-if="specialJudge">
                <input type="checkbox" v-model="testSpecialJudge">
                <span class="sub-label">{{ $t("problem.testSpecialJudge") }}</span>
            </div>

            <div class="form-group" v-if="specialJudge && testSpecialJudge">
                <textarea v-model="specialJudgeTestCase" class="form-control" rows="4"></textarea>
            </div>
            <div class="form-group" v-if="specialJudge && testSpecialJudge">
                <button type="button" class="btn btn-primary">{{ $t("adminUtils.submit") }}</button>
            </div>

        </div>
        <div class="col-md-12 test-special-jduge" v-if="specialJudge && testSpecialJudge">
            <p class="sub-label">{{ $t("problem.specialJudgeTestResult") }}</p>
            <p>{{ $t("adminUtils.CPUTime") }}: {{ CPUTime }} ms</p>
            <p>{{ $t("adminUtils.memory") }}: {{ memory }} KB</p>
            <p>{{ $t("problem.runResult") }}: {{ runResult }}</p>
            <p v-if="output">{{ $t("problem.output") }}</p>
            <pre v-if="output">{{ output }}</pre>
        </div>
    </div>
</template>

<script>
    import codeMirror from "../utils/codeMirror.vue"

    export default ({
        props: {
            specialJudge: {
                type: Boolean,
                required: true
            },
            selectedLanguage: {
                type: String,
                required: true,
            },
            languageList: {
                type: Array,
                required: true
            }
        },
        data() {
            return {
                testSpecialJudge: true,
                specialJudgeTestCase: "",
                CPUTime: 0,
                memory: 0,
                runResult: "Loading",
                output: ""
            }
        },
        components: {
            codeMirror
        },
        methods: {
            switchSpecialJudge(e) {
                confirm(this.$t("problem.switchSpecialJudge"), ()=> {}, ()=> {this.specialJudge = !this.specialJudge});
            }
        }
    })
</script>

<style scoped>
    .test-special-judge {
        padding-top: 5px;
    }
</style>