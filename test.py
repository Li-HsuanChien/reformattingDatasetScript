import json
from sklearn.model_selection import train_test_split


ctgy = {}
with open('input_metadata.json', 'r') as file:
    i = 0
    for line in file:
        metadata = json.loads(line)
        if isinstance(metadata.get('category', []), list):
            processed_categories =  metadata['category']  # Remove spaces in each item
            for item in processed_categories:
                if item not in ctgy:
                    ctgy[item] = 1
                else:
                    ctgy[item] += 1
            print({k: v for k, v in sorted(ctgy.items(), key=lambda item: item[1], reverse=True)})
            break
            