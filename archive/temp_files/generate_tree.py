import os

def print_tree(startpath, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = {'.git', 'node_modules', '__pycache__', '.pytest_cache', '.github', '.agents'}
    
    tree_str = ""
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        tree_str += f"{indent}{os.path.basename(root)}/\n"
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            tree_str += f"{subindent}{f}\n"
    return tree_str

with open('full_repo_tree.txt', 'w', encoding='utf-8') as f:
    f.write(print_tree('.'))
