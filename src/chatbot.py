import json

# Chargement du fichier FAQ
def load_faq(path='data/faq.json'):
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Fonction de recherche simple par correspondance exacte
def get_answer(user_input, faq_data):
    for item in faq_data:
        if user_input.strip().lower() == item["question"].strip().lower():
            return item["answer"]
    return "Je suis désolé, je n'ai pas compris votre question. Pouvez-vous la reformuler ? 😊"

# Exemple de test
if __name__ == "__main__":
    faq = load_faq()
    print("Bienvenue dans le chatbot formation marketing digital !")
    while True:
        question = input("Vous : ")
        if question.lower() in ["exit", "quit", "bye"]:
            print("Chatbot : Merci et à bientôt ! 👋")
            break
        response = get_answer(question, faq)
        print("Chatbot :", response)
