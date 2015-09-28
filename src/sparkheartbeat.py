import urllib2
import json

SPARK_REST_ENDPOINT = "/api/v1"
SPARK_REST_APPLICATIONS = "/applications"

# Spark cluster status:
#   0 - cluster is free
#   -1 - cluster is busy
#   -2 - cluster is unavailable
# takes Spark UI URL (usually it is localhost:8080)
def sparkStatus(sparkurl):
    status, arr = 0, list()
    try:
        f = urllib2.urlopen(sparkurl + SPARK_REST_ENDPOINT + SPARK_REST_APPLICATIONS)
    except:
        status = -2
    else:
        # if we cannot load json, return status -2
        try:
            arr = json.loads(f.read())
        except:
            status = -2
        index, ln = 0, len(arr)
        while index < ln and status >= 0:
            attempts = arr[index][u'attempts']
            for attempt in attempts:
                completed = attempt[u'completed']
                if not completed:
                    status = -1
                    break
            index += 1
    return status
