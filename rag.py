import os
from dotenv import load_dotenv
from groq import Groq
import chromadb
from chromadb.utils import embedding_functions

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Vektör veritabanı
chroma_client = chromadb.PersistentClient(path="./chroma_db")
ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = chroma_client.get_or_create_collection(name="docs", embedding_function=ef)

def dosya_yukle(dosya_yolu):
    with open(dosya_yolu, "r", encoding="utf-8") as f:
        metin = f.read()
    
    # Metni parçalara böl
    parcalar = [metin[i:i+500] for i in range(0, len(metin), 500)]
    
    collection.add(
        documents=parcalar,
        ids=[f"parca_{i}" for i in range(len(parcalar))]
    )
    print(f"{len(parcalar)} parça yüklendi.")

def sor(soru):
    # İlgili parçaları bul
    sonuclar = collection.query(query_texts=[soru], n_results=2)
    context = "\n".join(sonuclar["documents"][0])
    
    # Modele gönder
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": f"Sadece aşağıdaki bilgilere dayanarak cevap ver:\n\n{context}"},
            {"role": "user", "content": soru}
        ]
    )
    return response.choices[0].message.content

# Ana akış
print("1. Dosya yükle\n2. Soru sor")
secim = input("Seçim: ").strip()

if secim == "1":
    dosya = input("Dosya adı (örn: data.txt): ").strip()
    dosya_yukle(dosya)
else:
    while True:
        soru = input("\nSoru (quit: çık): ").strip()
        if soru.lower() == "quit":
            break
        print(f"\nCevap: {sor(soru)}\n")