import requests
import time
import os
import json
import urllib.request
max_recursion = 10
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

def search_mods(query,version,modloader):
    results = []
    found_mods = []
    offest = 0
    count = 0
    rec_count = 0
    while count < 10 and rec_count < max_recursion:
        try:
            response = modrinth_search(query,10,offest)
            if response.status_code == 200:
                data = response.json()
                print("Got hit")
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
                rec_count+=1
                
            else:
                print("Search failed: %s" % response.status_code)
        except requests.exceptions.RequestException as e:
            print("Error: %s" % e)
    return results
def find_correct_versions(results, version):
    correct_items = []
    print(results[0]['dependencies'])
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


def get_version_data(version):
    if(version == None):
        return None
    url = f'https://api.modrinth.com/v2/version/{version}'
    data = requests.get(url).json()
    return data
def get_dependencies_url(version_id):
    dep_data = get_version_data(version_id)
    if(dep_data != None):
        # print("dep_data=",dep_data)
        dep_files = dep_data['files']
        for dep_file in dep_files:
            if(dep_file['primary'] == True):
                dep_url = dep_file["url"]
                dep_id = dep_data["project_id"]
                print(dep_id)
                # print()
                return dep_url,dep_id
    print("No dependencies")
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
            print(dependency["dependency_type"])
            dep_url,dep_id = get_dependencies_url(dependency["version_id"])
            if(dep_url == None and dependency["dependency_type"] == "required"):
                dep_error = True
            if(dep_url != None):
                # dep_urls_api_internal.append(dep_url)
                dep = {
                    "url":dep_url,
                    "id":dep_id
                }
                dep_urls_api_internal.append(dep)
                print("dep_url == " + str(dep_url))
            else:
                print("continue")
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