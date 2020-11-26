import io

from flask import Blueprint, jsonify, request, send_file
from flask_app.core.models.user import Group, Role, User
from flask_security import current_user, login_required

user_api_bp = Blueprint(
  name="user_api",
  import_name=__name__,
  url_prefix='/api/users/'
  )


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



@user_api_bp.route('/current/regen_auth', methods=['GET'])
@login_required
def regen_auth_files():
  current_user.gen_vpn_files()
  return {"status":"success"},200

@user_api_bp.route('/', methods=['GET'])
@login_required
def get_all_users():
  ret = []
  users = User.get_all_users()
  for user in users:
    ret.append(user.get_json())
  return jsonify(ret)

@user_api_bp.route('/groups/', methods=['GET'])
@login_required
def get_all_groups():
  ret = []
  groups = Group.get_all_groups()
  for group in groups:
    ret.append(group.get_json())
  return jsonify(ret)


@user_api_bp.route('/groups/create', methods=['POST'])
@login_required
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
def delete_group(id):
  group = Group.get_group_by_id(id)
  json = group.get_json()
  group.delete()
  return json
