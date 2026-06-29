import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Konuşma geçmişi — başlangıçta sadece system mesajı var
messages = [
    {"role": "system", "content": "Sen yardımcı bir asistansın."}
]

print("Sohbet başladı. Çıkmak için 'quit' yaz.\n")

while True:
    # Kullanıcıdan mesaj al
    user_input = input("Sen: ")
    
    if user_input.lower() == "quit":
        print("Görüşürüz!")
        break
    
    # Kullanıcı mesajını geçmişe ekle
    messages.append({"role": "user", "content": user_input})
    
    # Tüm geçmişi modele gönder
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    
    # Modelin cevabını al
    assistant_message = response.choices[0].message.content
    
    # Cevabı geçmişe ekle
    messages.append({"role": "assistant", "content": assistant_message})
    
    print(f"Model: {assistant_message}\n")