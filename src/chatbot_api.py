import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# ✔️ Charge la clé API depuis le fichier .env
load_dotenv()
client = OpenAI()

# ✔️ Chemin vers le fichier de questions/réponses
FAQ_PATH = "data/faq.json"

# ✔️ Charge le fichier FAQ
def load_faq():
    with open(FAQ_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ✔️ Fonction principale qui envoie la requête à l'API OpenAI
def ask_openai(user_input, faq_data):
    base_texte = "Voici une base de questions-réponses d'une formation en marketing digital :\n"
    for item in faq_data:
        base_texte += f"Q : {item['question']}\nR : {item['answer']}\n"

    base_texte += f"\nVoici la question de l'utilisateur : {user_input}\n"
    base_texte += "Réponds de manière claire et professionnelle, en utilisant la FAQ ci-dessus comme base."

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Tu es un assistant IA pour un centre de formation."},
            {"role": "user", "content": base_texte},
        ],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()

# ✔️ Lancement du chatbot en ligne de commande
if __name__ == "__main__":
    faq = load_faq()
    print("Bienvenue dans le chatbot IA formation marketing digital (API GPT) !")
    while True:
        question = input("Vous : ")
        if question.lower() in ["exit", "quit", "bye"]:
            print("Chatbot : Merci et à bientôt ! 👋")
            break
        answer = ask_openai(question, faq)
        print("Chatbot :", answer)
