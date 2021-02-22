import datetime
import json
import os
import random
import re
import shutil
import tempfile
import threading
import uuid
from distutils.dir_util import copy_tree

from flask import abort, current_app
from flask_app.core import utils
from flask_app.core.exceptions import docker as errors
from flask_app.core.models.core import BaseModel
from flask_security import current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

import docker

from ..db import db

### Constants ###
CONTAINER_STATE_RUNNING = "running"
CONTAINER_STATE_RESTARTING = "restarting"
CONTAINER_STATE_PAUSED = "paused"
CONTAINER_STATE_EXITED = "exited"
CONTAINER_STATE_DEAD = "dead"


### Helper Tables ###
network_users = db.Table('network_users',
        db.Column('user_id',    db.Integer(), db.ForeignKey('user.id')),
        db.Column('network_id', db.Integer(), db.ForeignKey('network.id')))

network_groups = db.Table('network_groups',
        db.Column('group_id',    db.Integer(), db.ForeignKey('group.id')),
        db.Column('network_id', db.Integer(), db.ForeignKey('network.id')))

docker_client = docker.from_env()        
### Container Management ###
class Container(BaseModel):
  name = db.Column(db.String(255), unique=True, nullable=False)
  files_location = db.Column(db.String(1024), unique=True, nullable=False)
  docker_id = db.Column(db.String(255), unique=True)
  network_id = db.Column(db.Integer, db.ForeignKey('network.id'))
  ip = db.Column(db.String(16))
  flags = db.relationship("Flag",backref="container")


  def update_hosts_file(self):
    file_lines = self.network.get_hosts_file_lines()

    for line in file_lines:
      cmd = f'echo {line} >> /etc/hosts'
      self.exec_command(cmd)

  def exec_command(self,cmd):
      obj = self.get_container_object()
      bash_cmd = f'/bin/sh -c "{cmd}"'
      return obj.exec_run(
        cmd=bash_cmd,
        privileged=True
        )

  def get_status(self):
    try:
      return   str(self.get_container_object().status)
    except:
      return "not existing"
    

  def read_properties(self,key=None):
    path = os.path.join(self.files_location,"properties.json")
    try:
      with open(path) as json_file:
        str_data = json_file.read()
        if self.ip != None:
          str_data = str_data.replace("[! container_ip !]",self.ip)
        data = json.loads(str_data)

        if key != None:
          try:
            return data[key]
          except:
            return None

        return data
    except:
      current_app.logger.warning("Couldn't read properties of at " + path )
      return "error"

  def stop(self):
    try:

      container = self.get_container_object()
      container.stop()
      docker_client.images.remove(self.name, force=True)
      
    except Exception as err:
      current_app.logger.error(str(err))
    try:
      shutil.rmtree(self.files_location)
    except:
      current_app.logger.warning(f"Couldn't delete {self.files_location}")
      pass



    for flag in self.flags:
      flag.delete()
    
    docker_client.images.prune()
    container_name = self.name
    db.session.delete(self)
    db.session.commit()
    current_app.logger.info("Stopped container: " + container_name)

  def get_json(self):
    json = {
      "name":self.name,
      "docker_id": self.docker_id,
      "network_id": self.network_id,
      "ip": self.ip,
      "files_location": self.files_location,
      "properties": self.read_properties(),
      "status": self.get_status()
    }
    return json

  def delete(self):
    self.stop()

  def get_container_object(self):
    """Returns the container object of the docker sdk"""
    try:
      container_object = docker_client.containers.get(self.name)
      container_object.reload() # Also tell docker-daemon to fetch current information about the container. 
      return container_object
    except docker.errors.NotFound:
      current_app.logger.warning("Requested docker container of " + str(self.name) + "was not found.")
      return None

  def place_flags(self):
    flag_regex = r'(\[\#\ )+([a-z,A-Z,0-9,_])+(\ \#\])'
    rootdir = self.files_location

    ignore_paths = []

    # iterate over all dirs
    for subdir, dirs, files in os.walk(rootdir):
      # iterate over every file in the current dir
      for file in files:
        # get the full path to the current file
        filepath = os.path.join(subdir, file)
        

        # open it in read mode, to search for flag tags
        try:
          with open(filepath,"r") as fr:
            # get the file contents 
            # and replace the flag tags 
            # by regex
            f_content = fr.read()
            new_content = re.sub(
              pattern=flag_regex,
              repl= lambda match: self.network.get_flag(match,self),
              string=f_content
              )

            # Only overwrite the file if it has changed
            if new_content != f_content:
              with open(filepath,"w") as fw:
                fw.write(new_content)
        except:
          current_app.logger.warning("Couldnt open file " + filepath)

  def place_context(self):
    flag_regex = r'(\[\!\ )+([a-z,A-Z,0-9,_])+(\ \!\])'
    rootdir = self.files_location

    for subdir, dirs, files in os.walk(rootdir):
      for file in files:
        filepath = os.path.join(subdir, file)
        with open(filepath,"r") as fr:
          f_content = fr.read()
          new_content = re.sub(
            pattern=flag_regex,
            repl= lambda match: self.get_context(match),
            string=f_content
            )

          if new_content != f_content:
            with open(filepath,"w") as fw:
              fw.write(new_content)
  
  def get_context(self,match):
    pass


  ### STATIC METHODS ###
  @staticmethod 
  def create_container_dir(folder_name,container_name):
    import os
    data_path = os.path.join(current_app.config["CONTAINER_DIR"],folder_name)
    
    root_location = tempfile.mkdtemp(prefix=container_name)
    copy_tree(data_path, root_location)
    
    return root_location

  @staticmethod
  def create_detatched_container(
    folder_name,            
    network,                
    privileged=True,        # Need privileges for network sniffing       
    existing_location=None, 
    command=None, 
    cap_add=[], 
    ports=None,
    volumes=None,
    caching=True
    ):

    # generate unique name with network and image name as prefix
    container_name = f"{network.name}_{secure_filename(folder_name)}_{str(uuid.uuid4()).split('-')[0]}"

    # check if the name contains invalid characters
    if not utils.is_valid_docker_name(container_name):
      raise errors.InvalidContainerNameException(container_name)

    # Check if an existing location was given
    data_path = None
    if existing_location is None:
      data_path = Container.create_container_dir(folder_name,container_name)
    else:
      data_path = existing_location

    # Create database entry to call the place_flags method on
    container_db = Container(
      name=container_name,
      files_location=data_path,
      network = network
    )

    # Place flags in the files_location
    container_db.place_flags()

    # Build the image
    current_app.logger.info(f"Building image for {container_name} ({folder_name})")
    image, logs = docker_client.images.build(
      path=data_path,
      nocache=not caching,  # Dont use caching, so the modified files get used
      forcerm=True,     # Remove the image after the container has stopped
      tag=container_name.lower() # Tag it with the container name, for debugging purposes
    )

    if volumes == None:
      volumes = {data_path:{"bind":"/container_data","mode":"rw"}}    

    # Actually start the docker container
    container = docker_client.containers.run(
      image=image,            # Use the previously built image
      remove=False,            # Remove the container after it was stopped
      detach=True,            # Detatch the container after it was started
      name=container_name,   
      network=network.name,   # Assign the container to the network
      privileged=privileged,  
      ports=ports,            # Map ports if they were provided
      command=command,        # Run an alternative command if it was provided
      volumes=volumes,        # Mount volumes if they were provided
      hostname= container_db.read_properties("hostname"), # Get the desired hostname from the properties.json
      dns=["8.8.8.8"]         # Use google dns for now
    )

    container.reload() # Let the docker daemon refetch container information

    # Fetch container information from docker and update the database entry
    container_db.docker_id = container.id
    container_db.ip = container.attrs["NetworkSettings"]["Networks"][network.name]["IPAddress"]
    current_app.logger.info("Started container: " + container_name)

    # Return the database entry, still has to be committed
    return container_db
  
  @staticmethod
  def create_vpn_container(network):
    import os

    from flask_app.core.models.user import Role
    """Creates the vpn container for the specified network"""
    vpn_image = "vpn"
    network_name = network.name
    network_id = network.id
    data_path = Container.create_container_dir(vpn_image, network_name + "_vpn_container_")
    vpn_files = os.path.join(data_path,"data")

    users = network.assigned_users.copy() # Grant assigned users access

    # Grant users of assigned groups access
    for group in network.assigned_groups:
      users.extend(group.users)
    
    users.extend(Role.get_admin_users()) # Also grant admins access

    usrs = utils.remove_duplicates_from_list(users)
    

    gateway_ip = network.gateway
    gateway_mac = network.get_gateway_mac()
    current_app.logger.info(f"arp -s {gateway_ip} {gateway_mac}")
    # Actually start the container
    port = network.vpn_port
    vpn_container = Container.create_detatched_container(
      vpn_image,
      network,
      command=f"./entrypoint.sh {gateway_ip} {gateway_mac}",
      existing_location=data_path,
      ports={"1194/tcp": port},    # Map the port of container          
      privileged=True,
      cap_add="NET_ADMIN",
      caching=True
      )

    # Create users for authentification
    for user in usrs:
      username, password = user.get_vpn_credentials()
      command = f"useradd -g 'openvpn' -Ms /bin/bash {username} && echo '{username}:{password}' | chpasswd"
      vpn_container.exec_command(command)
      

    return vpn_container

  @staticmethod 
  def gen_vpn_crt_and_cfg(user):
    
    # use the vpn keygen image
    folder_name="vpn_keygen"
    # command to call the creation script in the container.
    crt_command= f"./create_client_files.sh {user.username}"
    # create a location where the container can write the file
    location = Container.create_container_dir(
      folder_name,
      f"{current_app.config['APP_PREFIX']}_auth_gen_"
    )

    # generate random name
    container_name = f"{current_app.config['APP_PREFIX']}_{secure_filename(folder_name)}-{user.username}_{str(uuid.uuid4()).split('-')[0]}"
    vpn_data_path = os.path.join(location,"data")

    # build the image
    image, logs = docker_client.images.build(
      path=location,
      nocache=True,
      tag=container_name
    )

    # let the container run attatched
    output = docker_client.containers.run(
      image=image,
      remove=True,
      detach=False,
      name=container_name,
      ports=None,
      command=crt_command,
      stdout=True,
      stderr=True,
      volumes={vpn_data_path:{"bind":"/etc/openvpn","mode":"rw"}} # mount the       
    )

    # Set the paths for the files
    user_crt_path = os.path.join(vpn_data_path,"userdata/",f"{user.username}.crt")
    user_crt = None
    user_key_path = os.path.join(vpn_data_path,"userdata/",f"{user.username}.key")
    user_key = None
    user_cfg_path = os.path.join(vpn_data_path,"userdata/",f"{user.username}.ovpn")
    user_cfg = None

    # Read the files to variables
    with open(user_crt_path,"r") as f:
      user_crt = f.read()
    with open(user_key_path,"r") as f:
      user_key = f.read()
    with open(user_cfg_path,"r") as f:
      user_cfg = f.read()
      # Do some corrections, for some reason server outputs faulty cfg
      user_cfg = user_cfg.replace("dev ","dev tun").replace("remote ","") 

    # Cleanup everything that was created
    # shutil.rmtree(location)
    docker_client.images.remove(container_name, force=True)
    
    # Return the read data
    return user_crt, user_key, user_cfg

  @staticmethod
  def cleanup():
    for container in docker_client.containers.list():
      if current_app.config["APP_PREFIX"] in container.name:
        container.kill()
    docker_client.images.prune()

