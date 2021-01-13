import io
import json

import flask_app.core.exceptions.user as user_errors
from flask import (Blueprint, current_app, flash, jsonify, redirect, request,
                   send_file, url_for)
from flask_app.core.models.user import Group, Role, User
from flask_security import current_user, login_required
from flask_security.decorators import roles_required

user_api_bp = Blueprint(
  name="user_api",
  import_name=__name__,
  url_prefix='/api/users/'
  )


### User ###

@user_api_bp.route('/current/cfg', methods=['GET'])
@login_required
def get_current_user_cfg():
  cfg_string = current_user.vpn_cfg
  filename = f"{current_user.username}.ovpn"
  cfg_bytes = io.BytesIO(bytes(cfg_string,'ascii'))
  return send_file(
    cfg_bytes,
    attachment_filename=filename,
    as_attachment=True
  )

@user_api_bp.route('/register', methods=['POST'])
def register_user():
  try:
    data = request.form
    username = data["username"]
    email = data["email"]
    password = data["password"]
    retype_password = data["retype_password"]

    if password != retype_password:
      raise user_errors.RetypePasswordDoesntMatchException()

    User.create_user(
      username=username,
      password=password,
      email=email
    )

  except user_errors.RegistrationException as err:
    flash(f"Something went wrong: {str(err)}","error")
    return redirect(url_for("security.register"))
  except Exception as err:
    current_app.logger.error(str(err))
    flash(f"Something went wrong","error")

    return redirect(url_for("security.register"))  
  
  flash(f"Account created! Log in to contine.","success")
  return redirect(url_for("security.login"))

@user_api_bp.route('/current/regen_auth', methods=['GET'])
@login_required
def regen_auth_files():
  current_user.gen_vpn_files()
  return {"status":"success"},200

@user_api_bp.route('/<int:user_id>/grant/<string:role_name>', methods=['PUT'])
@login_required
@roles_required('admin')
def grant_role(user_id,role_name):
  user = User.get_user_by_id(user_id)
  user.grant_role(role_name)
  return jsonify(user.get_json())

@user_api_bp.route('/<int:user_id>/revoke/<string:role_name>', methods=['PUT'])
@login_required
@roles_required('admin')
def revoke_role(user_id,role_name):
  user = User.get_user_by_id(user_id)
  user.revoke_role(role_name)
  return jsonify(user.get_json())

@user_api_bp.route('/<int:id>/delete', methods=['DELETE'])
@login_required
@roles_required('admin')
def delete_user(id):
  user = User.get_user_by_id(id)
  json = user.get_json()
  user.delete()
  return jsonify(json)

@user_api_bp.route('/<int:id>/reset_password', methods=['PUT'])
@login_required
@roles_required('admin')
def reset_password(id):
  user: User = User.get_user_by_id(id)
  new_password = user.reset_password()
  response = {
    "username":user.username,
    "new_password":new_password
  }
  return jsonify(response)


@user_api_bp.route('/', methods=['GET'])
@login_required
@roles_required('admin')
def get_all_users():
  ret = []
  users = User.get_all_users()
  for user in users:
    ret.append(user.get_json())
  return jsonify(ret)



### Groups ### 

@user_api_bp.route('/groups/', methods=['GET'])
@login_required
@roles_required('admin')
def get_all_groups():
  ret = []
  groups = Group.get_all_groups()
  for group in groups:
    ret.append(group.get_json())
  return jsonify(ret)

@user_api_bp.route('/groups/create', methods=['POST'])
@login_required
@roles_required('admin')
def create_group():
  json_data = request.get_json()
  name = json_data["name"]
  group = Group.create_group(
    name=name,
    assign_users=[]
  )
  return group.get_json()

@user_api_bp.route('/groups/delete/<int:id>', methods=['DELETE'])
@login_required
@roles_required('admin')
def delete_group(id):
  group = Group.get_group_by_id(id)
  json = group.get_json()
  group.delete()
  return json
