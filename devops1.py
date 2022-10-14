import subprocess
import boto3
import time
import random
import webbrowser
import urllib

##############################################################
#creating ec2 instance
##############################################################

ec2 = boto3.resource('ec2')
print ("..................INSTANCE...................")
print ("#############################################")
print ("Launching EC2 instance...")
print ("#############################################")

new_instances = ec2.create_instances(
    KeyName = 'MyKeyPair2022',
    SecurityGroupIds = ['sg-04405d3a7ef8c9b5f'],
    ImageId='ami-026b57f3c383c2eec',
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.nano',
    UserData="""#!/bin/bash
    sudo yum update
    yum install httpd -y
    systemctl enable httpd
    systemctl start httpd

    echo '<html>' > index.html

    echo 'Instance ID: ' >> index.html
    curl http://169.254.169.254/latest/meta-data/instance-id >> index.html
    echo ' | ' >> index.html

    echo 'AMI ID: ' >> index.html
    curl http://169.254.169.254/latest/meta-data/ami-id >> index.html
    echo ' | ' >> index.html

    echo 'Instance Type: ' >> index.html
    curl http://169.254.169.254/latest/meta-data/instance-type >> index.html        
    echo ' | ' >> index.html

    echo 'Public IP Address: ' >> index.html
    curl http://169.254.169.254/latest/meta-data/public-ipv4 >> index.html
    echo ' | ' >> index.html

    echo 'Image: ' >> index.html
    echo '<img src='http://media.corporate-ir.net/media_files/IROL/17/176060/Oct18/Amazon%20logo.PNG'>' >> index.html

    echo '</html>' >> index.html

    cp index.html /var/www/html/index.html


    """,

TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags' : [
                {
                    'Key' : 'Name',
                    'Value' : 'WebServer',

                }
            ]
        }
    ],
)
while new_instances[0].state['Name'] != 'running':
     print ("Current instance state: ")
     print (new_instances[0].state['Name'])
     print ("Waiting for instance status to be running...")
     print ("...loading...")
     new_instances[0].reload()
     time.sleep(10)

#waiter method to check the instance state
#0 so that I am pointing to the instance just created
new_instances[0].wait_until_running()

#with waiter method, the reload method is used
#so that the object's properties are refreshed
new_instances[0].reload()
print ("#############################################")
print ("Instance is now running...")
print ("#############################################")

instance_ip = new_instances[0].public_ip_address

print ("Opening Web Browser...")
print ("#############################################")
#sleep timer to wait for the UserData script
#to install and start the web server
time.sleep(30)


try:
    webbrowser.open_new_tab('http://' + instance_ip)
    print ("Web Browser launched successfully!")
except Exception as error:
    print (error)
    print ("!!!")
    print ("The web browser was not accessible...")

#download image
print ("...................BUCKET....................")
print ("#############################################")
print ("Downloading image to display on S3 Bucket Browser...")
image_url = "http://devops.witdemo.net/logo.jpg"
image_name = "logo.jpg"

#urllib.request module imported above
#method is called with the link and filename as parameters
urllib.request.urlretrieve(image_url, image_name)

##############################################################
#create an s3 bucket
##############################################################

s3 = boto3.resource("s3")
s3c = boto3.client("s3")
bucket_name = "sod-" + str(random.randint(1,10000000))
response = s3.create_bucket(Bucket=bucket_name)
print ("#############################################")
print ("Bucket name: " + bucket_name)

#set up static website hosting on an S3 bucket by
#creating a BucketWebsite resource
website_configuration = {
 'ErrorDocument': {'Key': 'error.html'},
 'IndexDocument': {'Suffix': 'index.html'},
}
bucket_website = s3.BucketWebsite(bucket_name)
response = bucket_website.put(WebsiteConfiguration=website_configuration)

#adding image to bucket
#make sure that it is public
s3c.upload_file('logo.jpg', bucket_name, 'logo.jpg', ExtraArgs = {'ContentType': 'image/jpg', 'ACL': 'public-read',})

s3c.upload_file('index.html', bucket_name, 'index.html', ExtraArgs = {'ContentType': 'text/html', 'ACL': 'public-read',})

#write URLs to a file
file = open('sodonovan.txt', 'w')
file.write('Instance URL: ' + new_instances[0].public_ip_address + '\nBucket URL: http://' + bucket_name + '.s3-website-us-east-1.amazonaws.com')
file.close()

print ("#############################################")
print ("Opening Bucket Web Browser...")

try:
    webbrowser.open_new_tab('http://' + bucket_name + '.s3-website-us-east-1.amazonaws.com')
    print ("Bucket Web Browser launched successfully!")
except Exception as error:
    print (error)
    print ("!!!")
    print ("The buckets' web browser was not accessible...")

print ("#############################################")
print (".................MONITORING..................")
#run the monitor script
result=subprocess.run("scp -o StrictHostKeyChecking=no -i MyKeyPair2022.pem  monitor.sh ec2-user@" + instance_ip + ":.", shell=True)
subprocess.run("ssh -o StrictHostKeyChecking=no -i MyKeyPair2022.pem  ec2-user@" + instance_ip + " 'chmod 700 monitor.sh'", shell=True)
subprocess.run("ssh -o StrictHostKeyChecking=no -i MyKeyPair2022.pem  ec2-user@" + instance_ip + " ' ./monitor.sh'", shell=True)

if result.returncode > 0:
    print ("There was an error copying the script to your instance.")

#top marks, counting towards robustness
# write a loop that checks every five seconds when waiting until running
# keep trying if it fails
# end of userdata
# write a file inside userdata and check for its creation which will ensure that userdata has finsihed
# touch /home/ec2.user/textfile
#get the most recent ami