class ContainerImage(BaseModel):
  """Model for holding a container image name"""
  name = db.Column(db.String(255)) 
  network_preset_id = db.Column(
    db.Integer, 
    db.ForeignKey('network_preset.id'),
    nullable=False
  )

  def get_json(self):
    json = {
      "name": self.name,
      "properties": self.get_properties()
    }
    return json

  def get_properties(self):
    properties_path = os.path.join(
      current_app.config["CONTAINER_DIR"],
      self.name,
      "properties.json"
    )
    try:
      with open(properties_path) as json_file:
        data = json.load(json_file)
    except FileNotFoundError:
        data = {"error":"container properties not found"}
    return data

  def does_exist(self):
    existing = {}
    existing = ContainerImage.get_available_container_images()
    if self.name not in existing.keys():
      return False
    return True

  @staticmethod
  def get_available_container_images():
    ret = {}
    hidden_images = ["vpn","vpn_keygen"]
    generator = os.walk(current_app.config["CONTAINER_DIR"]) # get all folders in containers folder
    root, dirs, files = list(generator)[0]
    
    # check if folders include dockerfile
    for d in dirs:
      path = os.path.join(root,d)
      _generator = os.walk(path)
      _root, _dirs, _files = list(_generator)[0]
      if "dockerfile" in _files and d not in hidden_images:
          path = os.path.join(_root,"properties.json")
          try:
            with open(path) as json_file:
              data = json.load(json_file)
              ret[d] = data
          except Exception as err :
            current_app.logger.error("Couln't load json of " + d + "; Error: " + str(err))

    return ret
  
