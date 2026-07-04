from foundry_local_sdk import Configuration, FoundryLocalManager

CONTEXT = """
Foundry Local is a Microsoft tool that lets you run large language models
entirely on your own device, with no internet connection required. It
automatically manages model downloads and hardware acceleration (CPU/GPU/NPU).
"""

SYSTEM_PROMPT = f"""You are a question-answering assistant. Only use the
information in the CONTEXT below to answer. If the answer is not in the
context, do not make anything up; just reply with
"I could not find this information in my documents."

CONTEXT:
{CONTEXT}
"""

SORULAR = [
    "Does Foundry Local require an internet connection?",
    "What are Foundry Local's pricing plans?",
]


def main():
    yapilandirma = Configuration(app_name="yerel_rag_asistanim")
    FoundryLocalManager.initialize(yapilandirma)
    yonetici = FoundryLocalManager.instance

    model = yonetici.catalog.get_model("phi-3.5-mini")
    model.download(lambda yuzde: print(f"\rİndiriliyor: %{yuzde:.1f}", end=""))
    print()
    model.load()
    chat_client = model.get_chat_client()

    for soru in SORULAR:
        yanit = chat_client.complete_chat([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": soru},
        ])
        print(f"\nSoru: {soru}")
        print(f"Cevap: {yanit.choices[0].message.content}")

    model.unload()


if __name__ == "__main__":
    main()
