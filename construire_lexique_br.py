#!/usr/bin/env python3
"""
Construit un dictionnaire breton pour IRaMuTeQ (lexique_br.txt) à partir du
dictionnaire morphologique libre d'Apertium (apertium-bre, licence GPL-3).

Usage :
  git clone https://github.com/apertium/apertium-bre.git
  git clone https://github.com/apertium/apertium-br-fr.git      # facultatif
  python3 construire_lexique_br.py apertium-bre/apertium-bre.bre.dix \
          --corpus-annote apertium-br-fr/corpus -o lexique_br.txt

Produit aussi expression_br.txt (même dossier), le fichier des expressions :
  expression <TAB> forme soudée <TAB> catégorie
appliqué aux textes par preparer_corpus_breton.py.

Format produit (celui d'IRaMuTeQ) : une ligne par forme,
  forme <TAB> lemme <TAB> catégorie
avec les catégories d'IRaMuTeQ (nom, ver, aux, adj, adv, pre, con, art_def…).

Conventions :
  * tout est en minuscules ;
  * le trigramme « c'h » est écrit « c_h » (IRaMuTeQ coupe les mots à
    l'apostrophe) : préparez vos textes avec preparer_corpus_breton.py ;
  * les noms propres (np) ne sont pas inclus : IRaMuTeQ les traite comme
    formes non reconnues, comme en français ;
  * une seule analyse par forme (contrainte d'IRaMuTeQ) : on préfère la
    lecture sans mutation, puis les mots-outils, puis nom > verbe > adjectif ;
    les analyses validées à la main du corpus Apertium sont prioritaires.
"""
import argparse
import collections
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from expanseur_dix import Expanseur, decouper_analyse  # noqa: E402

APOSTROPHES = "'’ʼ‘`"
AUXILIAIRES = {"bezañ", "kaout", "endevout"}

# Adverbes de négation : « ket » est étiqueté adverbe simple dans Apertium
# (paradigme ouzhpenn__adv, sans <neg>). On le range avec « ne » en adv_sup,
# comme « ne » et « pas » dans le dictionnaire français d'IRaMuTeQ.
NEGATIONS = {"ket"}

# Variantes enregistrées par Apertium comme des lemmes distincts (souvent en
# lecture seule, r="LR") : on les rattache au lemme standard pour ne pas
# compter deux fois le même verbe.
VARIANTES = {
    "monet": "mont",
    "gellout": "gallout",
    "lavarout": "lavaret",
    "lâret": "lavaret",
    "gelver": "gervel",
}

# Lemmes internes d'Apertium pour les pronoms personnels. On leur donne un
# lemme lisible : le pronom sujet de la personne, et pour les réfléchis la
# forme en -unan.
PRONOM_SUJET = {("p1", "sg"): "me", ("p2", "sg"): "te", ("p1", "pl"): "ni",
                ("p2", "pl"): "cʼhwi", ("p3", "pl"): "int",
                ("p3", "m", "sg"): "eñ", ("p3", "f", "sg"): "hi"}
PRONOM_REFLECHI = {("p1", "sg"): "ma-unan", ("p2", "sg"): "da-unan",
                   ("p1", "pl"): "hon-unan", ("p2", "pl"): "hocʼh-unan",
                   ("p3", "pl"): "o-unan", ("p3", "m", "sg"): "e-unan",
                   ("p3", "f", "sg"): "he-unan"}


def lemme_pronom(surface, etiquettes):
    """Lemme lisible pour « prpers » et « direct »."""
    s = set(etiquettes)
    pers = next((p for p in ("p1", "p2", "p3") if p in s), None)
    nb = "pl" if "pl" in s else "sg"
    cle = (pers, nb)
    if pers == "p3" and nb == "sg":
        cle = (pers, "f" if "f" in s else "m", nb)
    if "ref" in s:
        if surface.lower().startswith("an-unan"):
            return "an-unan"                # « an-unan » : soi-même
        return PRONOM_REFLECHI.get(cle)
    return PRONOM_SUJET.get(cle)


