from foundry_local_sdk import Configuration, FoundryLocalManager


def main():
    yapilandirma = Configuration(app_name="yerel_rag_asistanim")
    FoundryLocalManager.initialize(yapilandirma)
    yonetici = FoundryLocalManager.instance

    model = yonetici.catalog.get_model("phi-3.5-mini")
    model.download(lambda yuzde: print(f"\rİndiriliyor: %{yuzde:.1f}", end=""))
    print()
    model.load()

    chat_client = model.get_chat_client()
    yanit = chat_client.complete_chat([
        {"role": "user", "content": "Merhaba, kendini kısaca tanıtır mısın?"}
    ])
    print("Model cevabı:", yanit.choices[0].message.content)

    model.unload()


if __name__ == "__main__":
    main()
