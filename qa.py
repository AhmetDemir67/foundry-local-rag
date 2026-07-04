from config import CHAT_MODEL_ALIAS, EMBEDDING_MODEL_ALIAS
from foundry import load_model
from retrieval import get_top_chunks

SYSTEM_PROMPT_TEMPLATE = """You are a question-answering assistant. Only use the
information in the CONTEXT below to answer. If the answer is not in the
context, do not make anything up; just reply with
"I could not find this information in my documents."

CONTEXT:
{context}
"""


def answer_query(question, embedding_client, chat_client, k=3):
    top_chunks = get_top_chunks(question, embedding_client, k=k)
    context = "\n\n".join(f"(Source: {source}) {content}" for _, source, content in top_chunks)
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context)

    yanit = chat_client.complete_chat([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ])
    return yanit.choices[0].message.content, top_chunks


def main():
    embedding_model = load_model(EMBEDDING_MODEL_ALIAS, show_progress=True)
    embedding_client = embedding_model.get_embedding_client()

    chat_model = load_model(CHAT_MODEL_ALIAS, show_progress=True)
    chat_client = chat_model.get_chat_client()

    test_sorulari = [
        "Does Foundry Local need an internet connection to run models?",
        "What is Foundry Local's stock price?",
    ]

    for soru in test_sorulari:
        cevap, top_chunks = answer_query(soru, embedding_client, chat_client)
        print(f"\nQuestion: {soru}")
        print(f"Answer: {cevap}")
        print("Retrieved from:", [source for _, source, _ in top_chunks])

    embedding_model.unload()
    chat_model.unload()


if __name__ == "__main__":
    main()