# Formes que la règle « l'auxiliaire l'emporte sur un verbe plein » ne doit
# pas toucher : isolées, elles sont presque toujours un verbe plein. « deus »
# est l'impératif de « dont » (viens) ; « en deus », « he deus »… sont déjà
# couverts par les expressions soudées.
GARDER_VERBE_PLEIN = {"deus"}

# Formes absentes d'Apertium ou mal rattachées, fixées à la main :
# forme -> (lemme, catégorie)
AJOUTS = {
    "deze": ("kaout", "aux"),       # contraction de « deveze » (en deze)
    # v3 : erreurs révélées par le corpus Wikipédia « numérique ».
    # Quand plusieurs lectures ont le même rang, le verbe l'emporte sur
    # l'adjectif, l'adverbe et le numéral : on corrige les formes fréquentes.
    "c_hell": ("gallout", "ver"),   # « e c'hell » (il peut) ; lu « kell », cellule
    "unan": ("unan", "adj_num"),    # « un » ; lu « unaniñ », unir
    "du": ("du", "adj"),            # « noir » ; lu « duañ », noircir
    "ra": ("ober", "ver"),          # « a ra » (il fait) ; lu particule optative
    "mui": ("mui", "adv"),          # « plus » ; lu « muiañ », verbe
    "muiañ": ("mui", "adv"),
    "vuiañ": ("mui", "adv"),
    "muioc_h": ("mui", "adv"),
    "vuioc_h": ("mui", "adv"),
    "pennañ": ("pennañ_adj", "adj"),  # « principal » ; lu verbe « pennañ »
    "bennañ": ("pennañ_adj", "adj"),
    # « en o zouez » (parmi eux) : lu « touiñ », jurer
    "touez": ("e-touez", "pre"),
    "zouez": ("e-touez", "pre"),
    "douez": ("e-touez", "pre"),
    "ebarzh": ("e-barzh", "pre"),   # graphie soudée ; lu « ebarzhiñ »
}

# Locutions « préposition + nom » qu'Apertium donne comme figées et que l'on
# soude malgré la règle générale (voir choisir_expressions).
LOCUTIONS_FORCEES = {"da skouer", "e du"}  # « e du » : soudée en v2, à garder


PLEINS = {"nom", "ver", "adj", "adv"}

# rang : plus petit = préféré en cas d'ambiguïté
RANG = {"pre": 0, "art_def": 0, "art_ind": 0, "con": 1, "pro_per": 1,
        "pro_dem": 1, "pro_rel": 1, "pro_pos": 1, "pro_ind": 1,
        "adj_pos": 1, "adj_dem": 1, "adj_int": 1, "adj_ind": 1,
        "adv_sup": 2, "aux": 2, "nom": 3, "ver": 4, "adj": 5, "adv": 6,
        "adj_num": 7, "ono": 8}


def majoritaire(compteur):
    """Élément le plus fréquent, départage stable (résultat reproductible)."""
    return max(compteur.items(), key=lambda kv: (kv[1], str(kv[0])))[0]


def normaliser(mot):
    """minuscules, c'h -> c_h, apostrophes isolées retirées."""
    m = mot.lower()
    m = re.sub(r"c[" + APOSTROPHES + r"]h", "c_h", m)
    m = re.sub(r"[" + APOSTROPHES + r"]", "", m)
    return m.strip()


