# Yerel RAG Asistanı (Foundry Local + SQLite)

Şirket içi IT destek dokümanlarına dayanan, tamamen **çevrimdışı** çalışan bir
Soru-Cevap (RAG — Retrieval-Augmented Generation) asistanı. Bu proje,
Microsoft Foundry Local üzerinde çalışan yerel bir embedding modeli ve yerel
bir sohbet (chat) modeli kullanarak, kullanıcının sorusunu önce şirketin
bilgi tabanında arar, ardından bulduğu ilgili metin parçalarını modele
bağlam olarak vererek cevap ürettirir. İnternet bağlantısı gerekmez;
tüm model çıkarımı kullanıcının kendi cihazında yapılır.

Bu proje, "Local RAG AI Assistant with Microsoft Foundry Local" bir aylık
staj/yaz programı planının uygulamalı çıktısıdır (bkz. `Summer School
Foundry Local Plan.pdf`).

## Nasıl çalışır (mimari)

```
Kullanıcı Sorusu
      │
      ▼
[1] Soru, embedding modeliyle (qwen3-embedding-0.6b) vektöre çevrilir
      │
      ▼
[2] SQLite'taki (rag.db) tüm parça (chunk) vektörleriyle kosinüs benzerliği
    hesaplanır, en alakalı K parça (varsayılan 3) seçilir
      │
      ▼
[3] Seçilen parçalar "CONTEXT" olarak sistem promptuna eklenir ve
    chat modeline (phi-3.5-mini) soru ile birlikte gönderilir
      │
      ▼
[4] Model, YALNIZCA verilen bağlamı kullanarak cevap üretir;
    bağlamda yoksa "bulamadım" der (halüsinasyon önlenir)
      │
      ▼
Kullanıcıya cevap + kullanılan kaynak dosya adları gösterilir
```

## Proje yapısı

| Dosya | Amaç |
|---|---|
| `config.py` | Ortak ayarlar: model isimleri, dosya yolları |
| `foundry.py` | Foundry Local SDK'sını başlatma / model yükleme yardımcıları |
| `db.py` | SQLite tablo oluşturma, parça ekleme/okuma |
| `similarity.py` | Kosinüs benzerliği hesaplama |
| `ingest.py` | `data/` altındaki `.txt` dosyalarını parçalara ayırır, embedding üretir, `rag.db`'ye kaydeder |
| `retrieval.py` | `get_top_chunks(query)` — bir soruya en alakalı K parçayı döndürür |
| `qa.py` | `answer_query(question)` — retrieval + LLM çağrısını birleştirip cevap üretir |
| `main.py` | Komut satırı (CLI) arayüzü — kullanıcı sorularını döngüde alır |
| `test_suite.py` | Otomatik fonksiyonel test seti; `test_results.md` raporu üretir |
| `data/*.txt` | Bilgi tabanı: 8 adet kurgusal şirket-içi IT destek dokümanı |
| `hello_model.py`, `embed_demo.py`, `sqlite_demo.py`, `prompt_demo.py` | Öğrenme/deneme scriptleri (Faz 1: SDK kurulumu, embedding, SQLite, prompt engineering pratiği) |

### Bilgi tabanı hakkında not

`data/` klasöründeki dokümanlar **gerçek bir şirketten alınmamıştır**;
projenin RAG boru hattını (chunking → embedding → retrieval → generation)
uçtan uca test edebilmek için yazılmış, tutarlı kurgusal bir "şirket IT
destek" senaryosudur (parola sıfırlama, VPN, yazıcı, yazılım kurulumu,
güvenlik politikası, Wi-Fi, e-posta, yedekleme). `rag.db` bu dosyalardan
`ingest.py` çalıştırılarak **otomatik üretilir**; elle doldurulmuş bir
veritabanı değildir ve bu yüzden repoya commit edilmez (bkz. `.gitignore`).

## Kurulum

