import jdk
import os
import re
java_install_dir = "./java/jdk"
def install_java(version):
    if(os.path.exists(java_install_dir) == False):
        os.makedirs(java_install_dir)
    if(type(version) == type('java')):
        jdk.install(version,path=java_install_dir)
    else:
        log("wrong type")
def extract_java_version(java_path):
    java_path = os.path.normpath(java_path)
    # Split the path using directory separator
    parts = java_path.split(os.sep)
    
    # Regex patterns to match version parts
    jdk_pattern = re.compile(r'jdk-(\d+)')
    alt_pattern = re.compile(r'jdk(\d+)')
    
    version = None
    
    for part in parts:
        # Check for jdk- pattern
        match = jdk_pattern.match(part)
        if match:
            version = match.group(1)
            break
        # Check for jdk8u... pattern
        match = alt_pattern.match(part)
        if match:
            version = match.group(1)
            break
    
    return version
def get_directories(path):
    directories = []
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            directories.append(entry)
    return directories

def get_java_versions():
    main_path = java_install_dir
    javas = get_directories(main_path)
    java_versions = []
    for i in javas:
        java_versions.append(extract_java_version(os.path.join(main_path, i)))
    return java_versions,javas

def get_java_dir(version):
    java_versions,java_paths = get_java_versions()
    if(version not in java_versions):
        return None
    index = java_versions.index(version)
    return(java_paths[index])
    