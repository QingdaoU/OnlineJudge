<template>
    <div class="col-md-12"><br>
        <label>{{ $t("problem.sample") }}</label>
        <button class="btn btn-primary btn-sm add-sample-btn" v-on:click="addSample">{{ $t("problem.addSample") }}
        </button>

        <div>
            <div class="panel panel-default" v-for="sample in samples">
                <div class="panel-heading">
                    <span class="panel-title">{{ $t("problem.sample") }} {{ $index + 1 }}</span>
                    <button class="btn btn-primary btn-sm" v-on:click="toggleSample($index)">
                        {{ sample.visible?$t("problem.fold"):$t("problem.show") }}
                    </button>
                    <button class="btn btn-danger btn-sm" v-on:click="delSample($index)">
                        {{ $t("adminUtils.delete") }}
                    </button>
                </div>
                <div class="panel-body row" v-show="sample.visible">
                    <div class="col-md-6">
                        <div class="form-group">
                            <label>{{ $t("problem.sample") }}{{ $t("adminUtils.input") }}</label>
                            <textarea class="form-control" rows="5" required></textarea>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="form-group">
                            <label>{{ $t("problem.sample") }}{{ $t("adminUtils.output") }}</label>
                            <textarea class="form-control" rows="5" required></textarea>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    export default({
        data() {
            return {
                samples: [{input: "12334", output: "111", visible: true}]
            }
        },
        methods: {
            addSample() {
                this.samples.push({input: "", output: "", visible: true})
            },
            toggleSample(index) {
                this.samples[index].visible = !this.samples[index].visible;
            },
            delSample(index) {
                confirm(this.$t("problem.deleteThisSample"), ()=> {
                    this.samples.splice(index, 1)
                });
            }
        }
    })
</script>

<style>
    .add-sample-btn {
        margin-bottom: 5px;
    }
</style>