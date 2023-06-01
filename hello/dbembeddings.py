from .dbconnect import conn
import json
import unicodedata

def insert_embeddings(vector, content, file_id, vector_key, tokens): 
    with conn:
        with conn.cursor() as curs:
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
                query_e = f"select * from insert_embeddings(Array{vectorString}, E'{cleaned_content}', {file_id}, {vector_key}, {tokens})"
                print(query_e)
                curs.execute(query_e)
                results = curs.fetchall()

                try:
                    curs.execute(f"select dblink_disconnect('nara_embeddings')")
                except Exception as e:
                    # conn.close()
                    print(e)
                
                


                for rResult in results:
                    print(rResult)
            except Exception as e:
                # conn.close()
                print(content)
                print(e)


def match_documents(vector, threshold, count, files_ids): 
    response = []
    with conn:
        with conn.cursor() as curs:
            try:
                # try:
                #     curs.execute(f"select dblink_disconnect('nara_embeddings')")
                # except Exception as e:
                #     print("Already disconnected")
                    
                vectorString = '[' + ', '.join([str(vectorItem) for vectorItem in vector]) + ']'
                filesString = '[' + ', '.join([str(fileItem) for fileItem in files_ids]) + ']'
                curs.execute(f"select * from match_documents(Array{vectorString}, {threshold}, {count}, Array{filesString})")
                
                results = curs.fetchall()

                try:
                    curs.execute(f"select dblink_disconnect('nara_embeddings')")
                except Exception as e:
                    # conn.close()
                    print(e)

                for rResult in results:
                    response = [
                        *response,
                        rResult
                    ]
            except Exception as e:
                # conn.close()
                print(e)

    return response

