from colorama import Fore, Style, init
from subprocess import run, DEVNULL
import threading
import requests
import argparse
import signal
import shutil
import random
import time
import sys
import os

# ================================================================================ #
#      _______                  _            _    ____        _                    #
#     |__   __|                (_)          | |  / __ \      (_)                   #
#        | |_ __ __ _ _ __  ___ _  ___ _ __ | |_| |  | |_ __  _  ___  _ __         #
#        | | '__/ _` | '_ \/ __| |/ _ \ '_ \| __| |  | | '_ \| |/ _ \| '_ \        #
#        | | | | (_| | | | \__ \ |  __/ | | | |_| |__| | | | | | (_) | | | |       #
#        |_|_|  \__,_|_| |_|___/_|\___|_| |_|\__|\____/|_| |_|_|\___/|_| |_|       #
#                https://github.com/schyzoware/TransientOnion                      #
#                                                                                  #
#                  temporary & quick .onion link generator                         #
# ================================================================================ #

#----------------#
#--- Start-up ---#
#----------------#

init() # because this app totally supports Windows.
parser = argparse.ArgumentParser(description='Example usage: "./TransientOnion -in 8080 -out 80 -addr 127.0.0.1" --> 8080 is SOURCE,')
parser.add_argument("--addr", type=str, help="Source IP Address (127.0.0.1 default)", default="127.0.0.1")
parser.add_argument("--in-port", type=int, help="Source Port (80 default)", default=80)
parser.add_argument("--out-port", type=int, help="Output Port (80 default)", default=80)
parser.add_argument("--tor-config", type=str, help="Tor config file (/etc/tor/torrc default)", default="/etc/tor/torrc")
parser.add_argument("--instant", help="Remove 0.1s timer inbetween outputs", action="store_true")
parser.add_argument("--link-only", help="Print only the pure link", action="store_true")
parser.add_argument("--auto-kill", type=int, help="Kill the tunnel after X seconds (default 0 = infinity)", default=0)

#------------------------#
#--- Global Variables ---#
#------------------------#

# main variables
version = "1.0.1"
unique_id = random.randint(10000, 99999)

# variables for function output()
job = "job"
info = "info"
warn = "warn"
error = "error"
notif = "notif"
success = "success"
connection = "connection"

args = parser.parse_args()

# tor config template
torrc_tunnel_conf = f"""
HiddenServiceDir /var/lib/tor/TransientOnion_Temp_Tunnel_{unique_id}/
HiddenServicePort {args.out_port} {args.addr}:{args.in_port}
"""


#-----------------------#
#--- Basic Functions ---#
#-----------------------#

def output(msg_type, value, one_line=None):
    """Output text/status in terminal with colors and additional information."""

    text_clr = Fore.LIGHTWHITE_EX

    COLOR_MAP = {
        info: Fore.LIGHTBLACK_EX,
        warn: Fore.YELLOW,
        job: Fore.LIGHTBLUE_EX,
        error: Fore.RED,
        notif: Fore.LIGHTYELLOW_EX,
        success: Fore.LIGHTGREEN_EX,
        connection: Fore.LIGHTMAGENTA_EX
    }

    text_clr = COLOR_MAP.get(msg_type)

    # Let's ignore this.
    # I added this, just to make it more readable/visible.
    # Can be turned off with --instant argument.
    if not args.instant:
        time.sleep(0.1)

    if not args.link_only:
        if one_line != None:
            print(f"\r{Fore.LIGHTCYAN_EX}[TransientOnion]: {text_clr}[{msg_type.upper()}]: {value}{Style.RESET_ALL}", end="")
        else:
            print(f"{Fore.LIGHTCYAN_EX}[TransientOnion]: {text_clr}[{msg_type.upper()}]: {value}{Style.RESET_ALL}")
    else:
        pass

def github_version_check():
    """Check GitHub for newer releases of TransientOnion"""

    github_version = "https://api.github.com/repos/schyzoware/TransientOnion/releases/latest"
    gv_request = requests.get(github_version)
    gv_data = gv_request.json()

    gv_latest = gv_data["tag_name"].replace("v", "")

    if gv_latest != version:
        output(warn, f'New version of TransientOnion available: {gv_latest}')
    else:
        output(info, f'You are running the newest release of TransientOnion')

def restart_tor(): 
    """Restart TOR service with systemctl"""

    # subprocess.run ==> run
    run(["sudo", "systemctl", "restart", "tor"])

def torrc_add_tunnel():
    """Create a temporary tunnel in (most likely) /etc/tor/torrc using unique_id"""

    output(job, 'Adding temporary tunnel connection...')
    # subprocess.run ==> run
    run(
        ["sudo", "tee", "-a", args.tor_config],
        input=torrc_tunnel_conf.encode(),
        stdout=DEVNULL,
        stderr=DEVNULL
    )
    output(success, f'Created a tunnel in {args.tor_config}')
    restart_tor()

