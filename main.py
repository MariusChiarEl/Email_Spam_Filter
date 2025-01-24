import Word_Spam_Probability_Generator
import Email_Word_counter
import os
import csv
import math
import argparse
from bs4 import BeautifulSoup
import json
import langid

"""
This email classifier takes 3 major steps:
1. We compute the training sets and returns a csv file with the frequency of each word for each
   => We will work with <TRAINING_CLEAN_word_frequency.csv> and <TRAINING_SPAM_word_frequency.csv>

2. Using the word frequency files, we will determine the frequency of each word in both spam and clean emails
   => We will work with <Word_Spam_Probability.csv>

3. We will iterate through the Testing Set of emails (spam emails are marked with '(SPAM)' in their name)
   and use the Naive Bayes model based on <Word_Spam_Probability.csv> to classify them

Main point: If a word is found in spam emails at least once, the email that contains it is more likely to be spam
vice-versa for clean emails => The higher probability determines the classification
"""

# Method that loads word probabilities from the combined CSV file
def load_word_probabilities(csv_file):
    word_probs = {}
    with open(csv_file, mode='r', encoding='gb18030') as file:
        reader = csv.DictReader(file)
        for row in reader:
            word = row["Word"]
            spam_ratio = float(row["Spam Ratio"])
            not_spam_ratio = float(row["Not Spam Ratio"])
            word_probs[word] = {"spam_ratio": spam_ratio, "not_spam_ratio": not_spam_ratio}
    return word_probs

# Method that classifies an email as spam or not spam
def classify_email(email_path, word_probs):
    try:
        with open(email_path, mode='rb') as file:  # Open in binary mode to avoid decoding errors
            raw_content = file.read()

        # For .html files, decode and parse as HTML
        html_content = raw_content.decode('gb18030', errors='ignore')
        soup = BeautifulSoup(html_content, "html.parser")
        email_content = soup.get_text().lower().split()

        # Initialize log probabilities
        log_spam_prob = 0
        log_not_spam_prob = 0

        # Calculate probabilities for the email by taking its spam/not-spam ratios
        for word in email_content:
            if word in word_probs:
                lang, confidence = langid.classify(word)
                print(confidence)
                log_spam_prob += math.log(1 - (confidence+10)/20 + 1e-10)  # Add small value to avoid log(0)
                log_spam_prob += math.log(word_probs[word]["spam_ratio"] + 1e-10)
                log_not_spam_prob += math.log(word_probs[word]["not_spam_ratio"] + 1e-10)
                log_not_spam_prob += math.log((confidence+10)/20 + 1e-10)

        # Compare probabilities : whichever probability is higher determines the classification
        classification = "spam" if log_spam_prob > log_not_spam_prob else "not spam"
        return classification, " ".join(email_content)
    except Exception as e:
        print(f"Error processing file '{email_path}': {e}")
        return "error", ""


# Method that processes all emails from a directory and save results to a CSV
def classify_emails_to_csv(directory, word_probs, output_csv, output_txt):
    results = []
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return
    
    with open(output_txt, mode='w', encoding='gb18030', newline='') as file:
        for filename in os.listdir(directory):
            email_path = os.path.join(directory, filename)
            classification, content = classify_email(email_path, word_probs)
            if classification != "error":
                results.append({"Filename": filename, "Content": content, "Classification": classification})

            filename = filename.replace(" ", "_")
            conclusion = filename + '|'
            if classification == "spam":
                conclusion = conclusion + "inf"
            elif classification == "not spam":
                conclusion = conclusion + "cln"
            conclusion = conclusion + '\n'
            file.write(conclusion)
        print(f"(Text version) Classification results saved to {output_txt}")

    if not results:
        print("No valid emails were processed.")
        return

    # Write results to a CSV file
    try:
        with open(output_csv, mode='w', encoding='gb18030', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["Filename", "Content", "Classification"])
            writer.writeheader()
            writer.writerows(results)
        print(f"Classification results saved to {output_csv}")

        #with open
    except Exception as e:
        print(f"Error writing to CSV file '{output_csv}': {e}")

# Method that writes project info to a file
def dump_info(student_name, project_name, student_alias, project_version, output_file_path):
    info_dict = {
        "student_name": student_name,
        "project_name": project_name,
        "student_alias": student_alias,
        "project_version": project_version
    }
    with open(output_file_path, 'w') as f:
        json.dump(info_dict, f)

# Main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Naive Bayes Email Classifier")
    parser.add_argument("-info", metavar="output_file", type=str, help="Write project info to the specified file")
    parser.add_argument("-scan", nargs=2, metavar=("folder", "output_file"), help="Scan a folder and output results")
    args = parser.parse_args()

    if args.info:
        dump_info("Enache-Stratulat_Marius", "Email_Classifier", "Marius_Chiar_El", "1.2", args.info)
        exit(1)


    print("============================== PHASE 1: WORD COUNTING ============================== ")
    # Email_Word_counter.run("Clean")
    # Email_Word_counter.run("Spam")
    
    print("============================== PHASE 2: WORD SPAM PROBABILITY COMPUTING ============================== ")
    # Word_Spam_Probability_Generator.run()

    combined_csv_path = "./Word_Spam_Probability.csv"
    test_emails_directory = "./Test(Spam-are-marked)" # Default path
    output_csv_path = "./email_classification_results.csv"
    output_txt_path = "./results.txt" # Default path

    if args.scan:
        test_emails_directory = args.scan[0]
        output_txt_path = args.scan[1]

    # Load word probabilities
    try:
        word_probabilities = load_word_probabilities(combined_csv_path)
    except Exception as e:
        print(f"Error loading word probabilities: {e}")
        word_probabilities = {}
        
    print("============================== PHASE 3: EMAIL SPAM PROBABILITY COMPUTING ============================== ")
    # Classify emails and save results to CSV
    if word_probabilities:
        classify_emails_to_csv(test_emails_directory, word_probabilities, output_csv_path, output_txt_path)