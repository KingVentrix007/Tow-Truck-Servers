from mods.fabric import GetLatestStableFabricServerURL
from mods.forge import GetRecommendedURL
from minecraft.minecraft_versions import minecraft_versions
import requests
valid_mod_loaders = ["forge","fabric"]

def download_forge(version:str,name:str,progress_var,on_complete):
    forge_installer_url = GetRecommendedURL(version)
    response = requests.get(forge_installer_url, stream=True)
    print(response.headers)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024 # 1 Kibibyte
    bytes_so_far = 0
    use_name = name.replace(" ","")
    with open(f"./servers/{use_name}/forge_installer_{version}.jar", "wb") as file:
        for data in response.iter_content(block_size):
            file.write(data)
            bytes_so_far += len(data)
            progress = int(bytes_so_far * 100 / total_size)
            progress_var.set(progress)
    on_complete(name, version)
def download_fabric(version:str,name:str,on_complete):
    fabric_install_url = GetLatestStableFabricServerURL(version)
    print(fabric_install_url)
    response = requests.get(fabric_install_url, stream=True)
    if(response.status_code != 200):
        print(response.status_code)
    print(response.headers)
    block_size = 1024 # 1 Kibibyte
    use_name = name.replace(" ","")
    with open(f"./servers/{use_name}/fabric_installer_{version}.jar", "wb") as file:
        for data in response.iter_content(block_size):
            file.write(data)
    on_complete(name, version)
def download_server_jar(name:str, version:str,progress_var,on_complete,modloader:str):
    if(version not in minecraft_versions):
        return -1
    if(modloader not in valid_mod_loaders):
        return -2
    if(modloader == "fabric"):
        download_fabric(name=name, version=version,on_complete=on_complete)
        return 0
    elif(modloader == "forge"):
        download_forge(name=name, version=version,progress_var=progress_var,on_complete=on_complete)
        return 0
    