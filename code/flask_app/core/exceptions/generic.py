from flask import current_app


class Error(Exception):
  def __init__(self,message):
    self.message = message
    current_app.logger.error(message)
    super().__init__(self.message)
  
  def __str__(self):
    return self.message

class NameNotAvailableException(Error):
  pass
