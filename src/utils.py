import os

def load_sample_call() -> str:
    return open('sample_data/example_call.txt', 'r', encoding='utf-8').read()

def load_file(filename) -> str:
    return open('input_data/'+filename, 'r', encoding='utf-8').read()

def list_files(folderpath: str) -> list:
    return os.listdir(folderpath)
