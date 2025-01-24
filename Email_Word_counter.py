import os
import re
from bs4 import BeautifulSoup
from collections import Counter
import pandas as pd

"""
Method that takes an email as input and
returns a list of all its words
"""
def extract_words_from_file(file_path, encoding='gb18030'):
    try:
        with open(file_path, 'r', encoding=encoding, errors='ignore') as file:
            content = file.read()
        # Parse content and remove html script/style tags
        soup = BeautifulSoup(content, features="html.parser")
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        # Extract words using regex (only alphanumeric words)
        words = re.findall(r'\b\w+\b', text)
        return words
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return []

"""
Method that takes a plain text file as input
and returns a list of all its words
"""
def extract_words_from_txt(file_path, encoding='gb18030'):
    try:
        with open(file_path, 'r', encoding=encoding, errors='ignore') as file:
            text = file.read()
        # Extract words using regex (only alphanumeric words)
        words = re.findall(r'\b\w+\b', text)
        return words
    except Exception as e:
        print(f"Error processing TXT file {file_path}: {e}")
        return []

"""
Method that iterates through a directory of emails
and extracts the words found in each email
"""
def process_files_in_directory(directory_path):
    """
    Process all files in a directory, compute word frequencies, and create a table.
    """
    word_counter = Counter()
    
    # Walk through all files in the given directory
    for root, _, files in os.walk(directory_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            
            print(f"Processing file: {file_path}")
            words = extract_words_from_file(file_path, encoding='gb18030')  # Try 'gb18030' for compatibility

            # Update word counter
            word_counter.update(word.lower() for word in words)  # Convert words to lowercase
    
    # Convert Counter to a DataFrame for a table format
    word_freq_table = pd.DataFrame(word_counter.items(), columns=["Word", "Frequency"])
    word_freq_table = word_freq_table.sort_values(by="Frequency", ascending=False).reset_index(drop=True)
    return word_freq_table

"""
Main function
"""
def run(emailType):
    if emailType != "Clean" and emailType != "Spam":
        print("WRONG INPUT FOR EMAIL TYPE!")
        exit()

    input_directory = "./Train/Clean" if emailType == "Clean" else "./Train/Spam"
    
    word_frequency_table = process_files_in_directory(input_directory)
    
    print(word_frequency_table)
    
    output_csv = "TRAINING_CLEAN_word_frequency.csv" if emailType == "Clean" else "TRAINING_SPAM_word_frequency.csv"
    word_frequency_table.to_csv(output_csv, index=False, encoding='gb18030')
    print(f"Word frequency table saved to: {output_csv}")

