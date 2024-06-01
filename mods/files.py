import zipfile
import json
import re
import os
def decode_file_name(file_name):
    # Remove the path and file extension
    file_name = file_name.split('/')[-1].split('.')[0]
    # Replace non-alphanumeric characters with spaces
    file_name = re.sub(r'[^a-zA-Z0-9]', ' ', file_name)
    # Extract characters up until the first number
    match = re.match(r'^[a-zA-Z\s]*', file_name)
    if match:
        return match.group(0).strip()
    return file_name

def get_mod_name_from_jar(jar_path):
    mod_name = None
    method_used = None
    print()
    try:
        with zipfile.ZipFile(jar_path, 'r') as jar:
            # Check for META-INF/MANIFEST.MF
            try:
                with jar.open('META-INF/MANIFEST.MF') as manifest:
                    for line in manifest:
                        line = line.decode('utf-8').strip()
                        if line.startswith('Implementation-Title:'):
                            mod_name = line.split(':', 1)[1].strip()
                            method_used = 'META-INF/MANIFEST.MF'
                            break
            except KeyError:
                pass
            
            # Check for mcmod.info
            if not mod_name:
                try:
                    with jar.open('mcmod.info') as mcmod_info:
                        info = json.load(mcmod_info)
                        if isinstance(info, list):
                            mod_name = info[0].get('name')
                        elif isinstance(info, dict):
                            mod_name = info.get('name')
                        if mod_name:
                            method_used = 'mcmod.info'
                except KeyError:
                    pass
                except json.JSONDecodeError:
                    pass

            # Check for fabric.mod.json
            if not mod_name:
                try:
                    with jar.open('fabric.mod.json') as fabric_mod_json:
                        info = json.load(fabric_mod_json)
                        mod_name = info.get('name')
                        if mod_name:
                            method_used = 'fabric.mod.json'
                except KeyError:
                    pass
                except json.JSONDecodeError:
                    pass

        # Clean and compare mod name with jar file name
        if mod_name:
            mod_name_clean = re.sub(r'[^a-zA-Z]', '', mod_name).lower()
            file_name_clean = re.split(r'[^a-zA-Z]', jar_path.split('/')[-1])[0].lower()
            if mod_name_clean == file_name_clean:
                return mod_name, method_used, True, None
        jar_file = os.path.basename(jar_path)
        decoded_file_name = decode_file_name(jar_file)
        return mod_name, method_used, False, decoded_file_name
    except Exception as e:
        return None, None, None, None


def mod_already_installed(mod:str,installed_mods:list[str]) -> bool:
    if(os.path.sep in mod):
        checking_mod = os.path.basename(mod)
    else:
        checking_mod = mod
    
    for i_mod in installed_mods:
        if(os.path.sep in i_mod):
            i_mod_current  = os.path.basename(i_mod)
        else:
            i_mod_current = i_mod
        
        decoded_check_mod = decode_file_name(checking_mod)
        decoded_i_mod_current = decode_file_name(i_mod_current)
        print("decoded_i_mod_current",decoded_i_mod_current)
        print("decoded_check_mod",decoded_check_mod)
        if(decoded_check_mod == decoded_i_mod_current):
            return True

    return False
