#
# File: deactivateDevices.py
# Author: Nick Olmsted, Code 42 Software
# Last Modified: 05-24-2013
#
# Uses relativedelta python module that can be downloaded from:
# http://labix.org/python-dateutil
#
# Deactivates users based on the number of months since they have last connected to a master server
# Params:
# 1 arg - number of months (i.e 3)
# 2 arg - type of logging (values: verbose, nonverbose)
# 3 arg - set to deactivate devices or only print the devices that will be deactivated, but not deactivate them.
#        - values: deactivate, print
# Example usages: 
# python deactivateDevices.py 3 print DEBUG
# python deactivateDevices.py 3 deactivate
#
# NOTE: Make sure to set cpc_host, cpc_port, cpc_username, cpc_password to your environments values.
#

import sys

import json

import httplib

import base64

import math

import calendar

import logging

from dateutil.relativedelta import *

from datetime import *

# Number of Months of no backup (should be a number)
MAX_NUM_OF_MONTHS = str(sys.argv[1])

# Deactivate devices (should be text that equals "deactivate")
RUN_DEACTIVATION_SCRIPT = str(sys.argv[2])

# verbose logging (set to DEBUG for additional console output)
cp_logLevel = "INFO"
if len(sys.argv)==4:
    cp_logLevel = str(sys.argv[3])

MAX_PAGE_NUM = 250
NOW = datetime.now()

# Set to your environments vlaues
cpc_host = "<HOST OR IP ADDRESS>"
cpc_port = "<PORT>"
cpc_username = "<username"
cpc_password = "<pw>"

# Test values
#cpc_host = "localhost"
#cpc_port = "4285"
#cpc_username = "admin"
#cpc_password = "admin"

#
# Compute base64 representation of the authentication token.
#
def getAuthHeader(u,p):

    # 

    token = base64.b64encode('%s:%s' % (u,p))

    return "Basic %s" % token

#
# Get the total page count that is used to determine the number of GET requests needed to return all
# all of the devices since the API currently limits this call to return 250 devices. 
# Returns: total number of requests needed
#
def getDevicesPageCount():
    logging.debug("BEGIN - getDevicesPageCount")

    headers = {"Authorization":getAuthHeader(cpc_username,cpc_password),"Accept":"application/json"}

    try:
        conn = httplib.HTTPSConnection(cpc_host,cpc_port)
        conn.request("GET","/api/Computer?pgNum=1&pgSize=1&incCounts=true&active=true",None,headers)
        data = conn.getresponse().read()
        conn.close()

        devices = json.loads(data)['data']
        totalCount = devices['totalCount']

        # num of requests is rounding down and not up. Add+1 as we know we are completed because the computerId value returns as 0
        numOfRequests = math.ceil(totalCount/MAX_PAGE_NUM)+1

        logging.debug("numOfRequests: " + str(numOfRequests))
        logging.debug("END - getDevicesPageCount")
        return numOfRequests

    except httplib.HTTPException as inst:

        logging.error("Exception: %s" % inst)

        return None

    except ValueError as inst:

        logging.error("Exception decoding JSON: %s" % inst)

        return None

