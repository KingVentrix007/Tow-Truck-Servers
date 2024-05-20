import json
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