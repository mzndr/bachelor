#!/bin/bash
#Create static arp entry for the gateway, so arp spoofing won't affect the VPN.
arp -s $1 $2   

ufw enable 
ufw allow 1194/tcp 
/etc/init.d/openvpn start 
tail -f /dev/null 