from flask import Blueprint, render_template
from flask_security import current_user, login_required

index_bp = Blueprint(
  name="index",
  import_name=__name__
  )

@index_bp.route('/', methods=['GET'])
@login_required
def index():
  return render_template(
    "dashboard.jinja",
    title="index"
    )


@index_bp.route('/getting_started', methods=['GET'])
@login_required
def getting_started():
  return render_template(
    "getting_started.jinja",
    title="Getting Started"
    )
