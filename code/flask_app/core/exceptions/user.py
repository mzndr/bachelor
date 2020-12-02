from flask_app.core.exceptions.generic import Error


class RegistrationException(Error):
  def __init__(self,message):
    self.message = message
    super().__init__(self.message)


class UsernameAlreadyTakenException(RegistrationException):
  def __init__(self,name,message=None):
    if message==None:
      message= f"Username '{name}' is already taken."

    self.message = message
    super().__init__(self.message)

class EmailAlreadyTakenException(RegistrationException):
  def __init__(self,email,message=None):
    if message==None:
      message= f"Email '{email}' is already taken."

    self.message = message
    super().__init__(self.message)

class RetypePasswordDoesntMatchException(RegistrationException):
  def __init__(self,message=None):
    if message==None:
      message= f"Passwords do not match!"

    self.message = message
    super().__init__(self.message) 
