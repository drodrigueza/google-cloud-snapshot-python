
import pprint
import time
import datetime
import subprocess
import syslog

from oauth2client.client import GoogleCredentials
from googleapiclient import discovery

credentials = GoogleCredentials.get_application_default()
service = discovery.build('compute', 'v1', credentials=credentials)

project=''
retention=15

date = time.strftime('%Y-%m-%d-%H-%M')

delta_date = datetime.date.today() - datetime.timedelta(days=retention)
delete_date = delta_date.strftime('%Y-%m-%d')

zones = service.zones().list(project=project).execute()

syslog.syslog('Starting Snapshot Operations')

for zone in zones['items']:
    instance_list = service.instances().list(project=project, zone=zone['name']).execute()
    if 'items' in instance_list:
        for instance in instance_list['items']:
            if 'disks' in instance:
                for disk in instance['disks']:
                    snapshot_name = 'auto-' + disk['deviceName'] + '-' + date
                    syslog.syslog(syslog.LOG_INFO, "Starting Snapshot on " + disk['deviceName'] + " with name " + snapshot_name)
                    snapped = subprocess.Popen(["gcloud", "compute", "disks", "snapshot", disk['deviceName'], "--snapshot-names", snapshot_name, "--zone", zone['name']], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    std_out, std_err = snapped.communicate()
                    cmd_output = std_err.decode("utf-8")
                    if not 'Created' in cmd_output or snapped.returncode != 0:
                        syslog.syslog(syslog.LOG_ERR, "ERROR ALERT - Snapshot error on: " + disk['deviceName'] + " " + snapshot_name + " " + cmd_output)


snapshots = service.snapshots().list(project=project).execute()

if 'items' in snapshots:
    for snap in snapshots['items']:
        if snap['creationTimestamp'][:10] < delete_date and 'auto' in snap['name']:
            syslog.syslog(syslog.LOG_INFO,"Snapshot delete on " + snap['name'])
            snapdelete = service.snapshots().delete(project=project, snapshot=snap['name']).execute()
            if not 'operationType' in snapdelete:
                syslog.syslog(syslog.LOG_ERR, "ERROR ALERT - Snapshot delete error on: " + snap['name'])

