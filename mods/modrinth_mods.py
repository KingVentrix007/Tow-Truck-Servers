import requests
import time
import os
import json
import urllib.request

modrinth_search_limit = 10
cache_file = "modrinthapicache.json"
def load_cache():
    if os.path.exists(cache_file):
        with open(cache_file, "r") as file:
            return json.load(file)
    else:
        return {"downloads": {}}

def save_cache(cache):
    with open(cache_file, "w") as file:
        json.dump(cache, file, indent=4)

mod_loaders=["forge","fabric","quilt","paper","neoforge"]
def modrinth_search(query,limit,offest):
    url = "https://api.modrinth.com/v2/search"
    params = {
        'query': query,
        'limit':limit,
        "offest":offest
    }
    try:
        response = requests.get(url, params=params)
        return response
    except requests.exceptions.RequestException as e:
        print("Error: %s" % e)
def modrinth_search_id(id):
    url = f'https://api.modrinth.com/v2/project/{id}'
    data = requests.get(url).json()
    return data

def get_version_data(version):
    if(version == None):
        return None
    url = f'https://api.modrinth.com/v2/version/{version}'
    data = requests.get(url).json()
    return data
def isClientSide(mod):
    if(mod.get("server_side") == "required"):
        return False
    return True
def isServerSide(mod):
    if(mod.get("server_side") == "required") or (mod.get("server_side") == "optional"):
        return True
    return False
def get_mod_info(mod):
    mod_id = mod.get("project_id")
    data = modrinth_search_id(mod_id)
    return data
def search_mods(query,version,modloader):
    results = []
    found_mods = []
    offest = 0
    count = 0
    while count < 10:
        try:
            response = modrinth_search(query,10,offest)
            if response.status_code == 200:
                data = response.json()
                # print(data["hits"][0])
                for hit in data["hits"]:
                    supported_game_versions = hit["versions"]
                    if(version not in supported_game_versions or modloader not in hit['display_categories']):
                        continue
                    if(hit['project_id'] not in found_mods):
                        found_mods.append(hit['project_id'])
                        results.append(hit)
                        count+=1
                    else:
                        count+=1
                    if(count == 10):
                        break
                offest+=10
            else:
                print("Search failed: %s" % response.status_code)
        except requests.exceptions.RequestException as e:
            print("Error: %s" % e)
    return results
def extract_download_url(data):
    # print(data)
    # Check if data is a list and contains at least one dictionary
    if isinstance(data, list) and data and isinstance(data[0], dict):
        # Check if the 'url' key is present in the first dictionary
        if 'url' in data[0]:
            return data[0]['url']
    return None
# get("url")
def get_download_url(mod, needed_version, modloader):
    return get_download_url_and_version_hash(mod, needed_version, modloader)[0]

def get_download_mod(mod, needed_version, modloader):
    mod_url, mod_hash = get_download_url_and_version_hash(mod, needed_version, modloader)
    dep_urls = None
    if mod_hash is not None:
        dep_urls = get_dependencies_of_version(mod_hash)
    return mod_url,dep_urls

def download_file(url, filename):
    urllib.request.urlretrieve(url, filename)
def get_download_url_and_version_hash(mod, needed_version, modloader):
    # Ensure mod is a string
    mod_name = mod.get("title")
    if not isinstance(mod_name, str):
        raise TypeError(f"Expected mod name to be a string, got {type(mod_name)} instead")

    cache = load_cache()
    downloads = cache.get("downloads", {})
    # print("downloads before:", downloads)
    if mod_name not in downloads:
        downloads[mod_name] = {}

    data = get_mod_info(mod)
    versions = data.get("versions")
    
    for version in versions:
        version_hash = version
        cached_version = downloads[mod_name].get(version_hash)
        
        if cached_version:
            game_versions = cached_version.get('game_versions')
            if needed_version not in game_versions:
                continue
            if cached_version.get('download_url') and modloader in cached_version.get('loader'):
                # print(version_hash)
                print("Found cached version url")
                
                return cached_version.get('download_url'),version_hash
        else:
            versions_data = get_version_data(version_hash)
            game_versions = versions_data.get('game_versions')
            version_number = versions_data.get('version_number')
            loader = versions_data.get('loaders')
            downloads[mod_name][version_hash] = {
                "game_versions": game_versions,
                "download_url": None,
                "loader": loader,
                "version_number": version_number
            }
            # Update the main cache structure with the modified downloads
            cache["downloads"] = downloads
            # print("saving cache after new version added:", cache)
            save_cache(cache)
        
        versions_data = get_version_data(version_hash)
        loader = versions_data.get('loaders')
        
        if needed_version in versions_data.get('game_versions') and modloader in loader:
            file_data = versions_data.get("files")
            url = extract_download_url(file_data)
            
            # Update the cache with the download URL and loader
            downloads[mod_name][version_hash]["download_url"] = url
            downloads[mod_name][version_hash]["loader"] = loader
            # Update the main cache structure with the modified downloads
            cache["downloads"] = downloads
            # print("saving cache after URL found:", cache)
            save_cache(cache)
            print("Found version url")
            
            return url,version_hash

    # Update the main cache structure before returning
    cache["downloads"] = downloads
    # print("saving cache before returning None:", cache)
    save_cache(cache)
    return None,None
def get_mod_name(mod):
    return mod.get("title")           

def get_dependencies_of_version(version):
    # print(get_version_data(version))
    dependencies = get_version_data(version)['dependencies']
    dep_urls = []
    for dep in dependencies:
        dep_data = modrinth_search_id(dep['project_id'])
        dep_version_data = get_version_data(dep['version_id'])
        if(dep_version_data != None):
            dep_url = extract_download_url(dep_version_data.get("files"))
            dep_urls.append(dep_url)
    return dep_urls
        # print(f"{project_name} depends on {dep_name} {dep_url}")
def get_dependencies(mod):
    data = get_mod_info(mod)
    project_name = data.get("title")
    versions = data.get("versions")
    # Use this part of the code
    dependencies = get_version_data(versions[0])['dependencies']
    for dep in dependencies:
        dep_data = modrinth_search_id(dep['project_id'])
        dep_name = dep_data["title"]
        dep_version_data = get_version_data(dep['version_id'])
        dep_url = extract_download_url(dep_version_data.get("files"))
        
        print(f"{project_name} depends on {dep_name} {dep_url}")
    # print()

if __name__ == "__main__":
    search_timer_start = time.time()
    ret = search_mods("Create",'1.19.2','fabric')
    search_timer_end = time.time()
    # get_dependencies(ret[0])
    mod = ret[0]
    download_mod(mod,'1.19.2','fabric',"mods")

    # # print("len(ret) = %d" % len(ret))
    # download_url_timer_start = time.time()
    # # print(type(ret[0]))
    # print(get_download_url(ret[3],'1.19.2','fabric'))
    # download_url_timer_end = time.time()

    # print("Search time:",search_timer_end-search_timer_start)
    # print("Get URL:",download_url_timer_end-download_url_timer_start)
# data = get_mod_info(ret[0])
# versions = data.get("versions")
# version_1 = versions[0]
# versions_data = get_version_data(version_1)
# # print(get_mod_info(ret[0]).keys())
# print(versions_data)
# for i in ret:
    # print(i)
