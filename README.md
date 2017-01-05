# google-cloud-snapshot-python
Script to take automatic snapshots of all Google Cloud project Instances disks (python). You need googleapiclient for this.

Tested over python3

Usually this will run via crontab, all errors and good runs are sent to syslog.

To use this you need:
pip install --upgrade google-api-python-client

And:

gcloud init

Set up your project name on the script, and run :)
