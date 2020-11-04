from flask import Blueprint, current_app, jsonify
from flask_security import current_user, login_required

from ...core.models.docker import Container, Network
from ...core.models.user import User

docker_api_bp = Blueprint(
  name="docker",
  import_name=__name__,
  url_prefix='/api/docker/'
  )

@docker_api_bp.route('/containers', methods=['GET'])
@login_required
def get_available_container_files():
  files = Container.get_available_container_files()
  return jsonify(files)

@docker_api_bp.route('/createtest/<string:name>', methods=['GET'])
@login_required
def create_test_network(name):
  test_user = User.get_user_by_username(current_app.config["USERNAME"])
  Network.create_network(
    network_name=name,
    container_folder_names=["apache","apache","apache"],
    assign_users=[test_user]
  )
  
  return get_all_networks()

@docker_api_bp.route('/networks/create', methods=['POST'])
@login_required
def create_network():
  pass

@docker_api_bp.route('/networks/<string:name>', methods=['GET'])
@login_required
def get_network_by_name(name):
  network = Network.get_network_by_name(name)
  return network.get_json()

@docker_api_bp.route('/networks/<string:name>/vpndata', methods=['GET'])
@login_required
def get_network_vpn_data(name):
  network = Network.get_network_by_name(name)
  return jsonify(network.get_connection_command(current_user))

@docker_api_bp.route('/networks/<string:name>/delete', methods=['DELETE'])
@login_required
def delete_network(name):
  network = Network.get_network_by_name(name)
  json = network.get_json()
  network.delete()
  return json

@docker_api_bp.route('/networks/', methods=['GET'])
@login_required
def get_all_networks():
  networks = Network.get_all_networks()
  json = []
  for network in networks:
    json.append(network.get_json())

  return jsonify(json)
