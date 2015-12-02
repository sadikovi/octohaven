status = document.getElementById("octohaven-spark-server-status")
uiAddress = document.getElementById("octohaven-spark-ui-address")
masterAddress = document.getElementById("octohaven-spark-master-address")
unless status and uiAddress and masterAddress
    throw new Error("Cluster status entries are undefined")

_util = @util
_api = new @StatusApi
clstat = new @ClusterStatus

STATUS_PENDING = "Pending..."
STATUS_READY = "Cluster is ready"
STATUS_BUSY = "Cluster is busy"
STATUS_UNREACHABLE = "Cluster is unreachable"

# map status number to text representation
mapStatus = (status) ->
    return STATUS_READY if status == "0"
    return STATUS_BUSY if status == "-1"
    return STATUS_UNREACHABLE if status == "-2"
    return STATUS_PENDING
# map status number to element class
mapClass = (status) ->
    return "text-green" if status == "0"
    return "text-yellow" if status == "-1"
    return "text-red" if status == "-2"
    return "text-mute"

# settings cluster status
setClusterStatus = (clstat) ->
    status.className = ""
    _util.addClass(status, mapClass(clstat.get("status"), null))
    status.innerHTML = mapStatus(clstat.get("status"), null)
    uiAddress.innerHTML = clstat.getOrElse("spark-ui-address", "?")
    masterAddress.innerHTML = clstat.getOrElse("spark-master-address", "?")

reloadStatus = ->
    # run this function before performing any requests
    before = -> setClusterStatus(clstat)
    # once we have received response set all the elements to reflect change
    after = (ok, json) ->
        clstat = new @ClusterStatus(json["content"]) if ok
        setClusterStatus(clstat)
    # ask status for Spark Cluster info
    _api.requestStatus(before, after)

# reload status
reloadStatus?()
