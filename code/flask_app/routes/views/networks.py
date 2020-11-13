from flask import Blueprint, render_template
from flask_security import current_user, login_required

from flask_app.core.models.docker import Network, NetworkPreset

networks_bp = Blueprint(
  name="networks",
  import_name=__name__
  )

@networks_bp.route('/manage_networks', methods=['GET'])
@login_required
def manage_networks():
  networks = Network.get_all_networks()
  presets = NetworkPreset.query.all()
  return render_template(
    "manage_networks.jinja",
    networks=networks,
    presets=presets,
    title="Manage Networks"
    )
