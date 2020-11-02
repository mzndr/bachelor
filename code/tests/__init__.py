import os
import tempfile

import pytest
from flask_app import create_app

app = create_app()

@pytest.fixture
def client():
  
  db_fd, app.config['DATABASE'] = tempfile.mkstemp()
  app.config['TESTING'] = True
  with app.test_client() as client:
    yield client

  os.close(db_fd)
  os.unlink(app.config['DATABASE'])
