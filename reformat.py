import json
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import re
import random

def main():
    print("Starting script...")
    
    # Read JSON data from a file
    input_rating = []
    with open('input_rating.json', 'r') as file:
        for i, line in enumerate(file):
            if i >= 10:
                break
            input_rating.append(json.loads(line))
    print(input_rating)
    exit()

    print(f"Input data length: {len(input_rating)}")
    metadata_dict = {}
    with open('input_metadata.json', 'r') as file:
        for line in file:
            metadata = json.loads(line)
            if isinstance(metadata.get('category', []), list):
                processed_categories = [cat.replace(" ", "") for cat in metadata['category']]  # Remove spaces in each item
                metadata_dict[metadata['gmap_id']] = ("/".join(sorted(processed_categories))).lower()
            else:
                metadata_dict[metadata['gmap_id']] = "NA"

    unique_categories = set(metadata_dict.values())

    # Step 2: Create a mapping from category to a random 21-digit number starting with '1'
    def generate_random_22_digit_number():
        return int('1' + ''.join(str(random.randint(0, 9)) for _ in range(21)))

    category_to_number = {}
    for category in unique_categories:
        while True:
            rand_num = generate_random_22_digit_number()
            if rand_num not in category_to_number.values():
                category_to_number[category] = rand_num
                break

    # Extract relevant fields with a progress bar
    data = []
    for entry in tqdm(input_rating, desc="Processing entries", total=len(input_rating)):
        try:
            gmap_id = entry['gmap_id']
            category = metadata_dict.get(gmap_id, "NA")  # Default to "NA" if gmap_id not found
            data.append({
                'user_id': entry['user_id'],
                'gmap_id': gmap_id,
                'rating': entry['rating'],
                'review': entry['text'],
                'category': category
            })
        except KeyError as e:
            print(f"Missing key: {e} in entry {entry}")
    
    # Split the data into train, test, and dev sets
    data = [entry for entry in data if entry.get('review') and entry['review'].strip()]
    
    train, temp = train_test_split(data, test_size=0.2, random_state=42)
    test, dev = train_test_split(temp, test_size=0.5, random_state=42)
    
    def process_reviews(data_subset):
        for entry in tqdm(data_subset, desc="Processing reviews", total=len(data_subset)):
            review = entry['review']
            if review is None:
                review = ""  # Assign an empty string if the review is None

            reviews = re.split(r'([.!?])', review)

            # Combine each sentence with its punctuation mark
            reviews = [reviews[i] + reviews[i+1] if i + 1 < len(reviews) else reviews[i] for i in range(0, len(reviews), 2)]

            # Add <sssss> separator between sentences
            text_with_separators = "<sssss>".join(reviews)

            # Ensure no newlines or extra spaces are introduced
            entry['review'] = text_with_separators.replace('\n', ' ').strip()

            # Ensure that every entry has 4 fields: user_id, gmap_id, rating, review
            entry['user_id'] = str(entry.get('user_id', ''))
            entry['gmap_id'] = str(entry.get('gmap_id', ''))
            entry['rating'] = str(entry.get('rating', ''))
            entry['review'] = entry['review'] if entry.get('review', '') else ""
            entry['category'] = str(category_to_number.get(entry['category'], -1))

    # Process the train, test, and dev datasets
    process_reviews(train)
    process_reviews(test)
    process_reviews(dev)

    # Save the processed data to tab-separated files with UTF-8 encoding
    def write_to_file(filename, data_subset):
        with open(filename, 'w', encoding='utf-8') as f:
            for entry in data_subset:
                # Ensure consistent use of \t\t as the delimiter
                f.write(f"{entry['user_id']}\t\t{entry['gmap_id']}\t\t{entry['rating']}\t\t{entry['review']}\t\t{entry['category']}\n")
    
    write_to_file('google.train.ss', train)
    write_to_file('google.test.ss', test)
    write_to_file('google.dev.ss', dev)

    print("Files have been successfully created: google.train.ss, google.test.ss, and google.dev.ss.")

if __name__ == "__main__":
    main()
