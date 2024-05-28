# import modrinth
# import json
# import os
# def load_cache(cache_file='cache.json'):
#     if os.path.exists(cache_file):
#         with open(cache_file, 'r') as file:
#             return json.load(file)
#     return {}

# def save_cache(cache, cache_file='cache.json'):
#     with open(cache_file, 'w') as file:
#         json.dump(cache, file, indent=4)

# def search_mods_v2(query, game_version, mod_loader, callback, canvas, server_data):
#     cache_file = 'cache.json'
#     cache = load_cache(cache_file)
    
#     if 'modrinth' not in cache:
#         cache['modrinth'] = {}
    
#     if mod_loader not in cache['modrinth']:
#         cache['modrinth'][mod_loader] = {}
    
#     if game_version not in cache['modrinth'][mod_loader]:
#         cache['modrinth'][mod_loader][game_version] = {}

#     projects_search = modrinth.Projects.Search(query=query, versions=[game_version])
#     mods = []
#     for hit in projects_search.hits:
#         project = modrinth.Projects.ModrinthProject(hit.id)
#         project_name = project.name
        
#         # Check cache for the project
#         if project_name in cache['modrinth'][mod_loader][game_version]:
#             cached_data = cache['modrinth'][mod_loader][game_version][project_name]
#             cached_data['icon'] = None  # Set icon to None as per your requirement
#             mods.append(cached_data)
#             callback(cached_data, canvas, server_data)
#             continue
        
#         mod_versions_hash = project.versions
#         for mod_version in mod_versions_hash:
#             version = project.getVersion(mod_version)
#             print(project.name, ":", version.gameVersions)
#             if mod_loader in version.loaders and game_version in version.gameVersions:
#                 try:
#                     primary_file = version.getPrimaryFile()
#                     icon = project.iconURL
#                     user = modrinth.Users.ModrinthUser(version.AuthorID)
#                     url = version.getDownload(primary_file)
#                     data = {
#                         'title': project.name,
#                         'icon': icon,
#                         'user': user.name,
#                         'url': url
#                     }
                    
#                     # Cache the new mod data
#                     cache['modrinth'][mod_loader][game_version][project_name] = {
#                         'hash': mod_version,
#                         'id': project.id,
#                         'url': url,
#                         'user': user.name
#                     }
#                     save_cache(cache, cache_file)
                    
#                     mods.append(data)
#                     callback(data, canvas, server_data)
#                 except Exception as e:
#                     pass
#                 # Break after finding the first matching version
#                 break
#             elif mod_loader not in version.loaders:
#                 break
#     return mods
# def search_mods(query, game_version, mod_loader,callback,canvas,server_data):
#     print(game_version,mod_loader)
#     projects_search = modrinth.Projects.Search(query=query,versions=[game_version])
#     mods = []
#     for hit in projects_search.hits:
#         project = modrinth.Projects.ModrinthProject(hit.id)
#         if 1==1:
#             mod_versions_hash = project.versions
#             for mod_version in mod_versions_hash:
#                 version = project.getVersion(mod_version)
#                 print(project.name,":",version.gameVersions)
#                 if mod_loader in version.loaders and game_version in version.gameVersions:
#                     try:
                        
#                         primary_file = version.getPrimaryFile()
                        
#                         icon = project.iconURL
#                         user = modrinth.Users.ModrinthUser(version.AuthorID)
#                         url = version.getDownload(primary_file)
#                         data = {
#                             'title': project.name,
#                             'icon': icon,
#                             'user': user.name,
#                             'url': url
#                         }
#                         # Append mod details to mods list as a dictionary
#                         mods.append(data)
#                         callback(data,canvas,server_data)
#                     except Exception as e:
#                         pass
#                     # Break after finding the first matching version
#                     break
#                 elif(mod_loader not in version.loaders):
#                     break 
#     return mods
