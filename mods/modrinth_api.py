import modrinth

def search_mods(query, game_version, mod_loader,callback,canvas,server_data):
    print(game_version,mod_loader)
    projects_search = modrinth.Projects.Search(query=query,versions=[game_version],limit=10)
    mods = []
    for hit in projects_search.hits:
        project = modrinth.Projects.ModrinthProject(hit.id)
        if 1==1:
            mod_versions_hash = project.versions
            for mod_version in mod_versions_hash:
                version = project.getVersion(mod_version)
                print(project.name,":",version.gameVersions)
                if mod_loader in version.loaders and game_version in version.gameVersions:
                    try:
                        
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
                        callback(data,canvas,server_data)
                    except Exception as e:
                        pass
                    # Break after finding the first matching version
                    break
                elif(mod_loader not in version.loaders):
                    break 
    return mods
