"""
This file generates a directory tree structure for a given directory, 
along with any top-level comments found in Python files. It traverses 
the directory recursively, identifies Python files, and extracts any 
top-level comments (docstrings) present in those files. The generated 
output provides a structured representation of the directory tree with 
brief descriptions for Python files
"""

import os
import ast
import argparse

import os
import ast

elbow = "└──"
pipe = "│  "
tee = "├──"
tab = "   "


def tree(root_dir, prefix="", ignore_list=None):
    tree_output = ".\n" if len(prefix) == 0 else ""

    entries = os.listdir(root_dir)
    dirnames = sorted(
        [entry for entry in entries if os.path.isdir(os.path.join(root_dir, entry))]
    )
    filenames = sorted(
        [entry for entry in entries if os.path.isfile(os.path.join(root_dir, entry))]
    )

    # Directories
    for i, dirname in enumerate(dirnames):
        if ignore_list and any(
            ignore_dir in os.path.join(root_dir, dirname) for ignore_dir in ignore_list
        ):
            continue
        is_elbow = not (i != len(dirnames) - 1 or len(filenames) > 0)
        tree_output += f"{prefix}{elbow if is_elbow else tee} {dirname}\n"
        tree_output += tree(
            os.path.join(root_dir, dirname),
            prefix=prefix + f"{tab if is_elbow else pipe+tab}",
            ignore_list=ignore_list,
        )

    # Files
    for i, filename in enumerate(filenames):
        if ignore_list and any(
            ignore_dir in os.path.join(root_dir, filename) for ignore_dir in ignore_list
        ):
            continue
        tree_output += (
            f"{prefix}{tee if i != len(filenames) - 1 else elbow} {filename}\n"
        )

    return tree_output


def tree_with_comments(root_dir, prefix="", ignore_list=None):
    tree_output = ".\n" if len(prefix) == 0 else ""

    entries = os.listdir(root_dir)
    dirnames = sorted(
        [entry for entry in entries if os.path.isdir(os.path.join(root_dir, entry))]
    )
    filenames = sorted(
        [entry for entry in entries if os.path.isfile(os.path.join(root_dir, entry))]
    )

    # Directories
    for i, dirname in enumerate(dirnames):
        if ignore_list and any(
            ignore_dir in os.path.join(root_dir, dirname) for ignore_dir in ignore_list
        ):
            continue
        is_elbow = not (i != len(dirnames) - 1 or len(filenames) > 0)
        tree_output += f"{prefix}{elbow if is_elbow else tee} {dirname}\n"
        tree_output += tree_with_comments(
            os.path.join(root_dir, dirname),
            prefix=prefix + f"{tab if is_elbow else pipe+tab}",
            ignore_list=ignore_list,
        )

    # Files
    for i, filename in enumerate(filenames):
        if ignore_list and any(
            ignore_dir in os.path.join(root_dir, filename) for ignore_dir in ignore_list
        ):
            continue
        tree_output += (
            f"{prefix}{tee if i != len(filenames) - 1 else elbow} {filename}\n"
        )
        if filename.endswith(".py"):
            file_path = os.path.join(root_dir, filename)
            file_comments = extract_top_level_comments(file_path)
            if file_comments:
                tree_output += "".join(
                    [prefix + line + "\n" for line in file_comments.split("\n")]
                )
    return tree_output


def extract_top_level_comments(file_path):
    with open(file_path, "r") as file:
        file_content = file.read()

    try:
        tree = ast.parse(file_content)
    except SyntaxError:
        # Ignore files with syntax errors
        return None

    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            return format_comment(node.value.value)

    return None


def format_comment(comment):
    lines = comment.strip().split("\n")  # Strip leading and trailing whitespace
    if len(lines) > 1:
        # Multi-line comment, wrap in 「」 characters
        wrapped_comment = "「" + "\n".join(lines) + " 」"
        return wrapped_comment
    else:
        return comment


def main():
    parser = argparse.ArgumentParser(
        description="Generate directory tree structure with top-level comments"
    )
    parser.add_argument(
        "root_dir",
        nargs="?",
        default=os.getcwd(),
        help="Root directory to generate the tree structure for (default: current directory)",
    )
    parser.add_argument(
        "-I",
        "--ignore",
        nargs="+",
        help="List of directories to ignore (comma-separated)",
    )
    args = parser.parse_args()

    if not args.root_dir:
        print("Root Dir not given, using current working directory.")
        root_dir = os.getcwd()
    else:
        root_dir = args.root_dir

    root_dir = args.root_dir if args.root_dir else os.getcwd()
    ignore_list = args.ignore[0].split(",") if args.ignore else []

    tree_output = tree_with_comments(root_dir, ignore_list=ignore_list)
    print(tree_output)


if __name__ == "__main__":
    main()
