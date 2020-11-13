import io

from flask import Blueprint, send_file
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
