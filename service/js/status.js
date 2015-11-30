(function() {
  var reloadStatus, serverMasterAddress, serverStatus, serverUIAddress, setMasterAddress, setStatus, setUIAddress, _util;

  serverStatus = document.getElementById("octohaven-spark-server-status");

  serverUIAddress = document.getElementById("octohaven-spark-ui-address");

  serverMasterAddress = document.getElementById("octohaven-spark-master-address");

  if (!(serverStatus && serverUIAddress && serverMasterAddress)) {
    throw new Error("Server entries are unrecognized");
  }

  _util = this.util;

  setStatus = function(status) {
    serverStatus.className = "";
    if (status === false) {
      serverStatus.innerHTML = "" + this.Status.STATUS_PENDING;
      return _util.addClass(serverStatus, "text-mute");
    } else if (status === 0) {
      _util.addClass(serverStatus, "text-green");
      return serverStatus.innerHTML = "" + this.Status.STATUS_READY;
    } else if (status === -1) {
      _util.addClass(serverStatus, "text-yellow");
      return serverStatus.innerHTML = "" + this.Status.STATUS_BUSY;
    } else {
      _util.addClass(serverStatus, "text-red");
      return serverStatus.innerHTML = "" + this.Status.STATUS_UNREACHABLE;
    }
  };

  setUIAddress = function(address) {
    return serverUIAddress.innerHTML = address ? "" + address : "?";
  };

  setMasterAddress = function(address) {
    return serverMasterAddress.innerHTML = address ? "" + address : "?";
  };

  reloadStatus = function() {
    var after, before, status;
    status = new this.Status;
    before = function() {
      setStatus(false);
      setUIAddress(false);
      return setMasterAddress(false);
    };
    after = function(status, uiAddress, masterAddress) {
      setStatus(status);
      setUIAddress(uiAddress);
      return setMasterAddress(masterAddress);
    };
    return status.requestStatus(before, after);
  };

  if (typeof reloadStatus === "function") {
    reloadStatus();
  }

}).call(this);
