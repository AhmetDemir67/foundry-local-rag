import time

from config import CHAT_MODEL_ALIAS, EMBEDDING_MODEL_ALIAS
from foundry import load_model
from qa import answer_query

TEST_CASES = [
    {"query": "How do I reset my password?", "type": "answerable", "expected_source": "password_reset.txt"},
    {"query": "What VPN client do remote employees use?", "type": "answerable", "expected_source": "vpn_setup.txt"},
    {"query": "Who do I contact about a printer paper jam?", "type": "answerable", "expected_source": "printer_issues.txt"},
    {"query": "Can I install software myself without IT help?", "type": "answerable", "expected_source": "software_install.txt"},
    {"query": "What should I do if I get a phishing email?", "type": "answerable", "expected_source": "security_policy.txt"},
    {"query": "How do guests connect to the office Wi-Fi?", "type": "answerable", "expected_source": "wifi_setup.txt"},
    {"query": "How do I set up company email on my phone?", "type": "answerable", "expected_source": "email_setup.txt"},
    {"query": "How often are my files backed up automatically?", "type": "answerable", "expected_source": "data_backup.txt"},
    {"query": "What is the CEO's salary?", "type": "unanswerable"},
    {"query": "What is the company's current stock price?", "type": "unanswerable"},
    {"query": "How do I book a conference room?", "type": "unanswerable"},
    {"query": "What is today's cafeteria menu?", "type": "unanswerable"},
]

NOT_FOUND_PHRASE = "could not find this information"


def degerlendir(vaka, cevap, top_chunks):
    kaynaklar = [source for _, source, _ in top_chunks]
    cevap_kucuk = cevap.lower()

    if vaka["type"] == "answerable":
        basarili = vaka["expected_source"] in kaynaklar and NOT_FOUND_PHRASE not in cevap_kucuk
    else:
        basarili = NOT_FOUND_PHRASE in cevap_kucuk

    return basarili, kaynaklar


def main():
    embedding_model = load_model(EMBEDDING_MODEL_ALIAS, show_progress=True)
    embedding_client = embedding_model.get_embedding_client()

    chat_model = load_model(CHAT_MODEL_ALIAS, show_progress=True)
    chat_client = chat_model.get_chat_client()

    satirlar = [
        "# Test Sonuçları\n",
        "| # | Soru | Tip | Beklenen Kaynak | Bulunan Kaynaklar | Süre (sn) | Sonuç |",
        "|---|------|-----|------------------|--------------------|-----------|-------|",
    ]
    basarili_sayisi = 0

    for i, vaka in enumerate(TEST_CASES, start=1):
        baslangic = time.perf_counter()
        cevap, top_chunks = answer_query(vaka["query"], embedding_client, chat_client)
        sure = time.perf_counter() - baslangic

        basarili, kaynaklar = degerlendir(vaka, cevap, top_chunks)
        basarili_sayisi += basarili

        beklenen = vaka.get("expected_source", "-")
        sonuc = "PASS" if basarili else "FAIL"
        satirlar.append(
            f"| {i} | {vaka['query']} | {vaka['type']} | {beklenen} | "
            f"{', '.join(sorted(set(kaynaklar)))} | {sure:.2f} | {sonuc} |"
        )
        print(f"[{sonuc}] ({sure:.2f}s) {vaka['query']}")
        print(f"       Cevap: {cevap}\n")

    embedding_model.unload()
    chat_model.unload()

    satirlar.append(f"\n**Toplam: {basarili_sayisi}/{len(TEST_CASES)} test geçti.**")

    with open("test_results.md", "w", encoding="utf-8") as dosya:
        dosya.write("\n".join(satirlar))

    print(f"\n{basarili_sayisi}/{len(TEST_CASES)} test geçti. Rapor test_results.md dosyasına yazıldı.")


if __name__ == "__main__":
    main()