def categorie(etiquettes, lemme, pro_per=True):
    if not etiquettes:
        return None
    t = etiquettes[0]
    s = set(etiquettes[1:])
    if t == "n":
        return "nom"
    if t in ("vblex",):
        return "aux" if lemme in AUXILIAIRES else "ver"
    if t == "vbloc":
        return "aux"
    if t == "adj":
        return "adj"
    if t in ("adv", "preadv"):
        return "adv_sup" if "neg" in s or lemme in NEGATIONS else "adv"
    if t == "pr":
        return "pre"
    if t in ("cnjcoo", "cnjsub", "cnjadv"):
        return "con"
    if t == "det":
        if "def" in s:
            return "art_def"
        if "ind" in s:
            return "art_ind"
        if "pos" in s:
            return "adj_pos"
        if "dem" in s:
            return "adj_dem"
        if "itg" in s:
            return "adj_int"
        return "adj_ind"
    if t == "predet":
        return "adj_ind"
    if t == "num":
        return "adj_num"
    if t == "prn":
        if "dem" in s:
            return "pro_dem"
        if "rel" in s:
            return "pro_rel"
        if "pos" in s:
            return "pro_pos"
        if s & {"subj", "obj", "ref"} and pro_per:
            return "pro_per"
        return "pro_ind"
    if t == "vpart":
        return "adv_sup"           # particules verbales a, e, ez, o
    if t == "ij":
        return "ono"
    return None                    # np, abbr, sym, ponctuation…


def lire_corpus_annote(dossier):
    """Compte (forme, lemme) dans les fichiers *.tag.txt validés à la main."""
    vus = collections.Counter()
    for f in glob.glob(os.path.join(dossier, "**", "*.tag.txt"), recursive=True):
        forme = None
        for ligne in open(f, encoding="utf-8"):
            m = re.match(r'^"<(.+)>"', ligne)
            if m:
                forme = normaliser(m.group(1))
                continue
            m = re.match(r'^\s+"(.+?)"\s+(\S+)', ligne)
            if m and forme:
                vus[(forme, normaliser(m.group(1)), m.group(2))] += 1
                forme = None
    return vus


# ---------------------------------------------------------------------------
# Expressions (locutions en plusieurs mots)
# ---------------------------------------------------------------------------
# IRaMuTeQ soude les expressions avant de lemmatiser : « a benn ma » devient la
# forme « a_benn_ma », que le lexique doit connaître. Le fichier
# expression_br.txt suit le format d'IRaMuTeQ :
#     expression <TAB> forme soudée <TAB> catégorie
# Les clés sont écrites comme le texte après preparer_corpus_breton.py :
# minuscules, c'h -> c_h, traits d'union remplacés par des espaces.

def cle_expression(surface):
    """Locution Apertium -> clé d'expression, ou None si inutilisable."""
    s = surface.lower().strip()
    s = re.sub(r"c[" + APOSTROPHES + r"]h", "c_h", s)
    s = re.sub(r"(?<=\w)-(?=\w)", " ", s)
    mots = s.split()
    if len(mots) < 2 or not all(re.fullmatch(r"[a-zà-ÿœæ_]+", m) for m in mots):
        return None                 # élisions (ma'z), chiffres, sigles : écartés
    return " ".join(mots)


def format_categorie(cat):
    """nom -> NOM, adj_num -> ADJ:num : notation du fichier français d'IRaMuTeQ."""
    tete, _, reste = cat.partition("_")
    return tete.upper() + (":" + reste if reste else "")


