from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from dotenv import load_dotenv

from .models import Question

import pandas as pd
import openai
import numpy as np

from resemble import Resemble

import os

load_dotenv('.env')

Resemble.api_key(os.environ["RESEMBLE_API_KEY"])
openai.api_key = os.environ["OPENAI_API_KEY"]

COMPLETIONS_MODEL = "text-davinci-003"

MODEL_NAME = "curie"

DOC_EMBEDDINGS_MODEL = f"text-search-{MODEL_NAME}-doc-001"
QUERY_EMBEDDINGS_MODEL = f"text-search-{MODEL_NAME}-query-001"

MAX_SECTION_LEN = 500
SEPARATOR = "\n* "
separator_len = 3

COMPLETIONS_API_PARAMS = {
    # We use temperature of 0.0 because it gives the most predictable, factual answer.
    "temperature": 0.0,
    "max_tokens": 150,
    "model": COMPLETIONS_MODEL,
}

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

def construct_prompt(question: str, context_embeddings: dict, df: pd.DataFrame):
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

    header = """George Ferman is a Health optimization coach, and the creator of Atlantean genetics, a 90-day health program that aims to Increase testosterone levels, Improve the health of your thyroid, Detox from heavy metals, PUFAs and xenoestrogens the right way, Improve chronic fatigue and optimize mental clarity, Increase libido, Improve mood issues such as anxiety, Get daily deep sleep and cure insomnia, Improve blood markers, Lose fat, Get rid of dark circles and puffy eyes, Be motivated by default, Build muscle, Strength gains, Fix your posture, Decrease allergies, Improve lipid profile, Heal ED and PE, Clear skin from issues such as acne and eczema, Stop hair thinning, Improve ADD and ADHD, Improve migraines, Lower stress hormones, and Improve fertility. These are questions and answers by him. Please keep your answers to three sentences maximum, and speak in complete sentences. Stop speaking once your point is made.\n\nContext that may be useful, pulled from the description of his program:\n
    
    This program is a prescription i created in order to prevent and reverse health related problems.
    Without the bonuses, there are 500 pages of material inside of it.
    We start by resetting your metabolism, studying mitochondria, fixing root causes of sleep problems no one talks about (no, not circadian dysregulation), optimizing kyanine pathway, GABA, address excess serotonin the right way and so on.
    Then we move on to how to optimize your thyroid performance (i have used the exact same principle to optimize the blood work of many clients without thyroid medication), gut health, addressing and detoxing from PUFAs, heavy metals and xenoestrogens the right and effective way.
    In the second one we cover everything about nutrition ,testosterone, aromatase, SHBG, LH, bioavailable sources of nutrients and how to balance them, supplements, cures for ED, PE, how to address deficiencies and more such as  meal plans for optimizing thyroid and testosterone among other things.
    In lesson 3 we cover how to add muscle, how to lose fat, how to recomp, how to master bodyweight training all the way to advanced movements, how to stay in peak shape when extremely busy, training for women and training to optimize testosterone.
    Then we talk about other stuff such as your immune system but i do not want to turn this caption into an essay so i will say that with the principles i share here (many of which i share only with my 1-on-1 clients) have been proven to be more effective 5.000$ ( yes, i have calculated) of TRT, thyroid medications, blood pressure medications,  SSRIs, autoimmune medications and so on.
    So this $99 program is worth more than $5.000 of TRT and medication that most of the time do not work.
    Now, what makes this course different?
    It's not a 20 page pdf file that will cost you $50 and fix nothing.
    I also tested this product in 3 people for just 10 days and here's what they said.
    Keep in mind that these people had chronic insomnia, one was a low carbers who could not lose weight, one was  a person who was not able to treat acne with medications and one was on BP medication as well."""

    return (header + "".join(chosen_sections) + "\n\n\nQ: " + question + "\n\nA: "), ("".join(chosen_sections))

def answer_query_with_context(
    query: str,
    df: pd.DataFrame,
    document_embeddings,
):
    prompt, context = construct_prompt(
        query,
        document_embeddings,
        df
    )

    print("===\n", prompt)

    response = openai.Completion.create(
                prompt=prompt,
                **COMPLETIONS_API_PARAMS
            )

    return response["choices"][0]["text"].strip(" \n"), context

def index(request):
    return render(request, "index.html", { "default_question": "What is Metabolic Health?" })

@csrf_exempt
def ask(request):
    print("hola1")
    question_asked = request.POST.get("question", "")

    print("hola2")
    if not question_asked.endswith('?'):
        question_asked += '?'
    
    print("hola3")
    previous_question = Question.objects.filter(question=question_asked).first()
    #audio_src_url = previous_question and previous_question.audio_src_url if previous_question else None

    """if audio_src_url:
        print("previously asked and answered: " + previous_question.answer + " ( " + previous_question.audio_src_url + ")")
        previous_question.ask_count = previous_question.ask_count + 1
        previous_question.save()
        return JsonResponse({ "question": previous_question.question, "answer": previous_question.answer, "audio_src_url": audio_src_url, "id": previous_question.pk })"""

    print("hola4")
    df = pd.read_csv('book.pdf.pages.csv')
    print("hola5")
    document_embeddings = load_embeddings('book.pdf.embeddings.csv')
    print("hola6")
    answer, context = answer_query_with_context(question_asked, df, document_embeddings)

    project_uuid = '925953bd'
    voice_uuid = '9d89e4b3-george'

    """response = Resemble.v2.clips.create_sync(
        project_uuid,
        voice_uuid,
        answer,
        title=None,
        sample_rate=None,
        output_format=None,
        precision=None,
        include_timestamps=None,
        is_public=None,
        is_archived=None,
        raw=None
    )"""

    #print(response)

    question = Question(question=question_asked, answer=answer, context=context)
    print("hola7")
    question.save()
    print("hola8")
    return JsonResponse({ "question": question.question, "answer": answer, "audio_src_url": "", "id": question.pk })

@login_required
def db(request):
    questions = Question.objects.all().order_by('-ask_count')

    return render(request, "db.html", { "questions": questions })

def question(request, id):
    question = Question.objects.get(pk=id)
    return render(request, "index.html", { "default_question": question.question, "answer": question.answer})


