from flask_app.core.exceptions.generic import Error


class ImageNotFoundException(Error):
  def __init__(self,name,message=None):
    if message=None:
      message= f"Container image '{image_name}' does not exist on disk. If its there, check if there is a dockerfile in its root directory."

    self.message = message
    super().__init__(self.message)

class InvalidContainerNameException(Error):
  def __init__(self,name,message=None):
    if message=None:
      message= f"Invalid container name \"{ name }\". It must match [a-zA-Z0-9_.-]*"

    self.message = message
    super().__init__(self.message)


class InvalidNetworkNameException(Error):
  def __init__(self,name,message=None):
    if message=None:
      message= f"Invalid network name \"{ name }\". It must match [a-zA-Z0-9_.-]*"

    self.message = message
    super().__init__(self.message)

