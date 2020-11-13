from flask import Blueprint, render_template
from flask_security import current_user, login_required

from flask_app.core.models.user import Group, Role, User

users_bp = Blueprint(
  name="users",
  import_name=__name__
  )

@users_bp.route('/manage_users', methods=['GET'])
@login_required
def manage_users():
  users = User.get_all_users()
  groups = Group.get_all_groups()

  return render_template(
    "manage_users.jinja",
    users=users,
    groups=groups,
    title="Manage Users"
    )
