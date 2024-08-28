import os
import json
import subprocess
import argparse
import platform
import keyboard
import sys

DIRECTORY = os.path.dirname(os.path.realpath(__file__))

def read_prompt():
    PROMPT_FILE = f"{DIRECTORY}/new_prompt.txt"
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, encoding="utf-8") as f:
            prompt = f.read()
    else:
        prompt = input("new_prompt.txt does not exist, enter your prompt here to be saved to prompt.txt -> ")
        with open(PROMPT_FILE, 'w', encoding="utf-8") as f:
            f.write(prompt)
    return prompt

def open_console_window(name: str, account_token: str, prompt: str, out_folder: str, delay: float, maximum: int, venv: bool = False):
    name = name.split("@")[0]
    if platform.system() == 'Linux':
        spawn = ['xfce4-terminal', '--hold', '-T', f'sucorn API {name}', '-e']
    else:
        raise OSError("This script is intended for Linux environments only")

    # BUG: venv not working, thank goodness sub.py only needs 1 requirement, maybe put in sh shell?
    # After 1 hour of holy hell, I figured that prompt assumes no double quotation marks, if you have them, your screwed i guess
    command = f'sudo -u {os.getenv("SUDO_USER")} {f'source "{DIRECTORY}/../../venv/bin/activate" && ' if venv else ""}python "{DIRECTORY}/sub.py" {name} "{account_token}" "{prompt}" "{out_folder}" {delay} {maximum}'
    # Drop sudo [f'su $SUDO_USER && {command}'] .replace("'", "'\\''")
    # holy_hell = f'{command.replace('"', '\'').replace('\'', '\\\'')}'
    # input(holy_hell)
    process = subprocess.Popen(
        spawn + [command.replace("'", "\\'")],
    )

def organize_windows(dummy):
    columns = 5
    window_width = 450
    window_height = 240

    result = subprocess.run(['wmctrl', '-l'], stdout=subprocess.PIPE, check=True)
    windows = [line for line in result.stdout.decode().split('\n') if 'sucorn API' in line]

    for i, window in enumerate(windows):
        window_id = window.split()[0]

        row = i // columns
        col = i % columns

        x_position = col * (window_width - 10)
        y_position = row * (window_height + 2)

        subprocess.run(['wmctrl', '-ir', window_id, '-e', f'0,{x_position},{y_position},{window_width},{window_height}'], check=True)

def terminate():
    result = subprocess.run(['wmctrl', '-l'], stdout=subprocess.PIPE, check=True)
    windows = [line for line in result.stdout.decode().split('\n') if 'sucorn API' in line]

    for window in windows:
        window_id = window.split()[0]
        subprocess.run(['wmctrl', '-ic', window_id], check=True)
    print("Terminated")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='kitty farm')
    parser.add_argument('folder', type=str, help='folder name, ./images/your_name_here')
    parser.add_argument('-d', '--delay', type=float, default=0,
        help='Delay time in seconds (default is 0)')
    parser.add_argument('-m', '--max', type=int, default=80,
        help='Maximum number of failed redirects before killing process (default is 80)')
    parser.add_argument('-t', '--test', action='store_true',
        help='Runs the program with a testing cookie file named test_cookies.json (default is False)')
    parser.add_argument('-l', '--log', action='store_true',
        help='Logs all errors to /logs')
    parser.add_argument('-v', '--venv', action='store_true',
        help='Use venv located in top level directory')
    args = parser.parse_args()

    sudo_user = os.getenv("SUDO_USER")
    if not sudo_user:
        print("You need to be the superuser to use this (blame keyboard module)")
        quit()

    out_path = f"{DIRECTORY}/../../images/{args.folder}"
    if not os.path.exists(out_path):
        os.mkdir(out_path)
        os.system(f"sudo chown {sudo_user} -R {out_path}")
        prompt = read_prompt()
        with open(f"{out_path}/prompt.txt", "w", encoding="utf-8") as p_file:
            p_file.write(prompt)
        os.system(f"sudo chown {sudo_user} {out_path}/prompt.txt")  # unsure why recursive chown doesnt work here
    else:
        with open(f"{out_path}/prompt.txt", "r", encoding="utf-8") as p_file:
            prompt = p_file.read()

    for subfolder in ['positive', 'neutral', 'negative']:
        subfolder_path = f"{out_path}/{subfolder}"
        if not os.path.exists(subfolder_path):
            os.makedirs(subfolder_path)
            print(f"Created folder as it does not exist: {subfolder_path}")

    COOKIE_FILE = f'{DIRECTORY}/test_cookies.json' if args.test else f'{DIRECTORY}/cookies.json'
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, encoding="utf-8") as f:
            cookies = json.load(f)
    else:
        print("cookies.json does not exist, quitting since no cookies were found.")
        sys.exit(1)

    prompt = read_prompt()
    if len(prompt) > 480:
        if input("Prompt is over 480, continue? (Y or N) ").lower().strip() == "n":
            sys.exit(1)
    elif len(cookies.items()):
        prompt = prompt.replace('\n', ' ').strip()
        for account, token in cookies.items():
            open_console_window(account, token, prompt, out_path, args.delay, args.max, venv=args.venv)
            open_console_window(account, token, prompt, out_path, args.delay, args.max, venv=args.venv)

        print(f"Prompt: {prompt}")
        keyboard.on_press_key('ins', organize_windows)
        keyboard.wait('end')

        terminate()
