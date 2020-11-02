from flask import Blueprint

api_bp = Blueprint(
  name="api",
  import_name=__name__,
  url_prefix='/api'
  )

@api_bp.route('/test', methods=['GET'])
def test():
  return "hello"
