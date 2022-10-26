# You should enhance this script to monitor some additional items.
#!/usr/bin/bash
#
# Some basic monitoring functionality; Tested on Amazon Linux 2
#
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
MEMORYUSAGE=$(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')
PROCESSES=$(expr $(ps -A | grep -c .) - 1)
CPU_DATA=$(lscpu)
HTTPD_PROCESSES=$(ps -A | grep -c httpd)
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
PUBLIC_HOSTNAME=$(curl -s http://169.254.169.254/latest/meta-data/public-hostname)
SECURITY_GROUPS=$(curl -s http://169.254.169.254/latest/meta-data/security-groups)
echo "Running script..."
echo "############################################"
echo "Instance ID: $INSTANCE_ID"
echo "############################################"
echo "Memory utilisation: $MEMORYUSAGE"
echo "############################################"
echo "No of processes: $PROCESSES"
echo "############################################"
echo "Public ipv4 address: $PUBLIC_IP"
echo "############################################"
echo "Public hostname: $PUBLIC_HOSTNAME"
echo "############################################"
echo "Security group(s): $SECURITY_GROUPS"
echo "############################################"
echo "CPU information: $CPU_DATA"
echo "################### END ####################"

if [ $HTTPD_PROCESSES -ge 1 ]
then
    echo "Web server is running"
else
    echo "Web server is NOT running"
fi

