import os
from dotenv import load_dotenv
from groq import Groq
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

chroma_client = chromadb.PersistentClient(path="./chroma_db")
ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = chroma_client.get_or_create_collection(name="docs", embedding_function=ef)

def metin_oku(dosya_yolu):
    if dosya_yolu.endswith(".pdf"):
        reader = PdfReader(dosya_yolu)
        return "\n".join(sayfa.extract_text() for sayfa in reader.pages)
    else:
        with open(dosya_yolu, "r", encoding="utf-8") as f:
            return f.read()

def dosya_yukle(dosya_yolu):
    metin = metin_oku(dosya_yolu)
    parcalar = [metin[i:i+500] for i in range(0, len(metin), 500)]
    dosya_adi = os.path.basename(dosya_yolu)
    
    collection.add(
        documents=parcalar,
        ids=[f"{dosya_adi}_parca_{i}" for i in range(len(parcalar))],
        metadatas=[{"kaynak": dosya_adi} for _ in parcalar]
    )
    print(f"✓ {dosya_adi} — {len(parcalar)} parça yüklendi.")

def sor(soru, gecmis):
    sonuclar = collection.query(query_texts=[soru], n_results=3)
    context = "\n".join(sonuclar["documents"][0])
    kaynaklar = list(set(m["kaynak"] for m in sonuclar["metadatas"][0]))

    mesajlar = [
        {"role": "system", "content": f"Sadece aşağıdaki bilgilere dayanarak cevap ver. Bilgi yoksa 'Bu konuda bilgim yok' de.\n\nBilgi:\n{context}"}
    ]
    mesajlar += gecmis
    mesajlar.append({"role": "user", "content": soru})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=mesajlar
    )

    cevap = response.choices[0].message.content
    print(f"\nCevap: {cevap}")
    print(f"Kaynak: {', '.join(kaynaklar)}\n")
    return cevap

def main():
    print("=== RAG Sistemi ===")
    print("1. Dosya yükle")
    print("2. Soru sor")
    print("3. Yüklü dosyaları listele")
    secim = input("Seçim: ").strip()

    if secim == "1":
        while True:
            dosya = input("Dosya yolu (bitirmek için Enter): ").strip()
            if not dosya:
                break
            if os.path.exists(dosya):
                dosya_yukle(dosya)
            else:
                print("Dosya bulunamadı.")

    elif secim == "2":
        gecmis = []
        print("Sorularını yaz. Çıkmak için 'quit'.\n")
        while True:
            soru = input("Soru: ").strip()
            if soru.lower() == "quit":
                break
            cevap = sor(soru, gecmis)
            gecmis.append({"role": "user", "content": soru})
            gecmis.append({"role": "assistant", "content": cevap})

    elif secim == "3":
        sonuclar = collection.get()
        if not sonuclar["metadatas"]:
            print("Henüz dosya yüklenmedi.")
        else:
            dosyalar = set(m["kaynak"] for m in sonuclar["metadatas"] if m)
            print(f"\nYüklü dosyalar ({len(dosyalar)} adet):")
            for d in dosyalar:
                print(f"  - {d}")

if __name__ == "__main__":
    main()