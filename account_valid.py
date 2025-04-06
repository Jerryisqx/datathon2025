import json
import os
from pathlib import Path
import re
import csv

def load_json_file(filepath):
    """Load and return a JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {str(e)}")
        return None

def normalize_string(s):
    """Normalize strings for comparison by removing spaces, punctuation and converting to lowercase"""
    if not isinstance(s, str):
        return s
    return re.sub(r'[^a-zA-Z0-9]', '', s).lower()

def compare_fields(value1, value2, field_name):
    """Compare two field values, handling different data types and formats"""
    if value1 is None or value2 is None:
        return True  # Skip comparison if either value is None
    
    # Special handling for address fields
    if isinstance(value1, dict) and isinstance(value2, dict):
        # For address objects, we'll compare each component individually
        keys1 = set(value1.keys())
        keys2 = set(value2.keys())
        common_keys = keys1.intersection(keys2)
        
        if not common_keys:
            return True  # No common fields to compare
            
        for key in common_keys:
            if normalize_string(value1[key]) != normalize_string(value2[key]):
                return False
        return True
    
    # For regular fields, normalize and compare
    return normalize_string(value1) == normalize_string(value2)

def validate_client_info(client_dir):
    """Validate information consistency across a client's documents"""
    client_id = os.path.basename(client_dir)
    print(f"\nValidating client {client_id}...")
    
    # List of possible documents and their paths
    documents = {
        "passport": os.path.join(client_dir, "passport.json"),
        "client_profile": os.path.join(client_dir, "client_profile.json"),
        "account_form": os.path.join(client_dir, "account_form.json")
    }
    
    # Load available documents
    loaded_docs = {}
    for doc_type, doc_path in documents.items():
        if os.path.exists(doc_path):
            data = load_json_file(doc_path)
            if data:
                loaded_docs[doc_type] = data
    
    if len(loaded_docs) < 2:
        print(f"  Not enough documents found for client {client_id} to perform validation")
        return False, None
    
    # Collect all field names across documents
    all_fields = {}
    for doc_type, data in loaded_docs.items():
        extract_fields(data, "", doc_type, all_fields)
    
    # Find fields that appear in at least 2 documents
    validation_results = []
    for field_path, docs in all_fields.items():
        if len(docs) >= 2:
            doc_list = list(docs.keys())
            
            # Compare each pair of documents for this field
            for i in range(len(doc_list) - 1):
                for j in range(i + 1, len(doc_list)):
                    doc1 = doc_list[i]
                    doc2 = doc_list[j]
                    value1 = docs[doc1]
                    value2 = docs[doc2]
                    
                    if not compare_fields(value1, value2, field_path):
                        validation_results.append({
                            "field": field_path,
                            "document1": doc1,
                            "value1": value1,
                            "document2": doc2,
                            "value2": value2,
                            "status": "MISMATCH"
                        })
                    else:
                        validation_results.append({
                            "field": field_path,
                            "document1": doc1,
                            "value1": value1, 
                            "document2": doc2,
                            "value2": value2,
                            "status": "MATCH"
                        })
    
    # Display validation results
    has_mismatch = False
    print(f"  Found {len(validation_results)} fields to validate")
    for result in validation_results:
        if result["status"] == "MISMATCH":
            has_mismatch = True
            print(f"  ❌ MISMATCH in field '{result['field']}':")
            print(f"     {result['document1']}: {result['value1']}")
            print(f"     {result['document2']}: {result['value2']}")
    
    if not has_mismatch:
        print("  ✅ All matching fields are consistent!")
    
    # Get parent directory name (format: datathon_partX)
    parent_dir_path = os.path.dirname(client_dir)
    parent_dir_name = os.path.basename(parent_dir_path)
    
    return not has_mismatch, {
        "client_id": client_id,
        "valid": not has_mismatch,
        "part": parent_dir_name,
        "full_path": client_dir,
        "fields_validated": len(validation_results),
        "document_types": list(loaded_docs.keys())
    }

