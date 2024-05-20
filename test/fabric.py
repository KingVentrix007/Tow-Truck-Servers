import requests
import json
# Define the URL to get the loader version information
loader_info_url = 'https://meta.fabricmc.net/v2/versions/loader/1.19.2'



# Send a GET request to the URL
response = requests.get(loader_info_url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data_list = response.json()
    
    # Filter out stable versions and get the highest version number
    stable_versions = [data.get('loader', {}).get('version', '') for data in data_list if data.get('loader', {}).get('stable', False)]
    latest_stable_version = max(stable_versions, default=None)
    
    if latest_stable_version:
        # Construct the URL for the server installer JAR file
        download_url = f'https://meta.fabricmc.net/v2/versions/loader/1.19.2/{latest_stable_version}/1.0.1/server/jar'
        
        # Download the installer JAR file
        installer_response = requests.get(download_url)
        
        if installer_response.status_code == 200:
            # Save the JAR file to the local filesystem
            with open(f'fabric-server-installer-{latest_stable_version}.jar', 'wb') as file:
                file.write(installer_response.content)
            print(f'Fabric server installer for the latest stable version {latest_stable_version} downloaded successfully.')
        else:
            print(f'Failed to download the Fabric server installer for the latest stable version {latest_stable_version}.')
    else:
        print('No stable versions found in the response.')
else:
    print('Failed to fetch the loader version information.')


