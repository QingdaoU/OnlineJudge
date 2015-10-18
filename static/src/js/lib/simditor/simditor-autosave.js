(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    // AMD. Register as an anonymous module unless amdModuleId is set
    define('simditor-autosave', ["jquery","simple-module","simditor"], function (a0,b1,c2) {
      return (root['SimditorAutosave'] = factory(a0,b1,c2));
    });
  } else if (typeof exports === 'object') {
    // Node. Does not work with strict CommonJS, but
    // only CommonJS-like environments that support module.exports,
    // like Node.
    module.exports = factory(require("jquery"),require("simple-module"),require("simditor"));
  } else {
    root['SimditorAutosave'] = factory(jQuery,SimpleModule,Simditor);
  }
}(this, function ($, SimpleModule, Simditor) {

var SimditorAutosave,
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

SimditorAutosave = (function(superClass) {
  extend(SimditorAutosave, superClass);

  function SimditorAutosave() {
    return SimditorAutosave.__super__.constructor.apply(this, arguments);
  }

  SimditorAutosave.pluginName = 'Autosave';

  SimditorAutosave.prototype.opts = {
    autosave: true,
    autosavePath: null
  };

  SimditorAutosave.prototype._init = function() {
    var currentVal, link, name, val;
    this.editor = this._module;
    if (!this.opts.autosave) {
      return;
    }
    this.name = typeof this.opts.autosave === 'string' ? this.opts.autosave : 'simditor';
    if (this.opts.autosavePath) {
      this.path = this.opts.autosavePath;
    } else {
      link = $("<a/>", {
        href: location.href
      });
      name = this.editor.textarea.data('autosave') || this.name;
      this.path = "/" + (link[0].pathname.replace(/\/$/g, "").replace(/^\//g, "")) + "/autosave/" + name + "/";
    }
    if (!this.path) {
      return;
    }
    this.editor.on("valuechanged", (function(_this) {
      return function() {
        return _this.storage.set(_this.path, _this.editor.getValue());
      };
    })(this));
    this.editor.el.closest('form').on('ajax:success.simditor-' + this.editor.id, (function(_this) {
      return function(e) {
        return _this.storage.remove(_this.path);
      };
    })(this));
    val = this.storage.get(this.path);
    if (!val) {
      return;
    }
    currentVal = this.editor.textarea.val();
    if (val === currentVal) {
      return;
    }
    if (this.editor.textarea.is('[data-autosave-confirm]')) {
      if (confirm(this.editor.textarea.data('autosave-confirm') || 'Are you sure to restore unsaved changes?')) {
        return this.editor.setValue(val);
      } else {
        return this.storage.remove(this.path);
      }
    } else {
      return this.editor.setValue(val);
    }
  };

  SimditorAutosave.prototype.storage = {
    supported: function() {
      var error;
      try {
        localStorage.setItem('_storageSupported', 'yes');
        localStorage.removeItem('_storageSupported');
        return true;
      } catch (_error) {
        error = _error;
        return false;
      }
    },
    set: function(key, val, session) {
      var storage;
      if (session == null) {
        session = false;
      }
      if (!this.supported()) {
        return;
      }
      storage = session ? sessionStorage : localStorage;
      return storage.setItem(key, val);
    },
    get: function(key, session) {
      var storage;
      if (session == null) {
        session = false;
      }
      if (!this.supported()) {
        return;
      }
      storage = session ? sessionStorage : localStorage;
      return storage[key];
    },
    remove: function(key, session) {
      var storage;
      if (session == null) {
        session = false;
      }
      if (!this.supported()) {
        return;
      }
      storage = session ? sessionStorage : localStorage;
      return storage.removeItem(key);
    }
  };

  return SimditorAutosave;

})(SimpleModule);

Simditor.connect(SimditorAutosave);

return SimditorAutosave;

}));
