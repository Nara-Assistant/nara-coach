from dotenv import load_dotenv
import os

# Use load_env to trace the path of .env:
load_dotenv('.env')

import pandas as pd
from typing import Set
from transformers import GPT2TokenizerFast
import argparse, sys

import numpy as np

from PyPDF2 import PdfReader

import pandas as pd
import openai
import csv
import numpy as np
from resemble import Resemble
import os
import pickle
from transformers import GPT2TokenizerFast

openai.api_key = os.environ["OPENAI_API_KEY"]

Resemble.api_key(os.environ["RESEMBLE_API_KEY"])
COMPLETIONS_MODEL = "text-davinci-003"

MODEL_NAME = "curie"

DOC_EMBEDDINGS_MODEL = f"text-search-{MODEL_NAME}-doc-001"
QUERY_EMBEDDINGS_MODEL = f"text-search-{MODEL_NAME}-query-001"

tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

MAX_SECTION_LEN = 500
SEPARATOR = "\n* "
separator_len = 3

COMPLETIONS_API_PARAMS = {
    # We use temperature of 0.0 because it gives the most predictable, factual answer.
    "temperature": 0.0,
    "max_tokens": 150,
    "model": COMPLETIONS_MODEL,
}

def count_tokens(text: str) -> int:
    """count the number of tokens in a string"""
    return len(tokenizer.encode(text))

def extract_pages(
    page_text: str,
    index: int,
) -> str:
    """
    Extract the text from the page
    """
    if len(page_text) == 0:
        return []

    content = " ".join(page_text.split())
    print("page text: " + content)
    outputs = [("Page " + str(index), content, count_tokens(content)+4)]

    return outputs

def get_pdf_data(filename): 
    return PdfReader(filename)

def book_parser():
    parser=argparse.ArgumentParser()

    parser.add_argument("--pdf", help="Name of PDF")

    args=parser.parse_args()

    filename = f"{args.pdf}"
    reader = get_pdf_data(filename)
    
    return (reader, filename)

def get_dataframe(reader):
    res = []
    i = 1
    for page in reader.pages:
        res += extract_pages(page.extract_text(), i)
        i += 1
    df = pd.DataFrame(res, columns=["title", "content", "tokens"])
    df = df[df.tokens<2046]
    df = df.reset_index().drop('index',axis=1) # reset index
    df.head()
    return df


def save_dataframe(df, filename):
    df.to_csv(f'{filename}.pages.csv', index=False)

def get_embedding(text: str, model: str):
    result = openai.Embedding.create(
      model=model,
      input=text
    )
    return result["data"][0]["embedding"]

def get_doc_embedding(text: str):
    return get_embedding(text, DOC_EMBEDDINGS_MODEL)

def get_query_embedding(text: str):
    return get_embedding(text, QUERY_EMBEDDINGS_MODEL)

def compute_doc_embeddings(df: pd.DataFrame):
    """
    Create an embedding for each row in the dataframe using the OpenAI Embeddings API.

    Return a dictionary that maps between each embedding vector and the index of the row that it corresponds to.
    """
    return {
        idx: get_doc_embedding(r.content) for idx, r in df.iterrows()
    }

# CSV with exactly these named columns:
# "title", "0", "1", ... up to the length of the embedding vectors.

def files_to_datasets(paths):
    data_frame_list = []
    for path in paths:
        reader =  get_pdf_data(path)
        data_frame_list.append(get_dataframe(reader))

    return pd.concat(data_frame_list, sort = False)

def create_files():
    (reader, filename) = book_parser()
    df = get_dataframe(reader)

    save_dataframe(df, filename)

    doc_embeddings = compute_doc_embeddings(df)

    with open(f'{filename}.embeddings.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["title"] + list(range(4096)))
        for i, embedding in list(doc_embeddings.items()):
            writer.writerow(["Page " + str(i + 1)] + embedding)


def create_files_by_dataframe(df, filename):
    save_dataframe(df, filename)

    doc_embeddings = compute_doc_embeddings(df)

    with open(f'{filename}.embeddings.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["title"] + list(range(4096)))
        for i, embedding in list(doc_embeddings.items()):
            writer.writerow(["Page " + str(i + 1)] + embedding)


def load_embeddings(fname: str):
    """
    Read the document embeddings and their keys from a CSV.

    fname is the path to a CSV with exactly these named columns:
        "title", "0", "1", ... up to the length of the embedding vectors.
    """

    df = pd.read_csv(fname, header=0)
    max_dim = max([int(c) for c in df.columns if c != "title"])
    return {
           (r.title): [r[str(i)] for i in range(max_dim + 1)] for _, r in df.iterrows()
    }

def vector_similarity(x, y) -> float:
    """
    We could use cosine similarity or dot product to calculate the similarity between vectors.
    In practice, we have found it makes little difference.
    """
    return np.dot(np.array(x), np.array(y))

def order_document_sections_by_query_similarity(query: str, contexts):
    """
    Find the query embedding for the supplied query, and compare it against all of the pre-calculated document embeddings
    to find the most relevant sections.

    Return the list of document sections, sorted by relevance in descending order.
    """
    query_embedding = get_query_embedding(query)

    document_similarities = sorted([
        (vector_similarity(query_embedding, doc_embedding), doc_index) for doc_index, doc_embedding in contexts.items()
    ], reverse=True)

    return document_similarities

def construct_prompt(question: str, context_embeddings: dict, df: pd.DataFrame, avatar = None, built_questions = None, built_prompts = None, should_include_prompt = True):
    """
    Fetch relevant embeddings
    """
    most_relevant_document_sections = order_document_sections_by_query_similarity(question, context_embeddings)

    chosen_sections = []
    chosen_sections_len = 0
    chosen_sections_indexes = []

    for _, section_index in most_relevant_document_sections:
        document_section = df.loc[df['title'] == section_index].iloc[0]

        chosen_sections_len += document_section.tokens + separator_len
        if chosen_sections_len > MAX_SECTION_LEN:
            space_left = MAX_SECTION_LEN - chosen_sections_len - len(SEPARATOR)
            chosen_sections.append(SEPARATOR + document_section.content[:space_left])
            chosen_sections_indexes.append(str(section_index))
            break

        chosen_sections.append(SEPARATOR + document_section.content)
        chosen_sections_indexes.append(str(section_index))

    #todo: get name and description from avatar
    header = f"""{avatar['name']}.\n{avatar['description']}."""
    print(built_prompts)
    if should_include_prompt is True
        return (header + built_prompts + "".join(chosen_sections) + built_questions + "\n\n\nQ: " + question + "\n\nA: "), ("".join(chosen_sections))
    else 
        return (header + built_prompts + "".join(chosen_sections) + built_questions), ("".join(chosen_sections))

def answer_query_with_context(
    query: str,
    df: pd.DataFrame,
    document_embeddings,
    avatart = None,
    built_questions = None,
    built_prompts = None
):
    print("before 1")
    prompt, context = construct_prompt(
        query,
        document_embeddings,
        df,
        avatart,
        built_questions,
        built_prompts
    )
    print("before 2")
    print("===\n", prompt)

    response = openai.Completion.create(
                prompt=prompt,
                **COMPLETIONS_API_PARAMS
            )
    print(("before 3", response))
    return response["choices"][0]["text"].strip(" \n"), context

# create_files_by_dataframe(files_to_datasets(["book.pdf", "metadata.pdf"]), "new")



