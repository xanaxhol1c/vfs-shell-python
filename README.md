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

4. **Run Tests:**
    Execute the test suite with pytest:
    ```
    poetry run pytest tests/ -v
    ```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

This project includes an automated **GitHub Actions CI/CD pipeline** that runs on every push to `main` and on Pull Requests. The pipeline ensures code quality and reliability by running:

**Pipeline Triggers:**
- ✅ Every push to the `main` branch
- ✅ Every Pull Request to `main`

**Pipeline Steps:**
1. **Environment Setup** - Configures Python 3.11 runtime
2. **Dependency Installation** - Uses Poetry to install all dependencies
3. **Linting** - Runs Ruff to check PEP8 compliance and code quality
4. **Unit Tests** - Executes pytest with verbose output
5. **Coverage Report** - Generates and uploads HTML coverage reports

**Build Status:**
- ❌ **Build fails** if:
  - Any linting errors are detected (Ruff)
  - Any test fails
  - Dependencies fail to install

- ✅ **Build passes** only when all checks succeed

**View Pipeline:**
- Go to the **Actions** tab in your GitHub repository
- Click on any workflow run to see detailed logs and status

**Coverage Reports:**
- After each pipeline run, coverage reports are generated
- Download from the workflow run artifacts as `coverage-report.zip`
- Extract and open `htmlcov/index.html` in a browser to view detailed coverage

**Workflow File:** `.github/workflows/ci.yml`

---

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

---

## 🐳 Docker Support

### Building the Docker Image

The project includes a **multi-stage Dockerfile** that creates a lightweight container with all dependencies pre-installed.

```bash
# Build the image
docker build -t vfs-shell:latest .

# Optional: specify a custom tag
docker build -t vfs-shell:v0.1.0 .
```

**Build Details:**
- **Stage 1 (Builder):** Python 3.11 slim image with build tools (Poetry, curl, git)
  - Installs all dependencies from `pyproject.toml`
  - Compiles any necessary packages
- **Stage 2 (Runtime):** Lightweight Python 3.11 slim image
  - Contains only the virtual environment and source code
  - Runs as non-root user (`vfsuser`) for security
  - Reduces final image size significantly

### Running the Container

#### Interactive Mode
Start an interactive VFS Shell session:

```bash
docker run -it --name vfs-shell vfs-shell:latest
```

Then use VFS commands as usual:
```
vfs:/$ mkfs 1024
vfs:/$ mkdir /home
vfs:/$ ls /
```

#### Running Scripts from Files

Execute VFS Shell commands stored in a script file:


# Create a script file on your host machine
```bash
mkfs 2048
mkdir /home
mkdir /home/user
touch /home/user/data.txt "Hello VFS"
ls -la /home/user
cat /home/user/data.txt
```

# Run the script in the container via volume mount
```bash
docker run -v "$(pwd)/commands.sh:/app/commands.sh" vfs-shell:latest /app/commands.sh
```
or

```bash
docker run -v "$(pwd)/script_test.sh:/app/script_test.sh" vfs-shell:latest /app/script_test.s
```
#### Using Configuration Files

Pass custom configuration for encryption/compression rules:

```bash
# Mount your vfs_config.json file
docker run -v "$(pwd)/vfs_config.json:/app/vfs_config.json" \
           vfs-shell:latest --config /app/vfs_config.json
```

#### Volume Mounting for Input/Output

Share directories between host and container to pass input files and retrieve output:

```bash
# Create a shared directory
mkdir -p ./vfs-data

# Mount the directory and run a script
docker run -v "$(pwd)/vfs-data:/workspace" vfs-shell:latest /workspace/script.sh

# Check results on host
cat ./vfs-data/output.txt
```

**Example with Input/Output:**

```bash
# On host: create a script that reads from /workspace
cat > vfs-data/setup.sh << 'EOF'
mkfs 4096
mkdir /exports
touch /exports/results.txt "VFS is running!"
EOF

# Run container with volume
docker run -v "$(pwd)/vfs-data:/workspace" \
           vfs-shell:latest /workspace/setup.sh
```

### Container Environment Variables

The container automatically sets:
- `PATH=/app/.venv/bin:$PATH` - Virtual environment paths
- `PYTHONUNBUFFERED=1` - Ensures real-time output
- `PYTHONDONTWRITEBYTECODE=1` - Prevents .pyc file generation

### Docker Compose Example (Optional)

For more complex setups, create a `docker-compose.yml`:

```yaml
version: '3.8'
services:
  vfs-shell:
    build: .
    image: vfs-shell:latest
    container_name: vfs-shell-app
    stdin_open: true
    tty: true
    volumes:
      - ./data:/workspace
    environment:
      - PYTHONUNBUFFERED=1
```

Run with:
```bash
docker-compose up -d
docker-compose exec vfs-shell /bin/bash
```