### Network Management ###
class NetworkPreset(BaseModel):
  """Model for holding a network preset"""
  name = db.Column(db.String(255), unique=True)
  networks = db.relationship("Network",backref="preset")
  container_images = db.relationship(
    "ContainerImage",
    cascade="delete, delete-orphan"
    )

  def get_json(self):
    json = {
      "name":self.name,
      "container_images":[]
    }
    for container_image in self.container_images:
      json["container_images"].append(container_image.get_json())
    return json

  def delete(self):
    name = self.name
    db.session.delete(self)
    db.session.commit()
    current_app.logger.info("Deleted preset: " + name)

  def create_network(self,name,assign_users=[],assign_groups=[]):
    """Creates a network from the preset"""
    if not utils.is_valid_docker_name(name):
      raise errors.InvalidNetworkNameException(name)

    if not Network.name_available(name):
      raise errors.NetworkNameTakenException(name)

    container_image_names = []
    for image in self.container_images:
      if not image.does_exist():
        raise errors.ImageNotFoundException(image.name)
      container_image_names.append(image.name)



    assign_users = utils.remove_duplicates_from_list(assign_users)
    assign_groups = utils.remove_duplicates_from_list(assign_groups)

    # remove assigned users that are already in a group that is assigned,
    for group in assign_groups:
      for user in assign_users:
        if user in group.users:
          assign_users.remove(user)

    network = Network.create_network(
      network_name= name,
      container_image_names=container_image_names,
      assign_users=assign_users,
      assign_groups=assign_groups,
      preset=self
    )


    return network
  
  @staticmethod
  def get_network_preset_by_name(name):
    preset = NetworkPreset.query.filter_by(name=name).first()
    return preset

  @staticmethod
  def get_network_preset_by_id(id):
    preset = NetworkPreset.query.get(id)
    return preset

  
  @staticmethod
  def create_network_preset(name,container_image_names):
    container_images = []
    available_images = ContainerImage.get_available_container_images()
    for image_name in container_image_names:
      if image_name not in available_images:
        raise errors.ImageNotFoundException(image_name)
      
      image = ContainerImage(name=image_name)
      db.session.add(image)
      container_images.append(image)
    
    preset = NetworkPreset(
      name=name,
      container_images=container_images
    )
    db.session.add(preset)
    db.session.commit()
    return preset


