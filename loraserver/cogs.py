import requests
import os
import urllib2, base64
import datetime
import csv
from dateutil import parser
from dateutil import tz


cloudantHost = "https://8d7e1f8e-1f7d-4d64-8788-490379bcbad5-bluemix.cloudant.com/"
cloudantusername = "8d7e1f8e-1f7d-4d64-8788-490379bcbad5-bluemix"
cloudantPassword = "b69d78f8c5aad962b42e278c73cce8238522bdd4a73aaeec73fa8efc11524db3"
operationsDB = "operations/_find"

selector = {}
timestamp = {}
reqObj = {}
sortObj = {}
sortArray = []
sort = {}


def getDev(dev):

    print "--------"
    print dev

    try:

        #get system time in UTC
        currentTime = datetime.datetime.utcnow()
        #Encode Authorization string using password and username
        base64string = base64.encodestring('%s:%s' % (cloudantusername, cloudantPassword)).replace('\n', '')

        #create headers json object
        headers = {'content-type' : 'application/json', "Authorization" : "Basic %s" % base64string}
        headersObj = json.dumps(headers)

        #convert time to ISO string and add to request body object
        timestamp["$lt"] = currentTime.strftime('%Y-%m-%dT%H:%M:%S.000Z')

        selector["timestamp"] = timestamp
        selector["deviceId"] = dev

        sortObj["timestamp"] = "desc"
        sortArray.append(sortObj)

        #Final request body object
        reqObj["selector"] = selector
        reqObj["sort"] = sortArray
        # reqObj["limit"] = int(dataLimit)

        print "Request Body Object..."
        print reqObj

        #Post the requst body
        resp = requests.post(data = json.dumps(reqObj), url = cloudantHost+levelmeterDB, headers = headers)

        print "Response status code.. " + str(resp.status_code)

        #check whether request was succesful.
        if (resp.status_code == 200):

            #parse response string into a json object
            respObj = json.loads(resp.text)
            print respObj
            return respObj

        else:
            print "Encountered error fetching data, check internet connection"
            return resp.status_code



    except Exception as e:
        #return "err"
        print e
