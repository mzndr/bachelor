import json
import os
import shutil
import tempfile
import uuid
from distutils.dir_util import copy_tree

import docker
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

from ..db import db

### Helper Tables ###
network_users = db.Table('network_users',
        db.Column('user_id',    db.Integer(), db.ForeignKey('user.id')),
        db.Column('network_id', db.Integer(), db.ForeignKey('network.id')))

docker_client = docker.from_env()        
### Container Management ###
class Container(db.Model):
  id = db.Column(db.Integer(), primary_key=True, nullable=False)
  name = db.Column(db.String(255), unique=True, nullable=False)
  files_location = db.Column(db.String(1024), unique=True, nullable=False)
  docker_id = db.Column(db.String(255), unique=True, nullable=False)
  network_id = db.Column(db.Integer, db.ForeignKey('network.id'))
  
  def read_properties(self):
    path = os.path.join(self.files_location,"properties.json")
    with open(path) as json_file:
      data = json.load(json_file)
      return data

  def stop(self):
    try:
      container = self.get_container_object()
      container.stop()
    except:
      pass
    try:
      shutil.rmtree(self.files_location)
    except:
      pass

    db.session.delete(self)
    db.session.flush()

  def get_json(self):
    json = {
      "name":self.name,
      "docker_id": self.docker_id,
      "network_id": self.network_id,
      "files_location": self.files_location,
      "properties": self.read_properties()
    }
    return json

  def get_container_object(self):
    """Returns the container object of the docker sdk"""
    container_object = docker_client.containers.get(self.name)
    container_object.reload() # Also tell docker-daemon to fetch current information about the container. 
    return container_object

  ### STATIC METHODS ###
  @staticmethod 
  def create_container_dir(folder_name):
    data_path = os.path.join(current_app.config["CONTAINER_DIR"],folder_name)
    root_location = tempfile.mkdtemp(prefix=current_app.config["APP_PREFIX"] + "_" + folder_name + "_")
    copy_tree(data_path, root_location)
    return root_location

  @staticmethod
  def create_detatched_container(
    folder_name,
    network,
    privileged=False,
    existing_location=None,
    command=None, 
    cap_add=None, 
    ports=None,
    volumes=None,
    ):
    """Creates a container, adds it to the specified network and then runs it.
    """
    network_name = network.name
    network_id = network.id

    data_path = None
    if existing_location is None:
      data_path = Container.create_container_dir(folder_name)
    else:
      data_path = existing_location

    image, logs = docker_client.images.build(
      path=data_path,
      nocache=True,
    )

    # generate random name with network name as prefix
    container_name = f"{current_app.config['APP_PREFIX']}_{network_name}_{secure_filename(folder_name)}_{str(uuid.uuid4()).split('-')[0]}"
  


    container = docker_client.containers.run(
      image=image,
      remove=True,
      detach=True,
      name=container_name,
      network=network.name,
      privileged=privileged,
      ports=ports,
      command=command,
      volumes=volumes      
    )

    container.reload() # Let the docker daemon refetch container information
    container_db = Container(
      name=container.name,
      files_location=data_path,
      network_id = network_id,
      docker_id=container.id,
    )
    db.session.add(container_db)
    db.session.flush()
    return container_db
  
  @staticmethod
  def create_vpn_container(network):
    """Creates the vpn container for the specified network"""
    vpn_image = "vpn"
    network_name = network.name
    network_id = network.id
    data_path = Container.create_container_dir(vpn_image)
    vpn_files = os.path.join(data_path,"data")
    # Copy user authentication files into vpn
    for user in network.assigned_users:
      crt_location = os.path.join(vpn_files, f"pki/issued/{user.username}.crt")
      key_location = os.path.join(vpn_files, f"pki/private/{user.username}.key")
      with open(crt_location,"w") as crt_file:
        crt_file.write(user.vpn_crt)
      with open(key_location,"w") as key_file:
        key_file.write(user.vpn_key)

    
    vpn_container = Container.create_detatched_container(
      vpn_image,
      network,
      existing_location=data_path,
      ports={"1194/udp":None},              
      cap_add="NET_ADMIN",
      privileged=True,
      )




    return vpn_container

  @staticmethod 
  def gen_vpn_crt_and_cfg(user):
    
    folder_name="vpn_keygen"
    crt_command= f"./create_client_files.sh {user.username}"
    data_path = os.path.join(current_app.config["CONTAINER_DIR"],folder_name)
    location = Container.create_container_dir(folder_name)

    vpn_data_path = os.path.join(location,"data")
    image, logs = docker_client.images.build(
      path=location,
      nocache=True,
    )

    # generate random name
    container_name = f"{current_app.config['APP_PREFIX']}_{secure_filename(folder_name)}-{user.username}_{str(uuid.uuid4()).split('-')[0]}"
    output = docker_client.containers.run(
      image=image,
      remove=True,
      detach=False,
      name=container_name,
      privileged=True,
      ports=None,
      cap_add="NET_ADMIN",
      command=crt_command,
      stdout=True,
      stderr=True,
      volumes={vpn_data_path:{"bind":"/etc/openvpn","mode":"rw"}}           
    )

    user_crt_path = os.path.join(vpn_data_path,"userdata/",f"{user.username}.crt")
    user_crt = None
    user_key_path = os.path.join(vpn_data_path,"userdata/",f"{user.username}.key")
    user_key = None
    user_cfg_path = os.path.join(vpn_data_path,"userdata/",f"{user.username}.ovpn")
    user_cfg = None

    with open(user_crt_path,"r") as f:
      user_crt = f.read()
    with open(user_key_path,"r") as f:
      user_key = f.read()
    with open(user_cfg_path,"r") as f:
      user_cfg = f.read()
      # Do some corrections, for some reason server outputs faulty cfg
      user_cfg = user_cfg.replace("dev","dev tun").replace("remote ","") 

    shutil.rmtree(location)

    return user_crt, user_key, user_cfg

  @staticmethod
  def cleanup():
    containers = Container.query.all()
    for container in containers:
      container.delete()
    docker_client.containers.prune()

