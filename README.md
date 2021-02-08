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
```bash
sudo apt install mysql-server 
```
2. Login as the root and create a vitsl user for the database
```sql
CREATE USER 'vitsl'@'%' IDENTIFIED BY 'passwort';
```
3. Create the vitsl database
```sql
CREATE DATABASE vitsl;
```
4. Allow the vitsl user to do operations on the database
```sql
GRANT ALL PRIVILEGES ON vitsl.* TO 'vitsl'@'%';
FLUSH PRIVILEGES;
```
### Install Docker

1. Install Docker by following this guide: https://docs.docker.com/engine/install/ubuntu/

2. Add the user that runs the application to the docker group:
```bash        
sudo groupadd docker
sudo usermod -aG docker $USER
```
3. Re-Login to the user for changes to take effect.

4. Check if your docker installation was succesfull
```bash
docker run hello-world
```
## Install Python dependencies

1. Install pip3
```bash
sudo apt install python3-pip
```
2. Install venv
```bash
sudo pip3 install virtualenv 
```
3. In the vitsl folder do
```bash
python3 -m venv ./env
```
4. Activate the venv and install dependencies
```bash
source ./env/bin/activate
pip3 install -r ./requirements.txt
deactivate
```
5. Move the activate_this script into the env folder (only needed for wsgi deployment on an external webserver)
```bash
mv ./activate_this.py ./env/bin/
```

## Configuration

You can find the configuration file at vitsl/flask_app/config.py

1. Change the *PUBLIC_IP* line to the public IP of your server
```py
PUBLIC_IP = "your IP here"
```
2. Set the desired portrange for the vpn containers
```py
VPN_PORT_RANGE = (9000,9100)
```
3. Allow the portrange in your firewall
```bash
sudo ufw allow 9000:9100/tcp
```
4. Change the mySQL Connection string to your user
```py
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://vitsl:<YOUR PASSWORD HERE>@localhost:3306/vitsl"
```
4. Change the secret key to something random
```bash
head -128 /dev/urandom | md5sum
>> 9e83cab0f3ed72718d0d015545f54e8c

SECRET_KEY = "9e83cab0f3ed72718d0d015545f54e8c"
```
## Starting in foreground

In the ```./vitsl directory``` do:

1. Activate the venv
```bash
source ./env/bin/activate
```
2. Start the app
```bash
./run_prod.sh
```

## Deploying with Apache2 (might cause permission related errors)

1. Install wsgi for apache
```bash
sudo apt-get install libapache2-mod-wsgi-py3
```
2. Enable wsgi for apache
```bash
sudo a2enmod wsgi 
```
3. Move the vitsl folder to ```/var/www```
```bash
sudo cp -r ./vitsl /var/www
```
4. Create a new virtual host. 
```bash
sudo nano /etc/apache2/sites-available/vitsl.conf 
```
```xml
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
```
You might have to change the port of the virtual host

5. Add the www-data user to the docker group
```bash
sudo usermod -aG docker www-data 
```
6. Enable the new site
```bash
sudo a2ensite vitsl.conf 
```
7. Restart apache2
```bash
sudo service apache2 restart
```
## Creating a Container Image

1. You can use the ```apache_tutorial``` image as an example. 

2. Create a new folder in the containers directory. (default location ```.../vitsl/containers```).
The name of the folder will be the name of the image.

3. Inside that folder create a dockerfile to build the desired image (https://docs.docker.com/develop/develop-images/dockerfile_best-practices/). Please take note that the container has to be kept running. Exited containers might lead to errors.

4. Next to the dockerfile, place a ```properties.json``` file. It needs the following keys:
```js
        {
                "description":"Image description here", // Description of the image
                "show_info":true,                       // Show or hide container ip and description to the user
                "hostname":"apache_container",          // Desired hostname for the container
                "flags":{}                              // Flags
        }
```

Inside that file, you can use ```[! container_ip !]``` to insert the ip of the container. This might be usefull to give users instructions on what to do. For example you could tell them in the description to ssh to the container with ```ssh bob@[! container_ip !]```

4. Inside the folder of your image, you can place other files that might be needed for building the image (configuration files etc.). If you don't want to rely on the COPY command, the folder itself gets mounted at runtime inside the container at /container_data

### Placing flags
You can place a flag in any file you want. You do this by placing a textmarker like the following: 
```
[# <flag name here> #]
```
The name of the flag may consist out of lowercase letters, numbers and underscores (a-z,0-9._)

For example, you could place a flag inside a python script that gets run by the container:
```py
def some_kind_of_challenge():
        flag = "[# challenge_1 #]"
        # Do some challenging stuff here!
        if user_has_won:
                return flag
        else:
                return "not a flag!"
```
You could also put a flag inside C code, that gets compiled into a binary when
the image gets built. The possibilities are endless!

After you have placed a flag, and have given it a name, you need to create a entry for it in the properties.json file of the container:
```js
{
  // ...

  "flags":{
    "challenge_1":{                     // The key has to be the name of the flag
      "description":"What to do",       // A descripton on how to retrieve the flag
      "hints":[                         // A list of hints that the user can recieve to help him to get the flag.
        "Maybe you need to connect to the networks vpn first?",
        "Connect to the network with openvpn, then access the (http://[! container_ip !]).",
        "Copy the flag and redeem it at the redeem flag form."
      ]
    },
   "challenge_2":{                     
      "description":"What to do", 
      // ...
    }
  }
}
```
Thats it!