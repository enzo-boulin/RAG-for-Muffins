# 🧁 Muffin RAG Project

## Overview

This project is a RAG (Retrieval-Augmented Generation) application designed to help you find the perfect muffin recipe based on the ingredients in your fridge.

**Note on Language:** While the code and documentation are in English, the AI assistant—**MC Muffin**—is programmed to respond exclusively in **French**.

## Getting Started

### 1. Setup Environment

Ensure you have Python 3.10+ installed.

Using conda :

```bash
python3 -m venv .venv/muffin 
source .venv/muffin/bin/activate
pip install . 
```
Using uv :
```bash
uv sync 
```

### 2. Configure Ollama

To run the LLM backend:

1. Install [Ollama](https://ollama.ai/).
2. Pull the Mistral model:
```bash
ollama pull mistral
```
3. Ensure the Ollama server is running in the background so the `ollama.chat` calls can execute.

### 3. Initialize the Database

Before running the app, you need to prepare the recipe data:

```bash
# Setup the SQLite database schema
initialize_db

# Process raw data into the clean database
fill_db
```

*(Commands defined in `pyproject.toml`)*

### 4. Launch the App

Run the Streamlit interface (local):

```bash
launch_ragamuffin
```


## Features

* **Vector Search:** Uses `chromadb` and `sentence-transformers` to find the most relevant recipe from a SQLite database based on your input.
* **Local LLM:** Powered by **Ollama** running the **Mistral** model for secure, local text generation.
* **Interactive UI:** A user-friendly interface built with **Streamlit**.



Then, enter your ingredients (e.g., "chocolat, banane") and let MC Muffin drop the beat... and the recipe.

## 📦 Dependencies

Key libraries used in this project include:

* `ollama`: For LLM interaction.
* `chromadb`: For vector storage and similarity search.
* `streamlit`: For the web interface.
* `sqlalchemy`: For managing the recipe database.
* `beautifulsoup4`: For data scraping/parsing.