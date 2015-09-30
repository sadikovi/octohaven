serverStatus = document.getElementById("octohaven-spark-server-status")
serverUIAddress = document.getElementById("octohaven-spark-ui-address")
serverMasterAddress = document.getElementById("octohaven-spark-master-address")
unless serverStatus and serverUIAddress and serverMasterAddress
    throw new Error("Server entries are unrecognized")
# constants for status
STATUS_PENDING = "Pending..."
STATUS_READY = "Server is ready"
STATUS_BUSY = "Server is busy"
STATUS_UNREACHABLE = "Server is unreachable"

# setting status of Spark cluster on web UI
setStatus = (status) ->
    # clean up status
    serverStatus.className = ""
    if status == false
        serverStatus.innerHTML = "#{STATUS_PENDING}"
        @util.addClass(serverStatus, "text-mute")
    else if status == 0
        @util.addClass(serverStatus, "text-green")
        serverStatus.innerHTML = "#{STATUS_READY}"
    else if status == -1
        @util.addClass(serverStatus, "text-yellow")
        serverStatus.innerHTML = "#{STATUS_BUSY}"
    else
        @util.addClass(serverStatus, "text-red")
        serverStatus.innerHTML = "#{STATUS_UNREACHABLE}"

# setting Spark UI address
setUIAddress = (address) ->
    # if address is not defined use question mark
    if address
        serverUIAddress.innerHTML = "#{address}"
    else
        serverUIAddress.innerHTML = "?"

# setting Spark Master URL
setMasterAddress = (address) ->
    # if address is not defined use question mark
    if address
        serverMasterAddress.innerHTML = "#{address}"
    else
        serverMasterAddress.innerHTML = "?"

requestStatus = ->
    # first we update state on "pending"
    [status, uiAddress, masterAddress] = [false, false, false]
    setStatus(status)
    # send request to find out status
    @loader.sendrequest "get", "/api/v1/sparkstatus", {}, null
    , (code, response) =>
        if code == 200
            json = JSON.parse response
            status = json["content"]["sparkstatus"]
            uiAddress = json["content"]["spark-ui-address"]
            masterAddress = json["content"]["spark-master-address"]
        else
            # report error at this stage
            console.log "[ERROR] #{response}"
        setStatus(status)
        setUIAddress(uiAddress)
        setMasterAddress(masterAddress)
    , (error, response) =>
        setStatus(false)
        setUIAddress(false)
        setMasterAddress(false)
        console.log "[ERROR] #{response}"

# reload status
requestStatus?()
