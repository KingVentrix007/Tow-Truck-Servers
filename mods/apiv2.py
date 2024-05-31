import requests
import time
import os
import json
import urllib.request
from config.debug import log
max_recursion = 10

number_of_requests_left = -1
total_requests = -1

def limit_update(response):
    global number_of_requests_left
    global total_requests
    x_rate_limit = int(response.headers.get("x-ratelimit-limit",0))
    x_ratelimit_remaining = int(response.headers.get("x-ratelimit-remaining",0))
    number_of_requests_left = x_ratelimit_remaining
    total_requests = x_rate_limit

def in_limit():
    global number_of_requests_left
    if(number_of_requests_left <= 2 and number_of_requests_left != -1):
        return False
    return number_of_requests_left
def isServerSide(mod_data) -> bool:
            '''
            Check if the project is server side.
            '''
            if mod_data['server_side'] == 'optional' or mod_data['server_side'] == 'required':
                return True
            else:
                return False
def modrinth_search(query,limit,offest):
    if(in_limit() == False):
        return None
    url = "https://api.modrinth.com/v2/search"
    params = {
        'query': query,
        'limit':limit,
        "offset":offest
    }
    try:
        response = requests.get(url, params=params)
        limit_update(response)
        return response
    except requests.exceptions.RequestException as e:
        log("Error: %s" % e)
        return None

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
                # log(data["hits"][0])
                # log(data['total_hits'],data["offset"])
                total_hits = data['total_hits']
                for hit in data["hits"]:
                    hits+=1
                    if(hits >= total_hits):
                        return results,offset_int
                    supported_game_versions = hit["versions"]
                    log(hit["display_categories"])
                    if(version not in supported_game_versions or modloader not in hit["display_categories"]):
                        log("Skipped mod",hit["title"])
                        continue
                    elif(hit['project_id'] not in found_mods and isServerSide(hit) == True):

                        found_mods.append(hit['project_id'])
                        results.append(hit)
                        count+=1
                        # log(count)
                    # else:
                    #     # log("Got duplicate mods",hit["title"])
                    if(count == 20):
                        break
                offset_int+=10
                # log("offset_int == %d" % offset_int)
            else:
                log("Search failed: %s" % response.status_code)
        except requests.exceptions.RequestException as e:
            log("Error: %s" % e)
    return results,offset_int

def find_correct_versions(results, version):
    correct_items = []
    log(results[0]['dependencies'])
    for item in results:
        if version in item['game_versions']:
            correct_items.append(item)
    return correct_items
def search_project_by_version_and_modloader(project_id, modloader):
    if(in_limit() == False):
        return None
    url = f"https://api.modrinth.com/v2/project/{project_id}/version"
    params = {
        "modloader": modloader,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        limit_update(response)
        return response.json()
    else:
        return None

def id_to_name(project_id):
    if(in_limit() == False):
        return None
    try:
        log(project_id)
        url = f"https://api.modrinth.com/v2/project/{project_id}"
        data = requests.get(url)
        limit_update(data)
        data = data.json()
        return data["title"]
    except Exception as e:
        return None
def get_project_data_id(project_id):
    if(in_limit() == False):
        return None
    log(project_id)
    url = f"https://api.modrinth.com/v2/project/{project_id}"
    data = requests.get(url)
    limit_update(data)
    data = data.json()
    return data
def get_version_data(version):
    if(in_limit() == False):
        return None
    if(version == None):
        return None
    url = f'https://api.modrinth.com/v2/version/{version}'
    data = requests.get(url)
    limit_update(data)
    data = data.json()
    return data

def get_dependencies_url(dependency,version,loader):
    version_id = dependency["version_id"]
    dep_project_id = dependency["project_id"]
    if(version_id != None):
        dep_data = get_version_data(version_id)
        if(dep_data != None):
            # log("dep_data=",dep_data)
            print( dep_data)
            dep_files = dep_data['files']
            for dep_file in dep_files:
                if(dep_file['primary'] == True):
                    dep_url = dep_file["url"]
                    dep_id = dep_data["project_id"]
                    log(dep_id,dep_id)
                    # log()
                    return dep_url,dep_id
        log("No dependencies")
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
            # log("ver == ",ver)
    return None,None
            # log(dep_file)
        # log("\n================================\n")
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
            log(dependency["dependency_type"])
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
                log("dep_url == " + str(dep_url))
            else:
                log("continue")
        # log(dependencies)
        # log("File: "+version_name,"status: "+str(status),"date: "+date)
        if(dep_error == False):
            for file in file_data:
                filename = file["filename"]
                file_url = file["url"]
                is_primary = file["primary"]
                # log("dep_urls_api_internal=",dep_urls_api_internal)
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
            # log(f"\tFound {msg} file {filename} at url {file_url}")

# setup_logging("logs/apiv2.log")


def get_mod_icon(mod_name):
    response_int = modrinth_search(mod_name,20,0)
    if response_int.status_code == 200:

        data_int = response_int.json()
        # print(data_int)
        num_hits = data_int['total_hits']
        for hit in data_int["hits"]:
            name = hit["title"].lower()
            name_to_find = mod_name.lower()
            if(name_to_find == name):
                return hit["icon_url"]
        number_of_loops = int(int(num_hits)/20)


        