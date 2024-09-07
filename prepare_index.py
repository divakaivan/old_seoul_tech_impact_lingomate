import pandas as pd
import json
from elasticsearch import Elasticsearch
from tqdm import tqdm

def read_and_transform_csv(csv_file_path):
    """Reads a CSV file and transforms it into a dictionary."""
    df = pd.read_csv(csv_file_path)
    df.columns = ['category', 'situation_en', 'situation_kr', 'question_en', 'question_kr', 'answer_en', 'answer_kr']
    return df.to_dict(orient='records')

def save_to_json(data, json_file_path):
    """Saves data to a JSON file."""
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def create_elasticsearch_index(es_client, index_name, index_settings):
    """Creates an Elasticsearch index with the specified settings."""
    if es_client.indices.exists(index=index_name):
        print(f"Index '{index_name}' already exists.")
    else:
        es_client.indices.create(index=index_name, body=index_settings)
        print(f"Index '{index_name}' created.")

def index_documents(es_client, index_name, json_file_path):
    """Indexes documents into Elasticsearch from a JSON file."""
    with open(json_file_path, 'rt') as f_in:
        docs_raw = json.load(f_in)

    for doc in tqdm(docs_raw, desc="Indexing documents"):
        es_client.index(index=index_name, document=doc)
    print("Indexing complete.")

def main():
    csv_file_path = 'situations.csv'
    json_file_path = 'situations.json'
    index_name = 'learning-english'

    index_settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "category": {"type": "text"},
                "situation_en": {"type": "text"},
                "situation_kr": {"type": "text"},
                "question_en": {"type": "text"},
                "question_kr": {"type": "text"},
                "answer_en": {"type": "text"},
                "answer_kr": {"type": "text"},
            }
        }
    }

    # Initialize Elasticsearch client
    es_client = Elasticsearch('http://localhost:9200')

    # Process data
    data = read_and_transform_csv(csv_file_path)
    save_to_json(data, json_file_path)
    create_elasticsearch_index(es_client, index_name, index_settings)
    index_documents(es_client, index_name, json_file_path)

if __name__ == '__main__':
    main()
