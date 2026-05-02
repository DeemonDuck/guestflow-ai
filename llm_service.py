from langchain_community.chat_models import ChatOllama


llm = ChatOllama(
    model="phi3",
    temperature=0.5
)


def generate_guest_response(prompt):

    response = llm.invoke(prompt)

    return response.content