Got it 👍 — here’s the cleaned-up **README.md** file (with **Conda removed** and your instructions structured properly):

````markdown
# Project README

This is a Python project with three Python files representing different phases of the project. Below are the instructions for setting up the environment, installing prerequisites, and running the project.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
   * [Using Pipenv](#using-pipenv)
   * [Using Pip](#using-pip)
3. [Running Ollama + DeepSeek](#running-ollama--deepseek)
4. [Running the Project](#running-the-project)

---

## Prerequisites

Before running the project, ensure you have the following:

1. **Ollama Installed**
   * Download and install Ollama from [Ollama’s website](https://ollama.com).
   * Verify installation with:
     ```bash
     ollama -v
     ```
   * Pull the DeepSeek-R1 model (1.5B version for lightweight usage):
     ```bash
     ollama pull deepseek-r1:1.5b
     ```
   * Start the Ollama server:
     ```bash
     ollama serve
     ```

2. **Environment Variable**
   * Inside your virtual environment, set the `GROQ_API_KEY`.
   * Example (Linux/Mac):
     ```bash
     export GROQ_API_KEY="your_api_key_here"
     ```
   * Example (Windows PowerShell):
     ```powershell
     setx GROQ_API_KEY "your_api_key_here"
     ```

---

## Environment Setup

### Using Pipenv
1. Install Pipenv if you don't have it:
   ```bash
   pip install pipenv
````

2. Navigate to the project directory and create a virtual environment:

   ```bash
   pipenv install
   ```
3. Activate the virtual environment:

   ```bash
   pipenv shell
   ```
4. (Optional) Install any additional dependencies:

   ```bash
   pipenv install <package_name>
   ```

---

### Using Pip

1. Install virtualenv if you don't have it:

   ```bash
   pip install virtualenv
   ```
2. Create a virtual environment:

   ```bash
   virtualenv venv
   ```
3. Activate the virtual environment:

   * On Windows:

     ```bash
     venv\Scripts\activate
     ```
   * On macOS/Linux:

     ```bash
     source venv/bin/activate
     ```
4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## Running Ollama + DeepSeek

Make sure Ollama server is running before starting the project:

```bash
ollama serve
```

This allows the project to query the DeepSeek-R1 model locally.

---

## Running the Project

The project consists of three Python files, each corresponding to a different phase of the project:

### To run the App directly

```bash
streamlit run main.py
```

### To run app in different phases

1. Phase 1: Run the first phase using:

   ```bash
   streamlit run frontend.py
   ```
2. Phase 2: Run the second phase using:

   ```bash
   python vector_database.py
   ```
3. Phase 3: Run the third phase using:

   ```bash
   python rag_pipeline.py
   ```

---

## Troubleshooting

If you encounter any issues, ensure that:

* Ollama is installed and running (`ollama serve`).
* The DeepSeek-R1 model is pulled.
* Your virtual environment has the `GROQ_API_KEY` set.
