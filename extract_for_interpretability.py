"""
Extract 2WikiMultiHopQA data for interpretability research

This script extracts questions, answers, and bridge entities for testing
whether interpretability techniques can recover latent representations in LLMs
when answering multi-hop questions from parametric knowledge (no context).

Usage:
    python extract_for_interpretability.py --input data/train.json --output interpretability_data.jsonl
"""

import ujson as json
import argparse
from pathlib import Path
from collections import defaultdict


def extract_bridge_entities(sample):
    """
    Extract bridge entities from supporting facts and evidence triples.
    
    Bridge entities are the intermediate concepts needed for multi-hop reasoning.
    For example: "Who is the spouse of the director of Inception?"
    - Bridge entity: "Christopher Nolan" (the director)
    - Answer: His spouse
    """
    bridge_entities = []
    
    # Extract from supporting facts (titles of intermediate documents)
    supporting_facts = sample.get('supporting_facts', [])
    if supporting_facts:
        # The titles often contain or are the bridge entities
        titles = list(set([title for title, _ in supporting_facts]))
        bridge_entities.extend(titles)
    
    # Extract from evidence triples (subject-relation-object)
    evidences = sample.get('evidences', [])
    if evidences:
        # For multi-hop: first triple's object often becomes second triple's subject
        entities_in_chain = []
        for evidence in evidences:
            if len(evidence) >= 3:
                subject, relation, obj = evidence[0], evidence[1], evidence[2]
                entities_in_chain.extend([subject, obj])
        bridge_entities.extend(entities_in_chain)
    
    # Deduplicate while preserving order
    seen = set()
    unique_bridges = []
    for entity in bridge_entities:
        if entity and entity not in seen and entity != sample.get('answer'):
            seen.add(entity)
            unique_bridges.append(entity)
    
    return unique_bridges


def extract_reasoning_chain(sample):
    """
    Extract the reasoning chain from evidence triples.
    Returns a structured representation of the multi-hop reasoning path.
    """
    evidences = sample.get('evidences', [])
    chain = []
    
    for i, evidence in enumerate(evidences):
        if len(evidence) >= 3:
            chain.append({
                'hop': i + 1,
                'subject': evidence[0],
                'relation': evidence[1],
                'object': evidence[2]
            })
    
    return chain


def process_sample(sample, include_context=False):
    """
    Process a sample into the format needed for interpretability research.
    """
    # Extract core information
    processed = {
        'id': sample['_id'],
        'question': sample['question'],
        'answer': sample.get('answer'),
        'question_type': sample.get('type'),
        
        # Bridge entities - the key for interpretability!
        'bridge_entities': extract_bridge_entities(sample),
        
        # Reasoning chain structure
        'reasoning_chain': extract_reasoning_chain(sample),
        
        # Additional metadata
        'num_hops': len(sample.get('evidences', [])),
        'entity_ids': sample.get('entity_ids'),
    }
    
    # Optionally include supporting facts for reference
    if include_context:
        processed['supporting_facts'] = sample.get('supporting_facts', [])
        processed['context_titles'] = [title for title, _ in sample.get('context', [])]
    
    return processed


