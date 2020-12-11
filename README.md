# Virtual ITS-Lab
A docker-based application to provide isolated virtual network environments for it-security education. 
It incorporates a CTF-like flag system to verify if students have completed their tasks.
This application is supposed to provide students the ability to do their it-security seminar from home, because of the current Covid-19 pandemic.

Networks can be started from network presets, which are composed out of different docker containers. 
Files in the container can use a special syntax to insert generated CTF-like flags, which can be redeemed
by the students. Different tasks can be formed arround those flags. For example, a container could broadcast a flag
in the network, and students would have to sniff the traffic in order to learn about WireShark and network sniffing.

Users can be seperated into groups, and then those groups or individual users can be assigned to networks. Assigned users can use OpenVPN to connect 
to their assigned virtual networks.

"virtual-its-lab" is also part of my bachelor thesis.
