# %%
#pip install langchain
#pip install torch
#pip install transformers

# %%
import requests
import json
from flask import Flask, request, render_template
from transformers import GPT2LMHeadModel, GPT2Tokenizer

MAX_FILE_SIZE = 10000000

# %%
# Step 1: Fetching User's Repositories from GitHub
def fetch_user_repositories(username):
    api_url = 'https://api.github.com/users/'+username+'/repos'
    response = requests.get(api_url)
    if response.status_code == 200:
        repositories = json.loads(response.text)
        return repositories
    else:
        print("Failed to fetch repositories.")
        return None

# %%
data = fetch_user_repositories('vercel-labs')
data

# %%
# Step 2: Preprocessing Code in Repositories
def preprocess_code(repositories):
    # Split large Jupyter notebooks or package files
    for repository in repositories:
        # Split large Jupyter notebooks or package files
        if repository.get("file_type") == "Jupyter Notebook" or repository.get("file_type") == "Package":
            files = repository.get("files")
            if files is not None:
                repository["files"] = split_large_files(files)

    return repositories

# Split large files into smaller parts
def split_large_files(repository):
    split_files = []

    for file in repository.files:
        if file.size > MAX_FILE_SIZE:  # Define the maximum file size threshold
            chunks = split_file_into_chunks(file)
            split_files.extend(chunks)
        else:
            split_files.append(file)

    return split_files

# Split a file into smaller chunks
def split_file_into_chunks(file):
    MAX_CHUNK_SIZE = 50000  # Maximum chunk size threshold in bytes

    chunks = []
    content = file.code
    num_chunks = (len(content) // MAX_CHUNK_SIZE) + 1

    for i in range(num_chunks):
        start_idx = i * MAX_CHUNK_SIZE
        end_idx = (i + 1) * MAX_CHUNK_SIZE
        chunk_code = content[start_idx:end_idx]
        chunk = File(file.name, file.file_type, chunk_code)
        chunks.append(chunk)

    return chunks

# %%
# Step 3: Identify Technical Complexity Using GPT and LangChain
def assess_technical_complexity(repository):
    preprocess_code(repository)
    complexity_score = 0

    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    model = GPT2LMHeadModel.from_pretrained("gpt2")

    
    def process_repo(repository):
        prompt = f'Evaluate the technical complexity of the {repository}. Please analyze the code and provide insights on its complexity, potential issues, and areas for improvement.'
        input_ids = tokenizer.encode(prompt,truncation=True, max_length=100,return_tensors="pt")
        output = model.generate(input_ids, max_length=200,pad_token_id=tokenizer.eos_token_id)  # Example GPT-based evaluation
        process_repo = tokenizer.decode(output[0])
        return process_repo
           
    for file in repository:
        processed_repo = process_repo(file)
        complexity_score += len(processed_repo)

    return complexity_score
    
def find_most_complex_repository(repositories):
        most_complex_repository = None
        highest_complexity_score = 0

        for repository in repositories:
            complexity_score = assess_technical_complexity(repository)

            if complexity_score > highest_complexity_score:
                highest_complexity_score = complexity_score
                most_complex_repository = repository

        return most_complex_repository

# %%
assess_technical_complexity(data)

# %%



