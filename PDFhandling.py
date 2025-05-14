
import os
import shutil

pdfs_directory = "uploaded_pdfs"
figures_directory = "figures"
os.makedirs(pdfs_directory, exist_ok=True)
os.makedirs(figures_directory, exist_ok=True)

def upload_pdf(uploaded_file):
    with open(os.path.join(pdfs_directory, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.read())

def load_pdf(path):
    with open(path, "rb") as f:
        return f.read().decode("latin1", errors="ignore")
