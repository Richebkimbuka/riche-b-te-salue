"""Riche’b te salue — application Flask."""
import os
import re
import secrets
from datetime import datetime

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

SIGNATURE = "— Riche’b te salue"

MESSAGES_BY_CATEGORY = {
    "philosophie": [
        "Tu ne contrôles pas tout ce qui t’arrive, mais tu choisis toujours la manière dont tu y réponds.",
        "Le silence n’est pas le vide : c’est l’espace où les pensées justes finissent par se faire entendre.",
        "On ne possède vraiment que ce que l’on est devenu, pas ce que l’on a accumulé.",
        "Le temps n’est pas ton ennemi. Il le devient seulement quand tu le laisses passer sans intention.",
        "Celui qui veut tout comprendre avant d’agir finit souvent par ne rien vivre.",
        "La vraie liberté commence quand tu n’as plus besoin de l’approbation de tout le monde.",
        "Ce qui est facile t’apprend peu. Ce qui te résiste te façonne.",
        "Chaque jour est une page blanche. Ce que tu y écris ne s’efface pas, alors écris avec soin.",
    ],
    "conseils": [
        "Protège ta paix comme on protège un trésor : tout le monde n’a pas le droit d’y entrer.",
        "Ne fais jamais une promesse dans la joie, ni une décision dans la colère.",
        "Paie tes dettes, tiens ta parole et garde ta dignité : le reste viendra.",
        "Prends soin de ton corps : c’est la seule maison dont tu ne pourras jamais déménager.",
        "Apprends à dire non sans te justifier trois fois. Un non clair vaut mieux qu’un oui forcé.",
        "Dépense moins que tu ne gagnes, et la liberté cessera d’être un rêve.",
        "Ne compare pas ton chapitre 3 au chapitre 20 d’un autre.",
        "Ce que tu fais en secret, jour après jour, finit toujours par se voir en public.",
    ],
    "ambition": [
        "Les grands rêves font peur au début. C’est le signe qu’ils sont à ta mesure.",
        "Tu n’as pas besoin de voir tout l’escalier. Monte simplement la première marche.",
        "La discipline, c’est choisir ce que tu veux le plus plutôt que ce que tu veux maintenant.",
        "Personne ne se souvient de ceux qui ont abandonné à un pas du but. Continue.",
        "Ton retard n’est pas un échec : c’est le début de ton propre rythme.",
        "Travaille en silence, laisse tes résultats faire le bruit.",
        "Le succès n’est pas un coup de chance : c’est une habitude répétée quand personne n’applaudit.",
        "Tombe sept fois, relève-toi huit. La seule vraie défaite est de rester à terre.",
        "Ne te contente pas d’être occupé. Sois utile, sois précis, sois excellent.",
    ],
    "relations": [
        "Les vraies amitiés ne se mesurent pas au nombre d’appels, mais à la qualité des présences.",
        "Celui qui t’aime ne te force pas à te rapetisser pour se sentir grand.",
        "Les gens montrent qui ils sont par leurs actes, pas par leurs promesses.",
        "Ne cherche pas à être compris de tous. Cherche à être sincère avec ceux qui comptent.",
        "Le respect est la monnaie la plus rare. Donne-le et exige-le avec la même constance.",
        "Écouter pour comprendre, et non pour répondre, change toutes les relations.",
        "Certaines personnes sont des saisons dans ta vie. Remercie-les, puis laisse l’hiver passer.",
        "Celui qui parle mal des autres devant toi parlera de toi devant eux.",
    ],
    "developpement": [
        "Ta pensée d’aujourd’hui construit la personne que tu seras demain. Surveille ce que tu te répètes.",
        "Le changement commence quand tu cesses de dire « je suis comme ça ».",
        "Pardonner n’est ni oublier ni excuser : c’est refuser de porter un poids qui ne t’appartient plus.",
        "Respire. Ralentis. Ce que tu ressens maintenant n’est pas permanent.",
        "Offre-toi dix minutes de silence par jour. Tu y retrouveras ce que le bruit t’a volé.",
        "Ne te juge pas sur tes pires jours, mais sur ta capacité à revenir.",
        "Lis, apprends, pose des questions. L’ignorance n’est pas une honte, y rester l’est.",
        "L’estime de soi ne se demande pas aux autres : elle se bâtit par les promesses que tu tiens envers toi-même.",
        "Écris tes objectifs. Une idée écrite devient un plan, un plan répété devient une réalité.",
    ],
    "foi": [
        "Place ta confiance en Dieu de tout ton cœur et ne t’appuie pas sur ta seule intelligence : Il aplanira tes sentiers. (cf. Proverbes 3, 5-6)",
        "Il y a un temps pour toute chose sous le ciel. Ce qui tarde n’est pas refusé : c’est préparé. (cf. Ecclésiaste 3, 1)",
        "La foi, ce n’est pas voir le chemin entier : c’est marcher avec Celui qui le connaît.",
        "Quand tu es faible, ne crains pas : la grâce de Dieu te suffit, et sa puissance se déploie dans ta faiblesse. (cf. 2 Corinthiens 12, 9)",
        "Aime ton prochain comme toi-même : c’est le secret de tout ce qui dure. (cf. Marc 12, 31)",
        "Prie sans cesse, non pour changer Dieu, mais pour laisser Dieu te changer.",
        "Ne t’inquiète pas du lendemain : chaque jour a assez de sa propre peine, et Dieu veille sur toi. (cf. Matthieu 6, 34)",
        "Rends grâce en toute circonstance : la gratitude ouvre les yeux sur les bénédictions déjà là. (cf. 1 Thessaloniciens 5, 18)",
    ],
}

MESSAGES = [text for group in MESSAGES_BY_CATEGORY.values() for text in group]
assert len(MESSAGES) == 50, f"Il faut 50 messages, il y en a {len(MESSAGES)}"

NAME_MAX = 30
NAME_RE = re.compile(r"^[^\W\d_]+(?:[ '’-][^\W\d_]+)*$")


def clean_name(raw):
    """Valide et met en forme le prénom. Retourne None s'il est invalide."""
    if not isinstance(raw, str):
        return None
    name = " ".join(raw.split())
    if not name or len(name) > NAME_MAX or not NAME_RE.match(name):
        return None
    name = name.lower()
    return re.sub(r"(^|[ -])([^\W\d_])", lambda m: m.group(1) + m.group(2).upper(), name)


@app.get("/")
def index():
    return render_template("index.html", year=datetime.now().year)


@app.post("/api/message")
def api_message():
    data = request.get_json(silent=True) or {}
    name = clean_name(data.get("name"))
    if name is None:
        return jsonify(error="Entre un prénom valide (lettres, espaces, tirets ou apostrophes)."), 400

    last = data.get("last")
    choices = [i for i in range(len(MESSAGES)) if i != last]
    idx = secrets.choice(choices)  # aléatoire cryptographique, sans répétition immédiate

    return jsonify(
        id=idx,
        greeting=f"Bonjour {name}\u00a0!",
        text=MESSAGES[idx],
        signature=SIGNATURE,
    )


@app.after_request
def security_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    resp.headers["X-Frame-Options"] = "SAMEORIGIN"
    return resp


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG") == "1",
    )
