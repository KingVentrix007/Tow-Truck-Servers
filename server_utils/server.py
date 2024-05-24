from mods.forge import run_forge_server
def run_server(server_data,output,on_finish):
    modloader = server_data.get("modloader","null")
    if modloader == "null":
        return -1
    if(modloader == "forge"):
        return run_forge_server(server_data,output,on_finish)
    if(modloader == "fabric"):
        return -2    
