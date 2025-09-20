#!/usr/bin/env python3
"""
Obsidian Checker - Cross-Platform GUI
Modern Tkinter interface for Obsidian vault analysis
Works on Windows, macOS, and Linux
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
import subprocess
from pathlib import Path
import json
from typing import Optional, Dict, Any

class ObsidianCheckerGUI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.create_widgets()
        self.check_ai_availability()
        
    def setup_window(self):
        """Configure the main window"""
        self.root.title("🔗 Obsidian Checker")
        self.root.geometry("800x600")
        self.root.minsize(600, 500)
        
        # Configure style for better cross-platform appearance
        self.style = ttk.Style()
        
        # Try to use a modern theme if available
        available_themes = self.style.theme_names()
        if 'clam' in available_themes:
            self.style.theme_use('clam')
        elif 'alt' in available_themes:
            self.style.theme_use('alt')
            
        # Set up window close protocol
        self.root.protocol("WM_DELETE_WINDOW", self.exit_application)
        
        # Set up keyboard shortcuts
        self.root.bind('<Command-q>', lambda e: self.exit_application())  # macOS
        self.root.bind('<Control-q>', lambda e: self.exit_application())  # Windows/Linux
        self.root.bind('<Escape>', lambda e: self.clear_search())  # Clear search with Escape
            
    def setup_variables(self):
        """Initialize GUI variables"""
        self.vault_path = tk.StringVar()
        self.ai_available = tk.BooleanVar()
        self.check_backlinks = tk.BooleanVar(value=True)
        self.use_ai_search = tk.BooleanVar(value=False)
        self.export_results = tk.BooleanVar(value=False)
        self.search_term = tk.StringVar()
        self.running = False
        
    def create_widgets(self):
        """Create and layout all GUI widgets"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsive layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🔗 Obsidian Checker", 
                               font=('Helvetica', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Vault selection section
        vault_frame = ttk.LabelFrame(main_frame, text="📁 Obsidian Vault", padding="10")
        vault_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        vault_frame.columnconfigure(1, weight=1)
        
        ttk.Label(vault_frame, text="Vault Path:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.vault_entry = ttk.Entry(vault_frame, textvariable=self.vault_path, width=50)
        self.vault_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(vault_frame, text="Browse...", 
                  command=self.browse_vault).grid(row=0, column=2)
        
        ttk.Button(vault_frame, text="Auto-find", 
                  command=self.auto_find_vault).grid(row=0, column=3, padx=(5, 0))
        
        # Quick Search section
        search_frame = ttk.LabelFrame(main_frame, text="🔍 Quick Search", padding="10")
        search_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_term, width=40)
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.search_entry.bind('<Return>', lambda e: self.quick_search())
        
        ttk.Button(search_frame, text="🔍 Search", 
                  command=self.quick_search).grid(row=0, column=2, padx=(0, 5))
        
        ttk.Button(search_frame, text="Clear", 
                  command=self.clear_search).grid(row=0, column=3)
        
        # Features section
        features_frame = ttk.LabelFrame(main_frame, text="🔧 Analysis Options", padding="10")
        features_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Checkbutton(features_frame, text="Check backlinks and broken links", 
                       variable=self.check_backlinks).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.ai_checkbox = ttk.Checkbutton(features_frame, text="AI semantic search and analysis", 
                                          variable=self.use_ai_search)
        self.ai_checkbox.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        ttk.Checkbutton(features_frame, text="Export results to markdown file", 
                       variable=self.export_results).grid(row=2, column=0, sticky=tk.W, pady=2)
        
        # AI status indicator
        self.ai_status_frame = ttk.Frame(features_frame)
        self.ai_status_frame.grid(row=1, column=1, sticky=tk.E, padx=(10, 0))
        
        self.ai_status_label = ttk.Label(self.ai_status_frame, text="", foreground="gray")
        self.ai_status_label.grid(row=0, column=0)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(0, 10))
        
        self.run_button = ttk.Button(button_frame, text="🚀 Run Analysis", 
                                    command=self.run_analysis, style="Accent.TButton")
        self.run_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="⏹ Stop", 
                                     command=self.stop_analysis, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(button_frame, text="⚙️ Settings", 
                  command=self.show_settings).grid(row=0, column=2, padx=(0, 10))
        
        ttk.Button(button_frame, text="❓ Help", 
                  command=self.show_help).grid(row=0, column=3, padx=(0, 10))
        
        ttk.Button(button_frame, text="💪 Exit", 
                  command=self.exit_application).grid(row=0, column=4)
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="📊 Results", padding="10")
        results_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=15, width=80,
                                                     wrap=tk.WORD, state=tk.DISABLED)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
    def check_ai_availability(self):
        """Check if AI features are available"""
        try:
            # Check if AI environment exists
            ai_env_path = Path("obsidian_ai_env")
            if ai_env_path.exists():
                self.ai_available.set(True)
                self.ai_status_label.config(text="✅ AI Ready", foreground="green")
                self.use_ai_search.set(True)  # Enable by default if available
            else:
                self.ai_available.set(False)
                self.ai_status_label.config(text="⚠️ AI Not Set Up", foreground="orange")
                self.ai_checkbox.config(state=tk.DISABLED)
                
        except Exception as e:
            self.ai_available.set(False)
            self.ai_status_label.config(text="❌ AI Error", foreground="red")
            self.ai_checkbox.config(state=tk.DISABLED)
            
    def browse_vault(self):
        """Open file dialog to select vault directory"""
        directory = filedialog.askdirectory(
            title="Select Obsidian Vault Folder",
            initialdir=os.path.expanduser("~")
        )
        if directory:
            self.vault_path.set(directory)
            self.validate_vault(directory)
            
    def auto_find_vault(self):
        """Automatically find Obsidian vaults"""
        self.log_message("🔍 Searching for Obsidian vaults...")
        
        # Common Obsidian vault locations
        common_paths = [
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~/Obsidian"),
            os.path.expanduser("~/Documents/Obsidian"),
            os.path.expanduser("~/iCloud Drive (Archive)/Obsidian") if sys.platform == "darwin" else None,
        ]
        
        found_vaults = []
        
        for base_path in common_paths:
            if base_path and os.path.exists(base_path):
                for root, dirs, files in os.walk(base_path):
                    if '.obsidian' in dirs:
                        found_vaults.append(root)
                        
        if found_vaults:
            # Show selection dialog if multiple vaults found
            if len(found_vaults) == 1:
                self.vault_path.set(found_vaults[0])
                self.log_message(f"✅ Found vault: {found_vaults[0]}")
            else:
                self.show_vault_selection(found_vaults)
        else:
            messagebox.showinfo("No Vaults Found", 
                              "No Obsidian vaults found in common locations.\n"
                              "Please use 'Browse...' to select your vault manually.")
            
    def show_vault_selection(self, vaults):
        """Show dialog to select from multiple found vaults"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Vault")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Multiple Obsidian vaults found:", 
                 font=('Helvetica', 12, 'bold')).pack(pady=10)
        
        # Listbox with scrollbar
        frame = ttk.Frame(dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        for vault in vaults:
            listbox.insert(tk.END, vault)
            
        def select_vault():
            selection = listbox.curselection()
            if selection:
                selected_vault = vaults[selection[0]]
                self.vault_path.set(selected_vault)
                self.log_message(f"✅ Selected vault: {selected_vault}")
                dialog.destroy()
                
        ttk.Button(dialog, text="Select", command=select_vault).pack(pady=5)
        
    def validate_vault(self, path):
        """Validate if the selected path is an Obsidian vault"""
        obsidian_config = os.path.join(path, '.obsidian')
        if os.path.exists(obsidian_config):
            self.log_message(f"✅ Valid Obsidian vault detected")
            return True
        else:
            self.log_message(f"⚠️ No .obsidian folder found - may not be a valid vault")
            return False
            
    def run_analysis(self):
        """Run the Obsidian analysis in a separate thread"""
        if not self.vault_path.get():
            messagebox.showerror("Error", "Please select an Obsidian vault first.")
            return
            
        if not os.path.exists(self.vault_path.get()):
            messagebox.showerror("Error", "Selected vault path does not exist.")
            return
            
        # Disable run button and enable stop button
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.running = True
        
        # Start progress bar
        self.progress.start()
        self.status_var.set("Running analysis...")
        
        # Clear previous results
        self.clear_results()
        
        # Run analysis in separate thread
        thread = threading.Thread(target=self.run_analysis_thread)
        thread.daemon = True
        thread.start()
        
    def run_analysis_thread(self):
        """Run the actual analysis (called in separate thread)"""
        try:
            self.log_message("🚀 Starting Obsidian vault analysis...")
            self.log_message(f"📁 Vault: {self.vault_path.get()}")
            
            # Build command arguments
            cmd_args = []
            
            if self.ai_available.get() and self.use_ai_search.get():
                # Use AI-enabled script
                cmd_args = ["./run_with_ai.sh", "obsidian_checker_cli.py"]
                self.log_message("🤖 Using AI-enhanced analysis")
            else:
                # Use regular Python script
                cmd_args = [sys.executable, "obsidian_checker_cli.py"]
                self.log_message("🔍 Using standard analysis")
                
            # Add vault path
            cmd_args.extend(["--vault", self.vault_path.get()])
            
            # Add other options
            if not self.check_backlinks.get():
                cmd_args.append("--no-backlinks")
                
            if self.export_results.get():
                export_path = f"analysis_results_{Path(self.vault_path.get()).name}.md"
                cmd_args.extend(["--export", export_path])
                self.log_message(f"📄 Will export results to: {export_path}")
                
            self.log_message(f"Running command: {' '.join(cmd_args)}")
            self.log_message("-" * 60)
            
            # Run the analysis
            process = subprocess.Popen(
                cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=os.getcwd()
            )
            
            # Read output line by line
            while True:
                if not self.running:
                    process.terminate()
                    break
                    
                line = process.stdout.readline()
                if not line:
                    break
                    
                self.log_message(line.rstrip())
                
            # Wait for process to complete
            process.wait()
            
            if process.returncode == 0:
                self.log_message("-" * 60)
                self.log_message("✅ Analysis completed successfully!")
            else:
                self.log_message("-" * 60)
                self.log_message(f"❌ Analysis failed with exit code: {process.returncode}")
                
        except Exception as e:
            self.log_message(f"❌ Error during analysis: {str(e)}")
            
        finally:
            # Re-enable controls
            self.root.after(0, self.analysis_finished)
            
    def analysis_finished(self):
        """Called when analysis is complete (runs on main thread)"""
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
        self.running = False
        self.status_var.set("Analysis complete")
        
    def stop_analysis(self):
        """Stop the running analysis"""
        self.running = False
        self.status_var.set("Stopping analysis...")
        self.log_message("🛑 Analysis stopped by user")
        
    def log_message(self, message):
        """Add message to results text area (thread-safe)"""
        def update_text():
            self.results_text.config(state=tk.NORMAL)
            self.results_text.insert(tk.END, message + "\n")
            self.results_text.see(tk.END)
            self.results_text.config(state=tk.DISABLED)
            
        self.root.after(0, update_text)
        
    def clear_results(self):
        """Clear the results text area"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
        
    def show_settings(self):
        """Show settings dialog"""
        messagebox.showinfo("Settings", "Settings dialog coming soon!\n\nFor now, you can modify options in the Analysis Options section.")
        
    def show_help(self):
        """Show help dialog"""
        help_text = """
🔗 Obsidian Checker - Help

This tool analyzes your Obsidian vault for:
• Broken backlinks and references
• Missing files and attachments
• AI-powered semantic search (if enabled)
• Quick content search
• Export capabilities

How to use:
1. Select your Obsidian vault folder (the one containing .obsidian folder)
2. For quick search: Enter a search term and press Enter or click Search
3. For full analysis: Choose options and click 'Run Analysis'

🔍 Quick Search:
• Enter any text to search across your vault
• Uses AI semantic search if enabled
• Press Enter to search or click the Search button
• Press Escape to clear search field

AI Features:
If AI is enabled, you get additional features:
• Semantic concept search
• Similar file detection
• Content analysis

⌨️ Keyboard Shortcuts:
• Enter: Perform search (when in search field)
• Escape: Clear search field
• Cmd+Q (Mac) / Ctrl+Q (PC): Exit application

Supported file types:
• Markdown files (.md)
• All linked attachments

For more information, see the README.md file.
        """
        
        help_dialog = tk.Toplevel(self.root)
        help_dialog.title("Help - Obsidian Checker")
        help_dialog.geometry("500x400")
        help_dialog.transient(self.root)
        
        text_widget = scrolledtext.ScrolledText(help_dialog, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
        
        ttk.Button(help_dialog, text="Close", 
                  command=help_dialog.destroy).pack(pady=10)
    
    def quick_search(self):
        """Perform quick search in the selected vault"""
        if not self.vault_path.get():
            messagebox.showerror("Error", "Please select an Obsidian vault first.")
            return
            
        if not self.search_term.get().strip():
            messagebox.showwarning("Warning", "Please enter a search term.")
            self.search_entry.focus()
            return
            
        # Clear previous results and show search info
        self.clear_results()
        search_query = self.search_term.get().strip()
        self.log_message(f"🔍 Quick Search: '{search_query}'")
        self.log_message(f"📁 Vault: {self.vault_path.get()}")
        self.log_message("-" * 50)
        
        # Disable search during operation
        self.search_entry.config(state=tk.DISABLED)
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.running = True
        self.progress.start()
        self.status_var.set("Searching...")
        
        # Run search in separate thread
        thread = threading.Thread(target=self.quick_search_thread, args=(search_query,))
        thread.daemon = True
        thread.start()
        
    def quick_search_thread(self, search_query):
        """Run the quick search in a separate thread"""
        try:
            # Build search command
            cmd_args = []
            
            if self.ai_available.get() and self.use_ai_search.get():
                # Use AI search if available
                cmd_args = ["./run_with_ai.sh", "obsidian_checker_cli.py"]
                cmd_args.extend(["--ai-search", search_query])
                self.log_message("🤖 Using AI semantic search...")
            else:
                # Use regular search
                cmd_args = [sys.executable, "obsidian_checker_cli.py"]
                cmd_args.extend(["--search", search_query])
                self.log_message("🔍 Using text search...")
                
            # Add vault path
            cmd_args.extend(["--vault", self.vault_path.get()])
            
            self.log_message(f"Command: {' '.join(cmd_args)}")
            self.log_message("-" * 30)
            
            # Run the search
            process = subprocess.Popen(
                cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=os.getcwd()
            )
            
            # Read output line by line
            while True:
                if not self.running:
                    process.terminate()
                    break
                    
                line = process.stdout.readline()
                if not line:
                    break
                    
                self.log_message(line.rstrip())
                
            # Wait for process to complete
            process.wait()
            
            if process.returncode == 0:
                self.log_message("-" * 30)
                self.log_message("✅ Search completed!")
            else:
                self.log_message("-" * 30)
                self.log_message(f"❌ Search failed with exit code: {process.returncode}")
                
        except Exception as e:
            self.log_message(f"❌ Error during search: {str(e)}")
            
        finally:
            # Re-enable controls
            self.root.after(0, self.search_finished)
            
    def search_finished(self):
        """Called when search is complete (runs on main thread)"""
        self.search_entry.config(state=tk.NORMAL)
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
        self.running = False
        self.status_var.set("Search complete")
        
    def clear_search(self):
        """Clear the search term and focus the search entry"""
        self.search_term.set("")
        self.search_entry.focus()
        
    def exit_application(self):
        """Exit the application with confirmation"""
        if self.running:
            result = messagebox.askyesno(
                "Exit Application", 
                "An analysis or search is currently running.\n"
                "Do you want to stop it and exit?"
            )
            if result:
                self.running = False
                self.root.after(100, self.root.quit)  # Small delay to stop operations
        else:
            result = messagebox.askyesno(
                "Exit Application", 
                "Are you sure you want to exit Obsidian Checker?"
            )
            if result:
                self.root.quit()

def main():
    """Main function to run the GUI application"""
    root = tk.Tk()
    app = ObsidianCheckerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()