#
# Calls the API to get a list of active devices. Calls the API multiple times because the API limits the results to 250. 
# Loops through the devices and adds devices that are older than the month threshold (i.e. devices older than 3 months)
# Parameter: totalNumOfRequest - integrer that is used to determine the number of times the API needs to be called. 
# Returns: list of devices to be deactivated
# API: /api/Computer/
# API Params:
#   pgNum - pages through the results.
#   psSize - number of results to return per page. Current API max is 250 results.
#   incCounts - includes the total count in the result
#   active - return only active devices
#
def getDevices(totalNumOfRequests):

    logging.debug("BEGIN - getDevices")

    headers = {"Authorization":getAuthHeader(cpc_username,cpc_password),"Accept":"application/json"}

    currentRequestCount=0
    deactivateCount = 0
    deactivateList = []

    while (currentRequestCount <= totalNumOfRequests):

        logging.debug("BEGIN - getDevices - Building devices list request count: " + str(currentRequestCount))

        try:
            currentRequestCount = currentRequestCount + 1
            conn = httplib.HTTPSConnection(cpc_host,cpc_port)
            conn.request("GET","/api/Computer?pgNum=" + str(currentRequestCount) + "&pgSize=250&incCounts=true&active=true",None,headers)
            data = conn.getresponse().read()
            conn.close()
        except httplib.HTTPException as inst:

            logging.error("Exception: %s" % inst)

            return None

        except ValueError as inst:

            logging.error("Exception decoding JSON: %s" % inst)

            return None

        devices = json.loads(data)['data']
        for d in devices['computers']:
            # Get fields to compasre
            computerId = d['computerId']
            lastConnected = d['lastConnected']
            deviceName = d['name']
            # If last connected date is greater than month threshold than add device to deactivate list
            dtLastConnected = datetime.strptime(str(lastConnected)[:10], "%Y-%m-%d")
            comparedate = datetime(dtLastConnected.year, dtLastConnected.month, dtLastConnected.day)
            monthThreshold = NOW+relativedelta(months=-int(MAX_NUM_OF_MONTHS))
            if monthThreshold > comparedate:
                try:
                    logging.debug("DEACTIVATE - device id: " + str(computerId) + " device name: " + str(deviceName) + " with last connected date of: " + str(lastConnected))
                except:
                    #ignore name errors
                    pass
                deactivateCount = deactivateCount + 1
                deactivateList.append(d)
            else:
                logging.debug("IGNORE - device id: " + str(computerId) + " with last connected date of: " + str(lastConnected))
        
        logging.info("Building devices list... request count:  " + str(currentRequestCount))

        logging.debug("TOTAL Devices that are scheduled to be deactivated: " + str(deactivateCount))
        logging.debug("END - getDevices")

    return deactivateList

#
# Prints out all devices that will be deactivated
#
def printDevices(devices):
    count = 0
    logging.debug("BEGIN - printDevices")

    logging.debug("The following devices will be deactivated as they have not connected in more than " + str(MAX_NUM_OF_MONTHS) + " month(s):")
    for d in devices:
        count = count + 1
        try:
            logging.info("device name: " + str(d['name']))
        except:
            #ignore any name exceptions
            pass

    logging.debug("END - printDevices")

    return count

#
# Calls the API to deactivate a single device
#
def deactivateDevice(computerId):

    headers = {"Authorization":getAuthHeader(cpc_username,cpc_password),"Accept":"application/json","Content-Type":"application/json"}

    try:

        conn = httplib.HTTPSConnection(cpc_host,cpc_port)

        conn.request("PUT","/api/ComputerDeactivation/" + str(computerId),None,headers)

        data = conn.getresponse().read()

        conn.close()

        # Since no response is returned from a PUT request as long as no exception is thrown we can assume the device was deactivated
        return "success"

    except httplib.HTTPException as inst:

        logging.error("Exception in HTTP operations: %s" % inst)

        return None

    except ValueError as inst:

        logging.error("Exception decoding JSON: %s" % inst)

        return None

#
# Sets logger to file and console
#
def setLoggingLevel():
    # set up logging to file
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename='deactivateDevices.log',
                        filemode='w')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    
    if(cp_logLevel=="DEBUG"):
        console.setLevel(logging.DEBUG)
    else:
        console.setLevel(logging.INFO)
    
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

#
# Deactivates devices if argument is set to deacivate
#
def deactivateDevices():
    logging.debug("BEGIN - deactivateDevices")

    pageCount = getDevicesPageCount()
    devices = getDevices(pageCount)
    deviceCount = printDevices(devices)

    count = 0
    # Deactivate devices
    if (RUN_DEACTIVATION_SCRIPT == "deactivate"):
        logging.info("RUN_DEACTIVATION_SCRIPT set to true")

        for d in devices:
            succ = deactivateDevice(d["computerId"])
            try:
                if succ:
                    count = count + 1
                    logging.info("Deactivation successful for id: " + str(d["computerId"]) + " device name: " + str(d["name"]))
                else:
                    logging.info("Deactivation unsuccessful for id: " + str(d["computerId"]) + " device name: " + str(d["name"]))
            except:
                #ignore any name errors
                pass
    else:
        logging.info("RUN_DEACTIVATION_SCRIPT set to false")

    logging.info("TOTAL devices schdeuled to be deactivated: " + str(deviceCount))
    logging.info("TOTAL devices deactivated: " + str(count))

    logging.debug("END - DeactivateDevices")

setLoggingLevel()
deactivateDevices()