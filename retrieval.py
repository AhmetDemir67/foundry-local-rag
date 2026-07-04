from config import EMBEDDING_MODEL_ALIAS
from db import fetch_all_chunks, get_connection
from foundry import load_model
from similarity import cosine_similarity


def get_top_chunks(query, embedding_client, k=3):
    sorgu_sonucu = embedding_client.generate_embedding(query)
    sorgu_vektoru = sorgu_sonucu.data[0].embedding

    baglanti = get_connection()
    satirlar = fetch_all_chunks(baglanti)
    baglanti.close()

    skorlu = [
        (cosine_similarity(sorgu_vektoru, vektor), source, content)
        for source, content, vektor in satirlar
    ]
    skorlu.sort(key=lambda oge: oge[0], reverse=True)
    return skorlu[:k]


def main():
    model = load_model(EMBEDDING_MODEL_ALIAS, show_progress=True)
    embedding_client = model.get_embedding_client()

    test_sorgulari = [
        "How do I reset my password?",
        "What VPN client do remote employees use?",
    ]

    for sorgu in test_sorgulari:
        print(f"\nQuery: {sorgu}")
        for skor, source, content in get_top_chunks(sorgu, embedding_client, k=2):
            print(f"  [{skor:.4f}] ({source}) {content[:80]}...")

    model.unload()


if __name__ == "__main__":
    main()
