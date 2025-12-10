"""
Helper script to load and explore the 2WikiMultihopQA dataset

Usage:
    python load_dataset.py --file data/train.json --sample 5
"""

import ujson as json
import argparse
from pathlib import Path


def load_dataset(file_path):
    """Load the dataset from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def print_sample(sample, idx=0):
    """Pretty print a sample from the dataset"""
    print(f"\n{'='*80}")
    print(f"Sample {idx + 1}")
    print(f"{'='*80}")
    print(f"ID: {sample['_id']}")
    print(f"Type: {sample.get('type', 'N/A')}")
    print(f"\nQuestion: {sample['question']}")
    print(f"\nAnswer: {sample.get('answer', '[Test data - no answer provided]')}")
    
    if 'supporting_facts' in sample:
        print(f"\nSupporting Facts ({len(sample['supporting_facts'])} facts):")
        for i, (title, sent_idx) in enumerate(sample['supporting_facts'][:3]):
            print(f"  {i+1}. [{title}] sentence {sent_idx}")
        if len(sample['supporting_facts']) > 3:
            print(f"  ... and {len(sample['supporting_facts']) - 3} more")
    
    if 'evidences' in sample:
        print(f"\nEvidences ({len(sample['evidences'])} triples):")
        for i, evidence in enumerate(sample['evidences'][:2]):
            print(f"  {i+1}. {evidence}")
        if len(sample['evidences']) > 2:
            print(f"  ... and {len(sample['evidences']) - 2} more")
    
    print(f"\nContext: {len(sample['context'])} paragraphs")
    for i, (title, sentences) in enumerate(sample['context'][:2]):
        print(f"  {i+1}. [{title}] - {len(sentences)} sentences")
        if sentences:
            print(f"     First sentence: {sentences[0][:100]}...")
    if len(sample['context']) > 2:
        print(f"  ... and {len(sample['context']) - 2} more paragraphs")


def main():
    parser = argparse.ArgumentParser(description='Load and explore 2WikiMultihopQA dataset')
    parser.add_argument('--file', type=str, help='Path to dataset JSON file (e.g., data/train.json)')
    parser.add_argument('--sample', type=int, default=3, help='Number of samples to display')
    parser.add_argument('--stats', action='store_true', help='Show dataset statistics')
    
    args = parser.parse_args()
    
    if not args.file:
        print("Error: Please provide a dataset file with --file")
        print("\nAvailable datasets to download:")
        print("  1. Main dataset: https://www.dropbox.com/s/npidmtadreo6df2/data.zip")
        print("     Contains: train.json, dev.json, test.json")
        print("\n  2. Dataset with IDs: https://www.dropbox.com/s/7ep3h8unu2njfxv/data_ids.zip")
        print("     Contains: train.json, dev.json, test.json, id_aliases.json")
        print("\nExtract to a 'data/' or 'data_ids/' folder and run:")
        print("  python load_dataset.py --file data/train.json --sample 3")
        return
    
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return
    
    print(f"Loading dataset from: {file_path}")
    data = load_dataset(file_path)
    
    print(f"\n{'='*80}")
    print(f"Dataset: {file_path.name}")
    print(f"Total samples: {len(data)}")
    print(f"{'='*80}")
    
    if args.stats:
        # Count question types
        types = {}
        has_answer = 0
        has_evidences = 0
        
        for sample in data:
            q_type = sample.get('type', 'unknown')
            types[q_type] = types.get(q_type, 0) + 1
            if 'answer' in sample:
                has_answer += 1
            if 'evidences' in sample:
                has_evidences += 1
        
        print("\nQuestion Type Distribution:")
        for q_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {q_type}: {count} ({count/len(data)*100:.1f}%)")
        
        print(f"\nSamples with answers: {has_answer} ({has_answer/len(data)*100:.1f}%)")
        print(f"Samples with evidences: {has_evidences} ({has_evidences/len(data)*100:.1f}%)")
    
    # Show sample questions
    num_samples = min(args.sample, len(data))
    print(f"\nShowing {num_samples} sample(s):\n")
    
    for i in range(num_samples):
        print_sample(data[i], i)
    
    print(f"\n{'='*80}")
    print(f"To see more samples, use: --sample N")
    print(f"To see statistics, use: --stats")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()

