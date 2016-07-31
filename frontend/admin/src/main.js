import Vue from 'vue'
import App from './App'
import VueRouter from "vue-router"
import VueI18n from "vue-i18n"

import locale from "./locales"

import userList from "./components/account/userList.vue"
import editUser from "./components/account/editUser.vue"


var request = {
    install: function (Vue, options) {
        function getCookie(name) {
            var value = "; " + document.cookie;
            var parts = value.split("; " + name + "=");
            if (parts.length == 2) {
                return parts.pop().split(";").shift();
            }
        }

        Vue.prototype.request = function (option) {
            var request = new XMLHttpRequest();
            request.open(option.method, option.url, true);
            request.onerror = function () {
                if (option.error) {
                    option.error(request)
                }
                else {
                    alert("请求失败");
                }
            };
            request.onload = function () {
                if (request.status >= 200 && request.status < 400) {
                    try {
                        var data = JSON.parse(request.responseText);
                        if (data.code == 1 && data.data) {
                            alert(data.data);
                            return;
                        }
                    }
                    catch (err) {
                        request.onerror();
                    }
                    option.success(data);
                }
                else {
                    request.onerror();
                }
            };
            request.setRequestHeader('x-requested-with', 'XMLHttpRequest');
            if (option.method.toLowerCase() == 'post' || option.method.toLowerCase() == 'put') {
                request.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
                request.setRequestHeader('x-csrftoken', getCookie('csrftoken'));
                request.send(JSON.stringify(option.data));
            }
            else {
                request.send();
            }
        }
    }
};

Vue.use(request);

Vue.use(VueRouter);
Vue.use(VueI18n);

Vue.config.lang = "zh-cn";

Object.keys(locale).forEach(function (lang) {
    Vue.locale(lang, locale[lang])
});


var router = new VueRouter();

router.map({
    "/user/:page": {
        name: "userList",
        component: userList
    },
    "/user/edit/:userId": {
        name: "editUser",
        component: editUser
    }
});

router.redirect({"/user": "/user/1"});
router.start(App, '#app');