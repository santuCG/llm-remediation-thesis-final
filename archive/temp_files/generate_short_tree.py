import os

def print_tree(startpath, exclude_dirs=None, max_depth=3):
    if exclude_dirs is None:
        exclude_dirs = {'.git', 'node_modules', '__pycache__', '.pytest_cache', 'airflow', 'juice-shop', 'juice-shop-repo', 'af_venv', '.github'}
    
    tree_str = ""
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        level = root.replace(startpath, '').count(os.sep)
        
        if level > max_depth:
            continue
            
        indent = ' ' * 4 * (level)
        tree_str += f"{indent}{os.path.basename(root)}/\n"
        
        subindent = ' ' * 4 * (level + 1)
        if level < max_depth:
            for f in files:
                tree_str += f"{subindent}{f}\n"
        else:
            if files:
                tree_str += f"{subindent}... ({len(files)} files)\n"
    return tree_str

with open('short_repo_tree.txt', 'w', encoding='utf-8') as f:
    f.write(print_tree('.'))
