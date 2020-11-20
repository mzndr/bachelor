from flask_user import role_required
from flask import Blueprint, render_template
from flask_app.core.models.user import Group, Role, User
from flask_security import current_user, login_required

users_bp = Blueprint(
  name="users",
  import_name=__name__
  )

@users_bp.route('/manage_users', methods=['GET'])
@login_required
@roles_required("admin")
def manage_users():
  users = User.get_all_users()
  groups = Group.get_all_groups()

  return render_template(
    "manage_users.jinja",
    users=users,
    groups=groups,
    title="Manage Users"
    )

@users_bp.route('/group_invite/<string:code>', methods=['GET'])
@login_required
def group_invite(code):
  group: Group = Group.get_group_by_invite_code(code)
  group.assign_users([current_user])

  return {"status":"success"},200
