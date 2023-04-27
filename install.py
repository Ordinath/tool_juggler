import platform
import subprocess
import os


def main():
    os_platform = platform.system()

    print("Installation started...")

    if os_platform == 'Windows':
        install_script = './install.bat'
        os_env = 'windows'
    elif os_platform == 'Linux' or os_platform == 'Darwin':
        install_script = './install.sh'
        os_env = 'mac-linux'
    else:
        print(f"Unsupported platform: {os_platform}")
        exit(1)

    exit_code = subprocess.call(install_script, shell=True)

    if exit_code != 0:
        print(f"Installation script exited with code {exit_code}")
        exit(exit_code)
    else:
        print("Installation complete!")

    # Set the OS_ENV environment variable
    os.environ['OS_ENV'] = os_env
    with open('.env', 'w') as f:
        f.write(f'OS_ENV={os_env}\n')


if __name__ == "__main__":
    main()
