"""
Helper script to explore the para_with_hyperlink dataset

This dataset contains Wikipedia paragraphs with hyperlink information.

Usage:
    python explore_paragraphs.py --file para_with_hyperlink/wiki_*.json --sample 3
"""

import ujson as json
import argparse
from pathlib import Path
import glob


def load_paragraph_file(file_path):
    """Load a paragraph JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def print_paragraph(para, idx=0):
    """Pretty print a paragraph"""
    print(f"\n{'='*80}")
    print(f"Paragraph {idx + 1}")
    print(f"{'='*80}")
    print(f"Wikipedia ID: {para.get('id', 'N/A')}")
    print(f"Title: {para.get('title', 'N/A')}")
    
    sentences = para.get('sentences', [])
    print(f"\nSentences: {len(sentences)}")
    for i, sent in enumerate(sentences[:3]):
        print(f"  [{i}] {sent[:100]}{'...' if len(sent) > 100 else ''}")
    if len(sentences) > 3:
        print(f"  ... and {len(sentences) - 3} more sentences")
    
    mentions = para.get('mentions', [])
    if mentions:
        print(f"\nHyperlinks/Mentions: {len(mentions)}")
        for i, mention in enumerate(mentions[:3]):
            sent_idx = mention.get('sent_idx', '?')
            start = mention.get('start', 0)
            end = mention.get('end', 0)
            ref_url = mention.get('ref_url', 'N/A')
            print(f"  {i+1}. Sentence {sent_idx}, pos {start}-{end}: {ref_url}")
        if len(mentions) > 3:
            print(f"  ... and {len(mentions) - 3} more mentions")


def main():
    parser = argparse.ArgumentParser(description='Explore para_with_hyperlink dataset')
    parser.add_argument('--dir', type=str, default='para_with_hyperlink',
                       help='Directory containing paragraph JSON files')
    parser.add_argument('--sample', type=int, default=3,
                       help='Number of paragraphs to display')
    
    args = parser.parse_args()
    
    para_dir = Path(args.dir)
    
    if not para_dir.exists():
        print(f"Error: Directory not found: {para_dir}")
        print("\nTo extract para_with_hyperlink.zip, run:")
        print("  unzip para_with_hyperlink.zip")
        return
    
    # Find all JSON files in the directory
    json_files = list(para_dir.glob('*.json'))
    
    if not json_files:
        print(f"Error: No JSON files found in {para_dir}")
        return
    
    print(f"\n{'='*80}")
    print(f"Found {len(json_files)} JSON file(s) in {para_dir}")
    print(f"{'='*80}")
    
    # Load and display samples from the first file
    first_file = json_files[0]
    print(f"\nExploring: {first_file.name}")
    
    data = load_paragraph_file(first_file)
    
    if isinstance(data, dict):
        # Single paragraph
        paragraphs = [data]
    elif isinstance(data, list):
        # Multiple paragraphs
        paragraphs = data
    else:
        print(f"Unknown data format: {type(data)}")
        return
    
    print(f"Total paragraphs in this file: {len(paragraphs)}")
    
    num_samples = min(args.sample, len(paragraphs))
    print(f"\nShowing {num_samples} sample paragraph(s):\n")
    
    for i in range(num_samples):
        print_paragraph(paragraphs[i], i)
    
    print(f"\n{'='*80}")
    print(f"To explore more, use: --sample N")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()

