#!/usr/bin/env python3
"""
Obsidian Backlink Checker GUI
A simple GUI application to open Obsidian and check backlinks in vaults.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import os
import re
import subprocess
import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Set, Tuple
import threading

# AI Search functionality (optional)
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False



class ObsidianBacklinkChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("Obsidian Backlink Checker")
        self.root.geometry("800x600")
        
        # Variables
        self.vault_path = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")
        self.search_term = tk.StringVar()
        self.case_sensitive = tk.BooleanVar()
        self.whole_word = tk.BooleanVar()
        self.use_regex = tk.BooleanVar()
        self.broken_links = []
        self.search_results = []
        self.ai_model = None
        self.ai_embeddings = None
        self.ai_documents = []
        self.ai_search_enabled = AI_AVAILABLE
        
        
        self.setup_ui()
        self.detect_obsidian_vaults()
        
    def setup_ui(self):
        """Create the GUI interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Obsidian Backlink Checker", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Vault selection
        ttk.Label(main_frame, text="Obsidian Vault:").grid(row=1, column=0, sticky=tk.W, pady=5)
        vault_entry = ttk.Entry(main_frame, textvariable=self.vault_path, width=50)
        vault_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        browse_btn = ttk.Button(main_frame, text="Browse", command=self.browse_vault)
        browse_btn.grid(row=1, column=2, pady=5, padx=(5, 0))
        
        # Search section
        search_frame = ttk.LabelFrame(main_frame, text="Search & Export", padding="5")
        search_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        search_frame.columnconfigure(1, weight=1)
        
        # Search term
        ttk.Label(search_frame, text="Search for:").grid(row=0, column=0, sticky=tk.W, pady=2)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_term, width=40)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Search options
        options_frame = ttk.Frame(search_frame)
        options_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Checkbutton(options_frame, text="Case sensitive", variable=self.case_sensitive).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(options_frame, text="Whole word", variable=self.whole_word).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(options_frame, text="Regular expression", variable=self.use_regex).pack(side=tk.LEFT)
        
        # Search buttons
        search_btn_frame = ttk.Frame(search_frame)
        search_btn_frame.grid(row=2, column=0, columnspan=2, pady=5)
        
        search_btn = ttk.Button(search_btn_frame, text="🔍 Search", command=self.search_vault_threaded)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        export_search_btn = ttk.Button(search_btn_frame, text="📄 Export Search Results", command=self.export_search_results)
        export_search_btn.pack(side=tk.LEFT, padx=5)
        
        # AI Search section (if available)
        if self.ai_search_enabled:
            ai_frame = ttk.LabelFrame(main_frame, text="🤖 AI Concept Search (Beta)", padding="5")
            ai_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
            ai_frame.columnconfigure(1, weight=1)
            
            # AI search term
            ttk.Label(ai_frame, text="Concept:").grid(row=0, column=0, sticky=tk.W, pady=2)
            self.ai_search_term = tk.StringVar()
            ai_search_entry = ttk.Entry(ai_frame, textvariable=self.ai_search_term, width=40)
            ai_search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
            
            # AI search buttons
            ai_btn_frame = ttk.Frame(ai_frame)
            ai_btn_frame.grid(row=1, column=0, columnspan=2, pady=5)
            
            ai_search_btn = ttk.Button(ai_btn_frame, text="🤖 AI Concept Search", command=self.ai_search_threaded)
            ai_search_btn.pack(side=tk.LEFT, padx=5)
            
            build_index_btn = ttk.Button(ai_btn_frame, text="🔄 Build AI Index", command=self.build_ai_index_threaded)
            build_index_btn.pack(side=tk.LEFT, padx=5)
            
            similar_btn = ttk.Button(ai_btn_frame, text="🔍 Find Similar Files", command=self.find_similar_files_threaded)
            similar_btn.pack(side=tk.LEFT, padx=5)
            
            # Update grid row numbers for elements below
            current_row = 4
        else:
            # Show message about AI availability
            ai_info_frame = ttk.LabelFrame(main_frame, text="ℹ️ AI Search Info", padding="5")
            ai_info_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
            
            info_text = "AI Concept Search is available! Run: ./run_with_ai.sh obsidian_backlink_checker.py"
            ttk.Label(ai_info_frame, text=info_text, foreground="blue").pack()
            
            current_row = 4
        
        
        main_frame.rowconfigure(current_row + 2, weight=1)
        
        # Backlink check buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=current_row, column=0, columnspan=3, pady=20)
        
        # Main action button
        self.main_btn = ttk.Button(btn_frame, text="Open Obsidian & Check Backlinks", 
                                  command=self.run_check_threaded, style='Accent.TButton')
        self.main_btn.pack(side=tk.LEFT, padx=5)
        
        # Individual action buttons
        check_only_btn = ttk.Button(btn_frame, text="Check Backlinks Only", 
                                   command=self.check_backlinks_only_threaded)
        check_only_btn.pack(side=tk.LEFT, padx=5)
        
        open_only_btn = ttk.Button(btn_frame, text="Open Obsidian Only", 
                                  command=self.open_obsidian)
        open_only_btn.pack(side=tk.LEFT, padx=5)
        
        # Exit button
        exit_btn = ttk.Button(btn_frame, text="Exit", 
                             command=self.exit_application)
        exit_btn.pack(side=tk.RIGHT, padx=5)
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=current_row + 1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        status_frame.columnconfigure(0, weight=1)
        
        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, sticky=tk.W)
        status_label = ttk.Label(status_frame, textvariable=self.status_var, foreground="blue")
        status_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.grid(row=0, column=2, sticky=tk.E, padx=(10, 0))
        
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="5")
        results_frame.grid(row=current_row + 2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=20)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Export button
        export_btn = ttk.Button(results_frame, text="Export Results", command=self.export_results)
        export_btn.grid(row=1, column=0, pady=(5, 0))
        
    def detect_obsidian_vaults(self):
        """Try to detect Obsidian vaults automatically"""
        possible_paths = [
            os.path.expanduser("~/Documents/Obsidian"),
            os.path.expanduser("~/Obsidian"),
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Desktop"),
        ]
        
        for base_path in possible_paths:
            if os.path.exists(base_path):
                for item in os.listdir(base_path):
                    item_path = os.path.join(base_path, item)
                    if os.path.isdir(item_path) and self.is_obsidian_vault(item_path):
                        self.vault_path.set(item_path)
                        self.log_result(f"Auto-detected Obsidian vault: {item_path}")
                        return
        
        self.log_result("No Obsidian vault auto-detected. Please select manually.")
        
    def is_obsidian_vault(self, path):
        """Check if a directory is an Obsidian vault"""
        obsidian_config = os.path.join(path, ".obsidian")
        return os.path.exists(obsidian_config) and os.path.isdir(obsidian_config)
        
    def browse_vault(self):
        """Browse for Obsidian vault directory"""
        directory = filedialog.askdirectory(
            title="Select Obsidian Vault Directory",
            initialdir=os.path.expanduser("~")
        )
        if directory:
            self.vault_path.set(directory)
            
    def open_obsidian(self):
        """Open Obsidian application on macOS"""
        try:
            self.status_var.set("Opening Obsidian...")
            self.root.update()
            
            # Try to open Obsidian with the specific vault
            vault = self.vault_path.get()
            if vault and os.path.exists(vault):
                # Open Obsidian with specific vault
                subprocess.run(['open', '-a', 'Obsidian', vault], check=True)
                self.log_result(f"✅ Opened Obsidian with vault: {vault}")
            else:
                # Just open Obsidian
                subprocess.run(['open', '-a', 'Obsidian'], check=True)
                self.log_result("✅ Opened Obsidian")
                
            self.status_var.set("Obsidian opened successfully")
            
        except subprocess.CalledProcessError:
            error_msg = "❌ Failed to open Obsidian. Make sure Obsidian is installed."
            self.log_result(error_msg)
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Error opening Obsidian")
        except Exception as e:
            error_msg = f"❌ Unexpected error: {str(e)}"
            self.log_result(error_msg)
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Error")
            
    def run_check_threaded(self):
        """Run the full check in a separate thread"""
        threading.Thread(target=self.run_full_check, daemon=True).start()
        
    def check_backlinks_only_threaded(self):
        """Run only backlink check in a separate thread"""
        threading.Thread(target=self.check_backlinks, daemon=True).start()
        
    def run_full_check(self):
        """Open Obsidian and check backlinks"""
        self.main_btn.config(state='disabled')
        self.progress.start()
        
        try:
            # First open Obsidian
            self.open_obsidian()
            
            # Then check backlinks
            self.check_backlinks()
            
        finally:
            self.progress.stop()
            self.main_btn.config(state='normal')
            
    def check_backlinks(self):
        """Check all backlinks in the Obsidian vault"""
        vault = self.vault_path.get()
        
        if not vault or not os.path.exists(vault):
            error_msg = "❌ Please select a valid Obsidian vault directory"
            self.log_result(error_msg)
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Invalid vault path")
            return
            
        if not self.is_obsidian_vault(vault):
            error_msg = "❌ Selected directory is not an Obsidian vault"
            self.log_result(error_msg)
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Not an Obsidian vault")
            return
            
        self.status_var.set("Scanning vault...")
        self.root.update()
        
        try:
            # Clear previous results
            self.broken_links = []
            
            # Find all markdown files
            md_files = list(Path(vault).rglob("*.md"))
            total_files = len(md_files)
            
            self.log_result(f"🔍 Scanning {total_files} markdown files in vault: {vault}")
            self.log_result("-" * 60)
            
            # Get all file names (without extension) for reference
            all_notes = {f.stem for f in md_files}
            
            broken_count = 0
            total_links = 0
            
            for i, md_file in enumerate(md_files):
                self.status_var.set(f"Checking file {i+1}/{total_files}: {md_file.name}")
                self.root.update()
                
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Find all wiki-style links [[link]]
                    wiki_links = re.findall(r'\[\[([^\]]+)\]\]', content)
                    
                    # Find all markdown links [text](link)
                    md_links = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', content)
                    
                    for link in wiki_links:
                        total_links += 1
                        # Handle links with aliases [[link|alias]]
                        actual_link = link.split('|')[0].strip()
                        
                        # Check if the target note exists
                        if actual_link not in all_notes:
                            # Check if it's a file with extension
                            target_path = Path(vault) / f"{actual_link}.md"
                            if not target_path.exists():
                                self.broken_links.append({
                                    'file': str(md_file.relative_to(vault)),
                                    'link': link,
                                    'type': 'wiki'
                                })
                                broken_count += 1
                    
                    for text, link in md_links:
                        total_links += 1
                        # Only check local markdown links
                        if link.endswith('.md') and not link.startswith(('http', 'https', 'ftp')):
                            target_path = md_file.parent / link
                            if not target_path.exists():
                                self.broken_links.append({
                                    'file': str(md_file.relative_to(vault)),
                                    'link': link,
                                    'type': 'markdown'
                                })
                                broken_count += 1
                                
                except Exception as e:
                    self.log_result(f"❌ Error reading {md_file.name}: {str(e)}")
                    
            # Display results
            self.display_results(total_files, total_links, broken_count)
            
        except Exception as e:
            error_msg = f"❌ Error during backlink check: {str(e)}"
            self.log_result(error_msg)
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Error during check")
            
    def display_results(self, total_files, total_links, broken_count):
        """Display the results of the backlink check"""
        self.log_result("\n" + "=" * 60)
        self.log_result("📊 BACKLINK CHECK SUMMARY")
        self.log_result("=" * 60)
        self.log_result(f"Files scanned: {total_files}")
        self.log_result(f"Total links found: {total_links}")
        self.log_result(f"Broken links: {broken_count}")
        
        if broken_count == 0:
            self.log_result("\n🎉 All backlinks are working correctly!")
            self.status_var.set("All backlinks valid")
        else:
            self.log_result(f"\n⚠️  Found {broken_count} broken links:")
            self.log_result("-" * 40)
            
            for broken_link in self.broken_links:
                link_type = "[[...]]" if broken_link['type'] == 'wiki' else "[...](…)"
                self.log_result(f"📄 {broken_link['file']}")
                self.log_result(f"   🔗 {link_type}: {broken_link['link']}")
                self.log_result("")
                
            self.status_var.set(f"Found {broken_count} broken links")
            
        self.log_result("=" * 60)
        
    def log_result(self, message):
        """Add a message to the results text area"""
        self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
        self.root.update()
        
    def export_results(self):
        """Export results to a text file"""
        if not self.results_text.get("1.0", tk.END).strip():
            messagebox.showwarning("Warning", "No results to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Results As"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.results_text.get("1.0", tk.END))
                messagebox.showinfo("Success", f"Results exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results: {str(e)}")
                
    def search_vault_threaded(self):
        """Run vault search in a separate thread"""
        threading.Thread(target=self.search_vault, daemon=True).start()
        
    def search_vault(self):
        """Search for keywords in the Obsidian vault"""
        vault = self.vault_path.get()
        search_term = self.search_term.get().strip()
        
        if not search_term:
            messagebox.showwarning("Warning", "Please enter a search term")
            return
            
        if not vault or not os.path.exists(vault):
            error_msg = "❌ Please select a valid Obsidian vault directory"
            self.log_result(error_msg)
            messagebox.showerror("Error", error_msg)
            return
            
        self.progress.start()
        self.status_var.set("Searching vault...")
        self.root.update()
        
        try:
            # Clear previous search results
            self.search_results = []
            
            # Find all markdown files
            md_files = list(Path(vault).rglob("*.md"))
            total_files = len(md_files)
            
            self.log_result(f"\n🔍 Searching for '{search_term}' in {total_files} files...")
            self.log_result("=" * 60)
            
            # Prepare search pattern
            if self.use_regex.get():
                try:
                    flags = 0 if self.case_sensitive.get() else re.IGNORECASE
                    pattern = re.compile(search_term, flags)
                except re.error as e:
                    error_msg = f"❌ Invalid regex pattern: {e}"
                    self.log_result(error_msg)
                    messagebox.showerror("Regex Error", error_msg)
                    return
            else:
                # Escape special regex characters for literal search
                escaped_term = re.escape(search_term)
                if self.whole_word.get():
                    escaped_term = r'\b' + escaped_term + r'\b'
                flags = 0 if self.case_sensitive.get() else re.IGNORECASE
                pattern = re.compile(escaped_term, flags)
            
            total_matches = 0
            files_with_matches = 0
            
            for i, md_file in enumerate(md_files):
                self.status_var.set(f"Searching file {i+1}/{total_files}: {md_file.name}")
                self.root.update()
                
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    file_matches = []
                    for line_num, line in enumerate(lines, 1):
                        matches = list(pattern.finditer(line))
                        if matches:
                            file_matches.append({
                                'line_num': line_num,
                                'line_content': line.rstrip(),
                                'matches': len(matches)
                            })
                    
                    if file_matches:
                        files_with_matches += 1
                        file_total_matches = sum(m['matches'] for m in file_matches)
                        total_matches += file_total_matches
                        
                        self.search_results.append({
                            'file_path': md_file,
                            'relative_path': str(md_file.relative_to(vault)),
                            'matches': file_matches,
                            'total_matches': file_total_matches
                        })
                        
                except Exception as e:
                    self.log_result(f"❌ Error reading {md_file.name}: {str(e)}")
            
            # Display search results
            self.display_search_results(search_term, total_files, files_with_matches, total_matches)
            
        except Exception as e:
            error_msg = f"❌ Error during search: {str(e)}"
            self.log_result(error_msg)
            messagebox.showerror("Error", error_msg)
        finally:
            self.progress.stop()
            self.status_var.set("Search completed")
    
    def display_search_results(self, search_term, total_files, files_with_matches, total_matches):
        """Display the search results"""
        self.log_result("\n" + "=" * 60)
        self.log_result(f"📊 SEARCH RESULTS FOR: '{search_term}'")
        self.log_result("=" * 60)
        self.log_result(f"Files scanned: {total_files}")
        self.log_result(f"Files with matches: {files_with_matches}")
        self.log_result(f"Total matches: {total_matches}")
        
        if total_matches == 0:
            self.log_result(f"\n❌ No matches found for '{search_term}'")
        else:
            self.log_result(f"\n✅ Found {total_matches} matches in {files_with_matches} files:")
            self.log_result("-" * 60)
            
            for result in self.search_results:
                self.log_result(f"\n📄 {result['relative_path']} ({result['total_matches']} matches)")
                
                # Show up to 5 matches per file in the GUI
                for i, match in enumerate(result['matches'][:5]):
                    line_preview = match['line_content'][:100] + "..." if len(match['line_content']) > 100 else match['line_content']
                    self.log_result(f"   Line {match['line_num']}: {line_preview}")
                
                if len(result['matches']) > 5:
                    self.log_result(f"   ... and {len(result['matches']) - 5} more matches")
        
        self.log_result("=" * 60)
    
    def export_search_results(self):
        """Export search results to a formatted markdown file"""
        if not self.search_results:
            messagebox.showwarning("Warning", "No search results to export. Please run a search first.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")],
            title="Export Search Results As"
        )
        
        if file_path:
            try:
                self.create_search_export(file_path)
                messagebox.showinfo("Success", f"Search results exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export search results: {str(e)}")
    
    def create_search_export(self, file_path):
        """Create a formatted markdown export of search results"""
        search_term = self.search_term.get()
        vault_name = Path(self.vault_path.get()).name
        
        total_matches = sum(r['total_matches'] for r in self.search_results)
        files_with_matches = len(self.search_results)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"# Search Results: '{search_term}'\n\n")
            f.write(f"**Vault:** {vault_name}\n")
            f.write(f"**Search Term:** `{search_term}`\n")
            f.write(f"**Search Options:**\n")
            f.write(f"- Case Sensitive: {'Yes' if self.case_sensitive.get() else 'No'}\n")
            f.write(f"- Whole Word: {'Yes' if self.whole_word.get() else 'No'}\n")
            f.write(f"- Regular Expression: {'Yes' if self.use_regex.get() else 'No'}\n\n")
            
            f.write(f"**Summary:**\n")
            f.write(f"- Files with matches: {files_with_matches}\n")
            f.write(f"- Total matches: {total_matches}\n\n")
            
            f.write("---\n\n")
            
            # Results
            for result in self.search_results:
                f.write(f"## 📄 {result['relative_path']}\n\n")
                f.write(f"**Matches found:** {result['total_matches']}\n\n")
                
                for match in result['matches']:
                    f.write(f"**Line {match['line_num']}:**\n")
                    f.write(f"```\n{match['line_content']}\n```\n\n")
                
                f.write("---\n\n")
            
            # Footer
            from datetime import datetime
            f.write(f"*Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*\n")
    
    def build_ai_index_threaded(self):
        """Build AI index in a separate thread"""
        if not self.ai_search_enabled:
            messagebox.showwarning("AI Not Available", "AI search dependencies not installed.")
            return
        threading.Thread(target=self.build_ai_index, daemon=True).start()
    
    def build_ai_index(self):
        """Build semantic search index for the vault"""
        vault = self.vault_path.get()
        
        if not vault or not os.path.exists(vault):
            error_msg = "❌ Please select a valid Obsidian vault directory"
            self.log_result(error_msg)
            messagebox.showerror("Error", error_msg)
            return
            
        self.progress.start()
        self.status_var.set("Building AI index...")
        self.root.update()
        
        try:
            # Initialize AI model if not already loaded
            if self.ai_model is None:
                self.log_result("🤖 Loading AI model (first time may take a moment)...")
                self.ai_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            self.log_result("🤖 Building AI semantic index...")
            self.log_result("   This may take a few minutes for large vaults...")
            
            # Find all markdown files
            md_files = list(Path(vault).rglob("*.md"))
            
            # Extract content chunks
            all_chunks = []
            for i, md_file in enumerate(md_files):
                if i % 10 == 0:
                    self.status_var.set(f"Processing file {i+1}/{len(md_files)}: {md_file.name}")
                    self.root.update()
                
                chunks = self.extract_ai_content_chunks(md_file, vault)
                all_chunks.extend(chunks)
            
            if not all_chunks:
                self.log_result("❌ No content found to index")
                return
            
            self.log_result(f"   Creating embeddings for {len(all_chunks)} content chunks...")
            self.status_var.set("Creating AI embeddings...")
            self.root.update()
            
            # Create embeddings
            texts = [chunk['content'] for chunk in all_chunks]
            embeddings = self.ai_model.encode(texts)
            
            # Store everything
            self.ai_documents = all_chunks
            self.ai_embeddings = embeddings
            
            # Cache the results
            self.save_ai_cache(vault)
            
            self.log_result(f"✅ AI index built successfully!")
            self.log_result(f"   Indexed {len(all_chunks)} chunks from {len(md_files)} files")
            
        except Exception as e:
            error_msg = f"❌ Error building AI index: {str(e)}"
            self.log_result(error_msg)
            messagebox.showerror("Error", error_msg)
        finally:
            self.progress.stop()
            self.status_var.set("AI index ready")
    
    def extract_ai_content_chunks(self, file_path: Path, vault_path: str) -> List[Dict]:
        """Extract meaningful chunks from markdown files for AI processing"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            chunks = []
            
            # Split by headers and paragraphs
            sections = re.split(r'\n(?=#{1,6}\s)', content)
            
            for i, section in enumerate(sections):
                if section.strip():
                    # Clean up markdown formatting for better embedding
                    clean_text = self.clean_markdown_for_ai(section)
                    if len(clean_text.strip()) > 50:  # Skip very short sections
                        chunks.append({
                            'file': str(file_path.relative_to(vault_path)),
                            'content': clean_text,
                            'section': i,
                            'preview': clean_text[:200] + "..." if len(clean_text) > 200 else clean_text
                        })
            
            # If no headers, split by paragraphs
            if len(chunks) == 0:
                paragraphs = content.split('\n\n')
                for i, para in enumerate(paragraphs):
                    clean_para = self.clean_markdown_for_ai(para)
                    if len(clean_para.strip()) > 50:
                        chunks.append({
                            'file': str(file_path.relative_to(vault_path)),
                            'content': clean_para,
                            'section': i,
                            'preview': clean_para[:200] + "..." if len(clean_para) > 200 else clean_para
                        })
            
            return chunks
            
        except Exception as e:
            self.log_result(f"Error reading {file_path}: {e}")
            return []
    
    def clean_markdown_for_ai(self, text: str) -> str:
        """Clean markdown formatting for better embedding"""
        # Remove markdown formatting but keep the content
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Links
        text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)  # Wiki links
        text = re.sub(r'[#*_`]', '', text)  # Formatting chars
        text = re.sub(r'\n+', ' ', text)  # Multiple newlines
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces
        return text.strip()
    
    def load_ai_cache(self, vault_path: str) -> bool:
        """Load cached AI embeddings if available"""
        cache_file = os.path.join(vault_path, '.obsidian', 'ai_search_cache.pkl')
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    self.ai_documents = cache_data['documents']
                    self.ai_embeddings = cache_data['embeddings']
                self.log_result(f"✅ Loaded cached AI index ({len(self.ai_documents)} chunks)")
                return True
            except Exception as e:
                self.log_result(f"⚠️  Error loading AI cache: {e}")
        return False
    
    def save_ai_cache(self, vault_path: str):
        """Save AI embeddings to cache"""
        try:
            cache_dir = os.path.join(vault_path, '.obsidian')
            os.makedirs(cache_dir, exist_ok=True)
            cache_file = os.path.join(cache_dir, 'ai_search_cache.pkl')
            
            cache_data = {
                'documents': self.ai_documents,
                'embeddings': self.ai_embeddings
            }
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            self.log_result("💾 AI index cached for future use")
        except Exception as e:
            self.log_result(f"⚠️  Error saving AI cache: {e}")
    
    def ai_search_threaded(self):
        """Run AI search in a separate thread"""
        if not self.ai_search_enabled:
            messagebox.showwarning("AI Not Available", "AI search dependencies not installed.")
            return
        threading.Thread(target=self.ai_concept_search, daemon=True).start()
    
    def ai_concept_search(self):
        """Perform AI-powered concept search"""
        vault = self.vault_path.get()
        search_term = self.ai_search_term.get().strip()
        
        if not search_term:
            messagebox.showwarning("Warning", "Please enter a concept to search for")
            return
            
        if not vault or not os.path.exists(vault):
            error_msg = "❌ Please select a valid Obsidian vault directory"
            self.log_result(error_msg)
            messagebox.showerror("Error", error_msg)
            return
        
        self.progress.start()
        self.status_var.set("AI concept search...")
        self.root.update()
        
        try:
            # Initialize AI model if needed
            if self.ai_model is None:
                self.log_result("🤖 Loading AI model...")
                self.ai_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Load or build index
            if self.ai_embeddings is None:
                if not self.load_ai_cache(vault):
                    self.log_result("🤖 No AI index found. Building index first...")
                    self.build_ai_index()
                    if self.ai_embeddings is None:
                        return
            
            self.log_result(f"\n🤖 AI Concept Search for: '{search_term}'")
            self.log_result("=" * 60)
            
            # Create query embedding
            query_embedding = self.ai_model.encode([search_term])
            
            # Calculate similarities
            similarities = cosine_similarity(query_embedding, self.ai_embeddings)[0]
            
            # Get top results above threshold
            results = []
            min_similarity = 0.3
            for i, similarity in enumerate(similarities):
                if similarity >= min_similarity:
                    result = self.ai_documents[i].copy()
                    result['similarity'] = float(similarity)
                    results.append(result)
            
            # Sort by similarity
            results.sort(key=lambda x: x['similarity'], reverse=True)
            results = results[:10]  # Top 10 results
            
            # Display results
            self.display_ai_search_results(search_term, results)
            
        except Exception as e:
            error_msg = f"❌ Error during AI search: {str(e)}"
            self.log_result(error_msg)
            messagebox.showerror("Error", error_msg)
        finally:
            self.progress.stop()
            self.status_var.set("AI search completed")
    
    def display_ai_search_results(self, search_term: str, results: List[Dict]):
        """Display AI search results"""
        total_results = len(results)
        
        if total_results == 0:
            self.log_result(f"\n❌ No conceptually related content found for '{search_term}'")
        else:
            self.log_result(f"\n✅ Found {total_results} conceptually related chunks:")
            self.log_result("-" * 60)
            
            for i, result in enumerate(results, 1):
                similarity_pct = result['similarity'] * 100
                self.log_result(f"\n{i}. 📄 {result['file']} (similarity: {similarity_pct:.1f}%)")
                self.log_result(f"   {result['preview']}")
        
        self.log_result("=" * 60)
    
    def find_similar_files_threaded(self):
        """Find similar files in a separate thread"""
        if not self.ai_search_enabled:
            messagebox.showwarning("AI Not Available", "AI search dependencies not installed.")
            return
        threading.Thread(target=self.find_similar_files, daemon=True).start()
    
    def find_similar_files(self):
        """Find files similar to current selection or prompt user"""
        vault = self.vault_path.get()
        
        if not vault or not os.path.exists(vault):
            error_msg = "❌ Please select a valid Obsidian vault directory"
            self.log_result(error_msg)
            messagebox.showerror("Error", error_msg)
            return
        
        # Simple dialog to ask for file path
        from tkinter import simpledialog
        file_path = simpledialog.askstring(
            "Find Similar Files",
            "Enter relative file path (e.g., notes/example.md):"
        )
        
        if not file_path:
            return
        
        self.progress.start()
        self.status_var.set("Finding similar files...")
        self.root.update()
        
        try:
            # Load or build index
            if self.ai_embeddings is None:
                if not self.load_ai_cache(vault):
                    self.log_result("🤖 No AI index found. Building index first...")
                    self.build_ai_index()
                    if self.ai_embeddings is None:
                        return
            
            # Find chunks from the target file
            target_chunks = [doc for doc in self.ai_documents if doc['file'] == file_path]
            if not target_chunks:
                self.log_result(f"❌ File not found in AI index: {file_path}")
                return
            
            self.log_result(f"\n🔍 Finding files similar to: {file_path}")
            self.log_result("=" * 60)
            
            # Average the embeddings for the target file
            target_indices = [i for i, doc in enumerate(self.ai_documents) if doc['file'] == file_path]
            target_embedding = np.mean([self.ai_embeddings[i] for i in target_indices], axis=0)
            
            # Find similar chunks from other files
            similarities = cosine_similarity([target_embedding], self.ai_embeddings)[0]
            
            results = []
            seen_files = {file_path}  # Don't include the target file itself
            
            for i, similarity in enumerate(similarities):
                if similarity > 0.3 and self.ai_documents[i]['file'] not in seen_files:
                    result = self.ai_documents[i].copy()
                    result['similarity'] = float(similarity)
                    results.append(result)
                    seen_files.add(result['file'])
            
            # Sort and limit
            results.sort(key=lambda x: x['similarity'], reverse=True)
            results = results[:5]
            
            # Display results
            if results:
                self.log_result(f"✅ Found {len(results)} similar files:")
                self.log_result("-" * 60)
                for i, result in enumerate(results, 1):
                    similarity_pct = result['similarity'] * 100
                    self.log_result(f"\n{i}. 📄 {result['file']} (similarity: {similarity_pct:.1f}%)")
                    self.log_result(f"   {result['preview']}")
            else:
                self.log_result("❌ No similar files found")
            
            self.log_result("=" * 60)
            
        except Exception as e:
            error_msg = f"❌ Error finding similar files: {str(e)}"
            self.log_result(error_msg)
            messagebox.showerror("Error", error_msg)
        finally:
            self.progress.stop()
            self.status_var.set("Similar files search completed")
    
    
    def exit_application(self):
        """Exit the application"""
        self.root.quit()
        self.root.destroy()


def main():
    """Main function to run the application"""
    root = tk.Tk()
    
    # Set up the style
    style = ttk.Style()
    style.theme_use('aqua' if tk.TkVersion >= 8.5 else 'default')
    
    # Create and run the application
    app = ObsidianBacklinkChecker(root)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()