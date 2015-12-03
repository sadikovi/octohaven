(function() {
  var STATUS_BUSY, STATUS_PENDING, STATUS_READY, STATUS_UNREACHABLE, clstat, mapClass, mapStatus, masterAddress, reloadStatus, setClusterStatus, status, uiAddress, _api, _util;

  status = document.getElementById("octohaven-spark-server-status");

  uiAddress = document.getElementById("octohaven-spark-ui-address");

  masterAddress = document.getElementById("octohaven-spark-master-address");

  if (!(status && uiAddress && masterAddress)) {
    throw new Error("Cluster status entries are undefined");
  }

  _util = this.util;

  _api = new this.StatusApi;

  clstat = new this.ClusterStatus;

  STATUS_PENDING = "Pending...";

  STATUS_READY = "Cluster is ready";

  STATUS_BUSY = "Cluster is busy";

  STATUS_UNREACHABLE = "Cluster is unreachable";

  mapStatus = function(status) {
    if (status === "0") {
      return STATUS_READY;
    }
    if (status === "-1") {
      return STATUS_BUSY;
    }
    if (status === "-2") {
      return STATUS_UNREACHABLE;
    }
    return STATUS_PENDING;
  };

  mapClass = function(status) {
    if (status === "0") {
      return "text-green";
    }
    if (status === "-1") {
      return "text-yellow";
    }
    if (status === "-2") {
      return "text-red";
    }
    return "text-mute";
  };

  setClusterStatus = function(clstat) {
    status.className = "";
    _util.addClass(status, mapClass(clstat.get("status"), null));
    status.innerHTML = mapStatus(clstat.get("status"), null);
    uiAddress.innerHTML = clstat.getOrElse("spark-ui-address", "?");
    return masterAddress.innerHTML = clstat.getOrElse("spark-master-address", "?");
  };

  reloadStatus = function() {
    var after, before;
    before = function() {
      return setClusterStatus(clstat);
    };
    after = function(ok, json) {
      if (ok) {
        clstat = new this.ClusterStatus(json["content"]);
      }
      return setClusterStatus(clstat);
    };
    return _api.requestStatus(before, after);
  };

  if (typeof reloadStatus === "function") {
    reloadStatus();
  }

}).call(this);
