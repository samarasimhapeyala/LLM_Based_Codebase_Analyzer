from langchain.text_splitter import RecursiveCharacterTextSplitter  # Importing the text splitter from Langchain

# Function to chunk the code into smaller parts for analysis
def chunk_code(text, chunk_size=2000, chunk_overlap=200):
    """
    Splits a large block of text (code) into smaller chunks of a specified size
    with some overlap between consecutive chunks.

    Args:
        text (str): The source code or text to be chunked.
        chunk_size (int): The maximum size (in characters) of each chunk. Default is 2000.
        chunk_overlap (int): The number of overlapping characters between consecutive chunks. Default is 200.

    Returns:
        list: A list of text chunks with the specified size and overlap.
    """
    
    # Initialize the RecursiveCharacterTextSplitter with the given parameters
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,  # Maximum size of each chunk
        chunk_overlap=chunk_overlap,  # Number of characters to overlap between consecutive chunks
        separators=["\n\n", "\n", " ", ""]  # Define the splitting points: prefer splitting at newlines, then spaces
    )

    # Use the splitter to divide the input text into chunks and return the result
    return splitter.split_text(text)
