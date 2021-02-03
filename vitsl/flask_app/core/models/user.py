import random
import string
import uuid

import flask_app.core.exceptions.user as user_errors
import flask_app.core.utils as utils
from flask import current_app, flash, url_for
from flask_app.core.db import db
from flask_app.core.models.core import BaseModel
from flask_app.core.models.docker import Container, Network, NetworkPreset
from flask_security import RoleMixin, UserMixin
from flask_security.utils import hash_password
from flask_sqlalchemy import SQLAlchemy

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

  
class User(BaseModel, UserMixin):
  username = db.Column(db.String(255), unique=True)
  email = db.Column(db.String(255), unique=True)
  password = db.Column(db.String(255))

  redeemed_flags = db.relationship("Flag",backref=db.backref('redeemed_by'))

  vpn_crt = db.Column(db.Text(2**20))
  vpn_key = db.Column(db.Text(2**20))
  vpn_cfg = db.Column(db.Text(2**20))

  active = db.Column(db.Boolean())
  confirmed_at = db.Column(db.DateTime())
  roles = db.relationship('Role', secondary=roles_users,
                          backref=db.backref('users', lazy='dynamic'))

  group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

  def get_total_completion_percentage(self):
    networks = self.get_assigned_networks()
    completed = 0
    total = 0
    for network in networks:
      completed = completed + len(network.get_redeemed_flags())
      total = total + len(network.get_flags())
    if len(networks)  == 0:
      return 100
    
    if total == 0:
      return 100
    percentage = (completed / total) * 100
    return percentage

  def get_assigned_networks(self):
    networks = self.assigned_networks.all().copy()
    if self.group != None:
      networks.extend(self.group.assigned_networks)
    return networks

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def __str__(self):
    if self.group is None:
      return f"{self.username} (no group)"  
    return f"{self.username} ({self.group.name})"  

  def grant_role(self,role_name):
    role = Role.get_role_by_name(role_name)
    if role not in self.roles:
      self.roles.append(role)
    db.session.add(self)
    db.session.commit()
  
  def revoke_role(self,role_name):
    role = Role.get_role_by_name(role_name)
    if role in self.roles:
      self.roles.remove(role)
    db.session.add(self)
    db.session.commit()

  def gen_vpn_files(self):
    user_crt, user_key, user_cfg = Container.gen_vpn_crt_and_cfg(self)
    self.vpn_crt = user_crt
    self.vpn_key = user_key
    self.vpn_cfg = user_cfg
    db.session.add(self)
    db.session.commit()

  def get_json(self):
    json = {
      "id": self.id,
      "username":self.username,
      "email":self.email,
      "roles": [],
    }
    for role in self.roles:
      json["roles"].append(role.get_json())
    return json

  def reset_password(self):
    charset = []
    charset.extend(string.ascii_letters)
    charset.extend(string.digits)
    
    pass_length = current_app.config["RESET_PASSWORD_LENGTH"]
    password: str = ""
    for i in range(pass_length):
      password += (random.choice(charset))

    self.password = hash_password(password)
    db.session.add(self)
    db.session.commit()
    return password

  def leave_group(self):
    self.group = None
    db.session.add(self)
    db.session.commit()

  @staticmethod
  def create_user(username,password,email,roles=[]):

    if User.username_exists(username):
      raise user_errors.UsernameAlreadyTakenException(name=username)
    if not utils.is_valid_docker_name(username):
      raise user_errors.InvalidUsernameException(name=username)
    if User.email_exists(email):
      raise user_errors.EmailAlreadyTakenException(email=email)

    user =  User(
      username=username,
      password=hash_password(password),
      email=email,
      active=True,
      roles=roles
      )
    
    db.session.add(user)g
    db.session.commit()
    user.gen_vpn_files()

    if(current_app.config["CREATE_TUTORIAL_NETWORK_ON_REGISTRATION"]):
      try:
        NetworkPreset.get_network_preset_by_name("Tutorial").create_network(
          assign_users=[user],
          name= f"{user.username}_tutorial_network"
          )
      except Exception as err:
        current_app.logger.error(str(err))
        flash(f"Tutorial Network could not be created: {str(err)}","error")

    return user

  @staticmethod
  def get_all_users():
    return User.query.all()
  
  @staticmethod
  def get_user_by_username(username):
    user = User.query.filter_by(username=username).first()
    if user == None:
      raise user_errors.UserNotFoundException(identification=username)
    return user

  @staticmethod
  def get_user_by_email(email):
    user = User.query.filter_by(email=email).first()
    if user == None:
      raise user_errors.UserNotFoundException(identification=email)
    return user

  @staticmethod
  def get_user_by_id(id):
    user = User.query.get(id)
    if user == None:
      raise user_errors.UserNotFoundException(identification=id)
    return user

  @staticmethod 
  def username_exists(username):
    try:
      User.get_user_by_username(username)
    except user_errors.UserNotFoundException as err:
      return False
    return True
  
  @staticmethod 
  def email_exists(email):
    try:
      User.get_user_by_email(email)
    except user_errors.UserNotFoundException as err:
      return False
    return True


class Role(BaseModel, RoleMixin):
  name = db.Column(db.String(80), unique=True)
  description = db.Column(db.String(255))
  
  def get_json(self):
    json = {
      "name":self.name,
      "description":self.description,
    }
    return json

  def get_users(self):
    return self.users

  @staticmethod
  def get_admin_users():
    return Role.get_role_by_name("admin").get_users()

  @staticmethod
  def get_role_by_name(name):
    role = Role.query.filter_by(name=name).first()
    if role == None:
      raise user_errors.RoleNotFoundException(name=name)
    return role

  @staticmethod
  def create_role(name,description):
    role = Role(
      name=name,
      description=description
    )

    db.session.add(role)
    db.session.commit()
    return role

class Group(BaseModel):
  invite_code = db.Column(db.String(64), unique=True)
  name = db.Column(db.String(128), unique=True)
  users = db.relationship("User",backref="group")

  def __str__(self):
    return f"{self.id} {self.name}"

  def assign_users(self, users):
    for user in users:
      if user not in self.users:
        self.users.append(user)
    db.session.add(self)
    db.session.commit()
  
  def deassign_users(self,users):
    for user in self.users:
      if user in users:
        self.users.remove(user)


    db.session.add(self)
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def get_json(self):
    json = {
      "id":self.id,
      "name":self.name,
      "code":self.invite_code,
      "users":[],
    }

    for user in self.users:
      json["users"].append(user.get_json())

    return json

  def get_invite_url(self):
    return url_for('users.group_invite',code=self.invite_code, _external=True)

  @staticmethod
  def name_available(name):
    group = Group.get_group_by_name(name)
    return group == None
    
  @staticmethod
  def create_group(name,assign_users):
    group = Group()
    if not utils.is_valid_docker_name(name):
      raise user_errors.InvalidGroupNameException(name)
    if not Group.name_available(name):
      raise user_errors.GroupAlreadyExistsException(name)

    group.name = name
    group.assign_users(assign_users)
    group.invite_code = str(uuid.uuid4()).replace("-","")
    db.session.add(group)
    db.session.commit()

    return group

  @staticmethod
  def get_all_groups():
    return Group.query.all()

  @staticmethod
  def get_group_by_name(name):
    return Group.query.filter_by(name=name).first()

  @staticmethod
  def get_group_by_id(id):
    return Group.query.get(id)
  
  @staticmethod
  def get_group_by_invite_code(code):
    return Group.query.filter_by(invite_code=code).first()