def choisir_expressions(locutions, choix, cat_du_lemme, verbales=False):
    """Une analyse par expression.

    Par défaut, les locutions verbales (« gouzout brezhoneg », « mont e kêr »,
    conjuguées à toutes les personnes) sont écartées : les souder ferait
    disparaître des comptages des mots pleins comme « brezhoneg » ou « kêr ».
    On garde les locutions figées : adverbes, prépositions, conjonctions,
    noms composés, numéraux, pronoms, et les formes de « kaout » (en doa)."""
    retenues = {}
    for cle, ens in locutions.items():
        candidats = []
        for lemme, cat, verbale in ens:
            # « mont a rit », « glav a rae » (infinitif + ober) : même traitement
            verbale = verbale or cat == "ver"
            if verbale and not verbales:
                continue
            if verbale:
                # « dont da », « mont di » : la suite du verbe n'est faite que
                # de mots-outils, souder créerait de fausses locutions.
                suite = re.split(r"[_\- ]", lemme)[1:]
                if not any(len(m) >= 3 and choix.get(m, (None, None))[1] in PLEINS
                           for m in suite):
                    continue
                cat = "ver"
            candidats.append((RANG.get(cat, 9), lemme, cat))
        if not candidats:
            continue
        # « e brezhoneg », « e genver », « er skol » : préposition + mot plein.
        # Ces tournures sont libres ; les souder ôterait des comptages des
        # noms comme « brezhoneg » ou « skol ». On les laisse en deux mots.
        mots = cle.split()
        if (cle not in LOCUTIONS_FORCEES
                and len(mots) == 2 and choix.get(mots[0], (None, None))[1] == "pre"
                and choix.get(mots[1], (None, None))[1] in ("nom", "adj")):
            continue
        _, lemme, cat = min(candidats)
        soudee = cle.replace(" ", "_")
        if soudee in choix:
            continue
        retenues[cle] = (soudee, lemme, cat_du_lemme.setdefault(lemme, cat))
    return retenues


