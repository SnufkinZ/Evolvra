
# Evolvra AI Personal Secretary: Backend Tutorial

Welcome to the Evolvra AI backend! This project is the intelligent server-side component for your personal secretary application. It uses a powerful AI "brain" to understand user requests, manage tasks and goals, and provide personalized planning.

This guide covers the essential knowledge for setting up the development environment, managing the codebase with Git, and running the API server.

**Core Technologies:**

- **Language:** Python 3.10+
    
- **API Framework:** FastAPI
    
- **Web Server:** Uvicorn
    
- **Database:** MongoDB (communicated with via `motor`)
    
- **AI:** OpenAI GPT-4+
    
- **Dependency Management:** venv & pip
    

## 1. Project Setup & Environment Management

A clean, isolated environment is crucial for any Python project. This ensures that the packages for this project don't conflict with others on your system.

### 1.1. Python Version

This project is designed for **Python 3.10 or newer**. The code uses modern syntax (like the `|` union operator for type hints) that is not available in older versions. It is highly recommended to use a recent version (e.g., 3.11, 3.12) for better performance and security.

- On macOS, the recommended way to install and manage Python versions is with [Homebrew](https://brew.sh/): `brew install python@3.12`
    

### 1.2. Virtual Environment (`venv`)

We use a virtual environment to keep all project dependencies isolated.

1. **Create the environment** (only once):
    
    Bash
    
    ```
    # Make sure to use your specific new Python version
    python3.12 -m venv venv
    ```
    
2. **Activate the environment** (every time you open a new terminal for this project):
    
    Bash
    
    ```
    source venv/bin/activate
    ```
    
    You will see `(venv)` at the start of your terminal prompt when it's active.
    

### 1.3. Installing Dependencies (`requirements.txt`)

All necessary Python packages are listed in the `requirements.txt` file.

1. **Install all dependencies**: After activating your virtual environment, run:
    
    Bash
    
    ```
    pip install -r requirements.txt
    ```
    
2. **Adding a new dependency**: If you need to add a new package (e.g., `pip install some-new-package`), you must update the `requirements.txt` file immediately after:
    
    Bash
    
    ```
    pip freeze > requirements.txt
    ```
    

## 2. Professional Git & GitHub Workflow

Proper version control is key to a healthy project. The goal is to only track essential source code and configurations, while ignoring temporary files, secrets, and environment folders.

### 2.1. The `.gitignore` File

This file tells Git which files and folders to ignore. It is the **most important file for repository cleanliness**. Your `.gitignore` should contain the following to exclude virtual environments, Python cache, and secret files.

Code snippet

```
# Virtual Environment
venv/
.venv/

# Python cache files
__pycache__/
*.pyc

# IDE and editor files (VSCode, PyCharm, etc.)
.vscode/
.idea/
*.DS_Store

# Dotenv environment files - CRITICAL
# This file contains your secret API keys.
# NEVER upload it to GitHub!
.env
```

### 2.2. Cleaning a Repository That Already Has Unwanted Files

If you've already committed files like `__pycache__` or `.env` to GitHub, updating `.gitignore` is not enough. You must manually remove them from Git's tracking index.

1. **First, ensure your `.gitignore` file is correct and commit it:**
    
    Bash
    
    ```
    git add .gitignore
    git commit -m "Update .gitignore to ignore venv and pycache"
    ```
    
2. **Run the cleanup commands:**
    
    Bash
    
    ```
    # This removes everything from Git's index (but keeps your local files safe)
    git rm -r --cached .
    
    # This re-adds everything, but respects the new .gitignore rules
    git add .
    ```
    
3. **Commit the cleanup and push to GitHub:**
    
    Bash
    
    ```
    git commit -m "Clean repo: Remove tracked __pycache__ and other ignored files"
    git push
    ```
    

## 3. Building and Running the API Server

Our server acts as the bridge between the Flutter frontend and the Python `AIBrain`.

### 3.1. Architecture: The Restaurant Analogy

- **Frontend (Flutter)**: The restaurant's lobby and menu where the customer places an order.
    
- **Backend (Python/FastAPI)**: The kitchen and the chef who prepare the meal.
    
- **API (`/process-message`)**: The waiter who takes the order from the customer to the kitchen and brings the finished dish back.
    

### 3.2. Running the Server

With your virtual environment activated, use the following command to start the server:

Bash

```
# The recommended robust way to run Uvicorn
python3 -m uvicorn main:app --reload
```

- `main`: The `main.py` file.
    
- `app`: The `app = FastAPI()` object inside `main.py`.
    
- `--reload`: Enables auto-reloading for development, so the server restarts when you save a file.
    

The server will be running at `http://127.0.0.1:8000`.

### 3.3. Key Files and Structure

- **`main.py`**: The entry point of the API. It defines the API endpoints (routes) and connects them to the application logic.
    
- **`brain.py`**: Contains the core `AIBrain` class, which orchestrates calls to the LLM and the database operations.
    
- **`logic/`**: A directory for modules that perform specific database operations (e.g., `task_operations.py`, `goal_operations.py`). This is the "chef's skills".
    
- **`api/models.py`**: Contains Pydantic models that define the expected structure of request and response JSON data. This ensures data integrity.
    

### 3.4. Testing the API with Interactive Docs

FastAPI provides automatically generated documentation, which is perfect for testing.

1. **Start the server.**
    
2. Open your web browser and go to **`http://127.0.0.1:8000/docs`**.
    
3. You will see an interactive API documentation page (Swagger UI).
    
4. Find the `/process-message` endpoint, click to expand it, and click "Try it out".
    
5. Enter a JSON request in the request body, for example:
    
    JSON
    
    ```
    {
      "message": "add a task to finish the readme by tonight"
    }
    ```
    
6. Click "Execute". You will see the live response from your AI Brain, just as your Flutter app would.
