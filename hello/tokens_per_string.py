import tiktoken
import math

def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def split_chunks(string: str, encoding_name: str = "cl100k_base", chunk_size = 200) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    total_tokens = encoding.encode(string)
    num_tokens = len(total_tokens)
    total_chunks = math.ceil(num_tokens / chunk_size)
    chunks = []
    i = 0
    while i < total_chunks:
        current_tokens = total_tokens[(i * chunk_size):(((i + 1) * chunk_size))]
        chunks = [
            *chunks,
            (encoding.decode(current_tokens), len(current_tokens))
        ]
        i += 1

    print(chunks)
    print(total_tokens)
    return chunks

