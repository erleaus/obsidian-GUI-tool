#!/usr/bin/env python3
"""
Modern Web-Inspired Obsidian GUI
A contemporary-styled GUI with web-like appearance for the Obsidian tool
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, simpledialog
import os
import re
import subprocess
import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Set, Tuple
import threading
from datetime import datetime

# AI Search functionality (optional)
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# Conversational AI functionality (if available)
try:
    from obsidian_conversation import ObsidianConversation
    CONVERSATIONAL_AI_AVAILABLE = True
except ImportError:
    CONVERSATIONAL_AI_AVAILABLE = False


class ModernObsidianGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Obsidian AI Assistant")
        self.root.geometry("1200x800")
        
        # Modern color scheme (inspired by popular web apps)
        self.colors = {
            'bg_primary': '#1a1a1a',      # Dark background
            'bg_secondary': '#2d2d2d',    # Card background
            'bg_tertiary': '#3a3a3a',     # Input backgrounds
            'accent': '#007acc',          # Primary blue
            'accent_hover': '#005a9e',    # Darker blue
            'success': '#28a745',         # Green
            'warning': '#ffc107',         # Yellow
            'danger': '#dc3545',          # Red
            'text_primary': '#ffffff',    # White text
            'text_secondary': '#b0b0b0',  # Light gray text
            'text_muted': '#6c757d',      # Muted text
            'border': '#4a4a4a',          # Border color
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Variables
        self.vault_path = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready to analyze your Obsidian vault")
        self.search_term = tk.StringVar()
        self.ai_search_term = tk.StringVar()
        self.conversation_input = tk.StringVar()
        
        # Data storage
        self.broken_links = []
        self.search_results = []
        self.conversation_history = []
        
        # AI components
        self.ai_search_enabled = AI_AVAILABLE
        self.conversational_ai = None
        self.ai_model = None
        self.ai_embeddings = None
        self.ai_documents = []
        self.ai_search_results = []  # Store AI search results for export
        self.ai_similarity_threshold = tk.DoubleVar(value=0.3)
        self.ai_model_var = tk.StringVar(value="all-MiniLM-L6-v2")
        self.batch_processing = tk.BooleanVar(value=True)
        self.max_results_var = tk.IntVar(value=10)
        
        self.setup_styles()
        self.setup_ui()
        self.detect_obsidian_vaults()
        
    def setup_styles(self):
        """Configure modern ttk styles"""
        style = ttk.Style()
        
        # Configure modern theme
        style.theme_use('clam')
        
        # Modern button style
        style.configure(
            'Modern.TButton',
            background=self.colors['accent'],
            foreground='white',
            borderwidth=0,
            focuscolor='none',
            padding=(20, 12),
            font=('SF Pro Display', 11, 'normal')
        )
        style.map('Modern.TButton',
            background=[('active', self.colors['accent_hover']),
                       ('pressed', '#004080')])
        
        # Success button
        style.configure(
            'Success.TButton',
            background=self.colors['success'],
            foreground='white',
            borderwidth=0,
            focuscolor='none',
            padding=(20, 12),
            font=('SF Pro Display', 11, 'normal')
        )
        style.map('Success.TButton',
            background=[('active', '#218838'),
                       ('pressed', '#1e7e34')])
        
        # Danger button
        style.configure(
            'Danger.TButton',
            background=self.colors['danger'],
            foreground='white',
            borderwidth=0,
            focuscolor='none',
            padding=(15, 8),
            font=('SF Pro Display', 10, 'normal')
        )
        
        # Modern entry style
        style.configure(
            'Modern.TEntry',
            fieldbackground=self.colors['bg_tertiary'],
            foreground=self.colors['text_primary'],
            borderwidth=1,
            insertcolor=self.colors['text_primary'],
            padding=(12, 8),
            font=('SF Pro Display', 11)
        )
        
        # Modern label frame
        style.configure(
            'Modern.TLabelframe',
            background=self.colors['bg_secondary'],
            foreground=self.colors['text_primary'],
            borderwidth=1,
            relief='solid',
            bordercolor=self.colors['border'],
            font=('SF Pro Display', 12, 'bold')
        )
        
        # Modern label
        style.configure(
            'Modern.TLabel',
            background=self.colors['bg_primary'],
            foreground=self.colors['text_primary'],
            font=('SF Pro Display', 11)
        )
        
        # Heading label
        style.configure(
            'Heading.TLabel',
            background=self.colors['bg_primary'],
            foreground=self.colors['text_primary'],
            font=('SF Pro Display', 24, 'bold')
        )
        
        # Subheading label
        style.configure(
            'Subheading.TLabel',
            background=self.colors['bg_primary'],
            foreground=self.colors['text_secondary'],
            font=('SF Pro Display', 14)
        )
        
        # Status label
        style.configure(
            'Status.TLabel',
            background=self.colors['bg_primary'],
            foreground=self.colors['accent'],
            font=('SF Pro Display', 10)
        )
        
    def setup_ui(self):
        """Create the modern web-inspired interface"""
        # Create scrollable main frame
        canvas = tk.Canvas(self.root, bg=self.colors['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_primary'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Main container with padding
        main_container = tk.Frame(scrollable_frame, bg=self.colors['bg_primary'], padx=40, pady=30)
        main_container.pack(fill='both', expand=True)
        
        # Header section
        self.create_header(main_container)
        
        # Vault selection card
        self.create_vault_section(main_container)
        
        # Navigation tabs
        self.create_tabs(main_container)
        
        # Status bar
        self.create_status_bar(main_container)
        
    def create_header(self, parent):
        """Create modern header section"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        header_frame.pack(fill='x', pady=(0, 30))
        
        # Title and subtitle
        title = ttk.Label(header_frame, text="Obsidian AI Assistant", style='Heading.TLabel')
        title.pack(anchor='w')
        
        subtitle = ttk.Label(header_frame, 
                           text="Analyze, search, and chat with your knowledge vault", 
                           style='Subheading.TLabel')
        subtitle.pack(anchor='w', pady=(5, 0))
        
        # Quick stats (placeholder)
        stats_frame = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        stats_frame.pack(anchor='w', pady=(15, 0))
        
        self.stats_label = ttk.Label(stats_frame, 
                                   text="Select a vault to get started", 
                                   style='Modern.TLabel')
        self.stats_label.pack(side='left')
        
    def create_vault_section(self, parent):
        """Create vault selection card"""
        vault_card = self.create_card(parent, "📁 Vault Configuration")
        
        # Vault path selection
        vault_input_frame = tk.Frame(vault_card, bg=self.colors['bg_secondary'])
        vault_input_frame.pack(fill='x', pady=10)
        
        ttk.Label(vault_input_frame, text="Vault Path:", style='Modern.TLabel').pack(anchor='w', pady=(0, 5))
        
        input_frame = tk.Frame(vault_input_frame, bg=self.colors['bg_secondary'])
        input_frame.pack(fill='x')
        
        self.vault_entry = ttk.Entry(input_frame, textvariable=self.vault_path, 
                                   style='Modern.TEntry', font=('SF Pro Display', 11))
        self.vault_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(input_frame, text="Browse", 
                              command=self.browse_vault, style='Modern.TButton')
        browse_btn.pack(side='right')
        
        # Quick actions
        actions_frame = tk.Frame(vault_card, bg=self.colors['bg_secondary'])
        actions_frame.pack(fill='x', pady=(15, 0))
        
        open_btn = ttk.Button(actions_frame, text="🚀 Open Obsidian", 
                            command=self.open_obsidian, style='Success.TButton')
        open_btn.pack(side='left', padx=(0, 10))
        
        check_btn = ttk.Button(actions_frame, text="🔍 Check Links", 
                             command=self.check_backlinks_threaded, style='Modern.TButton')
        check_btn.pack(side='left', padx=(0, 10))
        
        exit_btn = ttk.Button(actions_frame, text="❌ Exit", 
                            command=self.exit_application, style='Danger.TButton')
        exit_btn.pack(side='right')
        
    def create_tabs(self, parent):
        """Create tabbed interface"""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill='both', expand=True, pady=20)
        
        # Configure notebook style
        style = ttk.Style()
        style.configure('TNotebook', background=self.colors['bg_primary'])
        style.configure('TNotebook.Tab', 
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       padding=[20, 10],
                       font=('SF Pro Display', 11))
        
        # Tab 1: Search & Analysis
        search_frame = tk.Frame(notebook, bg=self.colors['bg_primary'], padx=20, pady=20)
        notebook.add(search_frame, text="🔍 Search & Analysis")
        self.create_search_tab(search_frame)
        
        # Tab 2: AI Features
        if self.ai_search_enabled:
            ai_frame = tk.Frame(notebook, bg=self.colors['bg_primary'], padx=20, pady=20)
            notebook.add(ai_frame, text="🤖 AI Features")
            self.create_ai_tab(ai_frame)
        
        # Tab 3: Conversational AI
        if CONVERSATIONAL_AI_AVAILABLE:
            chat_frame = tk.Frame(notebook, bg=self.colors['bg_primary'], padx=20, pady=20)
            notebook.add(chat_frame, text="💬 AI Chat")
            self.create_chat_tab(chat_frame)
        
        # Tab 4: Results
        results_frame = tk.Frame(notebook, bg=self.colors['bg_primary'], padx=20, pady=20)
        notebook.add(results_frame, text="📊 Results")
        self.create_results_tab(results_frame)
        
    def create_search_tab(self, parent):
        """Create search and analysis tab"""
        # Basic search card
        search_card = self.create_card(parent, "🔍 Text Search")
        
        # Search input
        search_input_frame = tk.Frame(search_card, bg=self.colors['bg_secondary'])
        search_input_frame.pack(fill='x', pady=10)
        
        ttk.Label(search_input_frame, text="Search Term:", style='Modern.TLabel').pack(anchor='w', pady=(0, 5))
        
        search_entry_frame = tk.Frame(search_input_frame, bg=self.colors['bg_secondary'])
        search_entry_frame.pack(fill='x')
        
        self.search_entry = ttk.Entry(search_entry_frame, textvariable=self.search_term, 
                                    style='Modern.TEntry')
        self.search_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        search_btn = ttk.Button(search_entry_frame, text="Search", 
                              command=self.search_vault_threaded, style='Modern.TButton')
        search_btn.pack(side='right')
        
        # Search options
        options_frame = tk.Frame(search_card, bg=self.colors['bg_secondary'])
        options_frame.pack(fill='x', pady=(10, 0))
        
        self.case_sensitive = tk.BooleanVar()
        self.whole_word = tk.BooleanVar()
        self.use_regex = tk.BooleanVar()
        
        tk.Checkbutton(options_frame, text="Case Sensitive", variable=self.case_sensitive,
                      bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                      selectcolor=self.colors['bg_tertiary'], font=('SF Pro Display', 10)).pack(side='left', padx=(0, 20))
        
        tk.Checkbutton(options_frame, text="Whole Word", variable=self.whole_word,
                      bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                      selectcolor=self.colors['bg_tertiary'], font=('SF Pro Display', 10)).pack(side='left', padx=(0, 20))
        
        tk.Checkbutton(options_frame, text="Regular Expression", variable=self.use_regex,
                      bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                      selectcolor=self.colors['bg_tertiary'], font=('SF Pro Display', 10)).pack(side='left')
        
    def create_ai_tab(self, parent):
        """Create AI features tab"""
        # AI Concept Search card
        concept_card = self.create_card(parent, "🤖 Concept Search")
        
        # AI search input
        ai_input_frame = tk.Frame(concept_card, bg=self.colors['bg_secondary'])
        ai_input_frame.pack(fill='x', pady=10)
        
        ttk.Label(ai_input_frame, text="Concept or Topic:", style='Modern.TLabel').pack(anchor='w', pady=(0, 5))
        
        ai_entry_frame = tk.Frame(ai_input_frame, bg=self.colors['bg_secondary'])
        ai_entry_frame.pack(fill='x')
        
        self.ai_search_entry = ttk.Entry(ai_entry_frame, textvariable=self.ai_search_term, 
                                       style='Modern.TEntry')
        self.ai_search_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        ai_search_btn = ttk.Button(ai_entry_frame, text="Concept Search", 
                                 command=self.ai_search_threaded, style='Modern.TButton')
        ai_search_btn.pack(side='right')
        
        # AI action buttons
        ai_actions_frame = tk.Frame(concept_card, bg=self.colors['bg_secondary'])
        ai_actions_frame.pack(fill='x', pady=(15, 0))
        
        build_btn = ttk.Button(ai_actions_frame, text="🔄 Build Index", 
                             command=self.build_ai_index_threaded, style='Modern.TButton')
        build_btn.pack(side='left', padx=(0, 10))
        
        similar_btn = ttk.Button(ai_actions_frame, text="🔍 Find Similar", 
                               command=self.find_similar_files_threaded, style='Modern.TButton')
        similar_btn.pack(side='left', padx=(0, 10))
        
        summarize_btn = ttk.Button(ai_actions_frame, text="📝 Summarize", 
                                 command=self.auto_summarize_threaded, style='Modern.TButton')
        summarize_btn.pack(side='left')
        
    def create_chat_tab(self, parent):
        """Create conversational AI chat tab"""
        if not CONVERSATIONAL_AI_AVAILABLE:
            no_chat_card = self.create_card(parent, "💬 Conversational AI")
            ttk.Label(no_chat_card,
                     text="Conversational AI not available. Check OpenAI API setup.",
                     style='Modern.TLabel').pack(pady=20)
            return
        
        # Chat interface card
        chat_card = self.create_card(parent, "💬 AI Conversation")
        
        # Chat history
        history_frame = tk.Frame(chat_card, bg=self.colors['bg_secondary'])
        history_frame.pack(fill='both', expand=True, pady=(10, 15))
        
        # Chat display with modern styling
        self.chat_display = tk.Text(
            history_frame,
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            font=('SF Pro Display', 11),
            wrap='word',
            padx=15,
            pady=15,
            border=0,
            height=15
        )
        self.chat_display.pack(fill='both', expand=True)
        
        # Configure text tags for styling
        self.chat_display.tag_configure('user', foreground=self.colors['accent'], font=('SF Pro Display', 11, 'bold'))
        self.chat_display.tag_configure('assistant', foreground=self.colors['success'], font=('SF Pro Display', 11, 'bold'))
        self.chat_display.tag_configure('system', foreground=self.colors['text_muted'], font=('SF Pro Display', 10, 'italic'))
        
        # Chat input
        input_frame = tk.Frame(chat_card, bg=self.colors['bg_secondary'])
        input_frame.pack(fill='x')
        
        self.chat_input = ttk.Entry(
            input_frame,
            textvariable=self.conversation_input,
            style='Modern.TEntry',
            font=('SF Pro Display', 11)
        )
        self.chat_input.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.chat_input.bind('<Return>', lambda e: self.send_chat_message())
        
        send_btn = ttk.Button(input_frame, text="Send",
                            command=self.send_chat_message, style='Success.TButton')
        send_btn.pack(side='right')
        
        # Quick action buttons
        quick_actions = tk.Frame(chat_card, bg=self.colors['bg_secondary'])
        quick_actions.pack(fill='x', pady=(10, 0))
        
        summary_btn = ttk.Button(quick_actions, text="📊 Vault Summary",
                               command=self.get_vault_summary_threaded, style='Modern.TButton')
        summary_btn.pack(side='left', padx=(0, 10))
        
        connections_btn = ttk.Button(quick_actions, text="🔗 Suggest Connections",
                                   command=self.suggest_connections_threaded, style='Modern.TButton')
        connections_btn.pack(side='left', padx=(0, 10))
        
        clear_btn = ttk.Button(quick_actions, text="🗑️ Clear Chat",
                             command=self.clear_chat, style='Danger.TButton')
        clear_btn.pack(side='right')
        
    def create_results_tab(self, parent):
        """Create results display tab"""
        results_card = self.create_card(parent, "📊 Analysis Results")
        
        # Results display with modern styling
        self.results_display = tk.Text(
            results_card,
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            font=('Monaco', 10),
            wrap='word',
            padx=15,
            pady=15,
            border=0,
            height=25
        )
        self.results_display.pack(fill='both', expand=True, pady=10)
        
        # Configure result text tags
        self.results_display.tag_configure('success', foreground=self.colors['success'])
        self.results_display.tag_configure('warning', foreground=self.colors['warning'])
        self.results_display.tag_configure('error', foreground=self.colors['danger'])
        self.results_display.tag_configure('info', foreground=self.colors['accent'])
        
        # Export button
        export_frame = tk.Frame(results_card, bg=self.colors['bg_secondary'])
        export_frame.pack(fill='x', pady=(10, 0))
        
        export_btn = ttk.Button(export_frame, text="📄 Export Results",
                              command=self.export_results, style='Modern.TButton')
        export_btn.pack(side='right')
        
    def create_card(self, parent, title):
        """Create a modern card-style container"""
        card_container = tk.Frame(parent, bg=self.colors['bg_primary'])
        card_container.pack(fill='x', pady=(0, 20))
        
        card = tk.Frame(
            card_container,
            bg=self.colors['bg_secondary'],
            relief='flat',
            bd=1
        )
        card.pack(fill='x', padx=2, pady=2)
        
        # Add subtle shadow effect
        shadow = tk.Frame(
            card_container,
            bg='#000000',
            height=2
        )
        shadow.pack(fill='x')
        shadow.lower()
        
        # Card header
        header_frame = tk.Frame(card, bg=self.colors['bg_secondary'])
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        title_label = tk.Label(
            header_frame,
            text=title,
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            font=('SF Pro Display', 14, 'bold')
        )
        title_label.pack(anchor='w')
        
        # Card content area
        content_frame = tk.Frame(card, bg=self.colors['bg_secondary'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        return content_frame
        
    def create_status_bar(self, parent):
        """Create modern status bar"""
        status_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], height=50)
        status_frame.pack(fill='x', pady=(20, 0))
        status_frame.pack_propagate(False)
        
        # Status text
        status_left = tk.Frame(status_frame, bg=self.colors['bg_secondary'])
        status_left.pack(side='left', fill='y', padx=20)
        
        tk.Label(
            status_left,
            textvariable=self.status_var,
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_secondary'],
            font=('SF Pro Display', 10)
        ).pack(pady=15)
        
        # Progress indicator
        self.progress = ttk.Progressbar(
            status_frame,
            mode='indeterminate',
            length=200
        )
        self.progress.pack(side='right', pady=15, padx=20)
        
    # Event handlers and utility methods
    def browse_vault(self):
        """Browse for vault directory with modern styling"""
        directory = filedialog.askdirectory(
            title="Select Your Obsidian Vault",
            initialdir=os.path.expanduser("~")
        )
        if directory:
            self.vault_path.set(directory)
            self.update_vault_stats()
            
    def update_vault_stats(self):
        """Update vault statistics display"""
        vault = self.vault_path.get()
        if vault and os.path.exists(vault):
            try:
                md_files = list(Path(vault).rglob("*.md"))
                file_count = len(md_files)
                self.stats_label.config(text=f"📁 {Path(vault).name} • {file_count} notes")
            except Exception:
                self.stats_label.config(text="📁 Vault selected")
        else:
            self.stats_label.config(text="Select a vault to get started")
            
    def detect_obsidian_vaults(self):
        """Auto-detect Obsidian vaults"""
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
                        self.update_vault_stats()
                        self.log_result(f"✅ Auto-detected vault: {Path(item_path).name}", 'success')
                        return
                        
    def is_obsidian_vault(self, path):
        """Check if directory is an Obsidian vault"""
        return os.path.exists(os.path.join(path, ".obsidian"))
        
    def log_result(self, message, tag='info'):
        """Add message to results with styling"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.results_display.insert(tk.END, formatted_message, tag)
        self.results_display.see(tk.END)
        
    def log_chat(self, role, message):
        """Add message to chat display"""
        timestamp = datetime.now().strftime("%H:%M")
        
        if role == 'user':
            formatted = f"You ({timestamp}):\n{message}\n\n"
            self.chat_display.insert(tk.END, formatted, 'user')
        elif role == 'assistant':
            formatted = f"AI Assistant ({timestamp}):\n{message}\n\n"
            self.chat_display.insert(tk.END, formatted, 'assistant')
        else:
            formatted = f"System: {message}\n\n"
            self.chat_display.insert(tk.END, formatted, 'system')
            
        self.chat_display.see(tk.END)
        
    # Threading methods for UI responsiveness
    def search_vault_threaded(self):
        """Run search in background thread"""
        if not self.vault_path.get():
            messagebox.showerror("Error", "Please select a vault first")
            return
            
        threading.Thread(target=self.search_vault, daemon=True).start()
        
    def ai_search_threaded(self):
        """Run AI search in background thread"""
        if not self.ai_search_enabled:
            messagebox.showinfo("Info", "AI search not available. Install: pip install sentence-transformers")
            return
            
        threading.Thread(target=self.ai_search, daemon=True).start()
        
    def check_backlinks_threaded(self):
        """Run backlink check in background thread"""
        if not self.vault_path.get():
            messagebox.showerror("Error", "Please select a vault first")
            return
            
        threading.Thread(target=self.check_backlinks, daemon=True).start()
        
    def build_ai_index_threaded(self):
        """Build AI index in background thread"""
        threading.Thread(target=self.build_ai_index, daemon=True).start()
        
    def find_similar_files_threaded(self):
        """Find similar files in background thread"""
        threading.Thread(target=self.find_similar_files, daemon=True).start()
        
    def auto_summarize_threaded(self):
        """Auto-summarize in background thread"""
        threading.Thread(target=self.auto_summarize, daemon=True).start()
        
    def get_vault_summary_threaded(self):
        """Get vault summary via AI"""
        threading.Thread(target=self.get_vault_summary, daemon=True).start()
        
    def suggest_connections_threaded(self):
        """Suggest connections via AI"""
        threading.Thread(target=self.suggest_connections, daemon=True).start()
        
    # Core functionality methods
    def open_obsidian(self):
        """Open Obsidian application"""
        try:
            self.status_var.set("Opening Obsidian...")
            vault = self.vault_path.get()
            
            if vault and os.path.exists(vault):
                subprocess.run(['open', '-a', 'Obsidian', vault], check=True)
                self.log_result(f"✅ Opened Obsidian with vault: {Path(vault).name}", 'success')
            else:
                subprocess.run(['open', '-a', 'Obsidian'], check=True)
                self.log_result("✅ Opened Obsidian", 'success')
                
            self.status_var.set("Obsidian opened successfully")
            
        except subprocess.CalledProcessError:
            error_msg = "❌ Failed to open Obsidian. Make sure it's installed."
            self.log_result(error_msg, 'error')
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Error opening Obsidian")
            
    def search_vault(self):
        """Search for keywords in the Obsidian vault"""
        vault = self.vault_path.get()
        search_term = self.search_term.get().strip()
        
        if not search_term:
            messagebox.showwarning("Warning", "Please enter a search term")
            return
            
        if not vault or not os.path.exists(vault):
            error_msg = "❌ Please select a valid Obsidian vault directory"
            self.log_result(error_msg, 'error')
            messagebox.showerror("Error", error_msg)
            return
            
        self.progress.start()
        self.status_var.set("Searching vault...")
        
        try:
            # Clear previous search results
            self.search_results = []
            
            # Find all markdown files
            md_files = list(Path(vault).rglob("*.md"))
            total_files = len(md_files)
            
            self.log_result(f"\n🔍 Searching for '{search_term}' in {total_files} files...", 'info')
            self.log_result("=" * 60, 'info')
            
            # Prepare search pattern
            if self.use_regex.get():
                try:
                    flags = 0 if self.case_sensitive.get() else re.IGNORECASE
                    pattern = re.compile(search_term, flags)
                except re.error as e:
                    error_msg = f"❌ Invalid regex pattern: {e}"
                    self.log_result(error_msg, 'error')
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
                    self.log_result(f"❌ Error reading {md_file.name}: {str(e)}", 'error')
            
            # Display search results
            self.display_search_results(search_term, total_files, files_with_matches, total_matches)
            
        except Exception as e:
            error_msg = f"❌ Error during search: {str(e)}"
            self.log_result(error_msg, 'error')
            messagebox.showerror("Error", error_msg)
        finally:
            self.progress.stop()
            self.status_var.set("Search completed")
    
    def display_search_results(self, search_term, total_files, files_with_matches, total_matches):
        """Display the search results"""
        self.log_result("\n" + "=" * 60, 'info')
        self.log_result(f"📊 SEARCH RESULTS FOR: '{search_term}'", 'info')
        self.log_result("=" * 60, 'info')
        self.log_result(f"Files scanned: {total_files}", 'info')
        self.log_result(f"Files with matches: {files_with_matches}", 'info')
        self.log_result(f"Total matches: {total_matches}", 'info')
        
        if total_matches == 0:
            self.log_result(f"\n❌ No matches found for '{search_term}'", 'warning')
        else:
            self.log_result(f"\n✅ Found {total_matches} matches in {files_with_matches} files:", 'success')
            self.log_result("-" * 60, 'info')
            
            for result in self.search_results:
                self.log_result(f"\n📄 {result['relative_path']} ({result['total_matches']} matches)", 'info')
                
                # Show up to 5 matches per file in the GUI
                for i, match in enumerate(result['matches'][:5]):
                    line_preview = match['line_content'][:100] + "..." if len(match['line_content']) > 100 else match['line_content']
                    self.log_result(f"   Line {match['line_num']}: {line_preview}", 'info')
                
                if len(result['matches']) > 5:
                    self.log_result(f"   ... and {len(result['matches']) - 5} more matches", 'info')
        
        self.log_result("=" * 60, 'info')
            
    def ai_search(self):
        """Perform AI-powered concept search"""
        vault = self.vault_path.get()
        search_term = self.ai_search_term.get().strip()
        
        if not search_term:
            messagebox.showwarning("Warning", "Please enter a concept to search for")
            return
            
        if not vault or not os.path.exists(vault):
            error_msg = "❌ Please select a valid Obsidian vault directory"
            self.log_result(error_msg, 'error')
            messagebox.showerror("Error", error_msg)
            return
        
        self.progress.start()
        self.status_var.set("AI concept search...")
        
        try:
            # Initialize AI model if needed
            if self.ai_model is None:
                self.log_result("🤖 Loading AI model...", 'info')
                from sentence_transformers import SentenceTransformer
                self.ai_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Load or build index
            if self.ai_embeddings is None:
                if not self.load_ai_cache(vault):
                    self.log_result("🤖 No AI index found. Building index first...", 'info')
                    self.build_ai_index()
                    if self.ai_embeddings is None:
                        return
            
            self.log_result(f"\n🤖 AI Concept Search for: '{search_term}'", 'info')
            self.log_result("=" * 60, 'info')
            
            # Create query embedding
            query_embedding = self.ai_model.encode([search_term])
            
            # Calculate similarities
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(query_embedding, self.ai_embeddings)[0]
            
            # Get top results above threshold
            results = []
            min_similarity = self.ai_similarity_threshold.get()
            for i, similarity in enumerate(similarities):
                if similarity >= min_similarity:
                    result = self.ai_documents[i].copy()
                    result['similarity'] = float(similarity)
                    results.append(result)
            
            # Sort by similarity and limit results
            results.sort(key=lambda x: x['similarity'], reverse=True)
            max_results = self.max_results_var.get()
            results = results[:max_results]
            
            # Store and display results
            self.ai_search_results = results
            self.display_ai_search_results(search_term, results)
            
        except Exception as e:
            error_msg = f"❌ Error during AI search: {str(e)}"
            self.log_result(error_msg, 'error')
            messagebox.showerror("Error", error_msg)
        finally:
            self.progress.stop()
            self.status_var.set("AI search completed")
    
    def display_ai_search_results(self, search_term: str, results: List[Dict]):
        """Display AI search results"""
        total_results = len(results)
        
        if total_results == 0:
            self.log_result(f"\n❌ No conceptually related content found for '{search_term}'", 'warning')
        else:
            self.log_result(f"\n✅ Found {total_results} conceptually related chunks:", 'success')
            self.log_result("-" * 60, 'info')
            
            for i, result in enumerate(results, 1):
                similarity_pct = result['similarity'] * 100
                self.log_result(f"\n{i}. 📄 {result['file']} (similarity: {similarity_pct:.1f}%)", 'info')
                self.log_result(f"   {result['preview']}", 'info')
        
        self.log_result("=" * 60, 'info')
        
    def check_backlinks(self):
        """Check all backlinks in the Obsidian vault"""
        vault = self.vault_path.get()
        
        if not vault or not os.path.exists(vault):
            error_msg = "❌ Please select a valid Obsidian vault directory"
            self.log_result(error_msg, 'error')
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Invalid vault path")
            return
            
        if not self.is_obsidian_vault(vault):
            error_msg = "❌ Selected directory is not an Obsidian vault"
            self.log_result(error_msg, 'error')
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Not an Obsidian vault")
            return
            
        self.status_var.set("Scanning vault...")
        self.progress.start()
        
        try:
            # Clear previous results
            self.broken_links = []
            
            # Find all markdown files
            md_files = list(Path(vault).rglob("*.md"))
            total_files = len(md_files)
            
            self.log_result(f"🔍 Scanning {total_files} markdown files in vault: {vault}", 'info')
            self.log_result("-" * 60, 'info')
            
            # Get all file names (without extension) for reference
            all_notes = {f.stem for f in md_files}
            
            broken_count = 0
            total_links = 0
            
            for i, md_file in enumerate(md_files):
                self.status_var.set(f"Checking file {i+1}/{total_files}: {md_file.name}")
                
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
                    self.log_result(f"❌ Error reading {md_file.name}: {str(e)}", 'error')
                    
            # Display results
            self.display_backlink_results(total_files, total_links, broken_count)
            
        except Exception as e:
            error_msg = f"❌ Error during backlink check: {str(e)}"
            self.log_result(error_msg, 'error')
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Error during check")
        finally:
            self.progress.stop()
            self.status_var.set("Ready")
            
    def display_backlink_results(self, total_files, total_links, broken_count):
        """Display the results of the backlink check"""
        self.log_result("\n" + "=" * 60, 'info')
        self.log_result("📊 BACKLINK CHECK SUMMARY", 'info')
        self.log_result("=" * 60, 'info')
        self.log_result(f"Files scanned: {total_files}", 'info')
        self.log_result(f"Total links found: {total_links}", 'info')
        self.log_result(f"Broken links: {broken_count}", 'info')
        
        if broken_count == 0:
            self.log_result("\n🎉 All backlinks are working correctly!", 'success')
            self.status_var.set("All backlinks valid")
        else:
            self.log_result(f"\n⚠️  Found {broken_count} broken links:", 'warning')
            self.log_result("-" * 40, 'warning')
            
            for broken_link in self.broken_links:
                link_type = "[[...]]" if broken_link['type'] == 'wiki' else "[...](…)"
                self.log_result(f"📄 {broken_link['file']}", 'error')
                self.log_result(f"   🔗 {link_type}: {broken_link['link']}", 'error')
                self.log_result("", 'error')
                
            self.status_var.set(f"Found {broken_count} broken links")
            
        self.log_result("=" * 60, 'info')
        
    def build_ai_index(self):
        """Build semantic search index for the vault"""
        vault = self.vault_path.get()
        
        if not vault or not os.path.exists(vault):
            error_msg = "❌ Please select a valid Obsidian vault directory"
            self.log_result(error_msg, 'error')
            messagebox.showerror("Error", error_msg)
            return
            
        self.progress.start()
        self.status_var.set("Building AI index...")
        
        try:
            # Initialize AI model if not already loaded or model changed
            model_name = self.ai_model_var.get()
            if self.ai_model is None or (hasattr(self, '_current_model_name') and self._current_model_name != model_name):
                self.log_result(f"🤖 Loading AI model: {model_name} (first time may take a moment)...", 'info')
                try:
                    from sentence_transformers import SentenceTransformer
                    self.ai_model = SentenceTransformer(model_name)
                    self._current_model_name = model_name
                    self.log_result(f"✅ AI model loaded successfully", 'success')
                except Exception as e:
                    self.log_result(f"❌ Error loading model: {e}", 'error')
                    self.log_result("Falling back to default model...", 'warning')
                    self.ai_model = SentenceTransformer('all-MiniLM-L6-v2')
                    self._current_model_name = 'all-MiniLM-L6-v2'
            
            self.log_result("🤖 Building AI semantic index...", 'info')
            self.log_result("   This may take a few minutes for large vaults...", 'info')
            
            # Find all markdown files
            md_files = list(Path(vault).rglob("*.md"))
            
            # Extract content chunks
            all_chunks = []
            for i, md_file in enumerate(md_files):
                if i % 10 == 0:
                    self.status_var.set(f"Processing file {i+1}/{len(md_files)}: {md_file.name}")
                
                chunks = self.extract_ai_content_chunks(md_file, vault)
                all_chunks.extend(chunks)
            
            if not all_chunks:
                self.log_result("❌ No content found to index", 'error')
                return
            
            self.log_result(f"   Creating embeddings for {len(all_chunks)} content chunks...", 'info')
            self.status_var.set("Creating AI embeddings...")
            
            # Create embeddings with optimized batch processing
            texts = [chunk['content'] for chunk in all_chunks]
            
            if self.batch_processing.get() and len(texts) > 10:
                # Process in batches for better memory management
                batch_size = min(32, max(1, len(texts) // 10))  # Adaptive batch size
                embeddings = []
                
                for i in range(0, len(texts), batch_size):
                    batch_texts = texts[i:i + batch_size]
                    self.status_var.set(f"Processing batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}...")
                    
                    batch_embeddings = self.ai_model.encode(
                        batch_texts,
                        convert_to_numpy=True,
                        show_progress_bar=False,
                        normalize_embeddings=True  # Normalize for better similarity comparison
                    )
                    embeddings.extend(batch_embeddings)
                    
                embeddings = np.array(embeddings)
            else:
                # Single batch processing for smaller datasets
                embeddings = self.ai_model.encode(
                    texts, 
                    show_progress_bar=True, 
                    convert_to_numpy=True,
                    normalize_embeddings=True
                )
            
            # Store everything
            self.ai_documents = all_chunks
            self.ai_embeddings = embeddings
            
            # Cache the results
            self.save_ai_cache(vault)
            
            self.log_result(f"✅ AI index built successfully!", 'success')
            self.log_result(f"   Indexed {len(all_chunks)} chunks from {len(md_files)} files", 'success')
            
        except Exception as e:
            error_msg = f"❌ Error building AI index: {str(e)}"
            self.log_result(error_msg, 'error')
            messagebox.showerror("Error", error_msg)
        finally:
            self.progress.stop()
            self.status_var.set("AI index ready")
        
    def find_similar_files(self):
        """Find files similar to current selection or prompt user"""
        vault = self.vault_path.get()
        
        if not vault or not os.path.exists(vault):
            error_msg = "❌ Please select a valid Obsidian vault directory"
            self.log_result(error_msg, 'error')
            messagebox.showerror("Error", error_msg)
            return
        
        # Simple dialog to ask for file path
        file_path = simpledialog.askstring(
            "Find Similar Files",
            "Enter relative file path (e.g., notes/example.md):"
        )
        
        if not file_path:
            return
        
        self.progress.start()
        self.status_var.set("Finding similar files...")
        
        try:
            # Load or build index
            if self.ai_embeddings is None:
                if not self.load_ai_cache(vault):
                    self.log_result("🤖 No AI index found. Building index first...", 'info')
                    self.build_ai_index()
                    if self.ai_embeddings is None:
                        return
            
            # Find chunks from the target file
            target_chunks = [doc for doc in self.ai_documents if doc['file'] == file_path]
            if not target_chunks:
                self.log_result(f"❌ File not found in AI index: {file_path}", 'error')
                return
            
            self.log_result(f"\n🔍 Finding files similar to: {file_path}", 'info')
            self.log_result("=" * 60, 'info')
            
            # Average the embeddings for the target file
            target_indices = [i for i, doc in enumerate(self.ai_documents) if doc['file'] == file_path]
            target_embedding = np.mean([self.ai_embeddings[i] for i in target_indices], axis=0)
            
            # Find similar chunks from other files
            from sklearn.metrics.pairwise import cosine_similarity
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
                self.log_result(f"✅ Found {len(results)} similar files:", 'success')
                self.log_result("-" * 60, 'info')
                for i, result in enumerate(results, 1):
                    similarity_pct = result['similarity'] * 100
                    self.log_result(f"\n{i}. 📄 {result['file']} (similarity: {similarity_pct:.1f}%)", 'info')
                    self.log_result(f"   {result['preview']}", 'info')
            else:
                self.log_result("❌ No similar files found", 'warning')
            
            self.log_result("=" * 60, 'info')
            
        except Exception as e:
            error_msg = f"❌ Error finding similar files: {str(e)}"
            self.log_result(error_msg, 'error')
            messagebox.showerror("Error", error_msg)
        finally:
            self.progress.stop()
            self.status_var.set("Similar files search completed")
        
    def auto_summarize(self):
        """Auto-summarize vault content and identify key themes"""
        vault = self.vault_path.get()
        
        if not vault or not os.path.exists(vault):
            error_msg = "❌ Please select a valid Obsidian vault directory"
            self.log_result(error_msg, 'error')
            messagebox.showerror("Error", error_msg)
            return
        
        self.progress.start()
        self.status_var.set("Analyzing content for summary...")
        
        try:
            # Load or build index
            if self.ai_embeddings is None:
                if not self.load_ai_cache(vault):
                    self.log_result("🤖 Building AI index for summarization...", 'info')
                    self.build_ai_index()
                    if self.ai_embeddings is None:
                        return
            
            self.log_result("\n📝 AUTO-SUMMARIZING VAULT CONTENT", 'info')
            self.log_result("=" * 60, 'info')
            
            # Group documents by similarity to find themes
            theme_clusters = self.find_content_themes()
            
            if theme_clusters:
                self.log_result(f"✅ Identified {len(theme_clusters)} major themes:", 'success')
                self.log_result("-" * 40, 'info')
                
                for i, (theme_docs, centroid_text) in enumerate(theme_clusters[:5], 1):
                    # Extract key terms from the cluster
                    key_terms = self.extract_key_terms([doc['content'] for doc in theme_docs])
                    
                    self.log_result(f"\n🎯 Theme {i}: {', '.join(key_terms[:3])}", 'info')
                    self.log_result(f"   Files: {len(theme_docs)}", 'info')
                    
                    # Show representative files
                    unique_files = list(set(doc['file'] for doc in theme_docs))
                    for file_path in unique_files[:3]:
                        self.log_result(f"   📄 {file_path}", 'info')
                    
                    if len(unique_files) > 3:
                        self.log_result(f"   ... and {len(unique_files) - 3} more files", 'info')
                    
                    # Show theme summary
                    theme_summary = self.summarize_theme(theme_docs)
                    if theme_summary:
                        self.log_result(f"   💡 {theme_summary}", 'info')
            else:
                self.log_result("❌ Could not identify distinct themes in the content", 'warning')
            
            # File statistics
            file_stats = self.analyze_file_statistics()
            self.log_result(f"\n📊 VAULT STATISTICS", 'info')
            self.log_result("-" * 40, 'info')
            self.log_result(f"Total files: {file_stats['total_files']}", 'info')
            self.log_result(f"Total content chunks: {len(self.ai_documents)}", 'info')
            self.log_result(f"Average content per file: {file_stats['avg_content_per_file']:.0f} words", 'info')
            
            self.log_result("=" * 60, 'info')
            
        except Exception as e:
            error_msg = f"❌ Error during auto-summarization: {str(e)}"
            self.log_result(error_msg, 'error')
            messagebox.showerror("Error", error_msg)
        finally:
            self.progress.stop()
            self.status_var.set("Auto-summarization completed")
        
    def send_chat_message(self):
        """Send message to conversational AI"""
        message = self.conversation_input.get().strip()
        if not message:
            return
            
        self.log_chat('user', message)
        self.conversation_input.set("")
        
        # Start AI response in background
        threading.Thread(target=self.process_chat_message, args=(message,), daemon=True).start()
        
    def process_chat_message(self, message):
        """Process chat message with AI"""
        try:
            if not self.conversational_ai:
                vault = self.vault_path.get()
                if not vault:
                    self.log_chat('system', "Please select a vault first")
                    return
                    
                from obsidian_conversation import ObsidianConversation
                self.conversational_ai = ObsidianConversation(vault)
                
                if not self.conversational_ai.initialize_search_index():
                    self.log_chat('system', "Failed to initialize AI search index")
                    return
                    
            response = self.conversational_ai.ask_question(message)
            self.log_chat('assistant', response)
            
        except Exception as e:
            self.log_chat('system', f"Error: {str(e)}")
            
    def get_vault_summary(self):
        """Get AI-powered vault summary"""
        try:
            if not self.conversational_ai:
                vault = self.vault_path.get()
                if not vault:
                    self.log_chat('system', "Please select a vault first")
                    return
                    
                from obsidian_conversation import ObsidianConversation
                self.conversational_ai = ObsidianConversation(vault)
                
            summary = self.conversational_ai.get_vault_summary()
            self.log_chat('assistant', summary)
            
        except Exception as e:
            self.log_chat('system', f"Error getting summary: {str(e)}")
            
    def suggest_connections(self):
        """Get AI suggestions for note connections"""
        try:
            if not self.conversational_ai:
                vault = self.vault_path.get()
                if not vault:
                    self.log_chat('system', "Please select a vault first")
                    return
                    
                from obsidian_conversation import ObsidianConversation
                self.conversational_ai = ObsidianConversation(vault)
                
            connections = self.conversational_ai.suggest_connections()
            self.log_chat('assistant', connections)
            
        except Exception as e:
            self.log_chat('system', f"Error suggesting connections: {str(e)}")
            
    def clear_chat(self):
        """Clear chat history"""
        self.chat_display.delete(1.0, tk.END)
        if self.conversational_ai:
            self.conversational_ai.clear_conversation()
        self.log_chat('system', "Chat cleared")
        
    def export_results(self):
        """Export results to a text file"""
        if not self.results_display.get("1.0", tk.END).strip():
            messagebox.showwarning("Warning", "No results to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Markdown files", "*.md"), ("All files", "*.*")],
            title="Save Results As"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.results_display.get("1.0", tk.END))
                messagebox.showinfo("Success", f"Results exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results: {str(e)}")
    
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
            self.log_result(f"Error reading {file_path}: {e}", 'error')
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
            self.log_result("💾 AI index cached for future use", 'success')
        except Exception as e:
            self.log_result(f"⚠️  Error saving AI cache: {e}", 'warning')
    
    def load_ai_cache(self, vault_path: str) -> bool:
        """Load cached AI embeddings if available"""
        cache_file = os.path.join(vault_path, '.obsidian', 'ai_search_cache.pkl')
        if os.path.exists(cache_file):
            try:
                # Check cache freshness
                cache_time = os.path.getmtime(cache_file)
                vault_mod_time = self.get_vault_modification_time(vault_path)
                
                # If cache is older than vault contents, skip loading
                if cache_time < vault_mod_time:
                    self.log_result("⚠️  AI cache is outdated, will rebuild index", 'warning')
                    return False
                
                with open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    
                    # Validate cache structure
                    if 'documents' not in cache_data or 'embeddings' not in cache_data:
                        self.log_result("⚠️  Invalid cache format, will rebuild", 'warning')
                        return False
                    
                    self.ai_documents = cache_data['documents']
                    self.ai_embeddings = cache_data['embeddings']
                    
                    # Validate data consistency
                    if len(self.ai_documents) != len(self.ai_embeddings):
                        self.log_result("⚠️  Cache data inconsistency, will rebuild", 'warning')
                        return False
                        
                self.log_result(f"✅ Loaded cached AI index ({len(self.ai_documents)} chunks)", 'success')
                return True
            except Exception as e:
                self.log_result(f"⚠️  Error loading AI cache: {e}", 'warning')
        return False
    
    def get_vault_modification_time(self, vault_path: str) -> float:
        """Get the most recent modification time in the vault"""
        try:
            max_time = 0
            md_files = list(Path(vault_path).rglob("*.md"))
            
            # Check up to 50 most recently modified files for performance
            md_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            for md_file in md_files[:50]:
                mod_time = md_file.stat().st_mtime
                max_time = max(max_time, mod_time)
            
            return max_time
        except Exception:
            return float('inf')  # If error, force rebuild
    
    def find_content_themes(self, n_themes=5):
        """Use clustering to identify content themes"""
        try:
            from sklearn.cluster import KMeans
            from sklearn.decomposition import PCA
            from sklearn.metrics.pairwise import cosine_similarity
            
            if len(self.ai_embeddings) < n_themes:
                return []
            
            # Reduce dimensionality for better clustering
            pca = PCA(n_components=min(50, len(self.ai_embeddings)))
            reduced_embeddings = pca.fit_transform(self.ai_embeddings)
            
            # Cluster the embeddings
            kmeans = KMeans(n_clusters=n_themes, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(reduced_embeddings)
            
            # Group documents by cluster
            theme_clusters = []
            for cluster_id in range(n_themes):
                cluster_docs = [self.ai_documents[i] for i, label in enumerate(cluster_labels) if label == cluster_id]
                if len(cluster_docs) > 1:  # Only include clusters with multiple documents
                    # Find the document closest to cluster centroid
                    cluster_indices = [i for i, label in enumerate(cluster_labels) if label == cluster_id]
                    cluster_embeddings = [self.ai_embeddings[i] for i in cluster_indices]
                    centroid = np.mean(cluster_embeddings, axis=0)
                    
                    # Find most representative document
                    similarities = cosine_similarity([centroid], cluster_embeddings)[0]
                    best_doc_idx = cluster_indices[np.argmax(similarities)]
                    centroid_text = self.ai_documents[best_doc_idx]['content'][:200]
                    
                    theme_clusters.append((cluster_docs, centroid_text))
            
            return sorted(theme_clusters, key=lambda x: len(x[0]), reverse=True)
        except Exception as e:
            self.log_result(f"⚠️ Error in theme clustering: {e}", 'warning')
            return []
    
    def extract_key_terms(self, texts, top_k=5):
        """Extract key terms from a collection of texts"""
        try:
            from collections import Counter
            
            # Combine all texts
            combined_text = ' '.join(texts).lower()
            
            # Extract words (3+ characters, not common stop words)
            stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 
                         'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new',
                         'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'she', 'use', 'man', 'put'}
            
            words = re.findall(r'\b[a-zA-Z]{3,}\b', combined_text)
            words = [word for word in words if word not in stop_words]
            
            # Count frequency and return top terms
            word_counts = Counter(words)
            return [word for word, count in word_counts.most_common(top_k)]
        except Exception:
            return ['content', 'notes', 'ideas']
    
    def summarize_theme(self, theme_docs):
        """Create a brief summary of a theme cluster"""
        try:
            # Get the most common words from the theme
            theme_texts = [doc['content'] for doc in theme_docs]
            key_terms = self.extract_key_terms(theme_texts, top_k=3)
            
            # Create a simple summary
            unique_files = len(set(doc['file'] for doc in theme_docs))
            
            if len(key_terms) > 0:
                return f"Content related to {', '.join(key_terms)} across {unique_files} files"
            else:
                return f"Related content across {unique_files} files"
        except Exception:
            return None
    
    def analyze_file_statistics(self):
        """Analyze basic file statistics"""
        try:
            file_word_counts = {}
            for doc in self.ai_documents:
                file_path = doc['file']
                word_count = len(doc['content'].split())
                if file_path not in file_word_counts:
                    file_word_counts[file_path] = 0
                file_word_counts[file_path] += word_count
            
            total_files = len(file_word_counts)
            total_words = sum(file_word_counts.values())
            avg_content = total_words / total_files if total_files > 0 else 0
            
            return {
                'total_files': total_files,
                'total_words': total_words,
                'avg_content_per_file': avg_content
            }
        except Exception:
            return {'total_files': 0, 'total_words': 0, 'avg_content_per_file': 0}
    
    def exit_application(self):
        """Exit the application"""
        self.root.quit()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = ModernObsidianGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()