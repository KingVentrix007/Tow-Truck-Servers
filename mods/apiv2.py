import requests
import time
import os
import json
import urllib.request
import logging
max_recursion = 10
def setup_logging(log_file):
    """Setup logging configuration."""
    logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
def apiv2log(*args):
    """Log a message."""
    message = ' '.join(map(str, args))
    logging.info(message)


def modrinth_search(query,limit,offest):
    url = "https://api.modrinth.com/v2/search"
    params = {
        'query': query,
        'limit':limit,
        "offset":offest
    }
    try:
        response = requests.get(url, params=params)
        return response
    except requests.exceptions.RequestException as e:
        apiv2log("Error: %s" % e)

def search_mods(query,version,modloader):
    return search_mods_internal(query,version,modloader)[0]


def search_mods_internal(query,version,modloader,initial_offset=0,found_mods_start=[]):
    results = []
    found_mods = found_mods_start
    offset_int = initial_offset
    count = 0
    hits = initial_offset
    while count < 20:
        try:
            response = modrinth_search(query,20,offset_int)
            if response.status_code == 200:
                data = response.json()
                # print(data["hits"][0])
                # print(data['total_hits'],data["offset"])
                total_hits = data['total_hits']
                for hit in data["hits"]:
                    hits+=1
                    if(hits >= total_hits):
                        return results,offset_int
                    supported_game_versions = hit["versions"]
                    apiv2log(hit["display_categories"])
                    if(version not in supported_game_versions or modloader not in hit["display_categories"]):
                        apiv2log("Skipped mod",hit["title"])
                        continue
                    elif(hit['project_id'] not in found_mods):
                        found_mods.append(hit['project_id'])
                        results.append(hit)
                        count+=1
                        # print(count)
                    # else:
                    #     # print("Got duplicate mods",hit["title"])
                    if(count == 20):
                        break
                offset_int+=10
                # print("offset_int == %d" % offset_int)
            else:
                apiv2log("Search failed: %s" % response.status_code)
        except requests.exceptions.RequestException as e:
            apiv2log("Error: %s" % e)
    return results,offset_int

def find_correct_versions(results, version):
    correct_items = []
    apiv2log(results[0]['dependencies'])
    for item in results:
        if version in item['game_versions']:
            correct_items.append(item)
    return correct_items
def search_project_by_version_and_modloader(project_id, modloader):
    url = f"https://api.modrinth.com/v2/project/{project_id}/version"
    params = {
        "modloader": modloader,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def id_to_name(project_id):
    apiv2log(project_id)
    url = f"https://api.modrinth.com/v2/project/{project_id}"
    data = requests.get(url).json()
    return data["title"]
def get_project_data_id(project_id):
    apiv2log(project_id)
    url = f"https://api.modrinth.com/v2/project/{project_id}"
    data = requests.get(url).json()
    return data
def get_version_data(version):
    if(version == None):
        return None
    url = f'https://api.modrinth.com/v2/version/{version}'
    data = requests.get(url).json()
    return data

def get_dependencies_url(dependency,version,loader):
    version_id = dependency["version_id"]
    dep_project_id = dependency["project_id"]
    if(version_id != None):
        dep_data = get_version_data(version_id)
        if(dep_data != None):
            # print("dep_data=",dep_data)
            dep_files = dep_data['files']
            for dep_file in dep_files:
                if(dep_file['primary'] == True):
                    dep_url = dep_file["url"]
                    dep_id = dep_data["project_id"]
                    apiv2log(dep_id,dep_id)
                    # print()
                    return dep_url,dep_id
        apiv2log("No dependencies")
    elif(dep_project_id != None):
        project_version = search_project_by_version_and_modloader(dep_project_id,"")
        correct_versions = find_correct_versions(project_version,version)
        for ver in correct_versions:
            ver_loaders = ver["loaders"]
            ver_version = ver["game_versions"]
            ver_id = ver["project_id"]
            if(loader in ver_loaders and version in ver_version):
                dep_d_file = ver["files"]
                dep_url = dep_d_file[0]["url"]

                return dep_url,ver_id
            # apiv2log("ver == ",ver)
    return None,None
            # print(dep_file)
        # print("\n================================\n")
def get_download_urls(project_id,version,modloader,first_mod=False):
    urls = []
    data = search_project_by_version_and_modloader(project_id,modloader)
    
    if(data == None):
        return None
    correct_versions = find_correct_versions(data,version)
    for correct_version in correct_versions:
        file_data = correct_version["files"]
        version_name = correct_version["name"]
        date = correct_version["date_published"]
        version_type = correct_version["version_type"]
        dependencies = correct_version["dependencies"]
        dep_urls_api_internal = []
        dep_error = False
        for dependency in dependencies:
            apiv2log(dependency["dependency_type"])
            dep_url,dep_id = get_dependencies_url(dependency,version,modloader)
            if(dep_url == None and dependency["dependency_type"] == "required"):
                dep_error = True
            if(dep_url != None):
                # dep_urls_api_internal.append(dep_url)
                dep = {
                    "url":dep_url,
                    "id":dep_id
                }
                dep_urls_api_internal.append(dep)
                apiv2log("dep_url == " + str(dep_url))
            else:
                apiv2log("continue")
        # print(dependencies)
        # print("File: "+version_name,"status: "+str(status),"date: "+date)
        if(dep_error == False):
            for file in file_data:
                filename = file["filename"]
                file_url = file["url"]
                is_primary = file["primary"]
                # print("dep_urls_api_internal=",dep_urls_api_internal)
                mod_data = {
                    "filename": filename,
                    "project_id":project_id,
                    "url": file_url,
                    "primary": is_primary,
                    "version_type":version_type,
                    "dependencies":dep_urls_api_internal
                }
                urls.append(mod_data)
                # if(first_mod == False):
                    
                # else:
                #     return mod_data
        
    return urls
            # print(f"\tFound {msg} file {filename} at url {file_url}")

setup_logging("logs/apiv2.log")