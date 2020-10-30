#!/usr/bin/env python3
import docker

client = docker.from_env()
containers = []

def create_container(dockerfile_path,network_name,
container_name=None,
ports=None, 
command=None,
cap_add=None,
privileged=False,
):
  image, logs = client.images.build(
    path=dockerfile_path,
    nocache=True
  )
  return client.containers.run(
    image=image,
    name=container_name,
    remove=True,
    detach=True,
    ports=ports,
    command=command,
    network=network_name,
    cap_add=cap_add,
    privileged=privileged
    )



def create_network(name):
  # eth0 will be external virtual network where the vpn container is
  # eth1 will be internal virtual network where the other containers are
  #vpn_network_name = name + "_vpn"
  #vpn_network = client.networks.create(
  #  name=vpn_network_name,
  #  check_duplicate=True,
  #  internal=False
  #  )

  network = client.networks.create(
      name=name,
      check_duplicate=True,
      internal=False
    )

  vpn_container = create_container(
    "./containers/vpn",
    name,
    container_name= name + "_vpn_container",
    ports={"1194/udp":None},
    cap_add="NET_ADMIN",
    privileged=True
    )


  containers.append(vpn_container)



  return "network"

def stop_all_containers():
  for container in client.containers.list():
    container.kill()
    client.networks.prune()

def main():
  stop_all_containers()

  for i in range(2):
    network_name = f"testnetwork{i}"
    network = create_network(network_name)
    containers.append(create_container("./containers/apache",network_name, container_name=f"apache{i}"))



  print("Running networks")
  input("Press any button to kill the containers")
  stop_all_containers()


  #client.networks.prune()

  



if __name__ == "__main__":
  main()
