def retrieve_faq(query):

    with open("rag/hotel_FAQ.txt", "r") as file:
        faq_data = file.readlines()

    query_words = set(query.lower().split())

    best_match = None
    highest_score = 0

    for line in faq_data:

        line_words = set(line.lower().split())

        score = len(query_words.intersection(line_words))

        if score > highest_score:
            highest_score = score
            best_match = line.strip()

    if best_match:
        return best_match

    return "Sorry, no relevant hotel information found."