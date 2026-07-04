import math

from foundry_local_sdk import Configuration, FoundryLocalManager

CUMLELER = [
    "Kedi bahçede uyuyor.",
    "Python programlama dilini öğreniyorum.",
    "Yapay zeka modelleri metinden öğrenir.",
    "Bugün hava çok güzel ve güneşli.",
    "Vektör benzerliği ile anlamsal arama yapılabilir.",
]

SORGU = "Metin tabanlı yapay zeka nasıl çalışır?"


def kosinus_benzerligi(a, b):
    nokta_carpimi = sum(x * y for x, y in zip(a, b))
    a_boyu = math.sqrt(sum(x * x for x in a))
    b_boyu = math.sqrt(sum(y * y for y in b))
    return nokta_carpimi / (a_boyu * b_boyu)


def main():
    yapilandirma = Configuration(app_name="yerel_rag_asistanim")
    FoundryLocalManager.initialize(yapilandirma)
    yonetici = FoundryLocalManager.instance

    model = yonetici.catalog.get_model("qwen3-embedding-0.6b")
    model.download(lambda yuzde: print(f"\rİndiriliyor: %{yuzde:.1f}", end=""))
    print()
    model.load()

    embedding_client = model.get_embedding_client()

    cumle_sonuclari = embedding_client.generate_embeddings(CUMLELER)
    cumle_vektorleri = [oge.embedding for oge in cumle_sonuclari.data]

    sorgu_sonucu = embedding_client.generate_embedding(SORGU)
    sorgu_vektoru = sorgu_sonucu.data[0].embedding

    benzerlikler = [
        (cumle, kosinus_benzerligi(sorgu_vektoru, vektor))
        for cumle, vektor in zip(CUMLELER, cumle_vektorleri)
    ]
    benzerlikler.sort(key=lambda oge: oge[1], reverse=True)

    print(f"\nSorgu: {SORGU}\n")
    print("Benzerlik skoruna göre sıralı cümleler:")
    for cumle, skor in benzerlikler:
        print(f"  {skor:.4f}  -  {cumle}")

    model.unload()


if __name__ == "__main__":
    main()
