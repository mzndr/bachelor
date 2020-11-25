import uuid

from flask_app.core.db import db
from flask_app.core.models.docker import Container, Network
from flask_security import RoleMixin, UserMixin
from flask_security.utils import hash_password
from flask_sqlalchemy import SQLAlchemy

import docker

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

docker_client = docker.from_env()    
class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(255), unique=True)
  email = db.Column(db.String(255), unique=True)
  password = db.Column(db.String(255))

  redeemed_flags = db.relationship("Flag",backref=db.backref('redeemed_by'))

  vpn_crt = db.Column(db.String(2**16))
  vpn_key = db.Column(db.String(2**16))
  vpn_cfg = db.Column(db.String(2**16))

  active = db.Column(db.Boolean())
  confirmed_at = db.Column(db.DateTime())
  roles = db.relationship('Role', secondary=roles_users,
                          backref=db.backref('users', lazy='dynamic'))
  vpn_crt = db.Column(db.String(255))

  group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

    

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

  @staticmethod
  def create_user(username,password,email,roles=[]):
    user =  User(
      username=username,
      password=hash_password(password),
      email=email,
      active=True,
      roles=roles
      )
    
    db.session.add(user)
    db.session.commit()
    user.gen_vpn_files()

    return user

  @staticmethod
  def get_all_users():
    return User.query.all()
  
  @staticmethod
  def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

  @staticmethod
  def get_user_by_id(id):
    return User.query.get(id)

class Role(db.Model, RoleMixin):
  id = db.Column(db.Integer(), primary_key=True)
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
    return Role.get_roll_by_name("admin").get_users()

  @staticmethod
  def get_roll_by_name(name):
    return Role.query.filter_by(name=name).first()

  @staticmethod
  def create_role(name,description):
    role = Role(
      name=name,
      description=description
    )

    db.session.add(role)
    db.session.commit()
    return role

class Group(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  invite_code = db.Column(db.String, unique=True)
  name = db.Column(db.String, unique=True)
  users = db.relationship("User")

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

    if len(self.users) <= 0:
      self.delete()

    db.session.add(self)
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def get_json(self):
    json = {
      "id":self.id,
      "name":self.name,
      "users":[]
    }

    for user in self.users:
      json["users"].append(user.get_json())

    return json

  @staticmethod
  def create_group(name,assign_users):
    group = Group()
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
  def get_group_by_id(id):
    return Group.query.get(id)
  
  @staticmethod
  def get_group_by_invite_code(code):
    return Group.query.filter_by(invite_code=code).first()
