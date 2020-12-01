from flask_security.utils import hash_password
from flask_sqlalchemy import SQLAlchemy

from ..core.models import *

db = SQLAlchemy()

def init_data(app):
  """ function for creating initial data like roles, admin user etc."""


  from flask_app.core.models.docker import NetworkPreset
  from flask_app.core.models.user import Role, User

  with app.app_context():
    db.create_all()
    try:
        admin_role = Role.create_role(
            name="admin",
            description="Privilidged role for administration purposes"
        )

        User.create_user(
            username="admin",
            password="123456",
            email="admin@test.local",
            roles=[admin_role]
        )

        NetworkPreset.create_network_preset(
            name="Tutorial",
            container_image_names=["apache_tutorial"]
        )

        NetworkPreset.create_network_preset(
            name="_Debug_Preset",
            container_image_names=["debug_container"]
        )

        User.create_user(
            username="test_user",
            password="123456",
            email="test@test.local",
            roles=[]
        )
    except Exception as err:
        app.logger.error(str(err))
        pass