def analyze_dataset(data):
    """Provide statistics about the dataset for interpretability research."""
    stats = {
        'total_samples': len(data),
        'by_type': defaultdict(int),
        'by_num_hops': defaultdict(int),
        'with_bridge_entities': 0,
        'avg_bridge_entities': 0,
    }
    
    total_bridges = 0
    
    for sample in data:
        q_type = sample.get('question_type', 'unknown')
        stats['by_type'][q_type] += 1
        
        num_hops = sample.get('num_hops', 0)
        stats['by_num_hops'][num_hops] += 1
        
        bridges = sample.get('bridge_entities', [])
        if bridges:
            stats['with_bridge_entities'] += 1
            total_bridges += len(bridges)
    
    if stats['with_bridge_entities'] > 0:
        stats['avg_bridge_entities'] = total_bridges / stats['with_bridge_entities']
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description='Extract 2WikiMultiHopQA data for interpretability research'
    )
    parser.add_argument('--input', type=str, required=True,
                       help='Input JSON file (e.g., data/train.json)')
    parser.add_argument('--output', type=str, default='interpretability_data.jsonl',
                       help='Output JSONL file')
    parser.add_argument('--include-context', action='store_true',
                       help='Include context information for reference')
    parser.add_argument('--filter-type', type=str, choices=['comparison', 'inference', 'compositional', 'bridge_comparison'],
                       help='Filter to specific question type')
    parser.add_argument('--min-hops', type=int, default=0,
                       help='Minimum number of reasoning hops')
    parser.add_argument('--stats-only', action='store_true',
                       help='Only show statistics, do not write output')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        print("\nYou need to download the main dataset first:")
        print("  wget https://www.dropbox.com/s/npidmtadreo6df2/data.zip")
        print("  unzip data.zip")
        return
    
    print(f"Loading dataset from: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    print(f"Processing {len(raw_data)} samples...")
    
    # Process all samples
    processed_data = []
    for sample in raw_data:
        processed = process_sample(sample, args.include_context)
        
        # Apply filters
        if args.filter_type and processed['question_type'] != args.filter_type:
            continue
        if processed['num_hops'] < args.min_hops:
            continue
        
        processed_data.append(processed)
    
    print(f"Processed {len(processed_data)} samples (after filtering)")
    
    # Show statistics
    stats = analyze_dataset(processed_data)
    print(f"\n{'='*80}")
    print("Dataset Statistics for Interpretability Research")
    print(f"{'='*80}")
    print(f"Total samples: {stats['total_samples']}")
    print(f"\nQuestion types:")
    for q_type, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True):
        pct = count / stats['total_samples'] * 100
        print(f"  {q_type:20s}: {count:5d} ({pct:5.1f}%)")
    
    print(f"\nReasoning hops:")
    for num_hops, count in sorted(stats['by_num_hops'].items()):
        pct = count / stats['total_samples'] * 100
        print(f"  {num_hops} hops: {count:5d} ({pct:5.1f}%)")
    
    print(f"\nBridge entities:")
    print(f"  Samples with bridge entities: {stats['with_bridge_entities']} ({stats['with_bridge_entities']/stats['total_samples']*100:.1f}%)")
    print(f"  Average bridge entities per sample: {stats['avg_bridge_entities']:.2f}")
    
    # Show examples
    print(f"\n{'='*80}")
    print("Example samples:")
    print(f"{'='*80}")
    for i, sample in enumerate(processed_data[:3]):
        print(f"\n[Example {i+1}]")
        print(f"Type: {sample['question_type']}")
        print(f"Question: {sample['question']}")
        print(f"Answer: {sample['answer']}")
        print(f"Bridge entities: {sample['bridge_entities']}")
        if sample['reasoning_chain']:
            print(f"Reasoning chain:")
            for hop in sample['reasoning_chain']:
                print(f"  Hop {hop['hop']}: {hop['subject']} --[{hop['relation']}]--> {hop['object']}")
    
    if args.stats_only:
        print(f"\n{'='*80}")
        print("Stats-only mode: no output file written")
        return
    
    # Write output
    output_path = Path(args.output)
    print(f"\n{'='*80}")
    print(f"Writing to: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for sample in processed_data:
            f.write(json.dumps(sample) + '\n')
    
    print(f"Wrote {len(processed_data)} samples")
    print(f"{'='*80}\n")
    
    print("Next steps for interpretability research:")
    print("1. Load this data and strip away context from questions")
    print("2. Feed questions to your LLM without any context")
    print("3. Use bridge_entities as ground truth for what should be in activations")
    print("4. Apply interpretability techniques (probing, activation patching, etc.)")
    print("5. Check if you can recover bridge entities from model internals")


if __name__ == '__main__':
    main()

