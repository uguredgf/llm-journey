import os
import json
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Karakterler
CHARACTERS = {
    "1": {
        "name": "Yardımcı",
        "prompt": "Sen yardımcı bir asistansın. Açık ve net cevaplar verirsin."
    },
    "2": {
        "name": "Öğretmen",
        "prompt": "Sen sabırlı bir öğretmensin. Her şeyi örneklerle, adım adım açıklarsın."
    },
    "3": {
        "name": "Komik",
        "prompt": "Sen esprili bir asistansın. Her cevaba mutlaka bir şaka veya espri eklersin."
    }
}

def karakter_sec():
    print("\nHangi karakterle konuşmak istersin?")
    for key, char in CHARACTERS.items():
        print(f"{key}. {char['name']}")
    
    secim = input("\nSeçimin (1/2/3): ").strip()
    if secim not in CHARACTERS:
        print("Geçersiz seçim, varsayılan kullanılıyor.")
        secim = "1"
    
    return CHARACTERS[secim]

def konusmayi_kaydet(messages, karakter_adi, total_tokens):
    # conversations klasörü yoksa oluştur
    os.makedirs("conversations", exist_ok=True)
    
    # Dosya adı: tarih + karakter
    tarih = datetime.now().strftime("%Y%m%d_%H%M%S")
    dosya_adi = f"conversations/{tarih}_{karakter_adi}.json"
    
    kayit = {
        "tarih": tarih,
        "karakter": karakter_adi,
        "toplam_token": total_tokens,
        "mesajlar": messages
    }
    
    with open(dosya_adi, "w", encoding="utf-8") as f:
        json.dump(kayit, f, ensure_ascii=False, indent=2)
    
    print(f"\nKonuşma kaydedildi: {dosya_adi}")

def main():
    karakter = karakter_sec()
    
    messages = [
        {"role": "system", "content": karakter["prompt"]}
    ]
    
    total_tokens = 0
    
    print(f"\n'{karakter['name']}' karakteriyle sohbet başladı.")
    print("Çıkmak için 'quit' yaz.\n")
    
    while True:
        user_input = input("Sen: ").strip()
        
        if not user_input:
            continue
            
        if user_input.lower() == "quit":
            konusmayi_kaydet(messages, karakter["name"], total_tokens)
            print(f"Toplam kullanılan token: {total_tokens}")
            print("Görüşürüz!")
            break
        
        messages.append({"role": "user", "content": user_input})
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )
        
        assistant_message = response.choices[0].message.content
        kullanilan_token = response.usage.total_tokens
        total_tokens += kullanilan_token
        
        messages.append({"role": "assistant", "content": assistant_message})
        
        print(f"Model: {assistant_message}")
        print(f"[Bu mesaj: {kullanilan_token} token | Toplam: {total_tokens} token]\n")

if __name__ == "__main__":
    main()