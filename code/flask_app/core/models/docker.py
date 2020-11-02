import os
import shutil
import tempfile
import uuid

import docker
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

from ..db import db

network_users = db.Table('network_users',
        db.Column('user_id',    db.Integer(), db.ForeignKey('user.id')),
        db.Column('network_id', db.Integer(), db.ForeignKey('network.id')))

docker_client = docker.from_env()        

class Container(db.Model):
  id = db.Column(db.Integer(), primary_key=True, nullable=False)
  name = db.Column(db.String(255), unique=True, nullable=False)
  files_location = db.Column(db.String(1024), unique=True, nullable=False)
  docker_id = db.Column(db.String(255), unique=True, nullable=False)
  network_id = db.Column(db.Integer, db.ForeignKey('network.id'), nullable=False)



  def stop(self):
    container = self.get_container_object()
    container.stop()
    self.delete()
    db.session.flush()

  def get_json(self):
    json = {
      "name":self.name,
      "docker_id": self.docker_id,
      "network_id": self.network_id,
      "files_location": self.files_location
    }
    return json

  def get_container_object(self):
    """Returns the container object of the docker sdk"""
    container_object = docker_client.containers.get(self.name)
    container_object.reload() # Also tell docker-daemon to fetch current information about the container. 
    return container_object

  @staticmethod
  def create_container(
    folder_name,
    network,
    container_name=None,
    privileged=False,
    command=None, 
    cap_add=None, 
    ports=None,
    ):
    """Creates a container, adds it to the specified network and then runs it.
    """
    network_name = network.name
    data_path = os.path.join(current_app.config["CONTAINER_DIR"],folder_name)
    location = tempfile.mkdtemp() # Create a new temp dir for the files of the container

    new_datapath = os.path.join(location,folder_name) # Create a path for the new files to copy them to


    shutil.copytree(data_path, new_datapath) # Copy the files into the new tmp dir
    

    image, logs = docker_client.images.build(
      path=new_datapath,
      nocache=True,
    )

    # generate random name with network name as prefix
    default_container_name = network_name + "_" + secure_filename(folder_name) + \
                            "_" + str(uuid.uuid4()).split('-')[0] 

    container = docker_client.containers.run(
      image=image,
      remove=True,
      detach=True,
      name= container_name or default_container_name,
      network=network_name,
      privileged=privileged,
      ports=ports           
    )

    container.reload() # Let the docker daemon refetch container information
    container_db = Container(
      name=container.name,
      files_location=location,
      network_id = network.id,
      docker_id=container.id
    )
    db.session.add(container_db)
    db.session.flush()
    return container_db
  
  @staticmethod
  def create_vpn_container(network):
    network_name = network.name
    
    vpn_container = Container.create_container(
      "vpn",
      network,
      ports={"1194/udp":None},              
      cap_add="NET_ADMIN",
      privileged=True
      )

    return vpn_container

class Network(db.Model):
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
      "containers": []
    }

    for container in self.containers:
      json["containers"].append(container.get_json())

    return json

  def delete(self):
    for container in self.containers:
      container.stop()
    docker_client.networks.get(self.name).remove()
    db.session.commit()

  def get_vpn_port(self):
    vpn_container_object = self.get_container_object()
    return vpn_container_object.ports['1194/udp'][0]['HostPort']

  def get_connection_command(self,user):
    ip = current_app.config["PUBLIC_IP"]
    port = self.get_vpn_port()
    command = f"sudo openvpn --config ~/{user.username}.ovpn --remote {ip} {port} udp"

  ### STATIC METHODS ###

  @staticmethod 
  def get_network_by_name(name):
    network = Network.query.filter_by(name=name).first()
    return network

  @staticmethod
  def get_all_networks():
    return Network.query.all()

  @staticmethod
  def create_network(network_name,container_folder_names,assign_users = []):
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

    for container_folder in container_folder_names:
      Container.create_container(container_folder,network_db)
    
    
    db.session.commit()

    return network
