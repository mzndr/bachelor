#!/usr/bin/env python3
import docker

client = docker.from_env()

def create_container(dockerfile_path,network_name,container_name=None,ports=None):
  image, logs = client.images.build(
    path=dockerfile_path
  )
  return client.containers.run(
    image=image,
    name=container_name,
    remove=True,
    detach=True,
    ports=ports,
    network=network_name
    )

def create_network(name):
  return client.networks.create(
    name=name,
    check_duplicate=True
  )

def stop_all_containers():
  for container in client.containers.list():
    container.kill()

def main():
  network_name = "testnetwork"
  client.networks.prune()
  network = create_network(network_name)
  containers = []
  containers.append(create_container("./containers/apache",network_name))
  containers.append(create_container("./containers/apache",network_name))
  containers.append(create_container("./containers/apache",network_name))
  containers.append(create_container("./containers/apache",network_name))
  containers.append(create_container("./containers/apache",network_name))

  print("Running apache!")
  input("Press any button to kill the containers")
  stop_all_containers()

  



if __name__ == "__main__":
  main()
