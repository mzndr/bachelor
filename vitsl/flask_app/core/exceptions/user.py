from flask_app.core.exceptions.generic import Error


class RegistrationException(Error):
  def __init__(self,message):
    self.message = message
    super().__init__(self.message,log=False)


class UsernameAlreadyTakenException(RegistrationException):
  def __init__(self,name,message=None):
    if message==None:
      message= f"Username '{name}' is already taken."

    self.message = message
    super().__init__(self.message)

class InvalidUsernameException(RegistrationException):
  def __init__(self,name,message=None):
    if message==None:
      message= f"Username '{name}' is invalid. It must match [a-zA-Z0-9_.-]*"

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

class UserNotFoundException(Error):
    def __init__(self,identification,message=None):
      if message == None:
        message = f"User '{identification}' was not found."

      self.message = message
      super().__init__(self.message) 

class RoleNotFoundException(Error):
    def __init__(self,name,message=None):
      if message == None:
        message = f"Role '{name}' was not found."

      self.message = message
      super().__init__(self.message) 

class InvalidGroupNameException(Error):
  def __init__(self,name,message=None):
    if message==None:
      message= f"Invalid group name \"{ name }\". It must match [a-zA-Z0-9_.-]*"

    self.message = message
    super().__init__(self.message)

class GroupAlreadyExistsException(Error):
  def __init__(self,name,message=None):
    if message==None:
      message= f"Group \"{ name }\" already exists."

    self.message = message
    super().__init__(self.message)
