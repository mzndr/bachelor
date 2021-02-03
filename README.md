# Virtual ITS-Lab
A docker-based application to provide isolated virtual network environments for it-security education. 
It incorporates a CTF-like flag system to verify if students have completed their tasks.
This application is supposed to provide students the ability to do their it-security seminar from home, because of the current Covid-19 pandemic.

Networks can be started from network presets, which are composed out of different docker containers. 
Files in the container can use a special syntax to insert generated CTF-like flags, which can be redeemed
by the students. Different tasks can be formed arround those flags. 

Users can be seperated into groups, and then those groups or individual users can be assigned to networks. Assigned users can use OpenVPN to connect 
to their assigned virtual networks.

"virtual-its-lab" is also part of my bachelor thesis.

## Installation
### Install MySQL-server
1. Install the MySQL Server

        sudo apt install mysql-server 

2. Login as the root and create a vitsl user for the database

        CREATE USER 'vitsl'@'%' IDENTIFIED BY 'passwort';

3. Create the vitsl database

        CREATE DATABASE vitsl;

4. Allow the vitsl user to do operations on the database

        GRANT ALL PRIVILEGES ON vitsl.* TO 'vitsl'@'%';
        FLUSH PRIVILEGES;

### Install Docker

1. Install Docker by following this guide: https://docs.docker.com/engine/install/ubuntu/

2. Add the user that runs the application to the docker group:
        
        sudo groupadd docker
        sudo usermod -aG docker $USER

3. Re-Login to the user for changes to take effect.

4. Check if your docker installation was succesfull
        
        docker run hello-world

## Install Python dependencies

1. Install pip3

        sudo apt install python3-pip

2. Install venv

        sudo pip3 install virtualenv 

3. In the vitsl folder do

        python3 -m venv ./env

4. Activate the venv and install dependencies

        source ./env/bin/activate
        pip3 install -r ./requirements.txt
        deactivate

5. Move the activate_this script into the env folder

        mv ./activate_this.py ./env/bin/


## Configuration
1. Change the *PUBLIC_IP* line to the public IP of your server

        PUBLIC_IP = "your IP here"

2. Set the desired portrange for the vpn containers

        VPN_PORT_RANGE = (9000,9100)

3. Allow the portrange in your firewall

        sudo ufw allow 9000:9100/tcp
4. Change the mySQL Connection string to your user

        SQLALCHEMY_DATABASE_URI = "mysql+pymysql://vitsl:<YOUR PASSWORD HERE>@localhost:3306/vitsl"

4. Change the secret key to something random

        head -128 /dev/urandom | md5sum
        >> 9e83cab0f3ed72718d0d015545f54e8c

        SECRET_KEY = "9e83cab0f3ed72718d0d015545f54e8c"

## Deploying with Apache2

1. Install wsgi for apache

        sudo apt-get install libapache2-mod-wsgi-py3

2. Enable wsgi for apache

        sudo a2enmod wsgi 

3. Move the vitsl folder to /var/www

        sudo cp -r ./vitsl /var/www

4. Create a new virtual host. 

        sudo nano /etc/apache2/sites-available/vitsl.conf 

        <VirtualHost *:80>
        ServerName example.com
        WSGIScriptAlias / /var/www/vitsl/vitsl.wsgi
        <Directory /var/www/vitsl/flask_app>
                WSGIProcessGroup vitsl
                WSGIApplicationGroup %{GLOBAL}
                Order deny,allow
                Allow from all
        </Directory>
        </VirtualHost>

    You might have to change the port of the virtual host

5. Add the www-data user to the docker group

       sudo usermod -aG docker www-data 

6. Enable the new site

        sudo a2ensite vitsl.conf 

7. Restart apache2

        sudo service apache2 restart
