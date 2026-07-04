import json
import sqlite3

from foundry_local_sdk import Configuration, FoundryLocalManager

VERITABANI_DOSYASI = "belgeler.db"

CUMLELER = [
    "Kedi bahçede uyuyor.",
    "Python programlama dilini öğreniyorum.",
    "Yapay zeka modelleri metinden öğrenir.",
    "Bugün hava çok güzel ve güneşli.",
    "Vektör benzerliği ile anlamsal arama yapılabilir.",
]


def tabloyu_olustur(baglanti):
    baglanti.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
    """)


def cumleleri_kaydet(baglanti, embedding_client):
    sonuclar = embedding_client.generate_embeddings(CUMLELER)
    for cumle, oge in zip(CUMLELER, sonuclar.data):
        vektor_json = json.dumps(oge.embedding)
        baglanti.execute(
            "INSERT INTO documents (content, embedding) VALUES (?, ?)",
            (cumle, vektor_json),
        )
    baglanti.commit()


def tum_kayitlari_goster(baglanti):
    print("\nVeritabanındaki kayıtlar:")
    for id_, content in baglanti.execute("SELECT id, content FROM documents"):
        print(f"  [{id_}] {content}")


def anahtar_kelimeyle_ara(baglanti, kelime):
    print(f"\n'{kelime}' kelimesini içeren kayıtlar:")
    sorgu = "SELECT id, content FROM documents WHERE content LIKE ?"
    for id_, content in baglanti.execute(sorgu, (f"%{kelime}%",)):
        print(f"  [{id_}] {content}")


def main():
    yapilandirma = Configuration(app_name="yerel_rag_asistanim")
    FoundryLocalManager.initialize(yapilandirma)
    yonetici = FoundryLocalManager.instance

    model = yonetici.catalog.get_model("qwen3-embedding-0.6b")
    model.download(lambda yuzde: print(f"\rİndiriliyor: %{yuzde:.1f}", end=""))
    print()
    model.load()
    embedding_client = model.get_embedding_client()

    baglanti = sqlite3.connect(VERITABANI_DOSYASI)
    tabloyu_olustur(baglanti)

    sayim = baglanti.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    if sayim == 0:
        cumleleri_kaydet(baglanti, embedding_client)
    else:
        print(f"Veritabanında zaten {sayim} kayıt var, tekrar eklenmedi.")

    tum_kayitlari_goster(baglanti)
    anahtar_kelimeyle_ara(baglanti, "yapay zeka")

    baglanti.close()
    model.unload()


if __name__ == "__main__":
    main()
