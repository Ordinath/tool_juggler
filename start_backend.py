import platform
import subprocess


def main():
    os_platform = platform.system()
    command = ''

    if os_platform == 'Windows':
        command = 'cd backend && venv\\Scripts\\activate && python3.10 app.py'
    elif os_platform == 'Linux' or os_platform == 'Darwin':
        command = 'cd backend && source venv/bin/activate && python3.10 app.py'
    else:
        print(f"Unsupported platform: {os_platform}")
        exit(1)

    exit_code = subprocess.call(command, shell=True)

    if exit_code != 0:
        print(f"Backend process exited with code {exit_code}")
        exit(exit_code)


if __name__ == "__main__":
    main()
