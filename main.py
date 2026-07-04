from config import CHAT_MODEL_ALIAS, EMBEDDING_MODEL_ALIAS
from foundry import load_model
from qa import answer_query


def main():
    print("Modeller yükleniyor, lütfen bekleyin...")

    embedding_model = load_model(EMBEDDING_MODEL_ALIAS)
    embedding_client = embedding_model.get_embedding_client()

    chat_model = load_model(CHAT_MODEL_ALIAS)
    chat_client = chat_model.get_chat_client()

    print("Hazır! Sorunuzu yazın (çıkmak için 'q' yazın).\n")

    try:
        while True:
            soru = input("Soru: ").strip()
            if soru.lower() in ("q", "quit", "exit"):
                break
            if not soru:
                continue

            cevap, top_chunks = answer_query(soru, embedding_client, chat_client)
            print(f"Cevap: {cevap}")
            print(f"  (Kaynak: {', '.join(sorted(set(source for _, source, _ in top_chunks)))})\n")
    finally:
        embedding_model.unload()
        chat_model.unload()


if __name__ == "__main__":
    main()
