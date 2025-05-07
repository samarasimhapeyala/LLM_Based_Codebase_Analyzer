import os  

# Supported code file extensions. These are the types of files we want to process.
SUPPORTED_EXTENSIONS = {'.py', '.java', '.js', '.ts', '.go', '.cpp', '.c', '.cs', '.rb', '.php'}

# Folders to exclude from processing. We will not scan these directories for code files.
IGNORED_DIRS = {
    '.git', '.mvn', 'node_modules', '__pycache__',  # Version control and package manager folders
    '.idea', '.vscode', 'build', 'dist', 'venv', 'env'  # IDE and virtual environment folders
}

def load_code_files(directory):
    """
    Walks through a directory and returns a list of supported code files (with content).

    Args:
        directory (str): The root directory to begin the file search.

    Returns:
        list: A list of dictionaries, each containing the filename, full path, and file content.
    """
    code_files = []  # List to store dictionaries with code file information
    
    # os.walk generates the file tree, iterating over each directory, subdirectory, and file
    for root, dirs, files in os.walk(directory):
        # Clean up dirs in-place to avoid descending into ignored directories (like test, .git, etc.)
        dirs[:] = [
            d for d in dirs
            if d.lower() not in IGNORED_DIRS and 'test' not in d.lower()
        ]
        
        # Skip the directory if it contains 'test' in its path
        if 'test' in root.lower():
            continue  # Skip the entire directory if it's related to tests

        # Iterate over all files in the current directory
        for file in files:
            file_lower = file.lower()  # Convert the file name to lowercase for case-insensitive comparison
            file_ext = os.path.splitext(file)[1].lower()  # Extract and lower-case the file extension

            # Check if the file has a supported extension and doesn't belong to a test-related file
            if file_ext in SUPPORTED_EXTENSIONS and 'test' not in file_lower:
                full_path = os.path.join(root, file)  # Get the full path of the file

                try:
                    # Open and read the file content
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Add the file's information to the list
                    code_files.append({
                        "filename": file,  # Store the file name
                        "path": full_path,  # Store the full file path
                        "content": content  # Store the content of the file
                    })
                except Exception as e:
                    # If an error occurs (e.g., file read error), log it and skip the file
                    print(f"Skipped {full_path}: {e}")
    
    return code_files  # Return the list of code files with their content
