#
# File: addLocalUsers.py
# Author: Nick Olmsted, Code 42 Software
# Last Modified: 05-07-2013
#
# Takes a comma-delimited CSV file of user info and adds that to a local org. 
# 
# Python 2.7
# REQUIRED MODULE: Requests
#
# API Call: POST api/User
#
# Arguments: orgId, username
#

import sys

import json

import base64

import logging

import csv

import requests

# Set to your environments values
#cp_host = "<HOST OR IP ADDRESS>" ex: http://localhost or https://localhost
#cp_port = "<PORT>" ex: 4280 or 4285
#cp_username = "<username>"
#cp_password = "<pw>"
#cp_orgId = "<Org Id>" ex: 3
#cp_csv_file_name = "<filename.csv>" note: Place in same location as python script
cp_api = "/api/user"

#
# Compute base64 representation of the authentication token.
#
def getAuthHeader(u,p):

    token = base64.b64encode('%s:%s' % (u,p))

    return "Basic %s" % token

#
# Sets logger
#
def setLoggingLevel():
    logging.basicConfig(filename='addLocalUsers.log',level=logging.DEBUG, format='%(asctime)s %(message)s')

#
# Adds the user to the Local Org. Returns true if API call was successful
#
def addLocalUser(firstName, lastName, username, email, password, orgId):
    headers = {"Authorization":getAuthHeader(cp_username,cp_password)}
    url = cp_host + ":" + cp_port + cp_api
    payload = {'orgId': orgId, 'username': username, 'firstName': firstName, 'lastName': lastName, 'email': email, 'password': password}
    logging.debug("adding user: " + username)
    r = requests.post(url, data=json.dumps(payload), headers=headers)

    logging.debug(r.text)
    print r.text

    return r.status_code == requests.codes.ok

#
# Reads CSV file that contains a comma-delimited list of local users and adds the users through the API.
#
def addLocalUsers():
    logging.debug('BEGIN - addLocalUsers')
    count = 0
    try:
        with open(cp_csv_file_name, 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for item in csvreader:
                if item:
                    if (len(item) == 5):
                        #print ', '.join(item)
                        print 'firstName:[' + item[0] + '] lastName:[' + item[1] + '] username[' + item[2] + '] email:[' + item[3] + '] password:[' + item[4] + '] orgId:[' + cp_orgId + ']'
                        logging.debug('firstName:[' + item[0] + '] lastName:[' + item[1] + '] username[' + item[2] + '] email:[' + item[3] + '] password:[' + item[4] + '] orgId:[' + cp_orgId + ']')
                        if (addLocalUser(item[0], item[1], item[2], item[3], item[4], cp_orgId)):
                            count = count + 1
                    else:
                        print 'Missing item in CSV file, so skipping adding this user. Check the following line item: ' + ', '.join(item)
                        logging.debug('Missing item in CSV file, so skipping adding this user. Check the following line item: ' + ', '.join(item))
    except csv.Error as e:
        sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))

    print "Total Users Added: " + str(count)
    logging.debug("Total Users Added: " + str(count))
    logging.debug('END - addLocalUsers')

setLoggingLevel()
addLocalUsers()
