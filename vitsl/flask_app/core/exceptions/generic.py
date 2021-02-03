from flask import current_app


class Error(Exception):
  def __init__(self,message,log=True):
    self.message = message
    if log:
      current_app.logger.error(message)
    super().__init__(self.message)
  
  def __str__(self):
    return self.message
