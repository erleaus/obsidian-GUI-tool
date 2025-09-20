#!/usr/bin/env python3
"""
Obsidian Backlink Checker - Command Line Version
A command-line tool to open Obsidian and check backlinks in vaults.
"""

import os
import re
import subprocess
import sys
from pathlib import Path
import argparse


def detect_obsidian_vaults():
    """Try to detect Obsidian vaults automatically"""
    possible_paths = [
        os.path.expanduser("~/Documents/Obsidian"),
        os.path.expanduser("~/Obsidian"),
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/Desktop"),
    ]
    
    vaults = []
    for base_path in possible_paths:
        if os.path.exists(base_path):
            for item in os.listdir(base_path):
                item_path = os.path.join(base_path, item)
                if os.path.isdir(item_path) and is_obsidian_vault(item_path):
                    vaults.append(item_path)
    
    return vaults


def is_obsidian_vault(path):
    """Check if a directory is an Obsidian vault"""
    obsidian_config = os.path.join(path, ".obsidian")
    return os.path.exists(obsidian_config) and os.path.isdir(obsidian_config)


def open_obsidian(vault_path=None):
    """Open Obsidian application on macOS"""
    try:
        print("🚀 Opening Obsidian...")
        
        if vault_path and os.path.exists(vault_path):
            # Open Obsidian with specific vault
            subprocess.run(['open', '-a', 'Obsidian', vault_path], check=True)
            print(f"✅ Opened Obsidian with vault: {vault_path}")
        else:
            # Just open Obsidian
            subprocess.run(['open', '-a', 'Obsidian'], check=True)
            print("✅ Opened Obsidian")
            
        return True
        
    except subprocess.CalledProcessError:
        print("❌ Failed to open Obsidian. Make sure Obsidian is installed.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


def check_backlinks(vault_path):
    """Check all backlinks in the Obsidian vault"""
    if not vault_path or not os.path.exists(vault_path):
        print("❌ Please provide a valid Obsidian vault directory")
        return False
        
    if not is_obsidian_vault(vault_path):
        print("❌ Selected directory is not an Obsidian vault")
        return False
        
    print(f"🔍 Scanning vault: {vault_path}")
    print("-" * 60)
    
    try:
        # Find all markdown files
        md_files = list(Path(vault_path).rglob("*.md"))
        total_files = len(md_files)
        
        print(f"📁 Found {total_files} markdown files")
        
        # Get all file names (without extension) for reference
        all_notes = {f.stem for f in md_files}
        
        broken_links = []
        broken_count = 0
        total_links = 0
        
        for i, md_file in enumerate(md_files):
            if i % 10 == 0:  # Progress indicator
                print(f"📊 Progress: {i+1}/{total_files} files processed...", end='\r')
            
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
                        target_path = Path(vault_path) / f"{actual_link}.md"
                        if not target_path.exists():
                            broken_links.append({
                                'file': str(md_file.relative_to(vault_path)),
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
                            broken_links.append({
                                'file': str(md_file.relative_to(vault_path)),
                                'link': link,
                                'type': 'markdown'
                            })
                            broken_count += 1
                            
            except Exception as e:
                print(f"❌ Error reading {md_file.name}: {str(e)}")
                
        # Clear progress line
        print(" " * 50, end='\r')
        
        # Display results
        print("\n" + "=" * 60)
        print("📊 BACKLINK CHECK SUMMARY")
        print("=" * 60)
        print(f"Files scanned: {total_files}")
        print(f"Total links found: {total_links}")
        print(f"Broken links: {broken_count}")
        
        if broken_count == 0:
            print("\n🎉 All backlinks are working correctly!")
        else:
            print(f"\n⚠️  Found {broken_count} broken links:")
            print("-" * 40)
            
            for broken_link in broken_links:
                link_type = "[[...]]" if broken_link['type'] == 'wiki' else "[...](…)"
                print(f"📄 {broken_link['file']}")
                print(f"   🔗 {link_type}: {broken_link['link']}")
                print()
                
        print("=" * 60)
        return broken_count == 0
        
    except Exception as e:
        print(f"❌ Error during backlink check: {str(e)}")
        return False


def search_vault(vault_path, search_term, case_sensitive=False, whole_word=False, use_regex=False, export_path=None):
    """Search for keywords in the Obsidian vault"""
    if not vault_path or not os.path.exists(vault_path):
        print("❌ Please provide a valid Obsidian vault directory")
        return False
        
    if not is_obsidian_vault(vault_path):
        print("❌ Selected directory is not an Obsidian vault")
        return False
    
    if not search_term.strip():
        print("❌ Please provide a search term")
        return False
        
    print(f"🔍 Searching for '{search_term}' in vault: {vault_path}")
    print("-" * 60)
    
    try:
        # Find all markdown files
        md_files = list(Path(vault_path).rglob("*.md"))
        total_files = len(md_files)
        
        print(f"📁 Scanning {total_files} markdown files...")
        
        # Prepare search pattern
        if use_regex:
            try:
                flags = 0 if case_sensitive else re.IGNORECASE
                pattern = re.compile(search_term, flags)
            except re.error as e:
                print(f"❌ Invalid regex pattern: {e}")
                return False
        else:
            # Escape special regex characters for literal search
            escaped_term = re.escape(search_term)
            if whole_word:
                escaped_term = r'\b' + escaped_term + r'\b'
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = re.compile(escaped_term, flags)
        
        search_results = []
        total_matches = 0
        files_with_matches = 0
        
        for i, md_file in enumerate(md_files):
            if i % 10 == 0:  # Progress indicator
                print(f"📊 Progress: {i+1}/{total_files} files processed...", end='\r')
            
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
                    
                    search_results.append({
                        'file_path': md_file,
                        'relative_path': str(md_file.relative_to(vault_path)),
                        'matches': file_matches,
                        'total_matches': file_total_matches
                    })
                    
            except Exception as e:
                print(f"❌ Error reading {md_file.name}: {str(e)}")
        
        # Clear progress line
        print(" " * 50, end='\r')
        
        # Display results
        print("\n" + "=" * 60)
        print(f"📊 SEARCH RESULTS FOR: '{search_term}'")
        print("=" * 60)
        print(f"Files scanned: {total_files}")
        print(f"Files with matches: {files_with_matches}")
        print(f"Total matches: {total_matches}")
        
        if total_matches == 0:
            print(f"\n❌ No matches found for '{search_term}'")
        else:
            print(f"\n✅ Found {total_matches} matches in {files_with_matches} files:")
            print("-" * 60)
            
            for result in search_results:
                print(f"\n📄 {result['relative_path']} ({result['total_matches']} matches)")
                
                # Show up to 3 matches per file in CLI (less than GUI)
                for i, match in enumerate(result['matches'][:3]):
                    line_preview = match['line_content'][:80] + "..." if len(match['line_content']) > 80 else match['line_content']
                    print(f"   Line {match['line_num']}: {line_preview}")
                
                if len(result['matches']) > 3:
                    print(f"   ... and {len(result['matches']) - 3} more matches")
        
        print("=" * 60)
        
        # Export if requested
        if export_path and search_results:
            export_search_results_cli(search_results, search_term, vault_path, export_path, 
                                    case_sensitive, whole_word, use_regex)
        
        return len(search_results) > 0
        
    except Exception as e:
        print(f"❌ Error during search: {str(e)}")
        return False


def export_search_results_cli(search_results, search_term, vault_path, export_path, 
                             case_sensitive, whole_word, use_regex):
    """Export search results to a markdown file"""
    try:
        vault_name = Path(vault_path).name
        total_matches = sum(r['total_matches'] for r in search_results)
        files_with_matches = len(search_results)
        
        with open(export_path, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"# Search Results: '{search_term}'\n\n")
            f.write(f"**Vault:** {vault_name}\n")
            f.write(f"**Search Term:** `{search_term}`\n")
            f.write(f"**Search Options:**\n")
            f.write(f"- Case Sensitive: {'Yes' if case_sensitive else 'No'}\n")
            f.write(f"- Whole Word: {'Yes' if whole_word else 'No'}\n")
            f.write(f"- Regular Expression: {'Yes' if use_regex else 'No'}\n\n")
            
            f.write(f"**Summary:**\n")
            f.write(f"- Files with matches: {files_with_matches}\n")
            f.write(f"- Total matches: {total_matches}\n\n")
            
            f.write("---\n\n")
            
            # Results
            for result in search_results:
                f.write(f"## 📄 {result['relative_path']}\n\n")
                f.write(f"**Matches found:** {result['total_matches']}\n\n")
                
                for match in result['matches']:
                    f.write(f"**Line {match['line_num']}:**\n")
                    f.write(f"```\n{match['line_content']}\n```\n\n")
                
                f.write("---\n\n")
            
            # Footer
            from datetime import datetime
            f.write(f"*Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*\n")
        
        print(f"\n✅ Search results exported to: {export_path}")
        
    except Exception as e:
        print(f"❌ Error exporting search results: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='Obsidian Backlink Checker & Search Tool')
    parser.add_argument('--vault', '-v', help='Path to Obsidian vault')
    parser.add_argument('--open-only', '-o', action='store_true', help='Only open Obsidian')
    parser.add_argument('--check-only', '-c', action='store_true', help='Only check backlinks')
    parser.add_argument('--list-vaults', '-l', action='store_true', help='List detected vaults')
    parser.add_argument('--search', '-s', help='Search for keywords in vault')
    parser.add_argument('--case-sensitive', action='store_true', help='Case sensitive search')
    parser.add_argument('--whole-word', '-w', action='store_true', help='Match whole words only')
    parser.add_argument('--regex', '-r', action='store_true', help='Use regular expressions')
    parser.add_argument('--export', '-e', help='Export search results to markdown file')
    parser.add_argument('--ai-search', help='AI-powered concept search')
    parser.add_argument('--build-ai-index', action='store_true', help='Build AI search index')
    parser.add_argument('--similar-to', help='Find files similar to given file path')
    
    args = parser.parse_args()
    
    print("🔗 Obsidian Backlink Checker & Search Tool")
    print("=" * 50)
    
    # List detected vaults
    if args.list_vaults:
        vaults = detect_obsidian_vaults()
        if vaults:
            print("📁 Detected Obsidian vaults:")
            for i, vault in enumerate(vaults, 1):
                print(f"  {i}. {vault}")
        else:
            print("❌ No Obsidian vaults detected")
        return
    
    # Determine vault path
    vault_path = args.vault
    if not vault_path:
        vaults = detect_obsidian_vaults()
        if vaults:
            vault_path = vaults[0]  # Use first detected vault
            print(f"📁 Using auto-detected vault: {vault_path}")
        else:
            print("❌ No vault specified and none auto-detected")
            print("Use --vault /path/to/vault or --list-vaults to see detected vaults")
            return
    
    # Execute requested actions
    if args.ai_search:
        # Import AI functionality here
        try:
            from obsidian_ai_search import ObsidianAISearch
            ai_search = ObsidianAISearch(vault_path)
            if ai_search.is_available():
                if not ai_search.load_cache():
                    print("🤖 Building AI index first...")
                    ai_search.build_index()
                results = ai_search.semantic_search(args.ai_search)
                print(f"\n🤖 AI Concept Search Results for: '{args.ai_search}'")
                print("=" * 60)
                if results:
                    for i, result in enumerate(results, 1):
                        similarity_pct = result['similarity'] * 100
                        print(f"\n{i}. 📄 {result['file']} (similarity: {similarity_pct:.1f}%)")
                        print(f"   {result['preview']}")
                else:
                    print("❌ No conceptually related content found")
                print("=" * 60)
            else:
                print("❌ AI search not available. Install dependencies first.")
        except ImportError:
            print("❌ AI search module not found. Make sure obsidian_ai_search.py is available.")
    elif args.build_ai_index:
        try:
            from obsidian_ai_search import ObsidianAISearch
            ai_search = ObsidianAISearch(vault_path)
            if ai_search.is_available():
                ai_search.build_index()
            else:
                print("❌ AI search not available. Install dependencies first.")
        except ImportError:
            print("❌ AI search module not found.")
    elif args.similar_to:
        try:
            from obsidian_ai_search import ObsidianAISearch
            ai_search = ObsidianAISearch(vault_path)
            if ai_search.is_available():
                if not ai_search.load_cache():
                    print("🤖 Building AI index first...")
                    ai_search.build_index()
                results = ai_search.find_similar_to_file(args.similar_to)
                print(f"\n🔍 Files similar to: {args.similar_to}")
                print("=" * 60)
                if results:
                    for i, result in enumerate(results, 1):
                        similarity_pct = result['similarity'] * 100
                        print(f"\n{i}. 📄 {result['file']} (similarity: {similarity_pct:.1f}%)")
                        print(f"   {result['preview']}")
                else:
                    print("❌ No similar files found")
                print("=" * 60)
            else:
                print("❌ AI search not available. Install dependencies first.")
        except ImportError:
            print("❌ AI search module not found.")
    elif args.search:
        search_vault(vault_path, args.search, args.case_sensitive, args.whole_word, args.regex, args.export)
    elif args.open_only:
        open_obsidian(vault_path)
    elif args.check_only:
        check_backlinks(vault_path)
    else:
        # Default: open Obsidian and check backlinks
        print("🚀 Opening Obsidian and checking backlinks...")
        open_obsidian(vault_path)
        print("\n" + "⏱️  Waiting 2 seconds for Obsidian to load...")
        import time
        time.sleep(2)
        check_backlinks(vault_path)


if __name__ == "__main__":
    main()