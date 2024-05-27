import os
import re

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

if __name__ == "__main__":
    java_paths = [
        "java/jdk/jdk-11.0.23+9",
        "java/jdk/jdk8u412-b08"
    ]
    for java_path in java_paths:
        version = extract_java_version(java_path)
        print(f"Java version from '{java_path}': {version}")
