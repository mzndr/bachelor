from ..db import db


class BaseModel(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer(), primary_key=True, nullable=False)

    def get_json(self):
      raise NotImplementedError()

    def delete(self):
      raise NotImplementedError()

    def __str__(self):
      return self.id
