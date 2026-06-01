#!/usr/bin/env python3

import os
import subprocess
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import tempfile

def check_file_accessibility(file_path, cms_xrd_prefix="root://cms-xrd-global.cern.ch/"):
    """
    Check if a ROOT file is accessible using XRootD.
    
    Args:
        file_path (str): Path to the ROOT file
        cms_xrd_prefix (str): XRootD prefix for CMS global redirector
    
    Returns:
        tuple: (file_path, is_accessible)
    """
    if not file_path.strip():
        return file_path, False
    
    # Full path using CMS XRootD global redirector
    full_path = f"{cms_xrd_prefix}{file_path}"
    
    # Create temporary ROOT macro
    root_macro = f'''
    TFile *f = TFile::Open("{full_path}");
    if (f && !f->IsZombie()) {{
        f->Close();
        exit(0);
    }} else {{
        exit(1);
    }}
    '''
    
    try:
        # Create temporary file for ROOT macro
        with tempfile.NamedTemporaryFile(mode='w', suffix='.C', delete=False) as tmp_file:
            tmp_file.write(root_macro)
            tmp_file_path = tmp_file.name
        
        # Run ROOT command
        result = subprocess.run(
            ['root', '-b', '-l', '-q', tmp_file_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30  # 30 second timeout per file
        )
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        # Return result
        return file_path, result.returncode == 0
        
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
        # Clean up temporary file if it exists
        try:
            os.unlink(tmp_file_path)
        except:
            pass
        return file_path, False

def read_file_list(input_file):
    """
    Read file paths from input text file.
    
    Args:
        input_file (str): Path to input text file
    
    Returns:
        list: List of file paths
    """
    try:
        with open(input_file, 'r') as f:
            # Read lines and strip whitespace, filter out empty lines
            file_paths = [line.strip() for line in f if line.strip()]
        return file_paths
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return []

def main():
    parser = argparse.ArgumentParser(description='Check ROOT file accessibility using multi-threading')
    parser.add_argument('input_file', help='Text file containing list of ROOT file paths')
    parser.add_argument('-o', '--output', default='accessible_files.txt', 
                       help='Output file for accessible files (default: accessible_files.txt)')
    parser.add_argument('-t', '--threads', type=int, default=10,
                       help='Number of threads to use (default: 10)')
    parser.add_argument('--prefix', default='root://cms-xrd-global.cern.ch/',
                       help='XRootD prefix (default: root://cms-xrd-global.cern.ch/)')
    
    args = parser.parse_args()
    
    # Read file list
    print(f"Reading file list from {args.input_file}...")
    file_paths = read_file_list(args.input_file)   # defination 2
    
    if not file_paths:
        print("No files to process.")
        return
    
    print(f"Found {len(file_paths)} files to check.")
    
    # Clean up old output file if it exists
    if os.path.exists(args.output):
        os.remove(args.output)
    
    accessible_files = []
    
    # Process files with multi-threading and progress bar
    print(f"Checking file accessibility using {args.threads} threads...")
    
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(check_file_accessibility, file_path, args.prefix): file_path 
            for file_path in file_paths
        }
        
        # Process completed tasks with progress bar
        with tqdm(total=len(file_paths), desc="Checking files", unit="file") as pbar:
            for future in as_completed(future_to_file):
                file_path, is_accessible = future.result()
                
                if is_accessible:
                    accessible_files.append(file_path)
                
                pbar.update(1)
                pbar.set_postfix({
                    'accessible': len(accessible_files),
                    'checked': pbar.n
                })
    
    # Write accessible files to output
    print(f"Writing {len(accessible_files)} accessible files to {args.output}...")
    with open(args.output, 'w') as f:
        for file_path in accessible_files:
            f.write(f"{file_path}\n")
    
    # Summary
    total_files = len(file_paths)
    accessible_count = len(accessible_files)
    inaccessible_count = total_files - accessible_count
    
    print(f"\nSummary:")
    print(f"  Total files checked: {total_files}")
    print(f"  Accessible files: {accessible_count}")
    print(f"  Inaccessible files: {inaccessible_count}")
    print(f"  Success rate: {accessible_count/total_files*100:.1f}%")
    print(f"  Results written to: {args.output}")

if __name__ == "__main__":
    main()