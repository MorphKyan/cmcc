import csv
import os
import re
from collections import Counter

file_path = 'data/media.csv'
temp_file_path = 'data/media_filtered.csv'

def has_chinese(text):
    """Check if the text contains any Chinese character."""
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def get_lcs_length(s1, s2):
    """Calculate the length of the Longest Common Subsequence between s1 and s2."""
    m, n = len(s1), len(s2)
    # Optimization: if either string is shorter than 5, LCS cannot be 5
    if m < 5 or n < 5:
        return 0
    
    # Use 1D array for space optimization (we actually need 2 rows)
    # dp[j] stores LCS of s1[:i] and s2[:j]
    prev = [0] * (n + 1)
    
    for i in range(1, m + 1):
        curr = [0] * (n + 1)
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                curr[j] = prev[j-1] + 1
            else:
                curr[j] = max(prev[j], curr[j-1])
        prev = curr
        
    return prev[n]

def should_keep_basic(row):
    """Apply single-row filters."""
    name = row.get('name', '')
    
    # 1. Length less than 5
    if len(name) < 5:
        return False, "length < 5"
        
    # 2. Contains "测试"
    if '测试' in name:
        return False, "contains '测试'"
        
    # 3. Pure alphanumeric (letters and numbers only)
    # Note: 'No Chinese' check will also catch this, but we keep it for specific reporting
    if re.fullmatch(r'[a-zA-Z0-9]+', name):
        return False, "pure alphanumeric"
    
    # 4. No Chinese characters
    if not has_chinese(name):
        return False, "no Chinese characters"
        
    # 5. Repeated character count > 5
    if name:
        counts = Counter(name)
        if max(counts.values()) > 5:
            return False, "max char frequency > 5"

    return True, ""

try:
    with open(file_path, mode='r', encoding='utf-8', newline='') as infile, \
         open(temp_file_path, mode='w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        
        deleted_stats = {
            "length < 5": 0,
            "contains '测试'": 0,
            "pure alphanumeric": 0,
            "no Chinese characters": 0,
            "max char frequency > 5": 0,
            "duplicate (similarity)": 0
        }
        
        # Buffer to hold rows that pass basic filters for deduplication check
        kept_rows = []
        
        total_deleted = 0
        
        print("Starting filtering process...")
        for row in reader:
            # 1. Basic Filters
            keep, reason = should_keep_basic(row)
            if not keep:
                deleted_stats[reason] += 1
                total_deleted += 1
                continue
            
            # 2. Deduplication (Similarity Check)
            name = row.get('name', '')
            is_duplicate = False
            for kept_row in kept_rows:
                kept_name = kept_row.get('name', '')
                
                # Check for 5 identical characters in consistent order (LCS >= 5)
                # Optimization: Only check if they share at least one character set
                if get_lcs_length(name, kept_name) >= 5:
                    is_duplicate = True
                    # print(f"Duplicate found: '{name}' is similar to kept '{kept_name}'")
                    break
            
            if is_duplicate:
                deleted_stats["duplicate (similarity)"] += 1
                total_deleted += 1
                continue
                
            kept_rows.append(row)
            writer.writerow(row)
            
    # Replace the original file with the filtered file
    os.replace(temp_file_path, file_path)
    print(f"Successfully filtered {file_path}")
    print(f"Total deleted rows: {total_deleted}")
    for reason, count in deleted_stats.items():
        print(f"  - Deleted due to {reason}: {count}")
        
    print(f"Remaining rows: {len(kept_rows)}")

except Exception as e:
    print(f"An error occurred: {e}")
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)
