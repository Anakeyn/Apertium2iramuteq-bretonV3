"""Compare deux lexiques IRaMuTeQ (forme<TAB>lemme<TAB>catégorie)
et mesure l'effet de leurs différences sur un corpus préparé.

Usage :
    python3 comparer_lexiques.py lexique_v1.txt lexique_v2.txt corpus.txt
"""
import argparse
import re
from collections import Counter

MOT = re.compile(r"[a-zà-ÿœæ_]+")


def charger_lexique(chemin):
    """Lit un lexique IRaMuTeQ : forme -> (lemme, catégorie)."""
    lexique = {}
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            morceaux = ligne.rstrip("\n").split("\t")
            if len(morceaux) >= 3:
                lexique[morceaux[0]] = (morceaux[1], morceaux[2])
    return lexique


def comparer(v1, v2):
    """Formes ajoutées, retirées, et formes dont la lecture change."""
    ajoutees = sorted(set(v2) - set(v1))
    retirees = sorted(set(v1) - set(v2))
    changees = sorted(f for f in set(v1) & set(v2) if v1[f] != v2[f])
    return ajoutees, retirees, changees


def compter_occurrences(chemin):
    """Occurrences des formes du corpus, lignes étoilées exclues.
    Découpage simplifié : IRaMuTeQ découpe un peu différemment."""
    with open(chemin, encoding="utf-8") as f:
        lignes = [l for l in f if not l.startswith("****")]
    return Counter(MOT.findall("".join(lignes).lower()))


def occurrences_par_lemme(occ, lexique):
    """Total des occurrences par couple (lemme, catégorie)."""
    total = Counter()
    for forme, n in occ.items():
        if forme in lexique:
            total[lexique[forme]] += n
    return total


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("lexique_v1")
    p.add_argument("lexique_v2")
    p.add_argument("corpus")
    args = p.parse_args()

    v1 = charger_lexique(args.lexique_v1)
    v2 = charger_lexique(args.lexique_v2)

    # 1. Différences entre les deux lexiques
    ajoutees, retirees, changees = comparer(v1, v2)
    print(f"Formes : v1 {len(v1)}, v2 {len(v2)}")
    print(f"Ajoutées : {', '.join(ajoutees) or 'aucune'}")
    print(f"Retirées : {', '.join(retirees) or 'aucune'}")
    print(f"Formes dont le lemme ou la catégorie change : {len(changees)}\n")
    types = Counter((v1[f], v2[f]) for f in changees)
    for (avant, apres), n in types.most_common(10):
        print(f"{n:5d}  {avant[0]} ({avant[1]}) -> {apres[0]} ({apres[1]})")

    # 2. Effet sur le corpus
    occ = compter_occurrences(args.corpus)
    touchees = {f: n for f, n in occ.items() if v1.get(f) != v2.get(f)}
    print(f"\nCorpus : {sum(occ.values())} occurrences, {len(occ)} formes")
    print(f"Lecture modifiée : {sum(touchees.values())} occurrences, "
          f"{len(touchees)} formes")
    for f, n in sorted(touchees.items(), key=lambda x: -x[1])[:15]:
        print(f"{n:5d}  {f:12s} v1 : {v1.get(f)}   v2 : {v2.get(f)}")

    # 3. Les lemmes concernés, avant et après
    t1 = occurrences_par_lemme(occ, v1)
    t2 = occurrences_par_lemme(occ, v2)
    print("\nLemme (catégorie)        v1     v2")
    for cle in sorted(set(t1) | set(t2)):
        if t1[cle] != t2[cle]:
            print(f"{cle[0] + ' (' + cle[1] + ')':22s} {t1[cle]:5d}  {t2[cle]:5d}")


if __name__ == "__main__":
    main()
