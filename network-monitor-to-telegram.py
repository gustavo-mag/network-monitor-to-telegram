import importlib
import netifaces
from prettytable import PrettyTable
import requests
import logging
import datetime

TELEGRAM_BOT_TOKEN = 'YOUR_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID'

# Check for required dependencies
dependencies = ['netifaces', 'prettytable', 'requests']
missing_dependencies = []

for dependency in dependencies:
    try:
        importlib.import_module(dependency)
    except ImportError:
        missing_dependencies.append(dependency)

if missing_dependencies:
    print("The following dependencies are missing:")
    for dependency in missing_dependencies:
        print(dependency)
    install = input("Do you want to install the missing dependencies? (yes/no): ")
    if install.lower() == 'yes':
        import subprocess
        subprocess.check_call(['pip', 'install'] + missing_dependencies)
    else:
        print("Aborting script execution.")
        exit()

# Configure logging
logging.basicConfig(filename='network_monitor.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

def get_interfaces_with_private_ip():
    interfaces = netifaces.interfaces()
    interfaces_with_private_ip = []

    for interface in interfaces:
        private_ip = get_private_ip(interface)
        if private_ip:
            interfaces_with_private_ip.append(interface)

    return interfaces_with_private_ip

def get_private_ip(interface):
    addresses = netifaces.ifaddresses(interface).get(netifaces.AF_INET)
    if addresses:
        return addresses[0]["addr"]
    return ""

def get_main_ip():
    default_gateway = netifaces.gateways().get(netifaces.AF_INET)
    if default_gateway and default_gateway[0][1]:
        return default_gateway[0][0]
    return ""

def get_connection_type():
    default_gateway = netifaces.gateways().get(netifaces.AF_INET)
    if default_gateway and default_gateway[0][1]:
        return "WAN"
    return "LAN"

def print_network_info():
    interfaces = get_interfaces_with_private_ip()
    table = PrettyTable(["Interface", "Private IP"])

    for interface in interfaces:
        private_ip = get_private_ip(interface)
        table.add_row([interface, private_ip])

    print(table)
    return table.get_string()

def format_network_info():
    interfaces = get_interfaces_with_private_ip()
    connection_type = get_connection_type()
    main_ip = get_main_ip()
    info = "🗓️ [ {} ] | [ {} ]\n\n".format(
        datetime.datetime.now().strftime("%H:%M:%S"), 
        datetime.datetime.now().strftime("%Y.%m.%d")
    )
    info += "💻 <b>Hostname:</b> {}\n\n".format(get_hostname())
    info += "🟢 <b>Connection Type:</b> {}\n".format(connection_type)
    info += "ℹ️ <b>Main IP:</b> {}\n\n".format(main_ip)

    for interface in interfaces:
        private_ip = get_private_ip(interface)
        info += "⚙️ <b>Interface:</b> {}\n📡 <b>IP:</b> {}\n\n".format(interface, private_ip)

    return info

def get_hostname():
    import socket
    return socket.gethostname()

def send_message_to_telegram(text):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'HTML'
    }
    response = requests.post(url, data=data)
    return response.json()

network_info = print_network_info()
formatted_info = format_network_info()

# Sending network information to Telegram
message = "<b>Network Information:</b>\n\n"
message += formatted_info

response = send_message_to_telegram(message)

if response['ok']:
    logging.info('Network information sent to Telegram!')
else:
    logging.error('Failed to send network information to Telegram.')