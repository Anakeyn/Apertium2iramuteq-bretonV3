# Apertium2iramuteq-bretonV3

Dictionnaire de lemmatisation du **breton** pour [IRaMuTeQ](https://pratinaud.gitpages.huma-num.fr/iramuteq-website/), construit à partir du dictionnaire morphologique libre d'[Apertium](https://github.com/apertium/apertium-bre) (`apertium-bre`, par Francis Tyers, Fulup Jakez et Gwenvael Jekel, avec le soutien de l'Ofis ar Brezhoneg).

IRaMuTeQ ne propose pas de dictionnaire breton. Sans dictionnaire, les analyses portent sur les formes du texte : *tud*, *dud* et *den* sont trois mots différents. Avec ce dictionnaire, ils sont rattachés au même lemme, *den*.

Le dépôt contient :
- le **dictionnaire prêt à l'emploi** (`dictionnaire/lexique_br.txt`) ;
- un **dictionnaire d'expressions** bretonnes (`dictionnaire/expression_br.txt`) : *a-benn ma*, *meur a*, *da lavaret eo*, *c'hoari video*… ;
- un **script de préparation** des textes bretons pour IRaMuTeQ ;
- les **scripts de construction**, pour régénérer le dictionnaire depuis Apertium ;
- un **corpus de test** prêt à ouvrir.

Ce dépôt est la **version 3**. Elle corrige des erreurs que le corpus de test ne faisait pas ressortir, mais qu'a révélées un vrai corpus : les 123 articles de la Wikipédia bretonne sur le numérique, étudiés dans l'article *Le numérique vu par les Wikipédia bretonne et française : comparer deux corpus avec IRaMuTeQ* (dépôt [wiki-numerique-br-fr-iramuteq](https://github.com/Anakeyn/wiki-numerique-br-fr-iramuteq)). Les versions précédentes restent disponibles, inchangées, pour rester conformes à leurs articles : [v1](https://github.com/Anakeyn/Apertium2iramuteq-breton) et [v2](https://github.com/Anakeyn/Apertium2iramuteq-bretonV2).

## Ce qui change par rapport à la v2

Les sources Apertium sont les mêmes. Les statistiques textuelles d'IRaMuTeQ sur le corpus Wikipédia montraient, parmi les formes actives les plus fréquentes, des lemmes absurdes pour un corpus sur le numérique : *unaniñ* (unir), *kell* (cellule), *barzh* (poète), *touiñ* (jurer). Deux causes :

1. **Le verbe l'emporte trop souvent.** Quand plusieurs lectures sont possibles, le script de construction préfère le nom, puis le verbe, puis l'adjectif, l'adverbe et le numéral. Pour quelques formes très fréquentes, c'est faux. Elles sont corrigées une à une dans `AJOUTS` :

| Forme | v2 | v3 | Sens |
|---|---|---|---|
| *unan* | unaniñ (`ver`) | unan (`adj_num`) | « un » |
| *c'hell* | kell (`nom`) | gallout (`ver`) | « peut » (*e c'hell*) |
| *ra* | ra (`adv_sup`) | ober (`ver`) | « fait » (*a ra*) |
| *du* | duañ (`ver`) | du (`adj`) | « noir » |
| *mui*, *muiañ*, *muioc'h* | muiañ (`ver`) | mui (`adv`) | « plus », « le plus » |
| *pennañ* | pennañ (`ver`) | pennañ_adj (`adj`) | « principal » |
| *touez*, *zouez* | touiñ (`ver`) | e-touez (`pre`) | « parmi » (*en o zouez*) |
| *ebarzh* | ebarzhiñ (`ver`) | e-barzh (`pre`) | « dedans » |

2. **Les mots à trait d'union étaient coupés.** `preparer_corpus_breton.py` sépare les mots au tiret, et *e-barzh* (« dedans ») devenait *e* + *barzh* (« poète »), *e-touez* (« parmi ») *e* + *touez*, lu comme le verbe « jurer ». Le fichier d'expressions contient maintenant les 320 mots-outils et adverbes à trait d'union d'Apertium (*e-barzh*, *e-touez*, *dreist-holl*, *en-dro*, *war-dro*, *a-walc'h*…). Le script de préparation les soude **seulement quand ils sont écrits avec le tiret** : *a-fell* n'existe pas en deux mots, et *a fell* (« que veut ») reste séparé.

S'y ajoute la locution *da skouer* (« par exemple »), qu'Apertium donne comme figée mais que la règle « préposition + nom » laissait en deux mots : *skouer* (« exemple ») était l'un des mots pleins les plus fréquents.

**Effet sur le corpus Wikipédia** (123 articles) : 1 721 occurrences changent de lecture. *ober* passe de 563 à 739 occurrences, *gallout* de 346 à 480 ; *touiñ* et *ra* disparaissent, *kell* tombe de 135 à 1 ; *unaniñ* tombe de 159 à 31 (les vraies formes du verbe, comme *unanet*) et *barzh* de 127 à 12. Sur le corpus de test, l'effet est faible : 74 occurrences.

Le lexique compte 260 369 formes et 13 124 lemmes ; le fichier d'expressions, 4 059 expressions. Les formes de la v2 sont toutes conservées : 321 formes soudées sont ajoutées et 15 formes changent de lecture.

## Ce qui avait changé de la v1 à la v2

Les sources Apertium sont les mêmes (voir la [section 6](#6-régénérer-le-dictionnaire)), le fichier d'expressions est identique : seules les corrections ci-dessous distinguent les deux lexiques.

| Correction | v1 | v2 |
|---|---|---|
| Négation *ket* | `adv` (adverbe plein, actif dans les analyses) | `adv_sup`, comme *ne*, et comme *ne* et *pas* en français |
| Verbes en double dans Apertium | *monet*, *gellout*, *lavarout*, *lâret*, *gelver* : lemmes distincts | rattachés à *mont*, *gallout*, *lavaret*, *gervel* (421 formes) |
| Formes de *kaout* écrites en deux mots (*o devez*, *o devo*, *en doe*) | le second mot isolé était lu comme un verbe plein : *devez* et *devo* → deviñ, *doe* → teiñ | *kaout* (`aux`). *deus* isolé reste *dont* : c'est l'impératif « viens », et *en deus*, *he deus*… sont déjà soudés par les expressions |
| *deze*, contraction de *deveze* (*en deze*) | non reconnu | *kaout* (`aux`) |
| Pronoms personnels | lemmes internes d'Apertium `prpers` et `direct` | lemme du pronom sujet de la même personne : *anezhañ*, *hen* → eñ ; *ac'hanon*, *am* → me ; réfléchis en *-unan* : *e-unanik*, *e-unan* → e-unan |
| *te* (tu) | lu comme le nom *te* (thé) | pronom ; le nom devient *te_nom* |

Le lexique compte 256 310 formes et 11 844 lemmes hors expressions (v1 : 256 309 formes, 11 837 lemmes).

## Sommaire

1. [Le dictionnaire prêt à l'emploi](#1-le-dictionnaire-prêt-à-lemploi--aucune-commande-nécessaire)
2. [Ce que fait le dictionnaire](#2-ce-que-fait-le-dictionnaire)
3. [Préparer ses propres textes](#3-préparer-ses-propres-textes--preparer_corpus_bretonpy)
4. [Installer le dictionnaire dans IRaMuTeQ](#4-installer-le-dictionnaire-dans-iramuteq)
5. [Limites à connaître](#5-limites-à-connaître)
6. [Régénérer le dictionnaire](#6-régénérer-le-dictionnaire)
7. [Licence et citation](#7-licence-et-citation)

## 1. Le dictionnaire prêt à l'emploi : aucune commande nécessaire

| Fichier | Contenu |
|---|---|
| `dictionnaire/lexique_br.txt` | 260 369 formes, 13 124 lemmes (expressions soudées comprises), UTF-8, une ligne par forme : `forme<TAB>lemme<TAB>catégorie` |
| `dictionnaire/expression_br.txt` | 4 059 expressions, au format des fichiers d'expressions d'IRaMuTeQ : `expression<TAB>forme soudée<TAB>catégorie`. Les 320 mots à trait d'union y sont écrits avec leur tiret (`e-barzh<TAB>e_barzh<TAB>PRE`) |
| `corpus_test/corpus_test_breton.txt` | Corpus de test déjà préparé, UTF-8 (Linux, macOS) |
| `corpus_test/corpus_test_breton_windows.txt` | Le même, en Windows-1252 |

Le corpus de test reprend les 1 164 phrases du corpus d'Apertium, réparties en 47 textes. Ses expressions sont déjà soudées. C'est celui de la v2, inchangé : il a été préparé avant la soudure des mots à trait d'union, qui ne s'applique qu'aux textes préparés avec le script de la v3.

**Pour récupérer les fichiers :** sur GitHub, cliquez sur le fichier, puis sur le bouton de téléchargement (*Download raw file*). Vous pouvez aussi récupérer tout le dépôt avec le bouton vert **Code → Download ZIP**.

**Premier essai conseillé :** ouvrez le corpus de test avec ce dictionnaire (voir la [section 4](#4-installer-le-dictionnaire-dans-iramuteq)). Lancez ensuite les *Statistiques textuelles* et regardez combien de formes restent en `nr` (non reconnues) : ce sont surtout des noms propres.

## 2. Ce que fait le dictionnaire

- **Les mutations sont lemmatisées** : *dud*, *tud* → den ; *vamm* → mamm ; *zeu* → dont. *c'hoari* muté de *koari* est distingué de *c'hoari* (jouer).
- **Les verbes conjugués** sont rattachés à l'infinitif : *graet* → ober. *eo*, *emañ*, *bet* → bezañ, classé `aux` comme *kaout*, à l'image d'*être* et *avoir* en français.
- **Les pronoms personnels** sont rattachés au pronom sujet de la même personne : *anezhañ* → eñ, *ac'hanon* → me. Les réfléchis gardent leur forme en *-unan* : *hec'h-unanik* → he-unan.
- **Les prépositions conjuguées** sont rattachées à la préposition : *gantañ* → gant.
- **Les mots-outils** reçoivent les catégories d'IRaMuTeQ : `art_def`, `pre`, `con`, `pro_per`, `adj_pos`… Ils sont donc **supplémentaires** par défaut dans les analyses, comme en français.
- **Les noms propres ne sont pas inclus** : ils restent « non reconnus », comme avec le dictionnaire français.
- **Les expressions sont reconnues** : locutions figées en plusieurs mots, soudées en une seule forme avant la lemmatisation, comme *parce_que* en français. *a benn ma* devient *a_benn_ma* (conjonction), *meur a* devient *meur_a* (article indéfini), *en doa* devient *en_doa* (lemme *kaout*), *c'hoarioù video* devient *c_hoarioù_video* (nom, lemme *c_hoari_video*). Voir la [section 3](#3-préparer-ses-propres-textes--preparer_corpus_bretonpy).

**Couverture** mesurée sur le corpus de test : **98,8 % des occurrences**. Ce chiffre est optimiste, car ce corpus a servi au développement d'Apertium. Sur un texte contemporain ou dialectal, attendez-vous à moins.

## 3. Préparer ses propres textes : `preparer_corpus_breton.py`

### Pourquoi préparer les textes ?

IRaMuTeQ coupe les mots à l'apostrophe, ce qui casserait le trigramme *c'h* : *c'hoari* deviendrait *c* + *hoari*. Le dictionnaire écrit donc **c_h** (*c_hoari*, *merc_h*), et le texte doit être réécrit de la même façon.

Le script :
1. réécrit *c'h* en *c_h*, quelle que soit l'apostrophe utilisée (' ’ ʼ) ;
2. ramène les autres apostrophes à l'apostrophe droite ;
3. soude les mots-outils et adverbes à trait d'union connus du dictionnaire, quand ils sont écrits avec le tiret : *e-barzh* → *e_barzh*, *dreist-holl* → *dreist_holl* ;
4. sépare les autres mots à trait d'union : *an den-se* → *an den se*. Le dictionnaire couvre chaque élément ;
5. soude les expressions de `dictionnaire/expression_br.txt` : *a-benn ma* → *a_benn_ma*. La plus longue expression possible est retenue : *ar re all* → *ar_re_all*, et non *ar_re* + *all*.

**Pourquoi souder les expressions ici plutôt que dans IRaMuTeQ ?** IRaMuTeQ remplace les expressions par simple recherche de texte, sans vérifier où commencent et finissent les mots. Le breton compte beaucoup de mots-outils très courts, et ce remplacement les soude au milieu d'autres mots : *ar re* est trouvé dans *ar reizhiad*, *en doa* dans *en doare*. Sur le corpus Wikipédia breton de wiki2iramuteq, le remplacement d'IRaMuTeQ fait 2 525 soudures correctes, mais aussi 1 143 soudures en plein milieu d'un mot. Le script, lui, ne soude que des mots entiers.

Il accepte un fichier déjà au format IRaMuTeQ (lignes `****`) ou un texte brut.

### Prérequis

Il faut Python 3.8 ou plus récent, sans aucune bibliothèque à installer.

- **Linux, macOS** : Python est déjà présent ; les commandes s'utilisent telles quelles.
- **Windows** : installez Python depuis [python.org](https://www.python.org/downloads/) en cochant *Add Python to PATH*. Dans les commandes, remplacez `python3` par `python`.

Téléchargez le dépôt (**Code → Download ZIP**), décompressez-le, puis ouvrez un terminal dans ce dossier.

### Commandes

```
python3 preparer_corpus_breton.py mon_texte.txt -o corpus_pret.txt
python3 preparer_corpus_breton.py mon_texte.txt -o corpus_pret.txt --windows
python3 preparer_corpus_breton.py textes_bruts.txt --un-texte-par-paragraphe -o corpus_pret.txt
```

| Option | Effet |
|---|---|
| `-o fichier` | Fichier de sortie |
| `--windows` | Écrit en Windows-1252 avec fins de ligne Windows |
| `--un-texte-par-paragraphe` | Pour un texte brut : chaque paragraphe devient un texte IRaMuTeQ (`**** *texte_N`) |
| `--garder-tirets` | Ne sépare pas les mots à trait d'union (les expressions à trait d'union sont tout de même soudées) |
| `--sans-expressions` | Ne soude pas les expressions |
| `--expressions fichier` | Utilise un autre fichier d'expressions que `dictionnaire/expression_br.txt` |

Les corpus bretons de [wiki2iramuteq](https://github.com/Anakeyn/wiki2iramuteq) sont déjà au format IRaMuTeQ : il suffit de les passer dans ce script.

## 4. Installer le dictionnaire dans IRaMuTeQ

### Méthode A (recommandée) : choisir le dictionnaire à l'ouverture du corpus

Dans la fenêtre de paramètres qui s'affiche avec *Fichier → Ouvrir un corpus* :
1. encodage : **utf-8** (ou **cp1252** pour la version Windows) ;
2. langue : **autre** ;
3. dictionnaire : **Autre**, puis désignez `lexique_br.txt` ;
4. si la case est proposée, décochez **Utiliser le dictionnaire des expressions** : les expressions bretonnes sont déjà soudées par `preparer_corpus_breton.py`, et celui d'une autre langue n'a pas de sens pour le breton.

### Méthode B : si votre version d'IRaMuTeQ ne propose pas le dictionnaire « Autre »

Cette méthode remplace le dictionnaire d'une langue inutilisée. Ne l'utilisez que si la fenêtre d'ouverture du corpus ne propose pas le choix **Autre** pour le dictionnaire.

1. Les dictionnaires se trouvent dans le dossier `.iramuteq` (ou `.Iramuteq`) de votre dossier personnel, sous-dossier `dictionnaires`.
2. **Sauvegardez** le lexique d'une langue que vous n'utilisez pas.
3. Remplacez-le par `lexique_br.txt`, renommé au même nom.
4. Ouvrez vos corpus bretons en choisissant cette langue, et décochez le dictionnaire des expressions.

Remettez le fichier d'origine en place pour revenir en arrière.

### Et le fichier `expression_br.txt` ?

Il suit le format des fichiers d'expressions d'IRaMuTeQ, mais **ne l'installez pas** à la place du fichier d'expressions d'une langue : le remplacement d'IRaMuTeQ produirait les soudures erronées décrites en [section 3](#3-préparer-ses-propres-textes--preparer_corpus_bretonpy). Il est utilisé par `preparer_corpus_breton.py`, et le lexique contient déjà toutes les formes soudées.

## 5. Limites à connaître

- **Une seule analyse par forme**, c'est une contrainte d'IRaMuTeQ. Pour les formes ambiguës, le script préfère :
  1. la lecture **sans mutation** ;
  2. puis le mot-outil ;
  3. puis la catégorie dominante du lemme.

  Par exemple, *gant* peut être la préposition *gant* (« avec ») ou le nombre *kant* (« cent ») après mutation douce (k → g) : le dictionnaire retient la préposition.

  Environ 12 000 formes sont concernées, et certains choix seront faux en contexte. C'est la limite de toute lemmatisation sans désambiguïsation.

  Dans cet ordre, à rang égal, **le verbe passe avant l'adjectif, l'adverbe et le numéral**. La v3 corrige les cas fréquents relevés sur le corpus Wikipédia (*unan*, *du*, *pennañ*, *mui*…), mais il en reste sûrement d'autres. Si un verbe inattendu apparaît parmi vos formes les plus fréquentes, vérifiez sa forme d'origine dans le lexique, puis ajoutez-la à `AJOUTS` (section 6).
- **Un lemme = une catégorie**, c'est aussi une contrainte d'IRaMuTeQ. Quand un mot-outil et un mot plein partagent un lemme, le moins fréquent reçoit un suffixe. Exemple : *e_adv_sup* pour la particule verbale *e(z)*, à distinguer de la préposition *e*.
- **Mots-outils très ambigus** : *ma*, *o* et *e* reçoivent toujours la même lecture (possessif pour *ma* et *o*, préposition pour *e*), même quand ce sont des particules ou des conjonctions. Seul un étiquetage en contexte pourrait les distinguer. Comme ce sont des mots-outils, ils sont supplémentaires et n'influencent pas les classifications.
- **Catégorie `pro_per`** (pronoms personnels). Si votre IRaMuTeQ ne la connaît pas (fichier `key.cfg`), régénérez le dictionnaire avec `--sans-pro-per` pour les classer en `pro_ind`.
- **Expressions** : seules les locutions figées sont retenues. Les locutions verbales d'Apertium (*gouzout brezhoneg*, *mont e kêr*…) sont écartées : les souder ferait disparaître des comptages des mots comme *brezhoneg* ou *kêr*. Pour la même raison, les tournures préposition + nom ou adjectif (*e brezhoneg*, *er skol*, *e genver*) restent en deux mots.
- **Orthographe** : Apertium suit l'orthographe unifiée (*peurunvan*). Les textes en orthographe universitaire, interdialectale ou anciens seront moins bien couverts.

## 6. Régénérer le dictionnaire

Le dictionnaire se reconstruit à partir des dépôts d'Apertium, sans installer Apertium : `expanseur_dix.py` développe lui-même le dictionnaire XML en toutes ses formes fléchies et mutées, à la manière de la commande `lt-expand`.

```
git clone https://github.com/apertium/apertium-bre.git
git clone https://github.com/apertium/apertium-br-fr.git
python3 construire_lexique_br.py apertium-bre/apertium-bre.bre.dix --corpus-annote apertium-br-fr/corpus -o lexique_br.txt
```

Sans `git`, les deux dépôts se téléchargent aussi avec **Code → Download ZIP** sur leurs pages GitHub.

| Fichier | Rôle |
|---|---|
| `expanseur_dix.py` | Développe le dictionnaire Apertium (`.dix`) en couples forme / analyse |
| `construire_lexique_br.py` | Convertit les analyses aux catégories d'IRaMuTeQ, tranche les ambiguïtés, écrit le lexique et le fichier d'expressions. Les corrections propres au breton sont regroupées en tête du script : `NEGATIONS`, `VARIANTES`, `AJOUTS` et les lemmes des pronoms |
| `comparer_lexiques.py` | Compare deux lexiques (formes ajoutées, retirées, lectures modifiées) et mesure l'effet des différences sur un corpus préparé : `python3 comparer_lexiques.py lexique_v1.txt lexique_v2.txt corpus.txt` |

| Option de `construire_lexique_br.py` | Effet |
|---|---|
| `--corpus-annote dossier` | Utilise le corpus annoté à la main d'`apertium-br-fr` pour trancher les ambiguïtés |
| `--sans-pro-per` | Classe les pronoms personnels en `pro_ind` |
| `-o fichier` | Fichier de sortie du lexique ; `expression_br.txt` est écrit dans le même dossier |
| `--expressions fichier` | Fichier de sortie des expressions |
| `--sans-expressions` | Ne produit pas de fichier d'expressions |
| `--locutions-verbales` | Ajoute les locutions verbales conjuguées (environ 34 000 formes) |

La construction est reproductible : avec les versions ci-dessous, elle redonne exactement les fichiers `dictionnaire/lexique_br.txt` et `dictionnaire/expression_br.txt` du dépôt.

| Source | Version utilisée |
|---|---|
| [apertium-bre](https://github.com/apertium/apertium-bre) | commit `e69f6b6`, 21 juillet 2021 |
| [apertium-br-fr](https://github.com/apertium/apertium-br-fr) | commit `6f0ec11`, 31 mai 2023 |

Pour corriger une erreur de rattachement sans attendre Apertium, ajoutez la forme à `AJOUTS` ou la variante à `VARIANTES` dans `construire_lexique_br.py`, puis relancez la construction. Pour enrichir le dictionnaire, le plus utile est de contribuer à `apertium-bre`, puis de relancer la construction.

## 7. Licence et citation

`apertium-bre` est distribué sous licence GNU GPL version 3. Ce dictionnaire en est dérivé et est distribué sous la même licence, comme les scripts (voir `LICENSE`).

Pour citer ce travail :

> Rouarch, P. (2026). *Apertium2iramuteq-bretonV3 : dictionnaire breton pour IRaMuTeQ à partir d'Apertium, version 3*. Anakeyn. https://github.com/Anakeyn/Apertium2iramuteq-bretonV3

Pour en savoir plus :

- corpus qui a révélé les corrections de la v3 : https://github.com/Anakeyn/wiki-numerique-br-fr-iramuteq
- article de la v2 : https://www.anakeyn.com/2026/10/29/correction-du-dictionnaire-de-breton-dapertium-vers-iramuteq/
- article de la v1 : https://www.anakeyn.com/2026/10/29/transformation-dun-dictionnaire-de-breton-apertium-utilisable-par-iramuteq/
