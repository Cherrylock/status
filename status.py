import os
import time
import requests
import json

CONFIG_FILE = "config.json"
MAX_STATUSES = 10

ascii_art = """


 ▄████▄   ██░ ██ ▓█████  ██▀███   ██▀███ ▓██   ██▓   ▄▄▄█████▓ ▒█████   ▒█████   ██▓      ██████ 
▒██▀ ▀█  ▓██░ ██▒▓█   ▀ ▓██ ▒ ██▒▓██ ▒ ██▒▒██  ██▒   ▓  ██▒ ▓▒▒██▒  ██▒▒██▒  ██▒▓██▒    ▒██    ▒ 
▒▓█    ▄ ▒██▀▀██░▒███   ▓██ ░▄█ ▒▓██ ░▄█ ▒ ▒██ ██░   ▒ ▓██░ ▒░▒██░  ██▒▒██░  ██▒▒██░    ░ ▓██▄   
▒▓▓▄ ▄██▒░▓█ ░██ ▒▓█  ▄ ▒██▀▀█▄  ▒██▀▀█▄   ░ ▐██▓░   ░ ▓██▓ ░ ▒██   ██░▒██   ██░▒██░      ▒   ██▒
▒ ▓███▀ ░░▓█▒░██▓░▒████▒░██▓ ▒██▒░██▓ ▒██▒ ░ ██▒▓░     ▒██▒ ░ ░ ████▓▒░░ ████▓▒░░██████▒▒██████▒▒
░ ░▒ ▒  ░ ▒ ░░▒░▒░░ ▒░ ░░ ▒▓ ░▒▓░░ ▒▓ ░▒▓░  ██▒▒▒      ▒ ░░   ░ ▒░▒░▒░ ░ ▒░▒░▒░ ░ ▒░▓  ░▒ ▒▓▒ ▒ ░
  ░  ▒    ▒ ░▒░ ░ ░ ░  ░  ░▒ ░ ▒░  ░▒ ░ ▒░▓██ ░▒░        ░      ░ ▒ ▒░   ░ ▒ ▒░ ░ ░ ▒  ░░ ░▒  ░ ░
░         ░  ░░ ░   ░     ░░   ░   ░░   ░ ▒ ▒ ░░       ░      ░ ░ ░ ▒  ░ ░ ░ ▒    ░ ░   ░  ░  ░  
░ ░       ░  ░  ░   ░  ░   ░        ░     ░ ░                     ░ ░      ░ ░      ░  ░      ░  
░                                         ░ ░                                                    

    """

print(ascii_art)

def save_config_to_json(token, statuses, delay):
    config = {"DISCORD_TOKEN": token, "STATUSES": statuses, "DELAY": delay}
    with open(CONFIG_FILE, "w") as json_file:
        json.dump(config, json_file, indent=4)

def load_config_from_json():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as json_file:
            config = json.load(json_file)
            return config.get("DISCORD_TOKEN"), config.get("STATUSES", []), config.get("DELAY", 0.7)
    return None, [], 0.7

def cycle_token_status(token, statuses, delay=0.7):
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    while True:
        for status in statuses:
            response = requests.patch(
                "https://discord.com/api/v9/users/@me/settings",
                headers=headers,
                json=status
            )
            if response.status_code == 200:
                print(f"Status updated to: {status['custom_status']['text']}")
            else:
                print(f"Failed to update status. Status code: {response.status_code}, Response: {response.text}")
                if response.status_code == 429:
                    retry_after = response.json().get('retry_after', delay)
                    print(f"Rate limited. Retrying after {retry_after} seconds.")
                    time.sleep(retry_after)
                    continue
            time.sleep(delay)

def get_user_input(prompt, allow_empty=False):
    while True:
        user_input = input(prompt).strip()
        if user_input or allow_empty:
            return user_input

def configure_settings():
    token = get_user_input("Please enter your Discord token: ")
    
    statuses = []
    while len(statuses) < MAX_STATUSES:
        text = get_user_input("Please enter your status text: ")
        emoji = get_user_input("Please enter your status emoji (or press enter for none): ", allow_empty=True)
        if not emoji:
            emoji = None
        statuses.append({"custom_status": {"text": text, "emoji_name": emoji}})
        if len(statuses) < MAX_STATUSES:
            add_more = get_user_input("Do you want to add another status? (y/n): ").lower()
            if add_more != 'y':
                break

    delay = float(get_user_input("Please enter the delay between status updates (in seconds): "))
    
    return token, statuses, delay

if __name__ == "__main__":
    token, statuses, delay = load_config_from_json()
    
    if not token:
        token, statuses, delay = configure_settings()
    
    while True:
        save_choice = get_user_input("Do you want to save this token, statuses, and delay for future use? (y/n): ").lower()
        if save_choice == 'y':
            save_config_to_json(token, statuses, delay)
            break
        else:
            print("What would you like to change?")
            print("1. Token")
            print("2. Statuses (THIS RESETS ALL OF THE STATUSES YOU'VE SAVED)")
            print("3. Delay")
            choice = get_user_input("Please enter the number of your choice: ")
            
            if choice == '1':
                token = get_user_input("Please enter your Discord token: ")
            elif choice == '2':
                statuses = []
                while len(statuses) < MAX_STATUSES:
                    text = get_user_input("Please enter your status text: ")
                    emoji = get_user_input("Please enter your status emoji (or press enter for none): ", allow_empty=True)
                    if not emoji:
                        emoji = None
                    statuses.append({"custom_status": {"text": text, "emoji_name": emoji}})
                    if len(statuses) < MAX_STATUSES:
                        add_more = get_user_input("Do you want to add another status? (y/n): ").lower()
                        if add_more != 'y':
                            break
            elif choice == '3':
                delay = float(get_user_input("Please enter the delay between status updates (in seconds): "))
    
    if token and statuses:
        cycle_token_status(token, statuses, delay=delay)
    else:
        print("No Discord token or statuses provided.")
