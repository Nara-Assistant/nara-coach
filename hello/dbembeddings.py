from .dbconnect import emb_conn
import json
import unicodedata

def insert_embeddings(vector, content, file_id, vector_key, tokens): 
    print("Is here 1")
    try:
        # try:
        #     curs.execute(f"select dblink_disconnect('nara_embeddings')")
        # except Exception as e:
        #     print("Already disconnected")

        vectorString = '[' + ', '.join([str(vectorItem) for vectorItem in vector]) + ']'
        ## TODO: escape especial caracters before insert
        cleaned_content = content.replace("'", "''''").replace("\x00", "")
        # cleaned_content_en = cleaned_content.encode("ascii", "ignore")
        # cleaned_de = cleaned_content_en.decode('ascii')
        print(cleaned_content)
        print("Is here 2")
        query_e = f"select * from insert_embeddings(Array{vectorString}::vector, E'{cleaned_content}', {file_id}, {vector_key}, {tokens})"
        print(query_e)

        with emb_conn:
            with emb_conn.cursor() as emb_curs:
                emb_curs.execute(query_e)
                # results = emb_curs.fetchall()


        # for rResult in results:
        #     print(rResult)
    except Exception as e:
        print(content)
        print(e)
        raise e


    print("SUCCESS")

def match_documents(vector, threshold, count, files_ids): 
    response = []
    with emb_conn:
        with emb_conn.cursor() as curs:
            try:
                # try:
                #     curs.execute(f"select dblink_disconnect('nara_embeddings')")
                # except Exception as e:
                #     print("Already disconnected")
                    
                vectorString = '[' + ', '.join([str(vectorItem) for vectorItem in vector]) + ']'
                filesString = '[' + ', '.join([str(fileItem) for fileItem in files_ids]) + ']'
                curs.execute(f"select * from match_documents(Array{vectorString}::vector, {threshold}, {count}, Array{filesString})")
                
                results = curs.fetchall()


                for rResult in results:
                    response = [
                        *response,
                        rResult
                    ]
            except Exception as e:
                print(e)

    return response

