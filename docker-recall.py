import docker

client = docker.from_env()

# Check if Docker is running in swarm mode
info = client.info()
swarm_mode = info['Swarm']['LocalNodeState'] == 'active'

if swarm_mode:
    # List all services
    services = client.services.list()
    print("Services:")
    for service in services:
        print(service.name)
else:
    # List all containers
    containers = client.containers.list(all=True)
    print("Containers:")
    for container in containers:
        print(container.name)

# Get user selection
selection = input("Enter the name of the container or service you want to inspect: ")

if swarm_mode:
    # Find the selected service
    selected_service = None
    for service in services:
        if service.name == selection:
            selected_service = service
            break

    if selected_service:
        # Get service details
        service_info = selected_service.attrs
        envs = service_info['Spec']['TaskTemplate']['ContainerSpec']['Env']
        ports = service_info['Endpoint']['Ports']
        mounts = service_info['Spec']['TaskTemplate']['ContainerSpec']['Mounts']

        # Reconstruct docker-compose.yml
        compose = f"""
version: '3.8'
services:
  {selected_service.name}:
    image: {service_info['Spec']['TaskTemplate']['ContainerSpec']['Image']}
"""
        if envs:
            compose += "    environment:\n"
            for env in envs:
                if not env.startswith('PATH='):
                    compose += f"      - {env}\n"
        if ports:
            compose += "    ports:\n"
            for port in ports:
                compose += f"      - \"{port['TargetPort']}:{port['PublishedPort']}\"\n"
        if mounts:
            compose += "    volumes:\n"
            for mount in mounts:
                if mount['Type'] == 'bind':
                    compose += f"      - {mount['Source']}:{mount['Target']}\n"

        print(f"docker-compose.yml to start {selected_service.name}:")
        print(compose)
    else:
        print(f"No service found with name: {selection}")
else:
    # Find the selected container
    selected_container = None
    for container in containers:
        if container.name == selection:
            selected_container = container
            break

    if selected_container:
        # Get container details
        container_info = selected_container.attrs
        envs = container_info['Config']['Env']
        ports = container_info['HostConfig']['PortBindings']
        volumes = container_info['Mounts']

        # Reconstruct command
        command = f"docker run --name {selected_container.name}"
        for env in envs:
            if not env.startswith('PATH='):
                command += f" -e {env}"
        for port in ports:
            command += f" -p {ports[port][0]['HostPort']}:{port}"
        for volume in volumes:
            if volume['Type'] == 'bind':
                command += f" -v {volume['Source']}:{volume['Destination']}"
        command += f" {container_info['Config']['Image']}"

        print(f"Command to start {selected_container.name}:")
        print(command)
    else:
        print(f"No container found with name: {selection}")
