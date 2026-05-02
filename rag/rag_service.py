def retrieve_faq(query):

    with open("rag/hotel_FAQ.txt", "r") as file:
        faq_data = file.readlines()

    query = query.lower()

    best_match = None

    for line in faq_data:

        if any(word in line.lower() for word in query.split()):
            best_match = line.strip()
            break

    if best_match:
        return best_match

    return "Sorry, no relevant hotel information found."