1. Python 3.11+ ve [Foundry Local](https://learn.microsoft.com/azure/ai-foundry/foundry-local/get-started) kurulu olmalı.
2. Sanal ortam oluşturup bağımlılıkları kurun:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Foundry Local servisinin çalıştığından emin olun:
   ```
   foundry service start
   ```

## Çalıştırma

```
# 1) Bilgi tabanını işle ve veritabanını oluştur (modelleri ilk çalıştırmada indirir)
python ingest.py

# 2) Soru-cevap asistanını başlat
python main.py
```

`main.py` çalıştığında modelleri yükler, ardından konsoldan soru sormanızı
bekler. Çıkmak için `q` yazın.

Örnek oturum:

```
Soru: How do I reset my password?
Cevap: To reset your password, go to the self-service portal at
password.company.local and click "Forgot Password"...
  (Kaynak: password_reset.txt)

Soru: What is the CEO's salary?
Cevap: I could not find this information in my documents.
  (Kaynak: )
```

## Test

```
python test_suite.py
```

12 test sorgusu (8 cevaplanabilir + 4 cevaplanamaz) otomatik çalıştırılır,
her sorgu için doğru kaynağın bulunup bulunmadığı ve yanıt süresi ölçülür.
Sonuçlar `test_results.md` dosyasına yazılır (bkz. proje kökü).

**Son çalıştırma sonucu: 12/12 test geçti.** Ortalama yanıt süresi
~5,5 saniye (Foundry Local, CPU, `phi-3.5-mini` + `qwen3-embedding-0.6b`).

İlk çalıştırmada 10/12 test geçmişti; iki hata da model davranışından
kaynaklanıyordu (bkz. "Öğrenilenler").

## Tasarım kararları ve sınırlamalar

- **Brute-force benzerlik arama**: Vektörler SQLite'ta JSON metin olarak
  saklanır; sorgu anında tüm vektörler belleğe okunup Python'da kosinüs
  benzerliği hesaplanır. Bu, birkaç düzine parçalık küçük ölçek için
  yeterlidir; binlerce belgeye çıkıldığında özel bir vektör veritabanı
  (örn. FAISS, sqlite-vec) gerekir.
- **Chunking stratejisi**: Belgeler paragraf (`\n\n`) sınırlarına göre
  bölünür. Daha uzun/karmaşık belgeler için cümle bazlı veya sabit token
  uzunluklu chunking daha iyi sonuç verebilir.
- **Halüsinasyon önleme**: Sistem promptu modele yalnızca verilen bağlamı
  kullanmasını, bağlamda yoksa "bulamadım" demesini emreder. Bu, modelin
  kural ihlal etmeyeceği garantisi vermez ama pratikte gözlemlenen yanlış
  cevapları büyük ölçüde azaltır.
- **Arayüz**: CLI (Seçenek A) tercih edildi; zaman kısıtı nedeniyle
  Streamlit/Gradio veya HTML+JS arayüzü (Seçenek B/C) kapsam dışı bırakıldı.
- **Modeller**: `qwen3-embedding-0.6b` (embedding) ve `phi-3.5-mini` (chat) —
  hız/kalite dengesi için küçük modeller tercih edildi.

## Öğrenilenler

Chunk sınırlarının (paragraf bazlı bölme) retrieval kalitesini doğrudan
etkilediği gözlemlendi: çok kısa parçalar bağlamı eksik bırakırken çok uzun
parçalar alakasız bilgiyi de bağlama taşıyıp modelin dikkatini dağıtabiliyor.

En somut ders, ilk test koşusunda (10/12) ortaya çıktı:

1. **Yanlış-negatif cevaplanabilir soru**: "How do I set up company email on
   my phone?" sorusunda retrieval, doğru kaynağın (`email_setup.txt`) yanına
   alakasız bir `password_reset.txt` parçası da getirdi. Model doğru cevabı
   verdi ama sonuna gereksiz bir "bulamadım" cümlesi ekledi ve otomatik test
   bunu hata olarak işaretledi.
2. **Gevşek ret cümlesi**: "What is today's cafeteria menu?" gibi bağlam
   dışı bir soruda model, istenen tam cümle yerine kendi ifadesiyle ("I
   don't have access to real-time information...") cevap verdi.

Her iki durum da modelin *serbestçe* yorum yapmasından kaynaklanıyordu.
Sistem promptu şu şekilde sıkılaştırıldı: (a) bağlamın alakasız kısımlarını
yok saymasını, (b) soru tam olarak cevaplanabiliyorsa ek uyarı eklememesini,
(c) cevap yoksa *tam olarak* belirtilen cümleyi kullanmasını açıkça talep
ettik ([qa.py](qa.py) — `SYSTEM_PROMPT_TEMPLATE`). Bu değişiklikten sonra
test seti 12/12'ye çıktı. Bu, prompt mühendisliğinin retrieval kadar kritik
olduğunu gösteren somut bir örnek oldu.
