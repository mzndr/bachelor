import docker
from flask_security import RoleMixin, UserMixin
from flask_sqlalchemy import SQLAlchemy

from ..db import db
from ..models.docker import Container, Network

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

docker_client = docker.from_env()    
class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(255), unique=True)
  email = db.Column(db.String(255), unique=True)
  password = db.Column(db.String(255))

  vpn_crt = db.Column(db.String(2**16))
  vpn_key = db.Column(db.String(2**16))
  vpn_cfg = db.Column(db.String(2**16))

  active = db.Column(db.Boolean())
  confirmed_at = db.Column(db.DateTime())
  roles = db.relationship('Role', secondary=roles_users,
                          backref=db.backref('users', lazy='dynamic'))
  vpn_crt = db.Column(db.String(255))



    

  def gen_vpn_files(self):
    user_crt, user_key, user_cfg = Container.gen_vpn_crt_and_cfg(self)
    self.vpn_crt = user_crt
    self.vpn_key = user_key
    self.vpn_cfg = user_cfg
    db.session.add(self)
    db.session.commit()



  def get_json(self):
    json = {
      "username":self.username,
      "email":self.email,
      "roles": [],
    }
    for role in self.roles:
      json["roles"].append(role.get_json())
    return json

  @staticmethod
  def create_user():
    pass

  @staticmethod
  def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

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
