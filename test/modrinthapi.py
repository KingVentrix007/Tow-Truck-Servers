import modrinth


# def search_mods(query,version_to_find):
#     projects = modrinth.Projects.Search(query)
#     for i in projects.hits:
#         # print() # Prints the name of the first project found
#         for q in i.versions:
#             version = i.getVersion(q)
#             for v in version.gameVersions:
#                 if version_to_find == v:
#                     primaryFile = version.getPrimaryFile()
#                     return(version.getDownload(primaryFile))
#                 # print(v)
#             # if(version in  ):
                
#             # print)
        
def search_mods(query, game_version, mod_loader):
    projects_search = modrinth.Projects.Search(query=query,versions=[game_version],limit=10)
    mods = []
    for hit in projects_search.hits:
        project = modrinth.Projects.ModrinthProject(hit.id)
        if 1:
            # for d in project..__dict__:
            #     print(d)
            # exit()
            mod_versions_hash = project.versions
            for mod_version in mod_versions_hash:
                version = project.getVersion(mod_version)
                # for v in version.__dict__:
                    # print(v)
                # exit()
                if mod_loader in version.loaders:
                    try:
                        print(project.name)
                        # project_t = modrinth.Projects.ModrinthProject(project=project.id) # Get a project from slug/ID
                        # version_t = project_t.getVersion(version)           # Get the version with ID 'aaa111bb'

                        # primaryFile_t = version.getPrimaryFile()  # Returns the hash of the primary file
                        # print(version_t.getDownload(primaryFile_t)) # Returns the download URL of the primary file
                        
                        for dep in version.dependencies:
                            project_id = dep.get("project_id",None)
                            dep_data = modrinth.Projects.ModrinthProject(project_id)
                            print("[",project.name,"]","depends on",dep_data.name)
                            all_versions = dep_data.versions
                            
                            # print(">>",all_versions)
                            for dep_v in all_versions:
                                # dep_v_num = project.getVersion(dep_v)

                                print("dep_v_num","><")
                                print("dep_v = ",dep_v)
                                print("random_version")
                                
                        primary_file = version.getPrimaryFile()
                        icon = project.iconURL
                        user = modrinth.Users.ModrinthUser(version.AuthorID)
                        url = version.getDownload(primary_file)
                        data = {
                            'title': project.name,
                            'icon': icon,
                            'user': user.name,
                            'url': url
                        }
                        # Append mod details to mods list as a dictionary
                        mods.append(data)
                        # print(data,"\n\n--------\n\n")
                    except Exception as e:
                        pass
                    # Break after finding the first matching version
                    break
                else:
                    pass
                    # print(project.name,":",game_version,version.gameVersions,"\n",version.loaders)
    return mods

print(search_mods("Create","1.19.2","fabric"))