require(["jquery", "code_mirror"], function ($, code_mirror) {
    var code_editor = code_mirror($("#code-editor")[0], "text/x-csrc");
    var language = "1";

    $("#language-selector").change(function () {
        language = $("#language-selector").val();
        var language_types = {c: "text/x-csrc", cpp: "text/x-c++src", java: "text/x-java"};
        code_editor.setOption("mode", language_types[language]);
    });

    function show_loading() {
        $("#submit-code-button").attr("disabled", "disabled");
        $("#loading-gif").show();
    }

    function hide_loading() {
        $("#submit-code-button").removeAttr("disabled");
        $("#loading-gif").hide();
    }

    $("#submit-code-button").click(function () {
        show_loading();
        $.ajax({

        });
        setTimeout(
            function () {
                $("#a").animate({opacity: '1'})
            }, 3);
    });

    $("#show-more-btn").click(function(){
        $(".hide").attr("class", "problem-section");
        $("#show-more-btn").hide();
    })

});
