import re


def is_valid_docker_name(name):
  regex = r'[a-zA-Z0-9_.-]*'
  if re.fullmatch(regex,name) is not None:
    return True
  return False

