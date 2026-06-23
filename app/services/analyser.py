import re
import os
import csv

import zipfile
import tarfile

from concurrent.futures import ThreadPoolExecutor, as_completed


TOKEN_PATTERN = re.compile(r'<Tkn\d{3}[A-Z]{5}Tkn>')

# this function finds the token count in that particular file and returns the count
def analyze_file(file_path) -> dict[str, int]:
    # dict (token, count)
    occurrences = {}
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        for line in file:
            tokens = TOKEN_PATTERN.findall(line)

            for token in tokens:
                if token in occurrences:
                    occurrences[token] += 1
                else:
                    occurrences[token] = 1


    return occurrences

# function to walk the directory_tree and analyze each file returns (path, occurrences, token)
def analyze_firmware(directory_path, csv_output_path) -> dict[str, dict[str, int]]:
    file_paths = []
    # csv coulmn will be path, token, occurences
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_paths.append(file_path)
        
    excel_rows = []
    token_totals = {}
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(analyze_file, file_path) : file_path
            for file_path in file_paths
        }

        for future in as_completed(futures):
            file_path = futures[future]
            rel_file_path = os.path.relpath(file_path, directory_path)
            display_path = rel_file_path.replace(os.sep, '/')
            occurrences = future.result()

            for token, count in occurrences.items():
                excel_rows.append((display_path, token, count))
                token_totals[token] = token_totals.get(token, 0) + count

    # The results are sorted by file path, occurences, and token as mentioned in the requirements
    excel_rows.sort(key=lambda row : (row[0], row[2], row[1]))

    if csv_output_path:
        with open(csv_output_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['File Path', 'Token', 'Occurrences'])
            writer.writerows(excel_rows)
    return token_totals

def is_archive(file_path):
    lower = file_path.lower()
    return (
        lower.endswith('.zip') or
        lower.endswith('.tar') or
        lower.endswith('.tar.gz') or
        lower.endswith('.tgz')
    )


def extract_archive(archive_path, extract_to = 'outputs') : 
    folder_name = os.path.splitext(os.path.basename(archive_path))[0]
    temp_dir = os.path.join(extract_to, folder_name)
    os.makedirs(temp_dir, exist_ok=True)

    pending = [archive_path]
    processed = set()

    while pending:
        curr = pending.pop()
        if curr in processed:
            continue
        processed.add(curr)

        if zipfile.is_zipfile(curr):
            with zipfile.ZipFile(curr, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
        elif tarfile.is_tarfile(curr):
            with tarfile.open(curr, 'r:*') as tar_ref:
                tar_ref.extractall(temp_dir)
        else: 
            continue

        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)

                if is_archive(file_path) and file_path not in processed:
                    pending.append(file_path)
    
    return temp_dir
