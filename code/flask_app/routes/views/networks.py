from flask import Blueprint, render_template, abort
from flask_security import current_user, login_required
from flask_security.decorators import roles_required
from flask_app.core.models.docker import Network, NetworkPreset

networks_bp = Blueprint(
  name="networks",
  import_name=__name__
  )

@networks_bp.route('/manage_networks', methods=['GET'])
@login_required
@roles_required("admin")
def manage_networks():
  networks = Network.get_all_networks()
  presets = NetworkPreset.query.all()
  return render_template(
    "manage_networks.jinja",
    networks=networks,
    presets=presets,
    title="Manage Networks"
    )

@networks_bp.route('/assigned_networks/<int:id>/details', methods=['GET'])
@login_required
def network_details(id):
  network = Network.get_network_by_id(id)
  if network == None:
      abort(404)

  user = current_user
  if not network.user_allowed_to_access(user):
    return {"error","you are not assigned to this network"}, 403

  return render_template(
    "network_details.jinja",
    network=network,
    title=f"Networkdetails of \"{network.name}\""
    )

