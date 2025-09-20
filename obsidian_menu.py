#!/usr/bin/env python3
"""
Obsidian Backlink Checker - Interactive Menu
Simple menu interface to run the Obsidian checker
"""

import subprocess
import sys
import os

def show_menu():
    """Display the main menu"""
    print("\n" + "="*50)
    print("🔗 OBSIDIAN BACKLINK CHECKER")
    print("="*50)
    print("1. 🚀 Open Obsidian & Check Backlinks (Recommended)")
    print("2. 📋 List Available Vaults")
    print("3. 🔍 Check Backlinks Only")
    print("4. 📱 Open Obsidian Only")
    print("5. 📁 Check Specific Vault")
    print("6. 🔎 Search Vault Content")
    print("7. 🤖 AI Concept Search (Beta)")
    print("8. ❓ Show Help")
    print("9. 😪 Exit")
    print("="*50)

def run_command(cmd_args):
    """Run the obsidian checker with given arguments"""
    try:
        result = subprocess.run([sys.executable, 'obsidian_checker_cli.py'] + cmd_args, 
                              check=True, capture_output=False)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {e}")
        return False
    except FileNotFoundError:
        print("❌ obsidian_checker_cli.py not found in current directory")
        return False

def get_vault_path():
    """Get vault path from user input"""
    print("\nEnter the path to your Obsidian vault:")
    print("(You can drag and drop the folder here, or type the path)")
    vault_path = input("Vault path: ").strip().strip('"')
    
    if not vault_path:
        print("❌ No path provided")
        return None
        
    if not os.path.exists(vault_path):
        print(f"❌ Path does not exist: {vault_path}")
        return None
        
    return vault_path

def search_vault():
    """Interactive search functionality"""
    print("\n🔍 VAULT SEARCH")
    print("=" * 30)
    
    # Get search term
    search_term = input("Enter search term: ").strip()
    if not search_term:
        print("❌ No search term provided")
        return
    
    # Get search options
    print("\nSearch Options:")
    case_sensitive = input("Case sensitive? (y/N): ").lower().startswith('y')
    whole_word = input("Match whole words only? (y/N): ").lower().startswith('y')
    use_regex = input("Use regular expressions? (y/N): ").lower().startswith('y')
    
    # Ask about export
    export_results = input("\nExport results to markdown file? (y/N): ").lower().startswith('y')
    export_path = None
    if export_results:
        export_path = input("Enter export file path (e.g., search_results.md): ").strip()
        if not export_path:
            export_path = f"search_results_{search_term.replace(' ', '_')}.md"
    
    # Build command arguments
    cmd_args = ["--search", search_term]
    
    if case_sensitive:
        cmd_args.append("--case-sensitive")
    if whole_word:
        cmd_args.append("--whole-word")
    if use_regex:
        cmd_args.append("--regex")
    if export_path:
        cmd_args.extend(["--export", export_path])
    
    # Get vault path if needed
    vault_path = get_vault_path()
    if vault_path:
        cmd_args.extend(["--vault", vault_path])
    
    # Run the search
    print(f"\n🔍 Searching for '{search_term}'...")
    run_command(cmd_args)

def ai_concept_search():
    """Interactive AI concept search functionality"""
    print("\n🤖 AI CONCEPT SEARCH")
    print("=" * 30)
    
    # Get concept to search for
    concept = input("Enter concept to search for: ").strip()
    if not concept:
        print("❌ No concept provided")
        return
    
    print("\nAI Search Options:")
    print("1. 🤖 Concept search")
    print("2. 🔄 Build AI index first")
    print("3. 🔍 Find similar files")
    
    ai_choice = input("Select AI option (1-3): ").strip()
    
    if ai_choice == "1":
        print(f"\n🤖 Searching for concept '{concept}'...")
        run_command(["--ai-search", concept])
    elif ai_choice == "2":
        print("\n🔄 Building AI index...")
        run_command(["--build-ai-index"])
        print(f"\n🤖 Now searching for concept '{concept}'...")
        run_command(["--ai-search", concept])
    elif ai_choice == "3":
        file_path = input("Enter file path to find similar files (e.g., notes/example.md): ").strip()
        if file_path:
            print(f"\n🔍 Finding files similar to '{file_path}'...")
            run_command(["--similar-to", file_path])
        else:
            print("❌ No file path provided")
    else:
        print("❌ Invalid AI option")

def main():
    """Main interactive menu"""
    print("🎉 Welcome to Obsidian Backlink Checker!")
    
    while True:
        show_menu()
        
        try:
            choice = input("\nSelect an option (1-9): ").strip()
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
            
        if choice == "1":
            print("\n🚀 Opening Obsidian and checking backlinks...")
            run_command([])
            
        elif choice == "2":
            print("\n📋 Listing available vaults...")
            run_command(["--list-vaults"])
            
        elif choice == "3":
            print("\n🔍 Checking backlinks only...")
            run_command(["--check-only"])
            
        elif choice == "4":
            print("\n📱 Opening Obsidian only...")
            run_command(["--open-only"])
            
        elif choice == "5":
            vault_path = get_vault_path()
            if vault_path:
                print(f"\n🔍 Checking vault: {vault_path}")
                run_command(["--vault", vault_path])
            
        elif choice == "6":
            print("\n🔎 Searching vault content...")
            search_vault()
            
        elif choice == "7":
            print("\n🤖 AI Concept Search...")
            ai_concept_search()
            
        elif choice == "8":
            print("\n❓ Showing help...")
            run_command(["--help"])
            
        elif choice == "9":
            print("\n👋 Goodbye!")
            break
            
        else:
            print("\n❌ Invalid choice. Please select 1-9.")
            
        # Wait for user to continue
        if choice in ["1", "2", "3", "4", "5", "6", "7"]:
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()