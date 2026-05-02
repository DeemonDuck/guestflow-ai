import re


def clean_text(text):
    return re.findall(r'\w+', text.lower())


def retrieve_faq(query):

    with open("rag/hotel_faq.txt", "r") as file:
        faq_data = file.readlines()

    query_words = set(clean_text(query))

    best_match = None
    highest_score = 0

    for line in faq_data:

        line_words = set(clean_text(line))

        score = len(query_words.intersection(line_words))

        if score > highest_score:
            highest_score = score
            best_match = line.strip()

    if best_match:
        return best_match

    return "Sorry, no relevant hotel information found."