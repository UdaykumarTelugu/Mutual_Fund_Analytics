import nbformat
from nbclient import NotebookClient
import os

print("Executing Notebook EDA_Analysis.ipynb...")

notebook_path = 'notebooks/EDA_Analysis.ipynb'
with open(notebook_path) as f:
    nb = nbformat.read(f, as_version=4)

client = NotebookClient(nb, timeout=600, kernel_name='python3', resources={'metadata': {'path': 'notebooks/'}})

try:
    client.execute()
    print("Notebook executed successfully.")
except Exception as e:
    print(f"Error executing notebook: {e}")
    raise

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)

print("Notebook saved with outputs.")
