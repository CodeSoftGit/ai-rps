import os
import sys
import time
import random
import json
import configparser
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import inquirer
from colorama import just_fix_windows_console, Fore, Back, Style
just_fix_windows_console()

def clear():
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")

# Initialize variables
choices = ["r", "p", "s"]
choice_to_num = {"r": 0, "p": 1, "s": 2}
num_to_choice = {0: "r", 1: "p", 2: "s"}

# Initialize the model
model = Sequential(
    [
        Dense(128, input_dim=3, activation="relu"),
        Dense(64, activation="relu"),
        Dense(3, activation="softmax"),
    ]
)

model.compile(
    optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
)

# Helper function to convert a move to a one-hot vector
def move_to_onehot(move):
    onehot = [0, 0, 0]
    onehot[choice_to_num[move]] = 1
    return onehot

# Helper function to get AI's choice
def get_ai_choice(player_history):
    if len(player_history) < 3:
        return random.choice(choices)

    last_moves = np.array([move_to_onehot(player_history[-1])])
    predicted_probs = model.predict(last_moves)
    predicted_move = np.argmax(predicted_probs)

    counter_move = (predicted_move + 1) % 3
    return num_to_choice[counter_move]

# Helper function to decide the winner
def decide_winner(player, ai):
    if player == ai:
        return "It's a tie!"
    elif (
        (player == "r" and ai == "s")
        or (player == "p" and ai == "r")
        or (player == "s" and ai == "p")
    ):
        return Fore.GREEN + "You win!" + Style.RESET_ALL
    else:
        return Fore.RED + "AI wins!" + Style.RESET_ALL

# Get the appdata/roaming folder path
def get_appdata_folder():
    if sys.platform == "win32":
        return os.path.join(os.environ["APPDATA"], "RockPaperScissors")
    else:
        return os.path.join(os.path.expanduser("~"), ".config", "RockPaperScissors")

# Load profile
def load_profile(profile_path):
    if os.path.exists(profile_path):
        with open(profile_path, "r") as file:
            profile = json.load(file)
            return profile["player_history"], profile["ai_history"]
    else:
        return [], []

# Save profile
def save_profile(profile_path, player_history, ai_history):
    os.makedirs(os.path.dirname(profile_path), exist_ok=True)
    with open(profile_path, "w") as file:
        profile = {"player_history": player_history, "ai_history": ai_history}
        json.dump(profile, file)

# Load configuration
def load_config():
    config_path = os.path.join(get_appdata_folder(), "config.ini")
    config = configparser.ConfigParser()
    if not os.path.exists(config_path):
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as configfile:
            configfile.write(
                "[profiles]\ncurrent_profile_path=\ncurrent_profile_name=\n"
            )
    config.read(config_path)
    current_profile_path = config["profiles"]["current_profile_path"]
    current_profile_name = config["profiles"]["current_profile_name"]
    return current_profile_path, current_profile_name

# Save configuration
def save_config(profile_path, profile_name):
    config_path = os.path.join(get_appdata_folder(), "config.ini")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    config = configparser.ConfigParser()
    config["profiles"] = {
        "current_profile_path": profile_path,
        "current_profile_name": profile_name,
    }
    with open(config_path, "w") as configfile:
        config.write(configfile)

# Prompt user to select or create a profile
def select_or_create_profile():
    profile_folder = get_appdata_folder()
    os.makedirs(profile_folder, exist_ok=True)
    profiles = [f for f in os.listdir(profile_folder) if f.endswith(".json")]
    profiles.append("Create new profile")
    questions = [
        inquirer.List(
            "profile", message="Select a profile or create a new one", choices=profiles
        ),
    ]
    answers = inquirer.prompt(questions)

    selected_profile = answers["profile"]
    if selected_profile == "Create new profile":
        new_profile_name = input("Enter the name for the new profile: ") + ".json"
        new_profile_path = os.path.join(profile_folder, new_profile_name)
        save_profile(new_profile_path, [], [])
        selected_profile = new_profile_path
        profile_name = new_profile_name
    else:
        selected_profile = os.path.join(profile_folder, selected_profile)
        profile_name = selected_profile

    save_config(selected_profile, profile_name)
    return selected_profile

# Main game loop
def main():
    clear()
    current_profile_path, current_profile_name = load_config()
    current_profile_path = select_or_create_profile()
    player_history, ai_history = load_profile(current_profile_path)

    print("Welcome to Rock, Paper, Scissors!")

    while True:
        clear()
        questions = [
            inquirer.List(
                "move",
                message="Enter your move",
                choices=["rock (r)", "paper (p)", "scissors (s)", "exit"],
            ),
        ]
        answers = inquirer.prompt(questions)
        player_choice = answers["move"][0]
        clear()
        if player_choice == "e":
            print("Thanks for playing!")
            save_profile(current_profile_path, player_history, ai_history)
            break
        if player_choice not in choices:
            print("Invalid choice. Please try again.")
            continue

        ai_choice = get_ai_choice(player_history)
        print(f"Player chose: {player_choice}")
        print(f"AI chose: {ai_choice}")
        result = decide_winner(player_choice, ai_choice)
        print(result)

        # Update histories
        player_history.append(player_choice)
        ai_history.append(ai_choice)

        # Save profile every time history is updated
        save_profile(current_profile_path, player_history, ai_history)

        if len(player_history) >= 3:
            X_train = np.array([move_to_onehot(move) for move in player_history[:-1]])
            y_train = np.array([choice_to_num[move] for move in player_history[1:]])
            model.fit(X_train, y_train, epochs=10, verbose=0)

        time.sleep(2)

if __name__ == "__main__":
    main()
