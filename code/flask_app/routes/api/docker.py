from flask_security.decorators import roles_required
from flask import Blueprint, current_app, jsonify, request
from flask_security import current_user, login_required

from ...core.models.docker import (Container, ContainerImage, Flag, Network,
                                   NetworkPreset)
from ...core.models.user import Group, User

docker_api_bp = Blueprint(
  name="docker_api",
  import_name=__name__,
  url_prefix='/api/docker/'
  )

@docker_api_bp.route('/containers', methods=['GET'])
@login_required
@roles_required("admin")
def get_available_container_images():
  files = ContainerImage.get_available_container_images()
  return jsonify(files)

@docker_api_bp.route('/createtest/<string:name>', methods=['GET'])
@login_required
@roles_required("admin")
def create_test_network(name):
  test_user = User.get_user_by_username(current_app.config["USERNAME"])
  Network.create_network(
    network_name=name,
    container_image_names=["apache","apache","apache"],
    assign_users=[test_user]
  )
  
  return get_all_networks()

@docker_api_bp.route('/networkpresets/create', methods=['POST'])
@login_required
@roles_required("admin")
def create_network_preset():
  try:
    json_data = request.get_json()
    preset_name = json_data["name"]
    container_images = json_data["containers"]
    network_preset = NetworkPreset.create_network_preset(
      name=preset_name,
      container_image_names=container_images
    )
    return jsonify(network_preset.get_json())
  except Exception as err:
    return ({"err":str(err)},500)

@docker_api_bp.route('/networkpresets/<int:id>/delete', methods=['DELETE'])
@login_required
@roles_required("admin")
def delete_network_preset(id):
  preset = NetworkPreset.get_network_preset_by_id(id)
  json = preset.get_json()
  preset.delete()

  return json

@docker_api_bp.route('/networkpresets/<int:id>/start', methods=['POST'])
@login_required
@roles_required("admin")
def start_network(id):
  try:
    preset = NetworkPreset.get_network_preset_by_id(id)
    json_data = request.get_json()
    assign_users_ids = json_data["assign_users"]
    assign_users = []
    assign_groups_ids = json_data["assign_groups"]
    assign_groups = []
    netork_name = json_data["network_name"]

    for user_id in assign_users_ids:
      assign_users.append(User.get_user_by_id(user_id))
    for group_id in assign_groups_ids:
      assign_groups.append(Group.get_group_by_id(group_id))

    network = preset.create_network(
      assign_users=assign_users,
      assign_groups=assign_groups,
      name=netork_name
      )
    return network.get_json()
  except Exception as err:
    return {"error": str(err) },500

@docker_api_bp.route('/networks/<string:name>', methods=['GET'])
@login_required
@roles_required("admin")
def get_network_by_name(name):
  network = Network.get_network_by_name(name)
  return network.get_json()

@docker_api_bp.route('/networks/<string:name>/vpndata', methods=['GET'])
@login_required
@roles_required("admin")
def get_network_vpn_data(name):
  network = Network.get_network_by_name(name)
  return jsonify(network.get_connection_command(current_user))

@docker_api_bp.route('/networks/<string:name>/delete', methods=['DELETE'])
@login_required
@roles_required("admin")
def delete_network(name):
  network = Network.get_network_by_name(name)
  json = network.get_json()
  network.delete()
  return json

@docker_api_bp.route('/networks/', methods=['GET'])
@login_required
@roles_required("admin")
def get_all_networks():
  networks = Network.get_all_networks()
  json = []
  for network in networks:
    json.append(network.get_json())

  return jsonify(json)


@docker_api_bp.route('/networks/redeem_flag', methods=['POST'])
@login_required
def redeem_flag():
  networks = Network.get_all_networks()
  json_data = request.get_json()
  flag_code = json_data["flag"]
  flag = Flag.get_flag_by_code(flag_code)
  for network in current_user.assigned_networks:
    if flag in network.get_redeemed_flags():
      return {"status":"flag already redeemed!"},410
    if flag in network.get_unredeemed_flags():
      flag.redeem(current_user)
      return {"status":"flag successfully redeemed!"},200
  
  return {"status":"invalid flag, flag not found!"},404
