File: addLocalUsers.py ReadMe
Author: Nick Olmsted, Code 42 Software
Last Modified: 05-07-2013

SUMMARY:
Takes a comma-delimited CSV file of user info and adds those users to an Org.

PRE-REQS:
* Python 2.7: http://www.python.org/getit/
* Setup Tools: https://pypi.python.org/pypi/setuptools#files
* Requests Module: http://www.python-requests.org/
* PROe Server Host and Port
* PROe Server Admin and Password
* CSV file name
* ORG ID. You can get this by navigating to the org and getting the org id value from the url. For examples: http://localhost:4280/console/app.html#v=orgs:overview&t=0mbunsjn5sbz91tlzg5clpd7qg&s=orgDetail&so[orgId]=3 would be an Org ID of 3.

STEPS:
1. Create CSV file with comma-delmited list of users to add to the PROe Server. Save it in the same location as the addLocalUsers.py script. Format for file: [firstName,lastName,username,email,password]
2. Update addLocalUsers.py and add your environment values for cp_host, cp_port, etc.
3. Execute the script and check the addLocalUsers.log file for your results.

Example CSV file:
John1,Doe1,johndoe1,john1@example.com,Super-secret
John2,Doe2,johndoe2,john2@example.com,Super-secret
John3,Doe3,johndoe3,john3@example.com,Super-secret


RESULTS:
Local Users will be added to the specified CrashPlan Organization according to the users within the CSV file. 
