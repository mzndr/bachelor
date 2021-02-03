import json

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_app.core.models.user import Group, Role, User
from flask_security import current_user, login_required
from flask_security.decorators import roles_required

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

@users_bp.route('/register/<string:group_invite>', methods=['GET'])
def register_with_group(group_invite):
  group = Group.get_group_by_invite_code(code)

@users_bp.route('/group_invite/<string:code>', methods=['GET'])
def group_invite(code):
  group = Group.get_group_by_invite_code(code)
  if current_user.is_anonymous:
    abort(403)
  
  if current_user in group.users:
    flash(f"You are already assigned to {group.name}!","error")
  else:
    if current_user.group is not None:
      current_user.group.deassign_users([current_user])

    group.assign_users([current_user])
    flash(f"You are now assigned to {group.name}!","success")

  return redirect(url_for("index.index"))
