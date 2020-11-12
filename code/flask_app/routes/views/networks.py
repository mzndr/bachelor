from flask import Blueprint, render_template
from flask_security import current_user, login_required

from flask_app.core.models.docker import NetworkPreset

networks_bp = Blueprint(
  name="networks",
  import_name=__name__
  )

@networks_bp.route('/create_preset', methods=['GET'])
@login_required
def create_network_preset():
  return render_template(
    "create_network_preset.jinja",
    title="Compose Network Preset"
    )

@networks_bp.route('/list_presets', methods=['GET'])
@login_required
def network_preset_list():
  presets = NetworkPreset.query.all()
  return render_template(
    "network_preset_list.jinja",
    title="Browse Network Presets",
    presets=presets
    )
