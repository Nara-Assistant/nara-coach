import hello.tokens_per_string as tokens_per_string 
import hello.openai_requests as openai_requests 
import hello.dbembeddings as dbembeddings
import hello.extract_pdf_text as extract_pdf_text
import hello.files as file_module
import time
import os
from urllib.parse import urlparse
from .dbconnect import emb_conn

def train_db(url, file_id):
    ts = time.time()
    a = urlparse(url)
    filename = f"{file_id}-{ts}"
    file_module.download_file(url, f"{filename}-{os.path.basename(a.path)}")
    pdf_text = extract_pdf_text.get_text(f"{filename}-{os.path.basename(a.path)}")

    # print(pdf_text)
    with emb_conn:
        with emb_conn.cursor() as emb_curs:
            try: 
                emb_curs.execute(f"delete from hello_file_embeddings where file_id={file_id}")
            except Exception as e:
                print(e)

    print("Is here")
    chunks = tokens_per_string.split_chunks(pdf_text, chunk_size = 200)
    print(chunks)
    chunk_array = [(key, chunk) for key, chunk in enumerate(chunks)]
    for key, chunk in chunk_array:
        try:  
            print("Hey first iteration")  
            response = openai_requests.get_embedding(chunk[0])
            print("Hey first iteration:after")  
            dbembeddings.insert_embeddings(response, chunk[0], file_id, key + 1, chunk[1])
        except Exception as e:
            chunk_array = [
                *chunk_array,
                (key, chunk)
            ]
        # print((key + 1, len(response)))

MAX_TOKENS = 6000
SEPARATOR = "\n* "

def build_prompt(query, files_ids):
    response = openai_requests.get_embedding(query)
    documents_response = dbembeddings.match_documents(response, threshold=0.5, count=30, files_ids=files_ids)
    print(documents_response)
    chunks = []
    total_tokens = 0
    separator_tokens = tokens_per_string.num_tokens_from_string(SEPARATOR)

    for (_file_id, chunk_content, _similarity, tokens) in documents_response:
        total_tokens += (tokens + separator_tokens)

        if total_tokens > MAX_TOKENS:
            chunks = [
                *chunks,
                chunk_content[:((MAX_TOKENS - (total_tokens - (tokens + separator_tokens))))]
            ]
            break
        else:
            chunks = [
                *chunks,
                chunk_content + SEPARATOR
            ]

    return ''.join(chunks)

