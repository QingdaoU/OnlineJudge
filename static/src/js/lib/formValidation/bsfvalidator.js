/**
 * !!!!!! dev-version and still in progress !!!!!!!
 * this plugin loads all required components
 * to start validaton process properly
 * How to use this:
 *    include bsfvalidator according to the following pattern
 *    bsfvalidator!LANG:VALIDATORS
 *
 *    Options:
 *        LANG - (optinal and single value) indicates which language will be used
 *        VALIDATORS - (required) defines which validators should be used
 *    Examples:
 *       1) bsfvalidator!ua_UA:notEmpty,stringLength,regexp,emailAddress
 *       2) bsfvalidator!notEmpty,stringLength,regexp,emailAddress
 *       3) bsfvalidator!notEmpty
 *    There is simple requirejs based project in demo/amd folder
 */
define("bsfvalidator", ["base", "helper", "framework/bootstrap"], function (base) {
    var buildMap = [];
    function getDeps (name) {
        var parts = name.match(/((.*):)?(.*)/),
            lang = null,
            deps = [],
            all = [];
        if (parts.length === 4) {
            lang = parts[2];
            deps = parts[3].split(',');
        }
        if (parts.length === 3) {
            deps = parts[2].split(',');
        }
        for (var i = 0, len = deps.length; i < len; i++) {
            deps[i] = './validator/' + deps[i];
        }
        if (lang) {
            lang = './language/' + lang;
            all.push(lang);
        }
        all = all.concat(deps);
        return {
            lang: lang,
            deps: deps,
            all: all
        };
    }
    return {
        load: function (name, req, onLoad, config) {
            var deps = getDeps(name);
            req(deps.all, function () {
                onLoad(base);
            });
        }
    }
});