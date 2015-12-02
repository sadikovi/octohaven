(function() {
  var ClusterStatus, Dictionary, Template, Timetable,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
    __hasProp = {}.hasOwnProperty;

  Dictionary = (function() {
    function Dictionary(_at_settings) {
      this.settings = _at_settings != null ? _at_settings : {};
      this.correct(this.settings);
    }

    Dictionary.prototype.set = function(key, value) {
      if (value !== null) {
        return this.settings[key] = value.toString();
      } else {
        return null;
      }
    };

    Dictionary.prototype.getOrElse = function(key, alternative) {
      if (key in this.settings) {
        return this.settings[key];
      } else {
        return alternative;
      }
    };

    Dictionary.prototype.get = function(key) {
      return this.getOrElse(key, null);
    };

    Dictionary.prototype.exists = function(key) {
      return this.get(key) !== null;
    };

    Dictionary.prototype.correct = function() {
      var key, value, _ref, _results;
      _ref = this.settings;
      _results = [];
      for (key in _ref) {
        value = _ref[key];
        _results.push(this.set(key, value));
      }
      return _results;
    };

    return Dictionary;

  })();

  Template = (function(_super) {
    __extends(Template, _super);

    function Template() {
      return Template.__super__.constructor.apply(this, arguments);
    }

    return Template;

  })(Dictionary);

  if (this.Template == null) {
    this.Template = Template;
  }

  Timetable = (function(_super) {
    __extends(Timetable, _super);

    function Timetable() {
      return Timetable.__super__.constructor.apply(this, arguments);
    }

    return Timetable;

  })(Dictionary);

  if (this.Timetable == null) {
    this.Timetable = Timetable;
  }

  ClusterStatus = (function(_super) {
    __extends(ClusterStatus, _super);

    function ClusterStatus() {
      return ClusterStatus.__super__.constructor.apply(this, arguments);
    }

    return ClusterStatus;

  })(Dictionary);

  if (this.ClusterStatus == null) {
    this.ClusterStatus = ClusterStatus;
  }

}).call(this);
