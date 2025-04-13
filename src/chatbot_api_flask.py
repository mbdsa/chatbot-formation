from flask import Flask, request, jsonify, send_from_directory, make_response
import os
import json
import difflib
from openai import OpenAI
from dotenv import load_dotenv

# === Charger la clé API depuis .env ===
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

app = Flask(__name__)

# === Base absolue du projet ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# === Charger la FAQ ===
faq_path = os.path.join(BASE_DIR, "data", "faq.json")
with open(faq_path, encoding="utf-8") as f:
    faq_data = json.load(f)

# === Charger les formations ===
formations_path = os.path.join(BASE_DIR, "data", "formations.json")
with open(formations_path, encoding="utf-8") as f:
    formations_data = json.load(f)

# === Routes pour fichiers statiques ===
@app.route("/")
def serve_index():
    public_dir = os.path.join(BASE_DIR, "public")
    return send_from_directory(public_dir, "index.html")

@app.route("/styles/<path:filename>")
def serve_styles(filename):
    styles_dir = os.path.join(BASE_DIR, "styles")
    return send_from_directory(styles_dir, filename)

@app.route("/img/<path:filename>")
def serve_images(filename):
    img_dir = os.path.join(BASE_DIR, "public", "img")
    return send_from_directory(img_dir, filename)

@app.route("/scripts/<path:filename>")
def serve_scripts(filename):
    scripts_dir = os.path.join(BASE_DIR, "scripts")
    return send_from_directory(scripts_dir, filename)

# === API chatbot ===
@app.route("/api/chat", methods=["POST"])
def chatbot_response():
    data = request.get_json()
    user_message = data.get("message", "").strip().lower()

    ready_keywords = ["je veux", "je suis prêt", "je veux commencer", "je suis ok", "je suis partant", "je suis partante", "oui"]
    progression = "pret" if any(kw in user_message for kw in ready_keywords) else "init"

    last_formation = request.cookies.get("last_formation")

    if "history" not in request.cookies:
        message_history = [
            {"role": "system", "content": (
                "Tu es un assistant IA professionnel spécialisé en marketing digital. "
                "Ta mission est d'aider les utilisateurs à s'informer sur les formations proposées. "
                "Pose une question ciblée si besoin. Si l'utilisateur cite un thème comme 'réseaux sociaux', 'SEO', ou 'publicité', explique brièvement. "
                "S’il confirme son intérêt, propose ce lien directement : https://formation.digital-marketing.com/start. "
                "Ne redis pas toujours les mêmes choses. Avance dans la discussion."
            )}
        ]
    else:
        message_history = json.loads(request.cookies.get("history"))

    message_history.append({"role": "user", "content": user_message})

    # === Check formations.json ===
    for formation in formations_data:
        keywords = formation.get("keywords", [])
        if any(kw.lower() in user_message for kw in keywords):
            nom = formation.get("nom", "")
            details = formation.get("details", formation.get("description", ""))
            prix = formation.get("tarif", "")
            duree = formation.get("duree", "")
            lien = formation.get("lien", "")
            response_text = f"📚 {nom} : {details}\n💰 Prix : {prix}\n⏱️ Durée : {duree}\n👉 {lien}"
            message_history.append({"role": "assistant", "content": response_text})
            response = make_response(jsonify({"response": response_text}))
            response.set_cookie("history", json.dumps(message_history), max_age=3600)
            response.set_cookie("last_formation", nom, max_age=3600)
            return response

    # === Check faq.json ===
    questions = [entry["question"].lower() for entry in faq_data]
    best_match = difflib.get_close_matches(user_message, questions, n=1, cutoff=0.6)
    if best_match:
        matched_question = best_match[0]
        matched_answer = next(item["answer"] for item in faq_data if item["question"].lower() == matched_question)
        message_history.append({"role": "assistant", "content": matched_answer})
        response = make_response(jsonify({"response": matched_answer}))
        response.set_cookie("history", json.dumps(message_history), max_age=3600)
        return response

    # === Infos détaillées après formation détectée ===
    if last_formation:
        formation = next((f for f in formations_data if f.get("nom", "").lower() in user_message or f.get("nom", "").lower() == last_formation.lower()), None)
        if formation:
            contenu_keywords = ["consiste", "contenu", "programme", "modules", "cours"]
            prix_keywords = ["prix", "tarif", "coût"]
            duree_keywords = ["durée", "temps", "combien de temps"]

            last_bot_msg = next((m["content"] for m in reversed(message_history[:-1]) if m["role"] == "assistant"), "")
            already_replied = "Souhaitez-vous plus d'informations sur la formation" in last_bot_msg

            if any(x in user_message for x in contenu_keywords):
                response_text = f"📚 Voici le contenu de la formation '{formation['nom']}' : {formation.get('details', formation.get('description', ''))}"
            elif any(x in user_message for x in prix_keywords):
                response_text = f"💰 Le tarif de la formation '{formation['nom']}' est de {formation.get('tarif', '')}."
            elif any(x in user_message for x in duree_keywords):
                response_text = f"⏱️ La formation '{formation['nom']}' dure {formation.get('duree', '')}."
            elif already_replied:
                return make_response(jsonify({"response": None}))
            else:
                response_text = f"Souhaitez-vous plus d'informations sur la formation '{formation['nom']}' ?"

            message_history.append({"role": "assistant", "content": response_text})
            response = make_response(jsonify({"response": response_text}))
            response.set_cookie("history", json.dumps(message_history), max_age=3600)
            return response

    # === Lien direct si prêt
    if progression == "pret":
        training_link = "Voici un lien pour commencer ta formation : https://formation.digital-marketing.com/start"
        message_history.append({"role": "assistant", "content": training_link})
        response = make_response(jsonify({"response": training_link}))
        response.set_cookie("history", json.dumps(message_history), max_age=3600)
        return response

    # === Génération IA + Fallback si flou
    try:
        completion = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=message_history,
            temperature=0.7
        )
        gpt_response = completion.choices[0].message.content

        fallback_text = (
            "Je n’ai peut-être pas la réponse exacte à ta question, "
            "mais tu peux consulter notre page contact ici pour en savoir plus : "
            "👉 https://formation.digital-marketing.com/contact"
        )

        if not gpt_response or "je ne sais pas" in gpt_response.lower():
            final_response = fallback_text
        else:
            final_response = gpt_response

        message_history.append({"role": "assistant", "content": final_response})
        response = make_response(jsonify({"response": final_response}))
        response.set_cookie("history", json.dumps(message_history), max_age=3600)
        return response

    except Exception as e:
        return jsonify({"response": f"Erreur API : {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
