define("admin", ["jquery", "avalon"], function($, avalon){
    function li_active(selector){
        $(selector).attr("class", "list-group-item active");
    }

    function li_inactive(selector){
        $(".list-group-item").attr("class", "list-group-item");
    }

    function show_template(url){
        $("#loading-gif").show();
        vm.template_url = url;
    }

    var vm = avalon.define({
        $id: "admin",
        template_url: "template/index/index.html",
        hide_loading: function(){
            $("#loading-gif").hide();
        }
    });

    var hash = window.location.hash.substring(1);

    if(hash){
        li_active("#li-" + hash.replace("/", "-"));
        show_template("template/" + hash + ".html");
    }else {
        li_active("#li-index-index");
    }

    window.onhashchange = function() {
        var hash = window.location.hash.substring(1);
        if(hash){
            li_inactive(".list-group-item");
            li_active("#li-" + hash.replace("/", "-"));
            show_template("template/" + hash + ".html");
        }
    };


});