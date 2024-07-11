"""
Repo-Structure Generator source files.
"""

import argparse
import os
import ast
import fnmatch


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
            fnmatch.fnmatch(
                os.path.join(root_dir, dirname), os.path.join(os.getcwd(), pattern)
            )
            for pattern in ignore_list
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
            fnmatch.fnmatch(
                os.path.join(root_dir, filename), os.path.join(os.getcwd(), pattern)
            )
            for pattern in ignore_list
        ):
            continue
        tree_output += (
            f"{prefix}{tee if i != len(filenames) - 1 else elbow} {filename}\n"
        )

    return tree_output

def tree_with_source_map(root_dir, prefix="", ignore_list=None):
    tree_output = ".\n" if len(prefix) == 0 else ""

    for entry in sorted(os.listdir(root_dir)):
        entry_path = os.path.join(root_dir, entry)

        if ignore_list and any(fnmatch.fnmatch(entry_path, os.path.join(os.getcwd(), pattern)) for pattern in ignore_list):
            continue

        if os.path.isdir(entry_path):
            tree_output += f"{prefix}├── {entry}\n"
            tree_output += tree_with_source_map(entry_path, prefix + "│   ", ignore_list)
        elif entry.endswith('.py'):
            tree_output += f"{prefix}├── {entry}\n"

            with open(entry_path, 'r', encoding='utf-8') as f:
                try:
                    tree = ast.parse(f.read())

                    functions = []
                    async_functions = []
                    classes = {}

                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            if isinstance(node, ast.AsyncFunctionDef):
                                async_functions.append(node.name)
                            else:
                                functions.append(node.name)
                        elif isinstance(node, ast.ClassDef):
                            class_name = node.name
                            class_methods = [m.name for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
                            classes[class_name] = class_methods

                    for func_type, func_list in [("Functions", functions), ("Async Functions", async_functions)]:
                        if func_list:
                            tree_output += prefix + f"│   ├── {func_type}:\n"
                            for func in func_list:
                                tree_output += prefix + f"│   │   ├── {func}\n"

                    if classes:
                        tree_output += prefix + "│   ├── Classes:\n"
                        for class_name, methods in classes.items():
                            tree_output += prefix + f"│   │   ├── {class_name}:\n"
                            for method in methods:
                                tree_output += prefix + f"│   │   │   ├── {method}\n"

                    file_comments = extract_top_level_comments(entry_path)
                    if file_comments:
                        tree_output += "".join([prefix + "│   " + line + "\n" for line in file_comments.split("\n")])

                except SyntaxError as e:
                    print(f"Error parsing {entry_path}: {e}")

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
            fnmatch.fnmatch(
                os.path.join(root_dir, dirname), os.path.join(os.getcwd(), pattern)
            )
            for pattern in ignore_list
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
            fnmatch.fnmatch(
                os.path.join(root_dir, filename), os.path.join(os.getcwd(), pattern)
            )
            for pattern in ignore_list
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
        return "「" + "".join(lines) + " 」"


def read_ignore_file(root_dir):
    ignore_list = []
    ignore_file_path = os.path.join(root_dir, ".rsgignore")
    if os.path.isfile(ignore_file_path):
        with open(ignore_file_path, "r") as file:
            for line in file:
                ignore_list.append(line.strip())
    return ignore_list


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
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Increase output verbosity"
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default=os.getcwd(),
        help="Output directory where the file will be saved (default: current directory)",
    )
    args = parser.parse_args()

    if not args.root_dir:
        print("Root Dir not given, using current working directory.")
        root_dir = os.getcwd()
    else:
        root_dir = args.root_dir

    root_dir = args.root_dir if args.root_dir else os.getcwd()
    ignore_list = args.ignore[0].split(",") if args.ignore else []
    output_dir = args.output_dir if args.output_dir else os.getcwd()

    # Read ignore list from .rsgignore file
    ignore_list_from_file = read_ignore_file(root_dir)
    if ignore_list_from_file:
        ignore_list.extend(ignore_list_from_file)

    if args.verbose:
        print("Generating directory tree structure...")

    tree_output = tree_with_source_map(root_dir, ignore_list=ignore_list)

    if args.verbose:
        print(tree_output)

    output_path = os.path.join(output_dir, "repo-structure.md")
    with open(output_path, "w") as file:
        file.write("```shell\n" + tree_output + "\n```")

    if args.verbose:
        print(
            f"Directory tree structure has been generated and saved to '{output_path}'."
        )


if __name__ == "__main__":
    main()
