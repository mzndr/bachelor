#!/bin/sh
easyrsa build-client-full "$1" nopass
mkdir /etc/openvpn/userdata
cp /etc/openvpn/pki/issued/$1.crt /etc/openvpn/userdata/$1.crt 
cp /etc/openvpn/pki/private/$1.key /etc/openvpn/userdata/$1.key
ovpn_getclient "$1" > "/etc/openvpn/userdata/$1.ovpn"

chmod 777 -R /etc/openvpn/userdata