#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère un CRA à partir du modèle PDF original.
Le tableau/calendrier du PDF est conservé. Le script remplit seulement :
- le mois + l'année dans le titre
- le nombre de jours travaillés
- l'intervenant
- le client

Exemple :
python generer_cra_v3.py --mois 6 --annee 2026 --nb-jours 20
"""

import argparse
import calendar
from pathlib import Path
import fitz  # pip install pymupdf

INTERVENANT = "MHOMA Ben Djadid"
CLIENT = "Wholshom"

MOIS_FR = {
    1: "JANVIER", 2: "FEVRIER", 3: "MARS", 4: "AVRIL",
    5: "MAI", 6: "JUIN", 7: "JUILLET", 8: "AOUT",
    9: "SEPTEMBRE", 10: "OCTOBRE", 11: "NOVEMBRE", 12: "DECEMBRE",
}

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_TEMPLATE = BASE_DIR / "Modele_CRA_sans_mois_tableau_conserve.pdf"


def main():
    parser = argparse.ArgumentParser(description="Générer automatiquement le CRA mensuel")
    parser.add_argument("--mois", type=int, required=True, choices=range(1, 13), help="Mois de 1 à 12")
    parser.add_argument("--annee", type=int, required=True, help="Année, ex: 2026")
    parser.add_argument("--nb-jours", "--jours", dest="nb_jours", type=float, required=True, help="Nombre de jours travaillés")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE), help="Chemin du modèle PDF")
    parser.add_argument("--sortie", default=None, help="Nom du PDF généré")
    args = parser.parse_args()

    template = Path(args.template)
    if not template.exists():
        raise FileNotFoundError(f"Modèle introuvable : {template}")

    mois_nom = MOIS_FR[args.mois]
    sortie = Path(args.sortie) if args.sortie else BASE_DIR / f"CRA_{mois_nom.capitalize()}_{args.annee}.pdf"

    doc = fitz.open(template)
    page = doc[0]

    # 1) Mois + année dans le titre, à l'endroit où 'MAI 2026' a été masqué.
    page.insert_text(
        (654, 184),
        f"{mois_nom} {args.annee}",
        fontsize=34,
        fontname="helv",
        color=(0, 0, 0),
    )

    # 2) Nombre de jours travaillés, dans le bloc 'TEMPS DE TRAVAIL'.
    # Ajuste légèrement x/y si ton modèle client bouge.
    jours_txt = str(args.nb_jours).rstrip("0").rstrip(".") if isinstance(args.nb_jours, float) else str(args.nb_jours)
    page.insert_text(
        (1185, 138),
        jours_txt,
        fontsize=38,
        fontname="helv",
        color=(0, 0, 0),
    )

    # 3) Intervenant et client.
    page.insert_text((1045, 278), INTERVENANT, fontsize=22, fontname="helv", color=(0, 0, 0))
    page.insert_text((1045, 426), CLIENT, fontsize=22, fontname="helv", color=(0, 0, 0))

    doc.save(sortie, deflate=True, garbage=4)
    doc.close()
    print(f"CRA généré : {sortie}")


if __name__ == "__main__":
    main()
