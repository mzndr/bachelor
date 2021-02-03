import sys
import logging
logging.basicConfig(stream=sys.stderr)

path = '/var/www/vitsl/'
if path not in sys.path:
   sys.path.insert(0, path)

activate_this = '/var/www/vitsl/env/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from flask_app import create_app
application = create_app()