#!/usr/bin/env python3
"""
Function Analysis Script for LogiStay
Analyzes Python and JavaScript functions to find unused and missing definitions
"""

import re
import os
import csv
import json
from collections import defaultdict
from pathlib import Path

class FunctionAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.python_defs = {}  # {function_name: [(file, line, full_def)]}
        self.python_calls = defaultdict(list)  # {function_name: [(file, line, context)]}
        self.js_defs = {}
        self.js_calls = defaultdict(list)
        
        # Load whitelist configuration
        self.whitelist = self.load_whitelist()
        
        # Frappe framework whitelisted patterns
        self.frappe_whitelist_patterns = [
            r'@frappe\.whitelist',
            r'def\s+validate\(',
            r'def\s+before_save\(',
            r'def\s+after_insert\(',
            r'def\s+on_update\(',
            r'def\s+on_submit\(',
            r'def\s+on_cancel\(',
            r'def\s+before_insert\(',
            r'def\s+get_context\(',
            r'def\s+get_data\(',
            r'def\s+execute\(',  # for patches
        ]
        
        # Build comprehensive ignore set from whitelist
        self.ignore_functions = set()
        if self.whitelist:
            for category in ['frappe_framework_functions', 'frappe_decorators', 
                           'frappe_lifecycle_methods', 'python_builtins', 
                           'string_methods', 'collection_methods', 'sql_keywords',
                           'third_party_common', 'custom_app_whitelist']:
                if category in self.whitelist:
                    self.ignore_functions.update(self.whitelist[category])
    
    def load_whitelist(self):
        """Load whitelist configuration from JSON file"""
        try:
            with open('reports/whitelist.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load whitelist.json: {e}")
            return None
        
    def parse_python_definitions(self, defs_file):
        """Parse Python function definitions from grep output"""
        if not os.path.exists(defs_file):
            return
            
        with open(defs_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                # Format: ./path/file.py:line_num:def function_name(
                match = re.match(r'([^:]+):(\d+):(.+)', line)
                if match:
                    file_path, line_num, definition = match.groups()
                    
                    # Extract function name
                    func_match = re.search(r'def\s+([A-Za-z_]\w*)\s*\(', definition)
                    if func_match:
                        func_name = func_match.group(1)
                        if func_name not in self.python_defs:
                            self.python_defs[func_name] = []
                        self.python_defs[func_name].append((file_path, line_num, definition))
    
    def parse_python_calls(self, calls_file):
        """Parse Python function calls from grep output"""
        if not os.path.exists(calls_file):
            return
            
        with open(calls_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                # Skip lines that are definitions or class declarations
                if re.search(r'^\s*def\s|^\s*class\s', line):
                    continue
                    
                # Format: ./path/file.py:line_num:context
                match = re.match(r'([^:]+):(\d+):(.+)', line)
                if match:
                    file_path, line_num, context = match.groups()
                    
                    # Extract function calls
                    func_calls = re.findall(r'([A-Za-z_]\w*)\s*\(', context)
                    for func_name in func_calls:
                        # Skip common built-ins and keywords
                        if func_name not in ['if', 'for', 'while', 'try', 'except', 'with', 'print', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple']:
                            self.python_calls[func_name].append((file_path, line_num, context))
    
    def is_frappe_whitelisted(self, file_path, func_name):
        """Check if function is whitelisted by Frappe framework"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
                # Look for whitelist decorators or special method names
                for pattern in self.frappe_whitelist_patterns:
                    if re.search(pattern, content):
                        return True
                        
                # Check if function has @frappe.whitelist decorator
                func_pattern = rf'@frappe\.whitelist.*?\ndef\s+{re.escape(func_name)}\s*\('
                if re.search(func_pattern, content, re.DOTALL):
                    return True
                    
        except Exception:
            pass
            
        return False
    
    def find_unused_functions(self):
        """Find functions that are defined but never called"""
        unused = []
        
        for func_name, definitions in self.python_defs.items():
            # Skip if function is called anywhere
            if func_name in self.python_calls:
                continue
                
            # Skip if function is whitelisted by framework
            is_whitelisted = False
            for file_path, line_num, definition in definitions:
                if self.is_frappe_whitelisted(file_path, func_name):
                    is_whitelisted = True
                    break
                    
            if not is_whitelisted:
                for file_path, line_num, definition in definitions:
                    unused.append({
                        'function_name': func_name,
                        'file_path': file_path,
                        'line_number': line_num,
                        'definition': definition,
                        'type': 'unused'
                    })
        
        return unused
    
    def find_missing_definitions(self):
        """Find function calls that have no corresponding definition"""
        missing = []
        
        for func_name, calls in self.python_calls.items():
            # Skip if function is defined
            if func_name in self.python_defs:
                continue
                
            # Skip common built-ins and framework functions
            if func_name in self.ignore_functions:
                continue
                
            for file_path, line_num, context in calls:
                missing.append({
                    'function_name': func_name,
                    'file_path': file_path,
                    'line_number': line_num,
                    'context': context,
                    'type': 'missing'
                })
        
        return missing
    
    def generate_reports(self):
        """Generate CSV reports for unused and missing functions"""
        unused = self.find_unused_functions()
        missing = self.find_missing_definitions()
        
        # Write unused functions report
        with open('reports/unused_functions.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['function_name', 'file_path', 'line_number', 'definition', 'type'])
            writer.writeheader()
            writer.writerows(unused)
        
        # Write missing definitions report
        with open('reports/missing_definitions.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['function_name', 'file_path', 'line_number', 'context', 'type'])
            writer.writeheader()
            writer.writerows(missing)
        
        return unused, missing

def main():
    analyzer = FunctionAnalyzer('.')
    
    # Parse extracted data
    analyzer.parse_python_definitions('reports/python_defs.txt')
    analyzer.parse_python_calls('reports/python_calls.txt')
    
    # Generate reports
    unused, missing = analyzer.generate_reports()
    
    print(f"Analysis Complete:")
    print(f"- Found {len(unused)} unused functions")
    print(f"- Found {len(missing)} missing function definitions")
    print(f"- Reports saved to reports/unused_functions.csv and reports/missing_definitions.csv")
    
    # Show top 10 unused functions
    if unused:
        print(f"\nTop 10 Unused Functions:")
        for i, func in enumerate(unused[:10]):
            print(f"{i+1}. {func['function_name']} in {func['file_path']}:{func['line_number']}")
    
    # Show top 10 missing definitions
    if missing:
        print(f"\nTop 10 Missing Definitions:")
        func_counts = defaultdict(int)
        for func in missing:
            func_counts[func['function_name']] += 1
        
        for i, (func_name, count) in enumerate(sorted(func_counts.items(), key=lambda x: x[1], reverse=True)[:10]):
            print(f"{i+1}. {func_name} (called {count} times)")

if __name__ == '__main__':
    main()