NETWORK_STATUS_RUNNING = "running"
NETWORK_STATUS_STARTING = "starting"
NETWORK_STATUS_RESTARTING = "restarting"
NETWORK_STATUS_DELETING = "deleting"
NETWORK_STATUS_ERROR = "error"

class Network(BaseModel):
  """Model for a running network"""

  vpn_port = db.Column(db.Integer(), unique=True)
  gateway = db.Column(db.String(16))
  subnet = db.Column(db.String(16))
  name = db.Column(db.String(255), unique=True)
  containers = db.relationship("Container",backref="network")
  last_hint_time = db.Column(db.DateTime)
  network_preset_id = db.Column(db.Integer, db.ForeignKey('network_preset.id'))
  flags = db.relationship("Flag",backref="network")
  status = db.Column(db.String(16))


  assigned_users = db.relationship(
                          'User', 
                          secondary=network_users,
                          backref=db.backref('assigned_networks', lazy='dynamic')
                          )
  assigned_groups = db.relationship(
                        'Group', 
                        secondary=network_groups,
                        backref=db.backref('assigned_networks', lazy='dynamic')
                        )
  
  def get_network_object(self):
    return docker_client.networks.get(self.name)

  def get_completion_percent(self):
    total_flags = len(self.get_flags())
    if total_flags == 0:
      return 100
    completed = len(self.get_redeemed_flags())
    percentage = (completed / total_flags) * 100
    return percentage
  
  def get_next_hint_time(self):
    if self.last_hint_time == None:
      return datetime.datetime.now()

    hint_timeout = current_app.config["HINT_TIMEOUT"]
    return self.last_hint_time + datetime.timedelta(minutes = hint_timeout)
    
  def get_hint(self,flag_id):
    flag = Flag.get_flag_by_id(flag_id)
    hints = flag.get_hints()
    hint_timeout = current_app.config["HINT_TIMEOUT"]
    data = {"status":"","hint":""}
    now = datetime.datetime.now()



    if self.last_hint_time == None:
      data["hint"] = flag.get_hint()
      data["status"] = "success"
      self.last_hint_time = now
    else:
      time_diff = (now - self.last_hint_time).total_seconds() / 60
      if time_diff >= hint_timeout:
        data["hint"] = flag.get_hint()
        data["status"] = "success"
        return data
      else:
        data["hint"] = str(self.get_next_hint_time())
        data["status"] = "timeout" 
        self.last_hint_time = now


    
    db.session.add(self)
    db.session.commit()
    return data
    
  def is_network_ready(self):
    """Checks if all containers are running"""
    return self.status == NETWORK_STATUS_RUNNING

  def get_json(self):
    json = {
      "id": self.id,
      "clean_name": self.get_clean_name(),
      "name": self.name,
      "ready": self.is_network_ready(),
      "gateway": self.gateway,
      "vpn_port": self.vpn_port,
      "assigned_users": [],
      "containers": [],
      "flags":[],
      "total_flags":len(self.get_flags()),
      "redeemed_flags":len(self.get_redeemed_flags()),
      "next_hint":self.get_next_hint_time(),
      "hosts_file": self.get_hosts_file_lines(),
      "status": self.status,
      "preset": self.preset.name,
      "command": self.get_connection_command(current_user),
      "completion": self.get_completion_percent()
    }

    if self.status == NETWORK_STATUS_RUNNING:
      for flag in self.flags:
        json["flags"].append(flag.get_json())
      for container in self.containers:
        json["containers"].append(container.get_json())


    for user in self.assigned_users:
      json["assigned_users"].append(user.get_json())



    return json

  def get_hosts_file_lines(self):
    lines = []
    for container in self.containers:
      hostname = container.read_properties("hostname")
      ip = container.ip
      if hostname != None:
        lines.append(f"{ip} {hostname}")
    return lines

  def restart(self):
    container_image_names = []

    self.vpn_port = Network.get_available_port()
    self.status = CONTAINER_STATE_RESTARTING
    db.session.add(self)
    db.session.commit()

    #get image names
    for image in self.preset.container_images:
      container_image_names.append(image.name)

    for container in self.containers:
      container.stop()

    self.vpn_port = Network.get_available_port()
    self.status = CONTAINER_STATE_RESTARTING


    #network_db.start_containers(container_image_names)
    worker_thread = threading.Thread(
      target=Network.start_containers,
      args=(
        self.name,
        container_image_names,
        current_app._get_current_object(),
        )
      )
    worker_thread.start()
    return self

  def get_gateway_mac(self):
    import netifaces
    
    interfaces = netifaces.interfaces()
    network_id = str(self.get_network_object().id)[:12]
    interface_name = None
    for i in interfaces:
      if network_id in i:
        interface_name = i
    if interface_name == None:
      raise ValueError(f"Interface f{network_id} not found!")
      
      
    mac = netifaces.ifaddresses(interface_name)[netifaces.AF_LINK][0]['addr']
    return mac

  def network_is_ready(self):
    return self.status == NETWORK_STATUS_RUNNING

  def user_allowed_to_access(self,user):
    return user in self.assigned_users or user.group in self.assigned_groups or user.has_role("admin")

  def get_flag(self,regex_match,container):
    """Gets a flag if it exists, or creates it and returns it if not"""

    flag_name = regex_match.group(0).replace("[# ","").replace(" #]","")
    
    for flag in self.flags:
      if flag.name == flag_name:
        return str(flag)

    flag = Flag.create_flag(
      network=self,
      container=container,
      flag_name=flag_name
    )

    return str(flag)

  def stop_all_containers(self):
    for container in self.containers:
      container.stop()

  def get_flags(self):
    return self.flags

  def get_redeemed_flags(self):
    ret = []
    for flag in self.flags:
      if flag.redeemed:
        ret.append(flag)
    return ret

  def get_unredeemed_flags(self):
    ret = []
    for flag in self.flags:
      if not flag.redeemed:
        ret.append(flag)
    return ret

  def delete(self):
    self.status = NETWORK_STATUS_DELETING
    db.session.commit()
    
    for container in self.containers:
      container.stop()
    try:
      self.get_network_object().remove()
    except:
      pass
    
    for flag in self.flags:
      flag.delete()

    network_name = self.name

    db.session.delete(self)
    db.session.commit()
    current_app.logger.info("Deleted network: " + network_name)

  def get_connection_command(self,user):
    ip = current_app.config["PUBLIC_IP"]
    port = self.vpn_port

    if self.status == NETWORK_STATUS_STARTING:
      return "Network is still starting..."
    elif self.status == NETWORK_STATUS_RESTARTING:
      return "Network is still restarting..."
    elif self.status == NETWORK_STATUS_ERROR:
      return "There was an error starting the network..."

    command = f"sudo openvpn --config ~/{user.username}.ovpn --auth-user-pass ~/{user.username}.creds --remote {ip} {port} tcp"
    return command

  def get_clean_name(self):
    return self.name.replace(current_app.config["APP_PREFIX"] + "_","")

  ### STATIC METHODS ###
  @staticmethod 
  def get_network_by_name(name):
    network = Network.query.filter_by(name=name).first()
    return network

  @staticmethod
  def get_network_by_id(id):
    network = Network.query.get(id)
    return network    

  @staticmethod
  def get_all_networks():
    return Network.query.all()

  @staticmethod 
  def name_available(name):
    matching_network = Network.get_network_by_name(name)
    return matching_network is None

  @staticmethod
  def start_containers(network_name,container_image_names,app):
    with app.app_context():

      # Create scoped session for the thread to prevent threading
      # related errors.
      session = db.create_scoped_session()
      try:
        # Query the network from the scoped session
        network = session.query(Network).filter(Network.name == network_name).first()

        # Start the VPN Container
        vpn_container = Container.create_vpn_container(network)


        # Start all containers
        for container_folder in container_image_names:
          Container.create_detatched_container(container_folder,network)
        # Update their hosts file, so they can easily 
        # reach eachother in scripts
        #for container in network.containers:
        #  container.update_hosts_file()
        
        # Set the network status to running
        # At this point all containers should be running
        network.status = NETWORK_STATUS_RUNNING
        
        session.commit()
        

      except Exception as err:

        # stop all containers that were created
        network_object = network.get_network_object()
        network_object.reload()

        # stop all containers that are left, because they had
        # no database entry
        for container in network_object.containers:
          container.stop()
        # update the networks status
        network.status = NETWORK_STATUS_ERROR
        session.commit()
        current_app.logger.error(err)
        raise err
      session.remove()

  @staticmethod
  def create_network(
    network_name,container_image_names,
    assign_users = [], 
    assign_groups = [],
    preset=None
    ):
    # append app prefix (vitsl) to the network
    network_name = current_app.config["APP_PREFIX"] +"_"+ network_name 

    # check if the network name contains invalid characters
    if not utils.is_valid_docker_name(network_name):
      raise errors.InvalidNetworkNameException(network_name)
 
    network = None
    network_db = None
    current_app.logger.info("Starting network: " + network_name)

    # catch errors to clean up leftover containers
    # if something went wrong
    try:

      # Create the docker network
      network = docker_client.networks.create(
          name=network_name, # Give it the networks name
          check_duplicate=True, # Check if a network with the name already exists
        )

      network.reload() # Let the docker daemon refetch network data
      gateway = network.attrs["IPAM"]["Config"][0]["Gateway"]
      subnet = network.attrs["IPAM"]["Config"][0]["Subnet"]

      # get all the assigned users and groups, remove duplicates
      assign_users = utils.remove_duplicates_from_list(assign_users)
      assign_groups = utils.remove_duplicates_from_list(assign_groups)

      # create the networks database entry
      # and set the status to "starting"
      network_db = Network(
        name=network_name,
        gateway=gateway,
        assigned_users=assign_users,
        assigned_groups=assign_groups,
        preset=preset,
        subnet=subnet,
        status=NETWORK_STATUS_STARTING,
        vpn_port=Network.get_available_port()
      )
      
      # Commit the network to the database
      # so the worker threads can access it through 
      # the database
      db.session.add(network_db)
      db.session.commit()

      # start the threaded container started
      # for a faster API response
      worker_thread = threading.Thread(
        target=Network.start_containers,
        args=(
          network_name,
          container_image_names,
          current_app._get_current_object(),
          )
        )
      worker_thread.start()

      current_app.logger.info("Created network: " + network_name)
      return network_db
    except Exception as err:
      # If we fail somewhere during the creation process
      # delete and remove everything that might already
      # got created.
      if network_db is not None:
        # Reflect that something went wrong on the
        # networks status
        network.status = NETWORK_STATUS_ERROR
        db.session.add(network)
        db.session.commit()

      current_app.logger.error(str(err))
      # re-raise the error so it can be propagated
      # to the frontend
      raise err

  @staticmethod
  def cleanup():
    for network in Network.get_all_networks():
      network.delete()

    for network in docker_client.networks.list():
      if current_app.config["APP_PREFIX"] in network.name:
        for container in network.containers:
          container.kill()
        network.remove()


    docker_client.networks.prune()

  @staticmethod
  def get_available_port():
    # Get all networks to get
    # their used ports
    networks = Network.get_all_networks()
    used_ports = []
    available_ports = []
    # Append all used ports to
    # the used_ports array
    for network in networks:
      used_ports.append(network.vpn_port)

    # Get the portrange from the config
    port_range = current_app.config["VPN_PORT_RANGE"]
    port_min = port_range[0]
    port_max = port_range[1]
    rnge = range(port_min,port_max)
    
    # Check if there are ports left
    if len(used_ports) == len(rnge):
      raise errors.NoPortsAvailableException()

    # Get all the available ports
    for port in rnge:
      if port not in used_ports:
        available_ports.append(port)

    # Chose a random port from the available ports
    rnd_port = random.choice(available_ports)
    
    return rnd_port



