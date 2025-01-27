import re
import pandas as pd
import networkx as nx
import numpy as np
from collections import Counter, defaultdict
import os
import logging
from pathlib import Path
from datetime import datetime
from pdfminer.high_level import extract_text
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
import spacy
import json
from sklearn.manifold import TSNE
from umap import UMAP
from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
from sklearn.metrics.pairwise import cosine_similarity

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailNetworkAnalyzer:
    def __init__(self):
        # Add at the start of __init__
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        
        # Set default json_data directory
        self.json_output_dir = os.path.join(os.path.dirname(__file__), 'json_data')
        
        # Initialize entity tracking
        self.entity_mentions = Counter()
        self.entity_connections = defaultdict(lambda: defaultdict(int))
        
        # Initialize spaCy with increased max length
        self.nlp = spacy.load("en_core_web_sm")
        self.nlp.max_length = 7000000  # Increase max length to 5M characters
        
        # Initialize document storage
        self.processed_documents = []
        
        # Initialize topic modeling components
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.topic_model = BERTopic(
            embedding_model=self.sentence_model,
            umap_model=UMAP(
                n_neighbors=15,
                n_components=2,
                min_dist=0.0,
                metric='cosine'
            )
        )

    def clear_output_directory(self):
        """Clear and recreate the output directory"""
        if os.path.exists(self.json_output_dir):
            for file in os.listdir(self.json_output_dir):
                os.remove(os.path.join(self.json_output_dir, file))
        os.makedirs(self.json_output_dir, exist_ok=True)

    def process_document(self, file_path):
        """Process a single document file (PDF or TXT)"""
        logger.info(f"Processing: {file_path}")
        
        try:
            # Extract text based on file type
            if file_path.endswith('.pdf'):
                text = extract_text(file_path).strip()
            else:  # .txt file
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read().strip()
            
            if not text:
                logger.warning(f"No text extracted from: {file_path}")
                return None
                
            logger.info(f"Extracted {len(text)} characters from {file_path}")
            
            # Store text for topic modeling
            self.processed_documents.append({
                'path': str(file_path),
                'text': text
            })
            
            # Extract entities using spaCy
            doc = self.nlp(text)
            logger.info(f"NLP processing complete for {file_path}")
            
            # Track entities in this document
            doc_entities = set()
            entity_pairs = []  # Store co-occurring pairs
            
            for ent in doc.ents:
                if ent.label_ in ['ORG', 'PERSON', 'GPE']:  # Organizations, People, Locations
                    doc_entities.add(ent.text)
            
            # Create pairs of co-occurring entities
            entities_list = list(doc_entities)
            for i in range(len(entities_list)):
                for j in range(i + 1, len(entities_list)):
                    entity_pairs.append((entities_list[i], entities_list[j]))
            
            # Return entity data
            return {
                'path': file_path,
                'entities': list(doc_entities),
                'entity_pairs': entity_pairs
            }
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            return None

    def analyze_directory(self, doc_dir, test_run=False):
        """Analyze all documents in directory"""
        logger.info(f"Scanning directory: {doc_dir}")
        
        # Recursively find all .txt and .pdf files
        doc_files = []
        for root, _, files in os.walk(doc_dir):
            for f in files:
                if f.endswith(('.txt', '.pdf')):
                    doc_files.append(os.path.join(root, f))
        
        logger.info(f"Found {len(doc_files)} document files")
        
        if len(doc_files) == 0:
            logger.error(f"No documents found in {doc_dir}. Please check the directory path.")
            raise ValueError(f"No documents found in {doc_dir}")
        
        if test_run:
            doc_files = doc_files[:50]  # Process 50 files in test mode
            logger.info(f"TEST RUN: Processing {len(doc_files)} documents")
        
        for file_path in tqdm(doc_files, desc="Processing documents"):
            try:
                result = self.process_document(file_path)
                if result:
                    # Store entity relationships
                    for entity in result['entities']:
                        self.entity_mentions[entity] += 1
                    
                    # Initialize entity connections
                    for entity1, entity2 in result['entity_pairs']:
                        if entity1 not in self.entity_connections:
                            self.entity_connections[entity1] = defaultdict(int)
                        if entity2 not in self.entity_connections:
                            self.entity_connections[entity2] = defaultdict(int)
                        
                        # Add bidirectional connection
                        self.entity_connections[entity1][entity2] += 1
                        self.entity_connections[entity2][entity1] += 1
                    
                    logger.info(f"Successfully processed: {file_path}")
                    
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {str(e)}")
                continue
        
        logger.info(f"Processed {len(doc_files)} documents")

    def save_json(self, data, filename):
        """Helper method to save JSON data to the json_data directory"""
        # Convert to absolute path if not already
        if not os.path.isabs(self.json_output_dir):
            self.json_output_dir = os.path.abspath(self.json_output_dir)
        
        filepath = os.path.join(self.json_output_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {filename} to {filepath}")

    def _create_umap_visualization(self, embeddings, topics):
        """Create UMAP visualization data"""
        umap_model = UMAP(n_components=2, metric='cosine')
        umap_embeddings = umap_model.fit_transform(embeddings)
        
        return {
            'points': umap_embeddings.tolist(),
            'topics': topics,
            'labels': self.topic_model.get_topic_info()['Name'].tolist()
        }

    def _create_tsne_visualization(self, embeddings, topics):
        """Create t-SNE visualization data"""
        tsne = TSNE(n_components=2)
        tsne_embeddings = tsne.fit_transform(embeddings)
        
        return {
            'points': tsne_embeddings.tolist(),
            'topics': topics,
            'labels': self.topic_model.get_topic_info()['Name'].tolist()
        }

    def _create_topic_similarity_network(self):
        """Create topic similarity network"""
        # Get topic info
        topic_info = self.topic_model.get_topic_info()
        topics = topic_info.index.tolist()
        
        # Calculate similarities using cosine similarity of topic embeddings
        topic_embeddings = []
        nodes = []
        
        for topic in topics:
            topic_words = self.topic_model.get_topic(topic)
            if isinstance(topic_words, bool):  # Skip if no words returned
                continue
            
            # Get topic representation
            try:
                words = [word for word, _ in topic_words]
                if words:  # Only process if we have words
                    topic_embeddings.append(self.sentence_model.encode(' '.join(words)))
                    nodes.append({
                        'id': str(topic),
                        'label': ' '.join(words[:3]),
                        'size': len(words)
                    })
            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping topic {topic}: {str(e)}")
                continue
        
        if not topic_embeddings:  # If no valid topics found
            return {'nodes': [], 'links': []}
        
        # Convert to numpy array
        topic_embeddings = np.array(topic_embeddings)
        
        # Calculate cosine similarity
        similarities = cosine_similarity(topic_embeddings)
        
        links = []
        # Create links for similar topics
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                similarity = similarities[i][j]
                if similarity > 0.2:  # Threshold for visualization
                    links.append({
                        'source': nodes[i]['id'],
                        'target': nodes[j]['id'],
                        'value': float(similarity)
                    })
        
        return {'nodes': nodes, 'links': links}

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze documents for topics and entities')
    parser.add_argument('--pdf_dir', required=True, help='Directory containing documents to analyze')
    parser.add_argument('--output_dir', required=True, help='Directory for output files')
    parser.add_argument('--test', action='store_true', help='Run in test mode (process only 5 files)')
    
    args = parser.parse_args()
    
    analyzer = EmailNetworkAnalyzer()
    
    # Override the default json_data directory with the one from command line
    analyzer.json_output_dir = args.output_dir
    analyzer.clear_output_directory()  # Clear AFTER setting the correct directory
    
    # Run the analysis
    analyzer.analyze_directory(args.pdf_dir, test_run=args.test)
    
    # Save entity network data
    top_entities = analyzer.entity_mentions.most_common(10)
    entity_network_data = {
        "nodes": [
            {"id": entity, "group": 1, "size": count}
            for entity, count in top_entities
        ],
        "links": []
    }
    
    entity_names = [e[0] for e in top_entities]
    for i, entity1 in enumerate(entity_names):
        for j, entity2 in enumerate(entity_names[i+1:], i+1):
            weight = analyzer.entity_connections[entity1][entity2]
            if weight > 0:
                entity_network_data["links"].append({
                    "source": entity1,
                    "target": entity2,
                    "value": weight
                })
    
    # Generate topic model visualizations
    logger.info("Generating topic model visualizations...")
    documents = [doc['text'] for doc in analyzer.processed_documents]
    embeddings = analyzer.sentence_model.encode(documents, show_progress_bar=True)
    topics, probs = analyzer.topic_model.fit_transform(documents, embeddings)
    
    # Save topic visualizations
    topic_vis = {
        'umap': analyzer._create_umap_visualization(embeddings, topics),
        'tsne': analyzer._create_tsne_visualization(embeddings, topics),
        'similarity': analyzer._create_topic_similarity_network(),
        'info': analyzer.topic_model.get_topic_info().to_dict('records')
    }
    
    for name, data in topic_vis.items():
        analyzer.save_json(data, f'topic_{name}_analysis.json')
    
    analyzer.save_json(entity_network_data, 'entity_network.json')
    
    logger.info("Analysis complete. JSON files have been saved to the output directory.")