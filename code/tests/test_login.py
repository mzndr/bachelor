from . import *


def login(client, username, password):
    return client.post('/login', data=dict(
        email=username,
        password=password
    ), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def test_login_logout(client):
    """Make sure login and logout works."""

    rv = login(client, app.config['USERNAME'], app.config['PASSWORD'])
    assert b'Login' in rv.data

    rv = logout(client)
    assert b'Login' in rv.data

    rv = login(client, app.config['USERNAME'] + 'x', app.config['PASSWORD'])
    assert app.config['SECURITY_MSG_USER_DOES_NOT_EXIST'] in rv.data

    rv = login(client, app.config['USERNAME'], app.config['PASSWORD'] + 'x')
    assert app.config['SECURITY_MSG_INVALID_PASSWORD'] in rv.data
