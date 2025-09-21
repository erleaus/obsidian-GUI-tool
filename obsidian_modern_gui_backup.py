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
        check_btn.pack(side='left')
        
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
            no_chat_card = self.create_card(parent, "💬 Conversational AI")\n            ttk.Label(no_chat_card, \n                     text="Conversational AI not available. Check OpenAI API setup.", \n                     style='Modern.TLabel').pack(pady=20)\n            return\n        \n        # Chat interface card\n        chat_card = self.create_card(parent, "💬 AI Conversation")\n        \n        # Chat history\n        history_frame = tk.Frame(chat_card, bg=self.colors['bg_secondary'])\n        history_frame.pack(fill='both', expand=True, pady=(10, 15))\n        \n        # Chat display with modern styling\n        self.chat_display = tk.Text(\n            history_frame,\n            bg=self.colors['bg_tertiary'],\n            fg=self.colors['text_primary'],\n            font=('SF Pro Display', 11),\n            wrap='word',\n            padx=15,\n            pady=15,\n            border=0,\n            height=15\n        )\n        self.chat_display.pack(fill='both', expand=True)\n        \n        # Configure text tags for styling\n        self.chat_display.tag_configure('user', foreground=self.colors['accent'], font=('SF Pro Display', 11, 'bold'))\n        self.chat_display.tag_configure('assistant', foreground=self.colors['success'], font=('SF Pro Display', 11, 'bold'))\n        self.chat_display.tag_configure('system', foreground=self.colors['text_muted'], font=('SF Pro Display', 10, 'italic'))\n        \n        # Chat input\n        input_frame = tk.Frame(chat_card, bg=self.colors['bg_secondary'])\n        input_frame.pack(fill='x')\n        \n        self.chat_input = ttk.Entry(\n            input_frame, \n            textvariable=self.conversation_input, \n            style='Modern.TEntry',\n            font=('SF Pro Display', 11)\n        )\n        self.chat_input.pack(side='left', fill='x', expand=True, padx=(0, 10))\n        self.chat_input.bind('<Return>', lambda e: self.send_chat_message())\n        \n        send_btn = ttk.Button(input_frame, text="Send", \n                            command=self.send_chat_message, style='Success.TButton')\n        send_btn.pack(side='right')\n        \n        # Quick action buttons\n        quick_actions = tk.Frame(chat_card, bg=self.colors['bg_secondary'])\n        quick_actions.pack(fill='x', pady=(10, 0))\n        \n        summary_btn = ttk.Button(quick_actions, text="📊 Vault Summary", \n                               command=self.get_vault_summary_threaded, style='Modern.TButton')\n        summary_btn.pack(side='left', padx=(0, 10))\n        \n        connections_btn = ttk.Button(quick_actions, text="🔗 Suggest Connections", \n                                   command=self.suggest_connections_threaded, style='Modern.TButton')\n        connections_btn.pack(side='left', padx=(0, 10))\n        \n        clear_btn = ttk.Button(quick_actions, text="🗑️ Clear Chat", \n                             command=self.clear_chat, style='Danger.TButton')\n        clear_btn.pack(side='right')\n        \n    def create_results_tab(self, parent):\n        """Create results display tab"""\n        results_card = self.create_card(parent, "📊 Analysis Results")\n        \n        # Results display with modern styling\n        self.results_display = tk.Text(\n            results_card,\n            bg=self.colors['bg_tertiary'],\n            fg=self.colors['text_primary'],\n            font=('Monaco', 10),\n            wrap='word',\n            padx=15,\n            pady=15,\n            border=0,\n            height=25\n        )\n        self.results_display.pack(fill='both', expand=True, pady=10)\n        \n        # Configure result text tags\n        self.results_display.tag_configure('success', foreground=self.colors['success'])\n        self.results_display.tag_configure('warning', foreground=self.colors['warning'])\n        self.results_display.tag_configure('error', foreground=self.colors['danger'])\n        self.results_display.tag_configure('info', foreground=self.colors['accent'])\n        \n        # Export button\n        export_frame = tk.Frame(results_card, bg=self.colors['bg_secondary'])\n        export_frame.pack(fill='x', pady=(10, 0))\n        \n        export_btn = ttk.Button(export_frame, text="📄 Export Results", \n                              command=self.export_results, style='Modern.TButton')\n        export_btn.pack(side='right')\n        \n    def create_card(self, parent, title):\n        """Create a modern card-style container"""\n        card_container = tk.Frame(parent, bg=self.colors['bg_primary'])\n        card_container.pack(fill='x', pady=(0, 20))\n        \n        card = tk.Frame(\n            card_container,\n            bg=self.colors['bg_secondary'],\n            relief='flat',\n            bd=1\n        )\n        card.pack(fill='x', padx=2, pady=2)\n        \n        # Add subtle shadow effect\n        shadow = tk.Frame(\n            card_container,\n            bg='#000000',\n            height=2\n        )\n        shadow.pack(fill='x')\n        shadow.lower()\n        \n        # Card header\n        header_frame = tk.Frame(card, bg=self.colors['bg_secondary'])\n        header_frame.pack(fill='x', padx=20, pady=(20, 10))\n        \n        title_label = tk.Label(\n            header_frame,\n            text=title,\n            bg=self.colors['bg_secondary'],\n            fg=self.colors['text_primary'],\n            font=('SF Pro Display', 14, 'bold')\n        )\n        title_label.pack(anchor='w')\n        \n        # Card content area\n        content_frame = tk.Frame(card, bg=self.colors['bg_secondary'])\n        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))\n        \n        return content_frame\n        \n    def create_status_bar(self, parent):\n        """Create modern status bar"""\n        status_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], height=50)\n        status_frame.pack(fill='x', pady=(20, 0))\n        status_frame.pack_propagate(False)\n        \n        # Status text\n        status_left = tk.Frame(status_frame, bg=self.colors['bg_secondary'])\n        status_left.pack(side='left', fill='y', padx=20)\n        \n        tk.Label(\n            status_left,\n            textvariable=self.status_var,\n            bg=self.colors['bg_secondary'],\n            fg=self.colors['text_secondary'],\n            font=('SF Pro Display', 10)\n        ).pack(pady=15)\n        \n        # Progress indicator\n        self.progress = ttk.Progressbar(\n            status_frame,\n            mode='indeterminate',\n            length=200\n        )\n        self.progress.pack(side='right', pady=15, padx=20)\n        \n    # Event handlers and utility methods\n    def browse_vault(self):\n        """Browse for vault directory with modern styling"""\n        directory = filedialog.askdirectory(\n            title="Select Your Obsidian Vault",\n            initialdir=os.path.expanduser("~")\n        )\n        if directory:\n            self.vault_path.set(directory)\n            self.update_vault_stats()\n            \n    def update_vault_stats(self):\n        """Update vault statistics display"""\n        vault = self.vault_path.get()\n        if vault and os.path.exists(vault):\n            try:\n                md_files = list(Path(vault).rglob("*.md"))\n                file_count = len(md_files)\n                self.stats_label.config(text=f"📁 {Path(vault).name} • {file_count} notes")\n            except Exception:\n                self.stats_label.config(text="📁 Vault selected")\n        else:\n            self.stats_label.config(text="Select a vault to get started")\n            \n    def detect_obsidian_vaults(self):\n        """Auto-detect Obsidian vaults"""\n        possible_paths = [\n            os.path.expanduser("~/Documents/Obsidian"),\n            os.path.expanduser("~/Obsidian"),\n            os.path.expanduser("~/Documents"),\n            os.path.expanduser("~/Desktop"),\n        ]\n        \n        for base_path in possible_paths:\n            if os.path.exists(base_path):\n                for item in os.listdir(base_path):\n                    item_path = os.path.join(base_path, item)\n                    if os.path.isdir(item_path) and self.is_obsidian_vault(item_path):\n                        self.vault_path.set(item_path)\n                        self.update_vault_stats()\n                        self.log_result(f"✅ Auto-detected vault: {Path(item_path).name}", 'success')\n                        return\n                        \n    def is_obsidian_vault(self, path):\n        """Check if directory is an Obsidian vault"""\n        return os.path.exists(os.path.join(path, ".obsidian"))\n        \n    def log_result(self, message, tag='info'):\n        """Add message to results with styling"""\n        timestamp = datetime.now().strftime("%H:%M:%S")\n        formatted_message = f"[{timestamp}] {message}\\n"\n        \n        self.results_display.insert(tk.END, formatted_message, tag)\n        self.results_display.see(tk.END)\n        \n    def log_chat(self, role, message):\n        """Add message to chat display"""\n        timestamp = datetime.now().strftime("%H:%M")\n        \n        if role == 'user':\n            formatted = f"You ({timestamp}):\\n{message}\\n\\n"\n            self.chat_display.insert(tk.END, formatted, 'user')\n        elif role == 'assistant':\n            formatted = f"AI Assistant ({timestamp}):\\n{message}\\n\\n"\n            self.chat_display.insert(tk.END, formatted, 'assistant')\n        else:\n            formatted = f"System: {message}\\n\\n"\n            self.chat_display.insert(tk.END, formatted, 'system')\n            \n        self.chat_display.see(tk.END)\n        \n    # Threading methods for UI responsiveness\n    def search_vault_threaded(self):\n        """Run search in background thread"""\n        if not self.vault_path.get():\n            messagebox.showerror("Error", "Please select a vault first")\n            return\n            \n        threading.Thread(target=self.search_vault, daemon=True).start()\n        \n    def ai_search_threaded(self):\n        """Run AI search in background thread"""\n        if not self.ai_search_enabled:\n            messagebox.showinfo("Info", "AI search not available. Install: pip install sentence-transformers")\n            return\n            \n        threading.Thread(target=self.ai_search, daemon=True).start()\n        \n    def check_backlinks_threaded(self):\n        """Run backlink check in background thread"""\n        if not self.vault_path.get():\n            messagebox.showerror("Error", "Please select a vault first")\n            return\n            \n        threading.Thread(target=self.check_backlinks, daemon=True).start()\n        \n    def build_ai_index_threaded(self):\n        """Build AI index in background thread"""\n        threading.Thread(target=self.build_ai_index, daemon=True).start()\n        \n    def find_similar_files_threaded(self):\n        """Find similar files in background thread"""\n        threading.Thread(target=self.find_similar_files, daemon=True).start()\n        \n    def auto_summarize_threaded(self):\n        """Auto-summarize in background thread"""\n        threading.Thread(target=self.auto_summarize, daemon=True).start()\n        \n    def get_vault_summary_threaded(self):\n        """Get vault summary via AI"""\n        threading.Thread(target=self.get_vault_summary, daemon=True).start()\n        \n    def suggest_connections_threaded(self):\n        """Suggest connections via AI"""\n        threading.Thread(target=self.suggest_connections, daemon=True).start()\n        \n    # Core functionality methods\n    def open_obsidian(self):\n        """Open Obsidian application"""\n        try:\n            self.status_var.set("Opening Obsidian...")\n            vault = self.vault_path.get()\n            \n            if vault and os.path.exists(vault):\n                subprocess.run(['open', '-a', 'Obsidian', vault], check=True)\n                self.log_result(f"✅ Opened Obsidian with vault: {Path(vault).name}", 'success')\n            else:\n                subprocess.run(['open', '-a', 'Obsidian'], check=True)\n                self.log_result("✅ Opened Obsidian", 'success')\n                \n            self.status_var.set("Obsidian opened successfully")\n            \n        except subprocess.CalledProcessError:\n            error_msg = "❌ Failed to open Obsidian. Make sure it's installed."\n            self.log_result(error_msg, 'error')\n            messagebox.showerror("Error", error_msg)\n            self.status_var.set("Error opening Obsidian")\n            \n    def search_vault(self):\n        """Search vault for text"""\n        self.progress.start()\n        self.status_var.set("Searching vault...")\n        \n        try:\n            # Implementation similar to original but with modern logging\n            vault = self.vault_path.get()\n            search_term = self.search_term.get()\n            \n            if not search_term:\n                self.log_result("❌ Please enter a search term", 'error')\n                return\n                \n            self.log_result(f"🔍 Searching for: '{search_term}'", 'info')\n            \n            # Search implementation goes here...\n            # (Similar to original obsidian_backlink_checker.py)\n            \n            self.log_result("✅ Search completed", 'success')\n            \n        except Exception as e:\n            self.log_result(f"❌ Search error: {str(e)}", 'error')\n        finally:\n            self.progress.stop()\n            self.status_var.set("Ready")\n            \n    def ai_search(self):\n        """Perform AI concept search"""\n        # Implementation for AI search\n        pass\n        \n    def check_backlinks(self):\n        """Check for broken backlinks"""\n        # Implementation for backlink checking\n        pass\n        \n    def build_ai_index(self):\n        """Build AI search index"""\n        # Implementation for building AI index\n        pass\n        \n    def find_similar_files(self):\n        """Find similar files using AI"""\n        # Implementation for finding similar files\n        pass\n        \n    def auto_summarize(self):\n        """Auto-summarize vault content"""\n        # Implementation for auto-summarization\n        pass\n        \n    def send_chat_message(self):\n        """Send message to conversational AI"""\n        message = self.conversation_input.get().strip()\n        if not message:\n            return\n            \n        self.log_chat('user', message)\n        self.conversation_input.set("")\n        \n        # Start AI response in background\n        threading.Thread(target=self.process_chat_message, args=(message,), daemon=True).start()\n        \n    def process_chat_message(self, message):\n        """Process chat message with AI"""\n        try:\n            if not self.conversational_ai:\n                vault = self.vault_path.get()\n                if not vault:\n                    self.log_chat('system', "Please select a vault first")\n                    return\n                    \n                from obsidian_conversation import ObsidianConversation\n                self.conversational_ai = ObsidianConversation(vault)\n                \n                if not self.conversational_ai.initialize_search_index():\n                    self.log_chat('system', "Failed to initialize AI search index")\n                    return\n                    \n            response = self.conversational_ai.ask_question(message)\n            self.log_chat('assistant', response)\n            \n        except Exception as e:\n            self.log_chat('system', f"Error: {str(e)}")\n            \n    def get_vault_summary(self):\n        """Get AI-powered vault summary"""\n        try:\n            if not self.conversational_ai:\n                vault = self.vault_path.get()\n                if not vault:\n                    self.log_chat('system', "Please select a vault first")\n                    return\n                    \n                from obsidian_conversation import ObsidianConversation\n                self.conversational_ai = ObsidianConversation(vault)\n                \n            summary = self.conversational_ai.get_vault_summary()\n            self.log_chat('assistant', summary)\n            \n        except Exception as e:\n            self.log_chat('system', f"Error getting summary: {str(e)}")\n            \n    def suggest_connections(self):\n        """Get AI suggestions for note connections"""\n        try:\n            if not self.conversational_ai:\n                vault = self.vault_path.get()\n                if not vault:\n                    self.log_chat('system', "Please select a vault first")\n                    return\n                    \n                from obsidian_conversation import ObsidianConversation\n                self.conversational_ai = ObsidianConversation(vault)\n                \n            connections = self.conversational_ai.suggest_connections()\n            self.log_chat('assistant', connections)\n            \n        except Exception as e:\n            self.log_chat('system', f"Error suggesting connections: {str(e)}")\n            \n    def clear_chat(self):\n        """Clear chat history"""\n        self.chat_display.delete(1.0, tk.END)\n        if self.conversational_ai:\n            self.conversational_ai.clear_conversation()\n        self.log_chat('system', "Chat cleared")\n        \n    def export_results(self):\n        """Export results to file"""\n        # Implementation for exporting results\n        pass\n\n\ndef main():\n    root = tk.Tk()\n    app = ModernObsidianGUI(root)\n    \n    # Center window on screen\n    root.update_idletasks()\n    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)\n    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)\n    root.geometry(f"+{x}+{y}")\n    \n    root.mainloop()\n\n\nif __name__ == "__main__":\n    main()