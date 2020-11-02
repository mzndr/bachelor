import docker

server_ip = '192.168.0.66'

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
  vpn_container.reload()
  ovpn_cmd = f"sudo openvpn --config ~/client.ovpn --remote 192.168.0.66 {vpn_container.ports['1194/udp'][0]['HostPort']} udp"
  print(f"Network '{name}' created:\n\tconnect with `{ovpn_cmd}`")

  return network

def stop_all_containers():
  print("\tCleaning up...")
  for container in client.containers.list():
    print("\t\tKilling container...")
    container.kill()
  print("\t\tRemoving unused networks (prune)...")
  client.networks.prune()

def main():
  try:
    print("Cleaning up before starting")
    stop_all_containers()

    print("Creating networks and containers...")
    for i in range(2):
      network_name = f"testnetwork{i}"
      network = create_network(network_name)
      containers.append(create_container("./containers/apache",network_name, container_name=f"apache{i}"))

    print("Running networks")
    input("Press enter to exit")

  except KeyboardInterrupt:
      print("Keyboard Interrupt.")
      
  stop_all_containers()
