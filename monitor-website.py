import smtplib
import os
import paramiko
import boto3
import time
import schedule
import requests

EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
AWS_REGION = os.environ.get('AWS_REGION')
INSTANCE_ID = '107.20.119.101'

def restart_server_and_container():
    # Restart EC2 instance
    print('Rebooting the server...')
    ec2_client = boto3.client('ec2', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=AWS_REGION)
    ec2_client.reboot_instances(InstanceIds=[INSTANCE_ID])

    # Wait for the instance to be running
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds=[INSTANCE_ID])

    # Restart the application
    while True:
        instance = ec2_client.describe_instances(InstanceIds=[INSTANCE_ID])['Reservations'][0]['Instances'][0]
        if instance['State']['Name'] == 'running':
            time.sleep(5)
            restart_container()
            break

def send_notification(email_msg):
    print('Sending an email...')
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.ehlo()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        message = f"Subject: SITE DOWN\n{email_msg}"
        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, message)

def restart_container():
    # Your code to restart the container goes here
    print('Restarting the application...')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname='107.20.119.101', username='root', key_filename='/Users/walid/.ssh/id_rsa')
    stdin, stdout, stderr = ssh.exec_command('docker start c3e706bc905e')
    print(stdout.readlines())
    ssh.close()
    # Modify this part to restart your container in AWS environment
    # You might use AWS SDK for ECS, EKS, or other service depending on your container setup.

def monitor_application():
    try:
        response = requests.get('http://107.20.119.101:8080/')
        if response.status_code == 200:
            print('Application is running successfully!')
        else:
            print('Application Down. Fix it!')
            msg = f'Application returned {response.status_code}'
            send_notification(msg)
            restart_container()
    except Exception as ex:
        print(f'Connection error happened: {ex}')
        msg = 'Application not accessible at all'
        send_notification(msg)
        restart_server_and_container()

schedule.every(5).minutes.do(monitor_application)

while True:
    schedule.run_pending()
    time.sleep(1)
schedule.run_pending()