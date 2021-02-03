from flask import Blueprint, abort, render_template
from flask_app.core.models.docker import Network, NetworkPreset
from flask_security import current_user, login_required
from flask_security.decorators import roles_required

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
  if not network.user_allowed_to_access(current_user):
      abort(403)

  return render_template(
    "network_details.jinja",
    network=network,
    title=f"Networkdetails of \"{network.name}\""
    )

