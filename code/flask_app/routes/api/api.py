from flask import Blueprint, jsonify
from flask_security import login_required

from ...core.models.docker import Container, Network

api_bp = Blueprint(
  name="api",
  import_name=__name__,
  url_prefix='/api'
  )

@api_bp.route('/containers/available', methods=['GET'])
@login_required
def get_available_container_files():
  files = Container.get_available_container_files()
  return jsonify(files)


@api_bp.route('/networks/<string:name>', methods=['GET'])
@login_required
def get_network_by_name(name):
  network = Network.get_network_by_name(name)
  return network.get_json()

@api_bp.route('/networks/<string:name>/delete', methods=['DELETE'])
#@login_required
def delete_network(name):
  network = Network.get_network_by_name(name)
  network.delete()
  return network.get_json()

@api_bp.route('/networks/', methods=['GET'])
@login_required
def get_all_networks():
  networks = Network.get_all_networks()
  json = []
  for network in networks:
    json.append(network.get_json())

  return jsonify(json)