class Flag(BaseModel):


  name = db.Column(db.String(32))
  code = db.Column(db.String(64), unique=True)
  network_id = db.Column(db.Integer, db.ForeignKey('network.id'))
  container_id = db.Column(db.Integer, db.ForeignKey('container.id'))
  last_hint = db.Column(db.Integer())
  redeemed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  redeemed = db.Column(db.Boolean)

  def __str__(self):
    return "FLAG{" + self.code + "}"

  def get_json(self):
    json = {
      "id":self.id,
      "name":self.name,
      "redeemed": self.redeemed,
      "last_hint": self.last_hint,
      "description": self.get_description(),
      "next_hint": self.network.get_next_hint_time(),
      "revealed_hints": self.get_revealed_hints()
    }
  
    hints_left = len(self.get_hints()) - len(self.get_revealed_hints())

    json["hints_left"] = hints_left
    if self.redeemed_by != None:
      json["redeemed_by"] = self.redeemed_by.get_json()
    else:
      json["redeemed_by"] = None

    return json

  def redeem(self,user):
    self.last_hint = len(self.get_hints()) - 1
    self.redeemed = True
    self.redeemed_by = user
    db.session.add(self)
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def get_description(self):
    if self.container == None:
      return None

    return self.container.read_properties()["flags"][self.name]["description"]

  def get_hint(self):
    hints = self.get_hints()
    last_hint_index = self.last_hint
    if last_hint_index == None:
      last_hint_index = -1
      
    last_hint_index = last_hint_index + 1

    if last_hint_index >= len(hints):
      return None

    hint = hints[last_hint_index]

    self.last_hint = last_hint_index
    db.session.add(self)
    db.session.commit()
    return hint

  def get_revealed_hints(self):
    ret = []
    hints = self.get_hints()
    
    if self.last_hint == None:
      return []

    for i in range(self.last_hint + 1):
      ret.append(hints[i])
    return ret

  def get_hints(self):
    if self.container == None:
      return []
    return self.container.read_properties()["flags"][self.name]["hints"]

  @staticmethod
  def create_flag(network, flag_name, container):
    code = str(uuid.uuid4()).replace("-","")

    container: Container = container

    flag = Flag(
      network=network,
      container=container,
      name=flag_name,
      code=code,
      redeemed=False
    )
    #db.session.add(flag)
    #db.session.commit()
    return flag

  @staticmethod
  def get_flag_by_code(code):
    code = code.replace("FLAG{","").replace("}","").strip()
    return Flag.query.filter_by(code=code).first()

  @staticmethod
  def get_flag_by_id(id):
    return Flag.query.get(id)
