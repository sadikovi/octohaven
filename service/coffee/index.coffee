serverStatus = document.getElementById("octohaven-spark-server-status")
serverUIAddress = document.getElementById("octohaven-spark-ui-address")
serverMasterAddress = document.getElementById("octohaven-spark-master-address")
unless serverStatus and serverUIAddress and serverMasterAddress
    throw new Error("Server entries are unrecognized")

################################################################
# Request Spark Cluster status and set all the elements.
################################################################

# setting status of Spark cluster on web UI
setStatus = (status) ->
    # clean up status
    serverStatus.className = ""
    if status == false
        serverStatus.innerHTML = "#{@Status.STATUS_PENDING}"
        @util.addClass(serverStatus, "text-mute")
    else if status == 0
        @util.addClass(serverStatus, "text-green")
        serverStatus.innerHTML = "#{@Status.STATUS_READY}"
    else if status == -1
        @util.addClass(serverStatus, "text-yellow")
        serverStatus.innerHTML = "#{@Status.STATUS_BUSY}"
    else
        @util.addClass(serverStatus, "text-red")
        serverStatus.innerHTML = "#{@Status.STATUS_UNREACHABLE}"

# setting Spark UI address
setUIAddress = (address) ->
    # if address is not defined use question mark
    serverUIAddress.innerHTML = if address then "#{address}" else "?"

# setting Spark Master URL
setMasterAddress = (address) ->
    # if address is not defined use question mark
    serverMasterAddress.innerHTML = if address then "#{address}" else "?"

reloadStatus = ->
    status = new @Status
    # run this function before performing any requests
    before = ->
        setStatus(false)
        setUIAddress(false)
        setMasterAddress(false)
    # once we have received response set all the elements to reflect change
    after = (status, uiAddress, masterAddress) ->
        setStatus(status)
        setUIAddress(uiAddress)
        setMasterAddress(masterAddress)
    # ask status for Spark Cluster info
    status.requestStatus(before, after)

# reload status
reloadStatus?()

################################################################
# Request all jobs from the server
################################################################
