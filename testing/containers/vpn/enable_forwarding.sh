#/bin/sh

# Enable forwarding between eth1 and tun0.
# Tun0 is the virtual device of openvpn where 
# the user traffic comes from-
# eth1 is the interface to the internal docker network
# where the other containers are.

# Enable ip forwarding
sysctl -w net.ipv4.conf.all.forwarding=1

# Set iptable rules for forwarding
iptables -A FORWARD -i eth1 -o tun0 -j ACCEPT
iptables -A FORWARD -i tun0 -o eth1 -j ACCEPT
