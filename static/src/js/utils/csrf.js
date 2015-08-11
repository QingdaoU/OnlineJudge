define("csrf",function(){
    function get_cookie(cookie_name) {
        var name = cookie_name + "=";
        var ca = document.cookie.split(';');
        for (var i = 0; i < ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0) == ' ') c = c.substring(1);
            if (c.indexOf(name) != -1) return c.substring(name.length, c.length);
        }
        return "";
    }
    function csrfHeader(){
        // jquery的请求
        if(arguments.length == 2) {
            arguments[0].setRequestHeader("X-CSRFToken", get_cookie("csrftoken"));
        }
        // 百度webuploader 的请求
        else if(arguments.length == 3){
            arguments[2]["X-CSRFToken"] = get_cookie("csrftoken");
        }
    }
    return csrfHeader;
});
