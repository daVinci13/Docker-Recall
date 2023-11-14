import docker

# Create a Docker client
client = docker.from_env()

# List all running containers excluding those part of a stack or service
containers = [container for container in client.containers.list() if 'com.docker.stack.namespace' not in container.labels]

# Print container information
print("Available Containers:")
for i, container in enumerate(containers, start=1):
    print(f"{i}. {container.name}")

# Ask the user to select a container
container_number = int(input("Select a container (enter the corresponding number): "))

# Validate user input
if 1 <= container_number <= len(containers):
    selected_container = containers[container_number - 1]

    # Print detailed information about the selected container
    print("\nDetails for Selected Container:")
    print(f"Container Name: {selected_container.name}")
    print(f"Container ID: {selected_container.id}")
    print(f"Image: {selected_container.image.tags[0] if selected_container.image.tags else 'None'}")

    # Print user-defined volumes
    volumes = selected_container.attrs['Mounts']
    if volumes:
        print("User-Defined Volumes:")
        for volume in volumes:
            print(f"  Container Path: {volume['Destination']}, Host Path: {volume['Source']}")

    # Print user-defined environment variables
    environment_variables = selected_container.attrs['Config']['Env']
    if environment_variables:
        print("User-Defined Environment Variables:")
        for env_var in environment_variables:
            print(f"  {env_var}")

    # Print reconstructed docker run command
    docker_run_command = f"docker run -d"

    # Add container name
    docker_run_command += f" --name {selected_container.name}"

    # Add port mapping
    ports = selected_container.attrs['NetworkSettings']['Ports']
    if ports:
        for container_port, host_ports in ports.items():
            host_port = host_ports[0]['HostPort']
            docker_run_command += f" -p {host_port}:{container_port}"

    # Add user-defined volumes
    if volumes:
        for volume in volumes:
            docker_run_command += f" -v {volume['Source']}:{volume['Destination']}"

    # Add user-defined environment variables
    if environment_variables:
        for env_var in environment_variables:
            docker_run_command += f" -e {env_var}"

    # Add image
    docker_run_command += f" {selected_container.image.tags[0] if selected_container.image.tags else 'None'}"

    print("\nReconstructed docker run command:")
    print(docker_run_command)

else:
    print("Invalid selection. Please enter a valid container number.")
