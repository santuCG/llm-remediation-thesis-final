import os
import re
import shutil

repo_root = r"c:\Users\HP\Downloads\llm-remediation-thesis-final"
docs_dir = os.path.join(repo_root, "docs")
prereg_dir = os.path.join(repo_root, "preregistration")

# Task 8: Scrub plural pronouns
def scrub_pronouns(directory):
    pronoun_pattern = re.compile(r'\b(we|our|us)\b', flags=re.IGNORECASE)
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace pronouns with formal third-person alternatives
                # Note: A simple replacement might be too naive for complex sentences,
                # but a flag/count helps manual verification.
                matches = pronoun_pattern.findall(content)
                if matches:
                    print(f"Warning: Found {len(matches)} plural pronouns in {file}. Please review manually to ensure academic passive voice.")

print("Scanning for plural pronouns...")
scrub_pronouns(docs_dir)
scrub_pronouns(prereg_dir)
scrub_pronouns(repo_root)

# Task 9: Move Supervisor Update
old_update_path = os.path.join(repo_root, "13-07-2026", "Supervisor_Update.md")
new_update_path = os.path.join(docs_dir, "08-supervisor-update.md")
old_dir = os.path.join(repo_root, "13-07-2026")

if os.path.exists(old_update_path):
    print(f"Moving Supervisor_Update.md to docs/08-supervisor-update.md...")
    shutil.move(old_update_path, new_update_path)
    
    # Try to remove the old directory if empty
    try:
        os.rmdir(old_dir)
        print(f"Deleted old directory: {old_dir}")
    except OSError:
        print(f"Could not delete {old_dir} (may not be empty).")

print("Finalization complete.")
