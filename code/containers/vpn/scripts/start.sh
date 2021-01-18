
./bridge-start.sh
iptables -A INPUT -i tap0 -j ACCEPT
iptables -A INPUT -i br0 -j ACCEPT
iptables -A FORWARD -i br0 -j ACCEPT

ufw enable & ufw allow 1194/tcp & ufw reload & /etc/init.d/openvpn start & tail -f /dev/null