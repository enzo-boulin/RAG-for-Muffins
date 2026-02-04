<img width="1920" height="1080" alt="mcmuffin" src="https://github.com/user-attachments/assets/c9ad4864-4fd3-4e51-bced-dfd8c1d23e4d" />
# 🧁 Muffin RAG Project

## Overview

This project is a RAG (Retrieval-Augmented Generation) application designed to help you find the perfect muffin recipe based on the ingredients in your fridge.

Not only does he cooks but the chatbot also loves to rap.

**Note on Language:** While the code and documentation are in English, the AI assistant—**MC Muffin**—is programmed to respond exclusively in **French**.

## Features
* **Web scraping**: Uses  `httpx` and `beautifulsoup4` to get all the french muffin recipes on Marmiton website.
* **Vector Search:** Uses `chromadb` and `sentence-transformers` to find the most relevant recipe from a SQLite database based on your input.
* **Local LLM:** Powered by **Ollama** running the **Mistral 7B** model for secure, local text generation.
* **Interactive UI:** A user-friendly interface built with **Streamlit**.


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

### 3. Initialize the Database (Optional)

I commited the SQLite and chroma db so this section can be skipped and directly lauch the app.

For the curious ones, I created my own crawler based on `httpx` to get the recipes :

1. Fetch all the muffin recipes as raw json on [Marmiton](https://www.marmiton.org/) website by running :
```bash
scrap_recipes
```
2. Create and fill SQLite DB and chromaDB embeddings DB :
```bash
# Setup the SQLite database schema
initialize_db

# Process raw data into the clean database
fill_db

# Map SQLite DB into an embedding db
create_and_fill_embeddings_db
```
*(Commands defined in `pyproject.toml`)*

### 4. Launch the App

Run the Streamlit interface (local):

```bash
streamlit run src/muffin/app.py
```


Then, enter your ingredients (e.g., "chocolat, banane") and let MC Muffin drop the beat... and the recipe.

## Dependencies

Key libraries used in this project include:

* `ollama`: For LLM interaction.
* `chromadb`: For vector storage and similarity search.
* `streamlit`: For the web interface.
* `sqlalchemy`: For managing the recipe database.
* `beautifulsoup4`: For data scraping/parsing.

## Performance

Running Mistral 7B locally can be quite intensive for the computer, the model needs 4.5 Go of free space and ideally 15 GB of RAM with a CPU, although it worked on my mac M1 8GB.
