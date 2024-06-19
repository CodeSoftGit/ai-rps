import subprocess
import platform
import sys
import os

# Check Python version
min_version = (3, 8)
max_version = (3, 11, 8)
current_version = sys.version_info

if not (min_version <= current_version <= max_version):
    print(
        f"Python version must be between {'.'.join(map(str, min_version))} and {'.'.join(map(str, max_version))}."
    )
    print(f"Current Python version: {'.'.join(map(str, current_version[:3]))}")
    sys.exit(1)

clear_terminal = True  # Change whether the terminal can be cleared


def clear():
    if clear_terminal:
        if sys.platform == "win32":
            os.system("cls")
        else:
            os.system("clear")


def install(package, upgrade=False):
    if upgrade == False:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    else:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--upgrade", package]
        )


try:
    install("inquirer")
except:
    print(
        "Failed to install a core module of this installation script. Install 'inquirer' manually."
    )
    exit()

import inquirer

install("pip", upgrade=True)

clear()

if __name__ == "__main__":
    if platform.architecture()[0] != "64bit":
        print(
            "Python is not 64bit. Your system may be 32bit, or you downloaded the 32bit version of Python."
        )
        quit()

    if sys.platform not in {"win32", "darwin", "linux"}:
        print(
            "Your OS appears to not be supported. Because this may be incorrect, you can choose your OS below."
        )
    if sys.platform == "win32":
        os_choices = ["Windows Native", "Windows WSL2"]
    elif sys.platform == "darwin":
        os_choices = ["MacOS", "Linux"]
    elif sys.platform == "linux":
        os_choices = ["MacOS", "Linux", "Windows WSL2"]
    else:
        os_choices = [
            "Windows Native",
            "Windows WSL2",
            "MacOS",
            "Linux",
            "My OS isn't here",
        ]  # fallback for unknown platforms

    questions = [
        inquirer.List(
            "os",
            message="What is your OS?",
            choices=os_choices,
        ),
    ]
    answers = inquirer.prompt(questions)["os"]

    clear()

    if answers == "Windows Native":
        print("These TensorFlow packages run on version 2.10.")
        tf_choices = [
            "TensorFlow-cpu [No GPU Support]",
            "TensorFlow [CUDA 3.5 required]",
        ]
    if answers == "Windows WSL2":
        print("GPU Support requires Windows 10 21H2 or later.")
        tf_choices = [
            "TensorFlow-cpu [No GPU Support]",
            "TensorFlow [CUDA 3.5 required]",
        ]
    if answers == "MacOS":
        print(
            "MacOS has no GPU support. Some additional packages may not work on Apple Silicon (M1 and later)"
        )
        tf_choices = ["TensorFlow-cpu [No GPU Support]"]
    if answers == "Linux":
        print(
            "These TensorFlow versions are maintained by Amazon AWS. They also install the tensorflow-cpu-aws package."
        )
        tf_choices = [
            "TensorFlow-cpu [No GPU Support]",
            "TensorFlow [CUDA 3.5 required]",
        ]
    if answers == "My OS isn't here":
        exit()
    questions = [
        inquirer.List(
            "package",
            choices=tf_choices,
        ),
    ]
    answers = inquirer.prompt(questions)["package"]

    clear()

    if answers == "TensorFlow-cpu [No GPU Support]":
        install("tensorflow-cpu<2.11")
    elif answers == "TensorFlow [CUDA 3.5 required]":
        install("tensorflow<2.11")
    install("numpy<2")
else:
    raise Exception("Script must be run as main")
