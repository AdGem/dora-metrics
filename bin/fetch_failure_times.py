#!/usr/bin/env python3
# This is a quick and dirty procedural script to pull metrics from JIRA
# for the purposes of Dora. It is not intended to be a production script as is.
import requests
from requests.auth import HTTPBasicAuth
import json
import csv
import sys
from datetime import datetime
import os

url = ""

auth = HTTPBasicAuth(os.environ.get('JIRA_USER'), os.environ.get('JIRA_TOKEN'));

headers = {
  "Accept": "application/json"
}

# Tickets in Jira with label SystemFailure represent a failure for
# our purposes with Dora. The custom fields customfield_10009 and
# customfield_10008 are the start and stop times for the outage.
query = {
  'jql': 'labels in (SystemFailure) order by created ASC',
  'fields': 'customfield_10009,customfield_10008'
}

# TODO: Add error handling
response = requests.request(
   "GET",
   url,
   headers=headers,
   params=query,
   auth=auth
)

data = json.loads(response.text)

# the results of the Jira pull are output as CSV to stdout
# Duration hours is calculated by converting the start and end to datetimes
# and finding the difference in seconds. This is then divided by 3600 to get
# the outage in hours.
csv_writer = csv.writer(sys.stdout)
csv_writer.writerow(["KEY","FAILURE_TIME","RESOLUTION_TIME","DURATION_HOURS"])
for issue in data['issues']:
    from datetime import datetime
    end_dt = datetime.strptime(issue['fields']['customfield_10009'], "%Y-%m-%dT%H:%M:%S.%f%z");
    start_dt = datetime.strptime(issue['fields']['customfield_10008'], "%Y-%m-%dT%H:%M:%S.%f%z");
    duration = end_dt - start_dt
    csv_writer.writerow([issue['key'], issue['fields']['customfield_10008'], issue['fields']['customfield_10009'], duration.total_seconds()/3600])