def extract_fields(data, prefix, doc_type, all_fields):
    """Recursively extract all fields from a document"""
    if isinstance(data, dict):
        for key, value in data.items():
            new_prefix = f"{prefix}.{key}" if prefix else key
            if isinstance(value, (dict, list)):
                extract_fields(value, new_prefix, doc_type, all_fields)
            else:
                if new_prefix not in all_fields:
                    all_fields[new_prefix] = {}
                all_fields[new_prefix][doc_type] = value
    elif isinstance(data, list):
        for i, item in enumerate(data):
            new_prefix = f"{prefix}[{i}]"
            extract_fields(item, new_prefix, doc_type, all_fields)

def find_client_directories(root_dir):
    """Find all client directories recursively across all datathon parts"""
    client_dirs = []
    
    # Look for datathon part directories
    datathon_parts = []
    for item in os.listdir(root_dir):
        full_path = os.path.join(root_dir, item)
        if os.path.isdir(full_path) and item.startswith("datathon_evaluation"):
            datathon_parts.append(full_path)
    
    print(f"Found {len(datathon_parts)} datathon part directories: {[os.path.basename(p) for p in datathon_parts]}")
    
    # Look for client directories within each part
    for part_dir in datathon_parts:
        for item in os.listdir(part_dir):
            client_path = os.path.join(part_dir, item)
            if os.path.isdir(client_path) and item.startswith("client_"):
                # Check if this directory contains any of the required documents
                files_in_dir = os.listdir(client_path)
                if any(f in files_in_dir for f in ["passport.json", "client_profile.json", "account_form.json"]):
                    client_dirs.append(client_path)
    
    return client_dirs

def save_validation_results(results, output_file):
    """Save validation results to CSV file"""
    if not results:
        print("No results to save.")
        return
    
    # with open(output_file, 'w', newline='') as csvfile:
    #     fieldnames = ["client_id", "valid", "part", "full_path", "fields_validated", "document_types"]
    #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
    #     writer.writeheader()
    #     for result in results:
    #         writer.writerow(result)
    
    # print(f"\nResults saved to {output_file}")
    
    # Also save a list of just the valid client IDs
    valid_clients = [r["client_id"] for r in results if r["valid"]]
    valid_clients_file = output_file.replace(".csv", "_valid_clients.txt")
    
    with open(valid_clients_file, 'w') as f:
        for client_id in valid_clients:
            f.write(f"{client_id}\n")
            
    print(f"List of {len(valid_clients)} valid clients saved to {valid_clients_file}")
    
    # Save a list of invalid client IDs
    invalid_clients = [r["client_id"] for r in results if not r["valid"]]
    invalid_clients_file = output_file.replace(".csv", "_invalid_clients.txt")
    
    with open(invalid_clients_file, 'w') as f:
        for client_id in invalid_clients:
            f.write(f"{client_id}\n")
            
    print(f"List of {len(invalid_clients)} invalid clients saved to {invalid_clients_file}")
    
    # Count valid clients per datathon part
    part_counts = {}
    for result in results:
        if result["valid"]:
            part = result["part"]
            if part not in part_counts:
                part_counts[part] = 0
            part_counts[part] += 1
    
    print("\nValid clients per datathon part:")
    for part, count in part_counts.items():
        print(f"  {part}: {count} valid clients")

def main():
    # Starting directory (the datathon folder)
    root_dir = Path(__file__).parent
    
    print("Looking for client directories across all datathon parts...")
    client_dirs = find_client_directories(root_dir)
    print(f"Found {len(client_dirs)} client directories")
    
    # Process each client directory
    validation_results = []
    valid_count = 0
    
    for client_dir in client_dirs:
        is_valid, result = validate_client_info(client_dir)
        if result:
            validation_results.append(result)
            if is_valid:
                valid_count += 1
    
    print(f"\nValidation complete: {valid_count} out of {len(client_dirs)} clients have consistent information.")
    
    # Save results to CSV
    output_file = os.path.join(root_dir, "validation_results.csv")
    save_validation_results(validation_results, output_file)

if __name__ == "__main__":
    main()