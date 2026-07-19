from config import DATA_DIR, DB_PATH, EMBEDDING_MODEL_ALIAS
from db import clear_chunks, create_table, get_connection, insert_chunk
from foundry import load_model


def belgeleri_parcala():
    """data/ altındaki her .txt dosyasını boş satıra göre paragraflara böler;
    her paragraf ayrı bir chunk olarak (kaynak_dosya, metin) çiftiyle döner."""
    parcalar = []
    for dosya in sorted(DATA_DIR.glob("*.txt")):
        metin = dosya.read_text(encoding="utf-8")
        paragraflar = [p.strip() for p in metin.split("\n\n") if p.strip()]
        for paragraf in paragraflar:
            parcalar.append((dosya.name, paragraf))
    return parcalar


def ingest():
    """Tüm chunk'ları embed'leyip rag.db'ye (chunks tablosu) yazar.
    Her çalıştırmada tablo temizlenip yeniden doldurulur (idempotent)."""
    model = load_model(EMBEDDING_MODEL_ALIAS, show_progress=True)
    embedding_client = model.get_embedding_client()

    baglanti = get_connection()
    create_table(baglanti)
    clear_chunks(baglanti)

    parcalar = belgeleri_parcala()
    icerikler = [icerik for _, icerik in parcalar]
    sonuclar = embedding_client.generate_embeddings(icerikler)

    for (kaynak, icerik), oge in zip(parcalar, sonuclar.data):
        insert_chunk(baglanti, kaynak, icerik, oge.embedding)

    baglanti.commit()
    baglanti.close()
    model.unload()

    print(f"\n{len(parcalar)} parça {DB_PATH.name} dosyasına kaydedildi.")


if __name__ == "__main__":
    ingest()
