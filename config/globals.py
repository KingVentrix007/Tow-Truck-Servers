
# Temporary variable to prevent multiple servers from running simultaneously
# Currently running multiple servers will lead to EBADF
# See Glitch22/05/2024/1 for more details
server_running = False
def is_server_running():
    return server_running
def set_server_running():
    global server_running
    server_running = True
def set_server_stopped():
    global server_running
    server_running = False

# Global variables for width and height of icons
tab_icon_width = 30
tab_icon_hight = 30

#Default name for servers, if .get("displayName") doesn't work this will be returned
default_server_name = "Unnamed Server"