def main():
    p = argparse.ArgumentParser(description="Apertium -> dictionnaire IRaMuTeQ breton")
    p.add_argument("dix")
    p.add_argument("--corpus-annote", help="dossier corpus d'apertium-br-fr")
    p.add_argument("--sans-pro-per", action="store_true",
                   help="classer les pronoms personnels en pro_ind")
    p.add_argument("-o", "--sortie", default="lexique_br.txt")
    p.add_argument("--expressions", help="fichier d'expressions (défaut : expression_br.txt à côté du lexique)")
    p.add_argument("--sans-expressions", action="store_true", help="ne pas produire de fichier d'expressions")
    p.add_argument("--locutions-verbales", action="store_true",
                   help="inclure les locutions verbales conjuguées (mont e kêr…)")
    a = p.parse_args()
    os.makedirs(os.path.dirname(a.sortie) or ".", exist_ok=True)

    analyses = collections.defaultdict(set)   # forme -> {(lemme, cat, mutée, composée)}
    locutions = collections.defaultdict(set)  # « a benn ma » -> {(lemme, cat, verbale)}
    # Morceaux de locutions, ajoutés seulement s'ils manquent : IRaMuTeQ coupe
    # « en doa » en deux mots et peut couper « a-raok » au tiret.
    morceaux = collections.defaultdict(collections.Counter)
    for surface, analyse, _ in Expanseur(a.dix).developper():
        if not surface.strip():
            continue
        lemme_brut, etiq = decouper_analyse(analyse)
        lemme_brut = VARIANTES.get(lemme_brut, lemme_brut)
        if lemme_brut in ("prpers", "direct"):
            lemme_brut = lemme_pronom(surface, etiq[1:]) or lemme_brut
        cat = categorie(etiq, lemme_brut, not a.sans_pro_per)
        if not cat:
            continue
        lemme_brut = lemme_brut.replace(" ", "_")      # « memes tra » -> memes_tra
        if " " in surface.strip():
            # « en doa », « hon doa » (kaout) : on garde le dernier mot
            if "#" not in analyse and cat in ("aux", "ver"):
                morceaux[normaliser(surface.split()[-1])][(normaliser(lemme_brut), cat)] += 1
            # La locution entière est candidate au fichier d'expressions
            # (sauf analyses composées « a<pr>+kalon<n> », qui sont libres).
            cle = cle_expression(surface)
            if cle and "+" not in analyse:
                locutions[cle].add((normaliser(lemme_brut), cat,
                                    "#" in analyse and cat in ("ver", "aux")))
            continue
        if "-" in surface and cat in ("pre", "adv", "con"):
            # « a-raok », « war-lerc'h », « e-kichen » : dernier élément
            morceaux[normaliser(surface.split("-")[-1])][(normaliser(lemme_brut), cat)] += 1
        forme, lemme = normaliser(surface), normaliser(lemme_brut)
        if (not forme or not re.fullmatch(r"[a-zà-ÿœæ_\-]+", forme)
                or not re.fullmatch(r"[a-zà-ÿœæ_\-]+", lemme)):
            continue
        # « mutée » au sens large : toute forme dont l'initiale diffère de
        # celle du lemme (mutation, mais aussi forme élidée ou dialectale :
        # vat -> avat, eur -> bezañ). Ces lectures passent après les autres.
        mutee = forme[:1] != lemme[:1] and not forme.startswith(lemme[:2])
        composee = "+" in analyse
        analyses[forme].add((lemme, cat, mutee, composee))

    gold = lire_corpus_annote(a.corpus_annote) if a.corpus_annote else {}
    gold_par_forme = collections.defaultdict(collections.Counter)
    for (forme, lemme, tag), n in gold.items():
        gold_par_forme[forme][lemme] += n

    # Catégorie dominante de chaque lemme (nombre de formes non mutées) :
    # « ober » est d'abord un verbe, même si le dictionnaire l'admet comme nom.
    dominante = collections.defaultdict(collections.Counter)
    for forme, ens in analyses.items():
        for lemme, cat, mutee, composee in ens:
            if not mutee and not composee:
                dominante[lemme][cat] += 1
    dominante = {l: majoritaire(c) for l, c in dominante.items()}

    choix = {}
    for forme, ens in analyses.items():
        candidats = sorted(ens, key=lambda x: (x[2], x[3],
                                               (x[1] in PLEINS and x[1] != dominante.get(x[0], x[1])),
                                               RANG.get(x[1], 9),
                                               x[0] != forme, x[0], x[1]))
        prefere = gold_par_forme.get(forme)
        if prefere:
            lemme_gold = majoritaire(prefere)
            meilleurs = [c for c in candidats if c[0] == lemme_gold]
            if meilleurs:
                candidats = meilleurs + [c for c in candidats if c not in meilleurs]
        choix[forme] = candidats[0][:2]

    # Contrainte IRaMuTeQ : un lemme = une seule catégorie.
    cats_par_lemme = collections.defaultdict(collections.Counter)
    for lemme, cat in choix.values():
        cats_par_lemme[lemme][cat] += 1
    # Entre mots pleins (nom, verbe, adjectif, adverbe), on aligne la catégorie
    # sur la catégorie majoritaire du lemme ; si un mot-outil partage son lemme
    # avec un mot plein (« e » préposition / « e » particule), on suffixe le
    # lemme du moins fréquent pour les distinguer.
    renommes = harmonises = 0
    for forme, (lemme, cat) in list(choix.items()):
        cat_maj = majoritaire(cats_par_lemme[lemme])
        if cat == cat_maj:
            continue
        if cat in PLEINS and cat_maj in PLEINS:
            choix[forme] = (lemme, cat_maj)
            harmonises += 1
        else:
            choix[forme] = (f"{lemme}_{cat}", cat)
            renommes += 1

    cat_du_lemme = {lemme: cat for lemme, cat in choix.values()}
    ajoutes = 0
    remplaces = []
    for morceau, compteur in morceaux.items():
        if len(morceau) < 2 or not re.fullmatch(r"[a-zà-ÿœæ_]+", morceau):
            continue
        # à égalité : graphie standard (war- plutôt que àr-), puis la plus courte
        # (raok -> a-raok plutôt que war-raok)
        (lemme, cat), _ = max(compteur.items(), key=lambda kv: (kv[1], kv[0][0].replace('_', '').isascii(), -len(kv[0][0]), kv[0]))
        if morceau in choix:
            # « en devez », « o devo », « en doe » : ces formes de kaout
            # n'existent dans Apertium qu'en deux mots ; le mot isolé y est un
            # verbe plein rare (deviñ, teiñ). L'auxiliaire l'emporte sur un
            # verbe plein, jamais sur un autre mot-outil, ni sur les formes
            # de GARDER_VERBE_PLEIN.
            if not (cat == "aux" and choix[morceau][1] == "ver"):
                continue
            if morceau in GARDER_VERBE_PLEIN:
                continue
            remplaces.append(f"{morceau} ({choix[morceau][0]} -> {lemme})")
        else:
            ajoutes += 1
        cat = cat_du_lemme.setdefault(lemme, cat)
        choix[morceau] = (lemme, cat)
    print(f"{ajoutes} éléments de locutions ajoutés (raok -> a-raok, doa -> kaout…).")
    print(f"{len(remplaces)} formes rendues à l'auxiliaire : {', '.join(sorted(remplaces))}.")

    for forme, (lemme, cat) in AJOUTS.items():
        choix[forme] = (lemme, cat_du_lemme.setdefault(lemme, cat))
    print(f"{len(AJOUTS)} formes ajoutées à la main ({', '.join(AJOUTS)}).")

    if not a.sans_expressions:
        chemin_exp = a.expressions or os.path.join(os.path.dirname(a.sortie) or ".", "expression_br.txt")
        expressions = choisir_expressions(locutions, choix, cat_du_lemme, a.locutions_verbales)
        # v3 : mots-outils et adverbes à trait d'union (« e-barzh », « e-touez »,
        # « dreist-holl », « en-dro »). preparer_corpus_breton.py coupe les mots
        # au tiret : « e-barzh » devenait « e » + « barzh » (poète) et
        # « e-touez » « e » + « touez » (jurer). On les écrit dans le fichier
        # d'expressions avec leur trait d'union (« e-barzh <TAB> e_barzh ») :
        # le script de préparation ne les soude que s'ils sont écrits avec le
        # tiret dans le texte, jamais quand les deux mots sont séparés par un
        # espace (« a fell » reste « a » + « fell » : « ce que veut »).
        tirets = {}
        deja_soudees = {soudee for soudee, _, _ in expressions.values()}
        for forme, (lemme, cat) in sorted(choix.items()):
            if "-" not in forme or cat not in ("pre", "adv", "con"):
                continue
            if not all(forme.split("-")):
                continue
            soudee = forme.replace("-", "_")
            if soudee in choix or soudee in deja_soudees:
                continue   # « a-vremañ » -> « a_vremañ », déjà soudé par une locution
            tirets[forme] = (soudee, lemme, cat)
        print(f"{len(tirets)} mots à trait d'union ajoutés aux expressions (e-barzh, e-touez…).")
        expressions.update(tirets)
        with open(chemin_exp, "w", encoding="utf-8", newline="\n") as out:
            for cle in sorted(expressions):
                soudee, lemme, cat = expressions[cle]
                out.write(f"{cle}\t{soudee}\t{format_categorie(cat)}\n")
                # la forme soudée doit être connue du lexique
                choix[soudee] = (lemme, cat)
        stats_exp = collections.Counter(c for _, _, c in expressions.values())
        print(f"{len(expressions)} expressions écrites dans {chemin_exp} : "
              + ", ".join(f"{c} {n}" for c, n in stats_exp.most_common()))

    with open(a.sortie, "w", encoding="utf-8", newline="\n") as out:
        for forme in sorted(choix):
            lemme, cat = choix[forme]
            out.write(f"{forme}\t{lemme}\t{cat}\n")

    stats = collections.Counter(c for _, c in choix.values())
    ambigues = sum(1 for e in analyses.values() if len({(l, c) for l, c, *_ in e}) > 1)
    print(f"{len(choix)} formes écrites dans {a.sortie} "
          f"({len({l for l, _ in choix.values()})} lemmes).")
    print(f"{ambigues} formes ambiguës résolues, {harmonises} catégories harmonisées "
          f"et {renommes} formes au lemme suffixé (une catégorie par lemme), "
          f"{len(gold_par_forme)} formes tranchées par le corpus annoté.")
    print("Catégories :", ", ".join(f"{c} {n}" for c, n in stats.most_common()))


if __name__ == "__main__":
    main()
