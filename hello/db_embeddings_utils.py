import hello.tokens_per_string as tokens_per_string 
import hello.openai_requests as openai_requests 
import hello.dbembeddings as dbembeddings
import hello.extract_pdf_text as extract_pdf_text
import hello.files as file_module
import time
import os
from urllib.parse import urlparse
from .dbconnect import emb_conn
from .models import files as files_model, FileFailedChunk
import json
from .notifications import send_notification

def set_failed_chunks(failed_chunks, file_id, avatar_id):
    for failed_chunk in failed_chunks:
        try:
            (FileFailedChunk(avatar_id = avatar_id, content = failed_chunk[2], tokens = failed_chunk[3], file_id = file_id, key = failed_chunk[0])).save()
        except Exception as e:
            print(e)

def train_db(url, file_id, raw_data = None, avatar_id = None):
    try: 
        if url is not None:
            url = url.strip()
            a = urlparse(url)

        ts = time.time()
        filename = f"{file_id}-{ts}"
        pdf_text = None

        if raw_data is not None:
            pdf_text = raw_data
        else:
            file_module.download_file(url, f"{filename}-{os.path.basename(a.path)}")
            pdf_text = extract_pdf_text.get_text(f"{filename}-{os.path.basename(a.path)}")

        # print(pdf_text)
        try:
            with emb_conn:
                with emb_conn.cursor() as emb_curs:
                    try: 
                        emb_curs.execute(f"delete from hello_file_embeddings where file_id={file_id}")
                    except Exception as e:
                        print(e)
        except Exception as e:
            print("Error deleting")

        print("Is here")
        chunks = tokens_per_string.split_chunks(pdf_text, chunk_size = 200)
        print(chunks)
        chunk_array = [(key, chunk) for key, chunk in enumerate(chunks)]
        failed_chunks = []

        current_position = 0

        while current_position < len(chunk_array):
            key, chunk = chunk_array[current_position]

            try:  
                print("Hey first iteration")  
                time.sleep(.05)
                response = openai_requests.get_embedding(chunk[0])
                print("Hey first iteration:after")  
                dbembeddings.insert_embeddings(response, chunk[0], file_id, key + 1, chunk[1])
                current_position = current_position + 1
            except Exception as e:
                current_position = current_position + 1
                failed_chunks = [
                    *failed_chunks,
                    (key, e, chunk[0], chunk[1])
                ]


        if failed_chunks:
            set_failed_chunks(failed_chunks, file_id, avatar_id)
            # send_notification("train_db", "nara-heroku", [("completion", f"done: {len(chunk_array) - len(failed_chunks)} - total: {len(chunk_array)}"), ("chunks", failed_chunks), ("file_id", file_id), ("description", "Error training chunks")])

            # print((key + 1, len(response)))
    except Exception as e:
        send_notification("train_db", "nara-heroku", [("url", url), ("file_id", file_id), ("e", str(e))])


MAX_TOKENS = 1000
SEPARATOR = "\n* "

def build_prompt(query, files_ids):
    response = openai_requests.get_embedding(query)
    documents_response = dbembeddings.match_documents(response, threshold=0.5, count=5, files_ids=files_ids)
    print(documents_response)
    chunks = []
    total_tokens = 0
    separator_tokens = tokens_per_string.num_tokens_from_string(SEPARATOR)

    chunks_by_file_id = {}

    for (_file_id, chunk_content, _similarity, tokens) in documents_response:
        if chunks_by_file_id.get(_file_id) is None:
            file_domain = files_model.objects.filter(id=_file_id).first()
            file_metadata = "" if file_domain is None else file_domain.metadata
            chunks_by_file_id[_file_id] = {
                "chunks": [],
                "metadata": file_metadata
            }
        total_tokens += (tokens + separator_tokens)

        if total_tokens > MAX_TOKENS:
            chunks_by_file_id[_file_id]["chunks"] = [
                *chunks_by_file_id[_file_id]["chunks"],
                chunk_content[:((MAX_TOKENS - (total_tokens - (tokens + separator_tokens))))]
            ]
            break
        else:
            chunks_by_file_id[_file_id]["chunks"] = [
                *chunks_by_file_id[_file_id]["chunks"],
                chunk_content + SEPARATOR
            ]

    response = []

    for key in chunks_by_file_id:
        response = [
            *response,
            {
                "content": ''.join(chunks_by_file_id[key]["chunks"]),
                "metadata": chunks_by_file_id[key]["metadata"]
            }
        ]
    ### JUST for test
    
    return json.dumps(response)

def get_valid_files(files_ids):
    return dbembeddings.get_valid_files(files_ids)