# VFS Shell: Virtual File System Simulator

## 📝 Project Description
This project is a Command Line Interface (CLI) tool that simulates a Unix-like file system entirely in RAM. It allows users to perform file operations such as creating directories, writing files, and managing permissions without interacting with the physical hard drive. 

The project is designed to demonstrate key software construction principles, including:
* **Tree/Composite Pattern:** For representing the hierarchical structure of files and folders.
* **Command Pattern:** To decouple command logic from the shell interface and support operation history.
* **Access Control & Quotas:** Implementation of octal permissions and disk size limitations.

---

## 🛠 Tech Stack
* **Language:** Python 3.11+
* **Dependency Management:** [Poetry](https://python-poetry.org/)
* **Linting & Formatting:** [Ruff](https://github.com/astral-sh/ruff)
* **Terminal Styling:** [Rich](https://github.com/Textualize/rich)

---

## 📥 Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/xanaxhol1c/vfs-shell-python.git

    cd vfs-shell-python
    ```

2.  **Install dependencies using Poetry:**
    *If you don't have Poetry installed, follow the [official guide](https://python-poetry.org/docs/#installation).*
    ```bash
    poetry install
    ```

3. **Linting & Quality Control:**
    We use Ruff to maintain high code quality and adhere to PEP8 standards. To run the static analysis:
    ```
    poetry run ruff check .
    ```

## 🚀 How to Run

### Interactive Mode
To start the virtual file system shell:
```bash
poetry run python main.py
```

### Run Commands from Script
You can execute commands from a script file:
```bash
poetry run python main.py script.sh
```

## 💻 Example Usage
```bash
mkfs 1024
mkdir /home
mkdir /home/user
touch /home/user/log.txt "Log started"
chmod 755 /home/user/log.txt
ls /home/user
cat /home/user/log.txt
```