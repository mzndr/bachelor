import re


def is_valid_docker_name(name):
  if name == "":
    return False

  regex = r'[a-zA-Z0-9_.-]*'
  if re.fullmatch(regex,name) is not None:
    return True
  return False

def remove_duplicates_from_list(_list):
  new_list = []
  for item in _list:
    if item not in new_list:
      new_list.append(item)
  return new_list


  mac = netifaces.ifaddresses(interface_name)[netifaces.AF_LINK][0]['addr']
  return mac