class ContainerImage(db.Model):
  """Model for holding a container image name"""
  id = db.Column(db.Integer(), primary_key=True)  
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

    with open(properties_path) as json_file:
          data = json.load(json_file)
    return data

  def does_exist(self):
    existing = {}
    existing = Container_Image.get_available_container_images()
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
          with open(path) as json_file:
            data = json.load(json_file)
            ret[d] = data

    return ret
  

### Network Management ###
class NetworkPreset(db.Model):
  """Model for holding a network preset"""
  id = db.Column(db.Integer(), primary_key=True)  
  name = db.Column(db.String(255), unique=True)
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
    db.session.delete(self)
    db.session.commit()

  def create_network(self,assign_users,name=None):
    """Creates a network from the preset"""
    container_image_names = []
    for image in self.container_images:
      if not image.does_exist():
        raise ValueError(f"Container image '{image_name}' does not exist on disk. If its there, check if there is a dockerfile in its root directory.")
      container_image_names.append(image.name)

    network = Network.create_network(
      network_name= name or self.name,
      container_image_names=container_image_names,
      assign_users=assign_users
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
        raise ValueError(f"Container image '{image_name}' does not exist on disk. If its there, check if there is a dockerfile in its root directory.")
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

class Network(db.Model):
  """Model for a running network"""
  id = db.Column(db.Integer(), primary_key=True)
  vpn_port = db.Column(db.Integer(), unique=True)
  name = db.Column(db.String(255), unique=True)
  containers = db.relationship("Container")
  assigned_users = db.relationship(
                          'User', 
                          secondary=network_users,
                          backref=db.backref('assigned_networks', lazy='dynamic')
                          )
  def get_json(self):
    json = {
      "id": self.id,
      "name": self.name,
      "vpn_port": self.vpn_port,
      "assigned_users": [],
      "containers": [],
    }

    for user in self.assigned_users:
      json["assigned_users"].append(user.get_json())

    for container in self.containers:
      json["containers"].append(container.get_json())

    return json

  def delete(self):
    for container in self.containers:
      container.stop()
    try:
      docker_client.networks.get(self.name).remove()
    except:
      pass
    db.session.delete(self)
    db.session.commit()

  def get_connection_command(self,user):
    ip = current_app.config["PUBLIC_IP"]
    port = self.vpn_port
    command = f"sudo openvpn --config ~/{user.username}.ovpn --remote {ip} {port} udp"
    return command

  ### STATIC METHODS ###
  @staticmethod 
  def get_network_by_name(name):
    network = Network.query.filter_by(name=name).first()
    return network

  @staticmethod
  def get_network_by_id(id):
    return Network.query.get(id)

  @staticmethod
  def get_all_networks():
    return Network.query.all()

  @staticmethod
  def create_network(network_name,container_image_names,assign_users = []):
    network = docker_client.networks.create(
        name=network_name,
        check_duplicate=True,
        internal=False
      )
    network_db = Network(
      name=network_name,
      assigned_users=assign_users
    )
    db.session.add(network_db)
    db.session.flush()

    vpn_container = Container.create_vpn_container(network_db)

    vpn_container_object = vpn_container.get_container_object()
    network_db.vpn_port = vpn_container_object.ports['1194/udp'][0]['HostPort']

    for container_folder in container_image_names:
      Container.create_detatched_container(container_folder,network_db)
    
    
    db.session.commit()

    return network

  @staticmethod
  def cleanup():
    networks = Network.query.all()
    for network in networks:
      network.delete()
    docker_client.networks.prune()
