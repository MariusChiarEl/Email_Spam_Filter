import csv
from collections import defaultdict

"""
Method that compiles the word frequencies from CSV or TXT files
and returns the respective dictionary
"""
def read_word_frequencies(file_path):
    word_freq = {}
    try:
        if file_path.endswith('.csv'):
            # Read CSV files
            with open(file_path, mode='r', encoding='gb18030') as file:
                reader = csv.reader(file)
                next(reader)  # Skip the header
                for row in reader:
                    word = row[0]
                    frequency = int(row[1])
                    word_freq[word] = frequency
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
    return word_freq

"""
Method that writes the combined word frequencies to a CSV file
"""
def write_combined_csv(output_path, combined_data):
    with open(output_path, mode='w', encoding='gb18030', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Word", "Spam Frequency", "Not Spam Frequency", "Spam Ratio", "Not Spam Ratio"])
        for word, data in combined_data.items():
            writer.writerow([word, data["spam"], data["not_spam"], data["spam_ratio"], data["not_spam_ratio"]])

"""
Main method that manages all the word
frequencies found in the training set of emails
"""
def compile_word_frequencies(spam_file, not_spam_file, output_csv):
    spam_data = read_word_frequencies(spam_file)
    not_spam_data = read_word_frequencies(not_spam_file)

    combined_data = defaultdict(lambda: {"spam": 0, "not_spam": 0, "spam_ratio": 0.0, "not_spam_ratio": 0.0})

    # Merge data from spam and not spam dictionaries
    all_words = set(spam_data.keys()).union(set(not_spam_data.keys()))
    
    total_spam_words = sum(spam_data.values())
    total_not_spam_words = sum(not_spam_data.values())

    """
    For each word found, we will compute the ratio between its frequency in
    spam emails and its frequency in clean emails
    """
    for word in all_words:
        spam_freq = spam_data.get(word, 0)
        not_spam_freq = not_spam_data.get(word, 0)
        total_freq = spam_freq + not_spam_freq

        combined_data[word]["spam"] = spam_freq
        combined_data[word]["not_spam"] = not_spam_freq
        if not_spam_freq == 0:
            combined_data[word]["spam_ratio"] = 1
            combined_data[word]["not_spam_ratio"] = 0
        elif spam_freq == 0:
            combined_data[word]["spam_ratio"] = 0
            combined_data[word]["not_spam_ratio"] = 1
        else:
            combined_data[word]["spam_ratio"] = spam_freq / total_freq if total_freq > 0 else 0
            combined_data[word]["not_spam_ratio"] = not_spam_freq / total_freq if total_freq > 0 else 0

    # Write the combined data to the output CSV
    write_combined_csv(output_csv, combined_data)

"""
Main function
"""
def run():
    # Specify the file paths (can be .csv or .txt)
    spam_file_path = "TRAINING_SPAM_word_frequency.csv"
    not_spam_file_path = "TRAINING_CLEAN_word_frequency.csv"
    output_csv_path = "Word_Spam_Probability.csv"

    compile_word_frequencies(spam_file_path, not_spam_file_path, output_csv_path)

    print(f"Combined word frequencies written to {output_csv_path}")
