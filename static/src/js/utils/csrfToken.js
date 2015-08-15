define("csrfToken",function(){
    function getCookie(cookie_name) {
        var name = cookie_name + "=";
        var ca = document.cookie.split(';');
        for (var i = 0; i < ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0) == ' ') c = c.substring(1);
            if (c.indexOf(name) != -1) return c.substring(name.length, c.length);
        }
        return "";
    }
    function csrfTokenHeader(){
        // jquery的请求
        if(arguments.length == 2) {
            arguments[0].setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
        }
        // 百度webuploader 的请求
        else if(arguments.length == 3){
            arguments[2]["X-CSRFToken"] = getCookie("csrftoken");
        }
    }
    return csrfTokenHeader;
});