def torrc_remove_tunnel():
    """Remove a temporary tunnel in (most likely) /etc/tor/torrc"""

    output(job, 'Removing temporary tunnel connection...')
    with open(args.tor_config, "r") as f:
        content = f.read()

    new_content = content.replace(torrc_tunnel_conf, "")

    # subprocess.run ==> run
    run(
        ["sudo", "tee", args.tor_config],
        input=new_content.encode(),
        stdout=DEVNULL,
        stderr=DEVNULL
    )

    # subprocess.run ==> run
    run(["sudo", "rm", "-r", f"/var/lib/tor/TransientOnion_Temp_Tunnel_{unique_id}/"])

    restart_tor()
    output(success, 'Tunnel closed!')

def get_tunnel_address():
    """Get temporary tunnel's address (hostname) in /var/lib/tor/(tunnel name)"""

    # subprocess.run ==> run
    result = run(
        ["sudo", "-n", "cat", f"/var/lib/tor/TransientOnion_Temp_Tunnel_{unique_id}/hostname"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return None

    if result != None:
        return result.stdout.strip()

def discard_old_tunnels():
    """Delete old/unused tunnels in /var/lib/tor/"""

    result = run(
        ["sudo", "ls", "/var/lib/tor"],
        capture_output=True,
        text=True
    )

    unused_count = 0

    for item in result.stdout.splitlines():
        if item.startswith('TransientOnion_Temp_Tunnel_'):
            item_path = f'/var/lib/tor/{item}'
            run(["sudo", "rm", "-r", item_path])
            unused_count += 1
    
    if unused_count > 0:
        output(info, f'Discarded {unused_count} unused tunnel(s).')

def handler(sig, frame):
    """CTRL+C (Interupt/Kill) Detection"""

    output(warn, "CTRL+C Detected, ending the tunnel...")
    torrc_remove_tunnel()
    sys.exit()


#-------------------#
#--- Application ---#
#-------------------#

if not args.link_only:
    print(f"{Fore.LIGHTBLACK_EX}--- TransientOnion ver. {version} ---{Style.RESET_ALL}")
github_version_check()

output(info, f'Starting with unique id "{unique_id}"')

if os.geteuid() == 0:
    output(info, 'Running as root (recommended)')
else:
    output(warn, 'Not running as root! Script may ask for sudo permission.')

if shutil.which('tor'): # check if tor is installed
    output(info, 'TOR is installed.')
else:
    output(error, 'TOR not detected, did you install it?')
    sys.exit()

discard_old_tunnels()

output(job, f'Preparing to edit {args.tor_config}')

torrc_add_tunnel()

wait_time = 0
while get_tunnel_address() is None:
    time.sleep(0.3) # Little delay so the console doesn't get spammed
    wait_time += 0.3
    wait_time = round(wait_time, 1) # So it doesn't return some wierd number like 4.4999999999999

    output(info, f"Waiting for TOR... (Time spent {wait_time}s)\n", one_line=True)
else:
    # Added few exceptions for widely used protocols like HTTP.

    address_prefix = ""

    PORT_PROTOCOL_MAP = {
        80: "http://",
        8080: "http://", # alternative
        443: "https://",
        8443: "https://", # alternative
        21: "ftp://",
        990: "ftps://",
        22: "ssh://",
        23: "telnet://",
        25: "smtp://",
        110: "pop3://",
        143: "imap://",
        389: "ldap://",
        445: "smb://",
        3389: "rdp://",
    }
    # And let's add 25565 next, right?

    address_prefix = PORT_PROTOCOL_MAP.get(args.out_port)

    if address_prefix != "":
        output(connection, f"Forwarding {args.addr}:{args.in_port} ──> {address_prefix}{get_tunnel_address()}")
    else:
        output(connection, f"Forwarding {args.addr}:{args.in_port} ──> {get_tunnel_address()}:{args.out_port}")
    
    if args.link_only:
        print(get_tunnel_address())

# Auto-kill tunnel after X seconds with --auto-kill argument
if args.auto_kill > 0:
    def autokill_countdown():
        output(info, f'Starting the countdown of {args.auto_kill} seconds.')

        try:
            time.sleep(args.auto_kill)
            output(warn, f"Countdown of {args.auto_kill} seconds ran out, killing the tunnel.")
            torrc_remove_tunnel()
        finally:
            os._exit(0)

    t = threading.Thread(target=autokill_countdown)
    t.start()

# When user interupted the program (CTRL+C) revert the temporary changes in the tor config file.
signal.signal(signal.SIGINT, handler)
while True: # Don't auto-end the program
    pass
