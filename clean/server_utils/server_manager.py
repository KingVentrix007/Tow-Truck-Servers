import json
import shutil
from server_utils.create_server import get_server
def remove_server_by_display_name(display_name: str, config_path='config.json'):
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        print("Config file not found.")
        return False
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return False

    servers = config.get('servers', [])

    updated_servers = [server for server in servers if server.get('displayName') != display_name]
    
    config['servers'] = updated_servers

    try:
        with open(config_path, 'w') as file:
            json.dump(config, file, indent=4)
        print(f"Server with display name '{display_name}' removed successfully.")
        return True
    except Exception as e:
        print(f"Error writing to config file: {e}")
        return False
def get_all_servers(config_path='config.json'):
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        print("Config file not found.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []

    return config.get('servers', [])
def load_properties(file_path):
    properties = {}
    with open(file_path, 'r') as file:
        for line in file:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                properties[key] = value
    return properties
def save_properties(file_path, properties):
    with open(file_path, 'w') as file:
        for key, value in properties.items():
            file.write(f"{key}={value}\n")

def del_server(name: str):
    data = makeserver.get_server(name)
    path = data["path"]
    remove_server_by_display_name(name)
    shutil.rmtree(path)