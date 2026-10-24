/* Dictionnaire français du site. Termes : docs/glossary.md.
   Le contenu après « = » est du JSON valide (lu tel quel par tests/test_frontend_build.py).
   Pluriels : objet {one, other} choisi par {count} ; {count} est formaté selon la langue. */
window.I18N_DICT = window.I18N_DICT || {};
window.I18N_DICT.fr = {
 "brand": {"title": "Observatoire des régimes", "sub": "Partis autoritaires · 1946–2024"},
 "nav": {"home": "Accueil", "label": "Pages", "atlas": "Atlas", "analyse": "Analyse", "simulation": "Simulation", "about": "À propos"},
 "status": {"data": "Données", "clock": "Horloge", "model": "Modèle", "ok": "Système opérationnel"},
 "common": {
  "language": "Langue du site", "yes": "oui", "no": "non", "colon": " : ", "listSep": " ; ", "period": ".",
  "skipToContent": "Aller au contenu", "skipToTimeline": "Aller à la ligne du temps"
 },
 "units": {
  "years": {"one": "{count} an", "other": "{count} ans"},
  "yearsWord": {"one": "an", "other": "ans"},
  "parties": {"one": "{count} parti", "other": "{count} partis"},
  "falls": {"one": "{count} chute", "other": "{count} chutes"},
  "countries": {"one": "{count} pays", "other": "{count} pays"},
  "partyYears": {"one": "{count} parti-année", "other": "{count} parti-années"},
  "regimes": {"one": "{count} régime", "other": "{count} régimes"},
  "factors": {"one": "{count} facteur", "other": "{count} facteurs"}
 },
 "labels": {
  "category": {
   "nodata": "Pas de données", "party": "Régime de parti", "military": "Régime militaire",
   "monarchy": "Monarchie autoritaire", "other_arpd": "Autre autocratie", "other_vdem": "Autre autocratie",
   "democracy": "Démocratie", "dependent": "Territoire non souverain"
  },
  "regimeType": {
   "party": "régime de parti", "military": "régime militaire", "military_monarchy": "régime militaro-monarchique",
   "monarchy": "monarchie autoritaire", "personal": "régime personnel", "occupation": "occupation étrangère",
   "transitional": "gouvernement de transition", "failed_state": "État failli", "civil_war": "guerre civile",
   "theocracy": "théocratie", "unclassified": "autocratie sans parti, non classée"
  },
  "origin": {
   "Dictator-Created": "créé par un dictateur", "Elite Coalition": "coalition d'élites",
   "Revolution": "issu d'une révolution", "Independence": "issu de la lutte pour l'indépendance",
   "Communist": "parti communiste", "Military": "fondé par des militaires", "Merger": "fusion de partis",
   "Split": "scission d'un parti", "Dictator-Created/Merger": "créé par un dictateur (fusion)",
   "Dictator-Created/Split": "créé par un dictateur (scission)", "Merger/Split": "fusion ou scission"
  },
  "originShort": {
   "Communist": "Communiste", "Dictator-Created": "Créé par un dictateur", "Elite Coalition": "Coalition d'élites",
   "Independence": "Indépendance", "Merger/Split": "Fusion / scission", "Military": "Militaire", "Revolution": "Révolution"
  },
  "gained": {
   "Election": "élection", "Dictator-Created": "création par le dirigeant en place", "Coup": "coup d'État",
   "Revolution": "révolution", "Military": "prise de pouvoir militaire", "Dictator-Supported": "soutien du dirigeant en place",
   "Communist-Imposed": "imposition par une puissance communiste", "Foreign-Imposed": "imposition par une puissance étrangère",
   "Dictator-Supported/Revolution": "révolution soutenue par le dirigeant en place", "Communist": "prise de pouvoir communiste",
   "Dictator-Supported/Election": "élection soutenue par le dirigeant en place",
   "Foreign-Imposed/Election": "élection imposée de l'étranger", "Revolution/Election": "révolution puis élection"
  },
  "ended": {
   "Coup": "coup d'État", "Election": "défaite électorale", "Continued": "continuité sous un autre régime",
   "Revolution": "révolution", "Dictator-Supported": "décision du dirigeant", "Protests/Election": "manifestations puis élections",
   "Occupation": "occupation étrangère", "Merger": "fusion avec un autre parti", "Protests": "manifestations",
   "Civil War": "guerre civile", "Split": "scission", "Protests/Coup": "manifestations puis coup d'État",
   "Country Merger": "fusion d'États", "Revolution/Election": "révolution puis élections"
  },
  "governance": {
   "Policy-Based": "fondée sur les politiques publiques", "Policy-Based/Repressive": "fondée sur les politiques publiques et la répression",
   "Repressive": "répressive", "Clientelist/Policy-Based": "fondée sur le clientélisme et les politiques publiques",
   "Clientelist": "clientéliste", "Clientelist/Repressive": "fondée sur le clientélisme et la répression"
  },
  "governanceShort": {"Policy-Based": "Politiques publiques", "Repressive": "Répressive", "Clientelist": "Clientéliste", "Non codé": "Non codée"},
  "vdemRegime": ["autocratie fermée", "autocratie électorale", "démocratie électorale", "démocratie libérale"],
  "vdemRegimeInSentence": ["autocratie fermée", "autocratie électorale", "démocratie électorale", "démocratie libérale"],
  "covariate": {
   "Marxist?": "Idéologie marxiste-léniniste", "Gov_Repressive": "Stratégie répressive",
   "Gov_Clientelist": "Stratégie clientéliste", "Gov_Non code": "Stratégie non codée",
   "polity2_entry": "Polity2 à l'entrée (par point)", "polity2_lag1": "Polity2, année précédente (par point)",
   "vdem_entry": "V-Dem à l'entrée (par 0,1)", "vdem_lag1": "V-Dem, année précédente (par 0,1)",
   "conflict_entry": "Conflit armé à l'entrée", "conflict_active_lag1": "Conflit armé, année précédente",
   "log_gdppc_entry": "log PIB/hab. à l'entrée", "log_gdppc_lag1": "log PIB/hab., année précédente",
   "Origin_Communist": "Origine communiste", "Origin_Elite Coalition": "Origine : coalition d'élites",
   "Origin_Independence": "Origine : indépendance", "Origin_Merger/Split": "Origine : fusion / scission",
   "Origin_Military": "Origine militaire", "Origin_Revolution": "Origine révolutionnaire",
   "Origin_Communist_x_late": "Origine communiste, après 10 ans", "Origin_Military_x_late": "Origine militaire, après 10 ans",
   "conflict_entry_x_late": "Conflit à l'entrée, après 10 ans", "niveau démocratique": "Niveau démocratique",
   "Origin": "Origine", "Gouvernance": "Stratégie de gouvernance", "start": "Durée au pouvoir"
  },
  "covariateShort": {
   "polity2_entry": "Polity2 (par point)", "conflict_entry": "Conflit armé", "log_gdppc_entry": "log PIB/hab.",
   "Marxist?": "Idéologie marxiste-léniniste", "Origin_Communist": "Origine communiste"
  },
  "factor": {
   "Origin": "Origine", "Gouvernance": "Gouvernance", "polity2_entry": "Polity2", "polity2_lag1": "Polity2",
   "Marxist?": "Idéologie", "conflict_entry": "Conflit", "conflict_active_lag1": "Conflit",
   "log_gdppc_lag1": "PIB", "log_gdppc_entry": "PIB"
  },
  "model": {
   "KM": "Kaplan-Meier (sans covariable)", "Cox": "Cox", "RSF": "Forêt aléatoire de survie", "GBSA": "Gradient boosting de survie",
   "Temps seul": "Durée seule", "Cox time-varying": "Cox time-varying", "Logistique": "Régression logistique", "LightGBM": "LightGBM"
  },
  "source": {
   "V-Dem (v2x_polyarchy)": "V-Dem", "Polity5 (polity2)": "Polity5", "Maddison (PIB par habitant)": "Maddison (PIB)",
   "UCDP (conflit)": "UCDP (conflits)", "REIGN (type de régime)": "REIGN", "Archigos (dirigeant)": "Archigos"
  },
  "era": {"avant 1945": "avant 1945", "1945-1989": "1945–1989", "depuis 1990": "depuis 1990"},
  "verdict": {
   "référence": "référence", "meilleur que Cox": "meilleur que Cox", "moins bon que Cox": "moins bon que Cox",
   "pas de différence nette": "pas de différence nette", "sans covariable : moins bon que Cox": "sans covariable : moins bon que Cox",
   "sans covariable : pas de différence nette": "sans covariable : pas de différence nette"
  }
 },
 "atlas": {
  "historyTitle": "Autocraties dans le monde, année par année",
  "graphShow": "Afficher le graphique",
  "graphHide": "Masquer le graphique",
  "pageTitle": "Atlas des régimes autoritaires",
  "pageDescription": "Globe interactif des régimes autoritaires de 1946 à 2024 (ARPD, V-Dem).",
  "globeAria": "Globe des régimes : faites glisser pour tourner, molette pour zoomer, cliquez sur un pays. La vue Liste donne les mêmes informations sous forme de tableau.",
  "loading": "Chargement du globe 3D…",
  "loadingNote": "La ligne du temps, les panneaux et la vue Liste fonctionnent déjà.",
  "noWebgl": "Le globe 3D nécessite WebGL, indisponible dans ce navigateur : les données de chaque année sont présentées ici en liste.",
  "world": "Situation mondiale",
  "kpiLabel": "autocraties souveraines",
  "kpiShare": "{pct} des {states} documentés",
  "sovereignStates": {"one": "{count} État souverain", "other": "{count} États souverains"},
  "legendAria": "Légende et décompte par type de régime",
  "legendToggle": "Cliquer pour masquer ou afficher",
  "legendNoteType": "Autre autocratie : régime personnel, occupation, transition, ou autocratie selon V-Dem absente de l'ARPD.",
  "legendNoteAge": "Années au pouvoir du régime en place (régimes répertoriés dans l'ARPD). Les autres pays restent sombres.",
  "legendNoteVdem": "Indice de démocratie électorale de V-Dem (0 à 1), pour tous les pays couverts.",
  "events": "Événements de l'année",
  "noEvents": "Aucun changement de régime répertorié.",
  "fallAfter": "Chute après {years}",
  "accession": "Arrivée au pouvoir",
  "oldest": "Les plus anciens au pouvoir",
  "inPower": "{years} au pouvoir",
  "controlsAria": "Commandes d'affichage",
  "viewLabel": "Vue", "viewGlobe": "Globe", "viewList": "Liste",
  "modeLabel": "Lecture", "modeAria": "Mode de coloration", "modeType": "Typologie", "modeAge": "Longévité", "modeVdem": "Démocratie",
  "relief": "Relief : durée au pouvoir", "reliefTitle": "Élève chaque autocratie selon sa durée au pouvoir",
  "rotate": "Rotation automatique",
  "searchLabel": "Rechercher un pays", "searchPlaceholder": "Ex. : Chine, Chili, URSS…",
  "historicalNames": [["URSS", "RUS"], ["Union soviétique", "RUS"], ["Yougoslavie", "SRB"], ["Tchécoslovaquie", "CZE"],
                      ["Allemagne de l'Est (RDA)", "DEU"], ["RDA", "DEU"], ["Allemagne de l'Ouest (RFA)", "DEU"],
                      ["Viêt Nam du Nord", "VNM"], ["Viêt Nam du Sud", "VNM"], ["Yémen du Nord", "YEM"],
                      ["Yémen du Sud", "YEM"], ["Zanzibar", "TZA"]],
  "list": {
   "title": "États en {year}", "count": {"one": "{count} État", "other": "{count} États"},
   "close": "Fermer la liste", "open": "Ouvrir le dossier : {name}",
   "col": {"name": "Pays", "type": "Type de régime", "party": "Parti au pouvoir", "years": "Années au pouvoir"}
  },
  "dossier": "Dossier pays", "dossierClose": "Fermer le dossier",
  "territory": "Territoire : {name}",
  "media": {
   "flagAlt": "Drapeau : {state}, {year}",
   "logoAlt": "Logo : {party}",
   "logoCaption": "Logo du parti",
   "logoCurrent": "Logo actuel du parti",
   "portraitAlt": "Portrait : {name}",
   "wikiSource": "Wikipédia, « {title} »",
   "credits": "Crédits des images et du texte",
   "creditFlag": "Drapeau",
   "creditFlagOf": "Drapeau — {state}",
   "creditLogo": "Logo du parti",
   "creditPortrait": "Portrait de {name}",
   "creditNote": "Images : Wikimedia Commons, chacune sous sa propre licence (voir le lien). Liens entre les données et les articles : Wikidata. Texte : Wikipédia, licence CC BY-SA 4.0. Les images sont chargées depuis les serveurs de Wikimedia."
  },
  "status": {
   "annexedUSSR": "Le territoire est alors annexé par l'URSS (annexion non reconnue).",
   "annexedIndonesia": "Le territoire est alors annexé par l'Indonésie (annexion non reconnue).",
   "crimea": "La Crimée, annexée par la Russie en 2014, est rattachée ici à l'Ukraine : l'annexion n'est pas reconnue (résolution 68/262 de l'Assemblée générale des Nations unies).",
   "spanishSahara": "Le territoire est alors une colonie espagnole, le Sahara espagnol (jusqu'en 1975).",
   "westernSahara": "Territoire non autonome selon l'ONU, dont le statut n'est pas réglé : le Maroc en administre la plus grande partie depuis 1975 ; le Front Polisario, qui a proclamé la République arabe sahraouie démocratique en 1976, revendique son indépendance."
  },
  "narr": {
   "inherited": "Le territoire de {territory} fait alors partie de <strong>{state}</strong>.",
   "noData": "Aucune donnée pour ce territoire en {year}.",
   "dependent": "En {year}, ce territoire n'est pas un État souverain : V-Dem le code comme colonie ou territoire dépendant.",
   "party": "<strong>Régime de parti.</strong> Le parti <em>{party}</em> détient le pouvoir depuis {start} — {ord} année en {year}.",
   "noParty": "<strong>{type}</strong>, sans parti au pouvoir, en place depuis {start} — {ord} année en {year}.",
   "traitOrigin": "origine : {value}", "traitGained": "accès au pouvoir : {value}", "traitMarxist": "idéologie marxiste-léniniste",
   "governance": "Stratégie de gouvernance {value}.",
   "gained": "Accès au pouvoir : {value}.",
   "how": " ({value})",
   "ongoing": "Toujours au pouvoir en {last}, dernière année observée.",
   "willEnd": "Ce régime quittera le pouvoir en {end}{how}.",
   "lastYear": "C'est sa dernière année au pouvoir{how}.",
   "otherVdem": "<strong>Autocratie hors ARPD.</strong> V-Dem classe ce pays comme {regime} en {year}, sans régime de parti ni junte répertorié dans l'ARPD pour cette année.",
   "democracy": "<strong>Démocratie.</strong> V-Dem classe ce pays comme {regime} en {year}."
  },
  "detail": {
   "regime": "Régime", "party": "Parti", "inPower": "Au pouvoir", "span": "{start} → {end}", "spanOngoing": "{start} → en cours", "founded": "Fondé en",
   "origin": "Origine", "gained": "Accès au pouvoir", "strategy": "Stratégie", "notCoded": "non codée par l'ARPD",
   "marxist": "Marxiste-léniniste", "independence": "Indépendance", "sinceIndependence": "au pouvoir depuis l'indépendance",
   "renamed": "Renommé en", "end": "Fin", "polyarchy": "Démocratie électorale"
  },
  "headOfState": "Chef de l'État", "headOfStateAndGov": "Chef de l'État et du gouvernement", "headOfGov": "Chef du gouvernement",
  "leaders": "Dirigeants au 31 décembre {year} (V-Dem)",
  "trajectory": "Trajectoire du territoire, {range}",
  "stripAria": "Type de régime par année, {range}",
  "polyarchyTitle": "Démocratie électorale (V-Dem, 0 à 1)",
  "sparkAria": "Indice de démocratie électorale V-Dem, {range}",
  "secondaryTitle": "État historique sur ce territoire",
  "secondaryOut": "Hors de la période de cet État en {year}.",
  "dossierSources": "Sources : ARPD (Miller, 2020) et extension post-2015 codée à la main ; V-Dem v16 (classification, indice, dirigeants au 31 décembre) ; drapeaux, logos, portraits et extraits : Wikidata, Wikimedia Commons et Wikipédia.",
  "timelineAria": "Ligne du temps", "year": "Année", "prevYear": "Année précédente", "nextYear": "Année suivante",
  "play": "Lancer l'animation des années", "pause": "Mettre l'animation en pause",
  "historyAria": "Nombre d'autocraties souveraines par type, {range}",
  "autocracies": {"one": "{count} autocratie", "other": "{count} autocraties"},
  "announce": {"one": "Année {year} : {count} autocratie souveraine.", "other": "Année {year} : {count} autocraties souveraines."},
  "credits": "Frontières actuelles (Natural Earth) ; les territoires des unions dissoutes (URSS, Yougoslavie…) prennent la couleur de l'État dont ils faisaient partie. Données : ARPD (Miller, 2020), V-Dem v16 (CC BY-SA 4.0)."
 },
 "analyse": {
  "pageTitle": "Analyse de la survie des partis autoritaires",
  "pageDescription": "Résultats des notebooks : survie, modèles de Cox, robustesse et benchmark prédictif.",
  "km": {
   "aria": "Courbes de survie de Kaplan-Meier", "median": "médiane : {years}", "all": "Ensemble",
   "tipHead": "{years} au pouvoir", "tipLine": "{label} : {pct} encore au pouvoir",
   "axisY": "part encore au pouvoir", "axisX": "années au pouvoir"
  },
  "model": {"static": "Statique", "staticGdp": "Statique + PIB", "corrected": "Corrigé", "timevarying": "Time-varying"},
  "factorName": {
   "Origin_Communist": "l'origine communiste", "Origin_Elite Coalition": "l'origine « coalition d'élites »",
   "Origin_Independence": "l'origine « lutte pour l'indépendance »", "Origin_Merger/Split": "l'origine « fusion ou scission »",
   "Origin_Military": "l'origine militaire", "Origin_Revolution": "l'origine révolutionnaire",
   "Marxist?": "l'idéologie marxiste-léniniste",
   "Gov_Repressive": "la stratégie répressive", "Gov_Clientelist": "la stratégie clientéliste",
   "conflict_entry": "le conflit armé à l'entrée au pouvoir", "polity2": "le score Polity2", "conflict": "le conflit armé",
   "gdp": "le PIB par habitant"
  },
  "howto": {
   "glossary": "Voir le glossaire :",
   "km": {
    "title": "Comment lire ces courbes",
    "items": [
     "Chaque courbe part de 100 % (tous les partis au pouvoir) et descend à chaque chute : sa hauteur à une durée donnée est la part des partis encore au pouvoir, par exemple {pct} après {years}.",
     "Le pointillé marque la médiane, la durée au bout de laquelle la moitié des partis est tombée : {median}.",
     "La zone grise autour de la courbe est l'intervalle de confiance à 95 % : plus elle est large, moins l'estimation est précise.",
     "Les {censored} partis encore au pouvoir en {year} comptent jusqu'à leur dernière année observée, sans date de chute inventée : c'est la censure.",
     "Dans le graphique « Par groupe », choisissez un regroupement, puis survolez une ligne du tableau pour mettre sa courbe en avant ; le test du log-rank indique si les courbes diffèrent plus que le hasard ne l'expliquerait."
    ]
   },
   "forest": {
    "title": "Comment lire ce graphique",
    "items": [
     "Chaque ligne est un facteur et chaque colonne un modèle de Cox ; le point donne le hazard ratio, le trait son intervalle de confiance à 95 %.",
     "La ligne verticale (1) correspond au même risque que le groupe de référence : à gauche, le parti tombe moins vite ; à droite, plus vite.",
     "Point plein : effet significatif au seuil de 5 % (l'intervalle ne croise pas 1). Point vide : l'écart peut venir du hasard.",
     "L'échelle est logarithmique : 0,5 (risque divisé par deux) et 2 (risque doublé) sont à la même distance de 1.",
     "Les modèles diffèrent par leur échantillon et la mesure des variables : un effet présent dans toutes les colonnes est plus solide."
    ],
    "example": "Exemple : {name}, {formula} dans le modèle statique, soit un risque de chute {k} fois plus faible."
   },
   "robust": {
    "title": "Comment lire ces tableaux",
    "items": [
     "Test de Schoenfeld : une p-value inférieure à 0,05 signale un effet qui change avec le temps. Ici, {factors} sont concernés : ils reçoivent un effet avant {cut} au pouvoir et un autre après.",
     "Avant / après : hazard ratio et intervalle de confiance à 95 % de chaque période.",
     "Sensibilité au seuil : le test de Wald compare les deux périodes pour plusieurs seuils ; une p-value élevée signifie que les effets avant et après ne diffèrent pas nettement.",
     "V-Dem : « même conclusion » quand l'effet garde le même sens et le même verdict, significatif ou non, avec les deux mesures du niveau démocratique."
    ],
    "example": "Exemple : {name} passe de {before} à {after}."
   },
   "bench": {
    "title": "Comment lire cette comparaison",
    "items": [
     "Chaque modèle apprend sur une partie des pays et il est évalué sur les autres ({folds} plis × {repeats} répétitions, soit {evaluations} évaluations) : on mesure ainsi sa capacité à prédire des pays qu'il n'a jamais vus.",
     "C de Harrell et ROC-AUC : 0,5 correspond au hasard, 1 à une prédiction parfaite ; plus c'est haut, mieux c'est. Brier intégré et perte logarithmique (↓) : plus c'est bas, mieux c'est.",
     "Le point donne la moyenne des {evaluations} évaluations et le trait ± un écart-type : des traits qui se chevauchent largement signalent des modèles équivalents.",
     "Verdict : comparaison avec le modèle de Cox par le test t rééchantillonné corrigé ; « pas de différence nette » signifie que l'écart peut venir du hasard."
    ]
   },
   "country": {
    "title": "Comment lire ce test",
    "items": [
     "Chaque variable est ajoutée seule au modèle existant : son hazard ratio indique comment le risque de chute change quand elle augmente de l'unité indiquée (au-dessus de 1, il augmente).",
     "Avec {tested} variables testées en même temps, certaines paraissent significatives par hasard : la correction de Holm relève le seuil en conséquence.",
     "Le C-index mesure la qualité des prédictions sur des pays que le modèle n'a pas vus ; le modèle existant atteint {c} sur l'ensemble des partis.",
     "Une variable non retenue peut quand même être liée à la durée des partis : le test montre seulement qu'elle n'apporte pas d'information mesurable en plus des facteurs déjà présents."
    ]
   },
   "shocks": {
    "title": "Comment lire ce test",
    "items": [
     "Chaque ligne compare l'année qui suit un choc à une année sans choc, pour des partis par ailleurs comparables : à droite de ×1, le risque de chute est plus élevé ; à gauche, plus faible.",
     "Pour les catastrophes et les morts au combat, l'effet correspond à 10 fois plus de morts par million d'habitants.",
     "Plusieurs chocs étant testés en même temps, certains paraissent significatifs par hasard : la correction de Holm relève le seuil en conséquence.",
     "Un choc non retenu peut quand même jouer un rôle : le test montre seulement qu'il ne change pas de façon mesurable le risque de chute, en plus des facteurs déjà présents."
    ]
   },
   "leaders": {
    "title": "Comment lire ce test",
    "items": [
     "Chaque ligne compare des partis par ailleurs comparables qui diffèrent par une seule caractéristique, mesurée à leur arrivée au pouvoir : à droite de ×1, le risque de chute est plus élevé ; à gauche, plus faible.",
     "Pour l'âge du parti, l'âge du dirigeant et son expérience politique, l'effet correspond à 10 ans de plus ; pour les autres variables, à « oui » plutôt que « non ».",
     "Les {tested} variables étant testées en même temps, certaines paraissent significatives par hasard : la correction de Holm relève le seuil en conséquence.",
     "Une variable non retenue peut quand même jouer un rôle : le test montre seulement qu'elle n'apporte pas d'information mesurable en plus des facteurs déjà présents."
    ]
   }
  },
  "gl": {
   "title": "Glossaire",
   "plain": {"one": "La notion qui revient dans tout le rapport, illustrée par un chiffre de l'analyse.", "other": "Les {count} notions qui reviennent dans tout le rapport, chacune illustrée par un chiffre de l'analyse."},
   "hr": {
    "term": "Hazard ratio (HR)",
    "def": "Rapport entre les risques de chute de deux groupes, à chaque instant. HR = 1 : même risque ; HR = 0,5 : risque divisé par deux ; HR = 2 : risque doublé.",
    "example": "Exemple : {name}, {formula} dans le modèle statique, soit un risque {k} fois plus faible que dans le groupe de référence."
   },
   "censoring": {
    "term": "Censure",
    "def": "Un parti encore au pouvoir à la fin de l'observation est dit censuré : on sait qu'il a duré au moins jusque-là, pas quand il tombera. C'est le cas de {censored} des {total} en {year} ; les méthodes de survie les comptent sans inventer de date de chute."
   },
   "median": {
    "term": "Médiane de survie",
    "def": "Durée au bout de laquelle la moitié des partis a perdu le pouvoir, estimée en tenant compte de la censure : {median} pour l'ensemble des partis nommés (intervalle de confiance à 95 % : {range} ans)."
   },
   "cindex": {
    "term": "C-index (indice de concordance)",
    "def": "Part des paires de partis que le modèle range dans le bon ordre : celui qui tombe le premier a le risque prédit le plus élevé. 0,5 correspond au hasard, 1 à une prédiction parfaite ; le modèle de Cox atteint {c} en validation croisée groupée par pays."
   },
   "pvalue": {
    "term": "p-value",
    "def": "Probabilité d'observer un écart au moins aussi grand si le facteur n'avait en réalité aucun effet. En dessous de 0,05, l'effet est dit significatif ; ce n'est ni la probabilité que l'effet existe, ni une mesure de sa taille.",
    "example": "Exemple : {name}, {p} dans le modèle statique."
   },
   "ci": {
    "term": "Intervalle de confiance (IC 95 %)",
    "def": "Plage de valeurs compatibles avec les données. Pour un hazard ratio, un intervalle qui contient 1 signifie que l'effet n'est pas significatif au seuil de 5 %.",
    "example": "Exemple : {name}, intervalle de confiance à 95 % du hazard ratio : {range}, qui ne contient pas 1."
   },
   "holm": {
    "term": "Correction de Holm",
    "def": "Quand on teste beaucoup de variables, certaines franchissent le seuil de 0,05 par hasard. La correction de Holm (1979) relève le seuil de chaque test selon leur nombre ; une variable n'est jugée significative que si elle le reste après correction."
   }
  },
  "s00": {
   "kpiPartiesSub": "arrivés au pouvoir entre {from} et {to}, suivis jusqu'en {end}"
  },
  "s01": {
   "title": "Données et échantillon",
   "lead": "Du jeu de données ARPD aux échantillons des modèles : chaque étape retire des observations pour une raison documentée.",
   "plain": "L'analyse part des {regimes} de l'ARPD et garde les {named} nommés, sans les juntes ; le modèle principal en utilise {used}, faute de données complètes pour les autres. La stratégie de gouvernance n'est connue que pour {coded} d'entre eux.",
   "flowAll": "régimes de l'ARPD (partis et juntes)",
   "flowNamed": {"one": "partis nommés · {count} junte sans parti exclue", "other": "partis nommés · {count} juntes sans parti exclues"},
   "flowFalls": "chutes parmi les partis nommés",
   "flowStatic": "modèle statique · {falls}",
   "flowTv": "modèle time-varying · {falls}, {rows}",
   "coverage": "Couverture des sources fusionnées", "coverageLabel": "par parti-année, {range}",
   "coverageAria": "Couverture de {source} par année", "coverageTip": "{pct} des parti-années couvertes",
   "checkMarxist": "Partis communistes codés marxistes", "checkMarxistSub": "contre {pct} des autres partis",
   "checkCorr": "Corrélation Polity2 / V-Dem", "checkCorrSub": {"one": "sur {count} parti-année", "other": "sur {count} parti-années"},
   "checkGov": "Stratégie de gouvernance codée", "checkGovSub": "des partis ; le reste forme la modalité « non codée »",
   "checkMacro": "Variables macro complètes", "checkMacroSub": "des parti-années (Polity2, PIB, conflit)",
   "synthesis": "Ce que les données imposent aux modèles", "synthesisSource": "02_eda · synthèse"
  },
  "s02": {
   "title": "Survie au pouvoir",
   "lead": "Estimateur de Kaplan-Meier : probabilité qu'un parti soit encore au pouvoir après t années, en tenant compte des partis toujours en place.",
   "plain": "La moitié des partis perd le pouvoir dans les {median} qui suivent leur arrivée, et {pct} y sont encore après {years}. Selon l'origine du parti, cette durée médiane va de {low} ({lowGroup}) à {high} ({highGroup}).",
   "groupAria": "Regroupement",
   "group": {"origin": "Origine", "governance": "Stratégie", "era": "Époque"},
   "col": {"group": "Groupe", "parties": "Partis", "falls": "Chutes", "median": "Médiane", "ci": "IC 95 %"},
   "notReached": "non atteinte",
   "logrank": "Test du log-rank : {chi}, {p} — {verdict}",
   "differ": "les courbes diffèrent significativement.", "noDiffer": "pas de différence significative au seuil de 5 %.",
   "notCodedNote": "« Non codée » n'est pas une stratégie : ce sont les partis dont la stratégie n'est pas codée par Miller (2020). Ce groupe n'est donc ni tracé ni comparé (durées la plus longue et la plus courte, test du log-rank, qui porte sur les trois stratégies codées) ; il reste grisé dans le tableau."
  },
  "s03": {
   "title": "Ce qui fait durer un parti",
   "lead": "Hazard ratios des modèles de Cox (échelle logarithmique) : à gauche de 1, le facteur protège le parti ; à droite, il accélère sa chute. Point plein : significatif au seuil de 5 %.",
   "plainBest": "Dans le modèle statique, le facteur le plus protecteur est {name} : à chaque instant, les partis concernés ont un risque de chute {k} fois plus faible que le groupe de référence ({formula}).",
   "plainWorst": "Le plus défavorable est {name}, avec un risque {k} fois plus élevé ({formula}).",
   "plainNone": "Aucun facteur n'est significatif au seuil de 5 % dans le modèle statique.",
   "covariate": "Covariable",
   "noteStatic": "valeurs à l'entrée", "noteStaticGdp": "variante", "noteCorrected": "effets avant / après {cut} ans",
   "noteTv": "valeurs de l'année précédente", "colSample": "{note} · {parties}, {falls}",
   "groupOrigin": "Origine (référence : créé par un dictateur)",
   "groupGov": "Stratégie de gouvernance (référence : politiques publiques)",
   "groupInst": "Idéologie", "groupContext": "Contexte",
   "notCoded": "Non codée (pas une stratégie)",
   "beforeCut": " · avant {cut} ans",
   "lateGroup": "Effets après {cut} ans au pouvoir (modèle corrigé)",
   "lateRow": "{label}, après {cut} ans",
   "axis": "Hazard ratio", "ci95": "IC 95 %",
   "note": "Polity2 : effet par point de l'échelle (−10 à +10). PIB : par unité de log (PIB multiplié par e ≈ 2,7). Modèle corrigé : pour les covariables dont l'effet change avec le temps, la première ligne donne l'effet avant le seuil. Erreurs standards groupées par pays (modèles statiques et corrigé)."
  },
  "s04": {
   "title": "Hypothèses et robustesse",
   "lead": "Le modèle de Cox suppose des effets constants dans le temps ; on le vérifie, on corrige, puis on remplace Polity2 par V-Dem.",
   "plainAll": "Le test de Schoenfeld repère {factors} dont l'effet change avec le temps : le modèle corrigé leur donne un effet avant {cut} au pouvoir et un autre après. Remplacer Polity2 par V-Dem ne change aucune des {count} conclusions significatives du modèle statique.",
   "plainSome": "Le test de Schoenfeld repère {factors} dont l'effet change avec le temps : le modèle corrigé leur donne un effet avant {cut} au pouvoir et un autre après. Remplacer Polity2 par V-Dem laisse inchangées {same} des {count} conclusions significatives du modèle statique.",
   "schoenfeld": "Test de Schoenfeld (modèle statique)", "schoenfeldLabel": "risques proportionnels",
   "col": {"covariate": "Covariable", "stat": "Statistique", "corrected": "Corrigée", "before": "Avant", "after": "Après",
           "cut": "Seuil", "pJoint": "p joint", "hrPolity": "HR Polity2", "hrVdem": "HR V-Dem", "robust": "Robuste"},
   "schoenfeldNote": "Les covariables dont p < 0,05 reçoivent un effet distinct avant et après {cut} ans au pouvoir.",
   "earlyLate": "Effets avant et après le seuil",
   "wald": "Sensibilité au seuil", "waldLabel": "test de Wald joint",
   "waldNote": "Au seuil retenu ({cut}) : {p}. Violations restantes après correction (test de Cox) : {remaining}.",
   "none": "aucune",
   "vdem": "Polity2 remplacé par V-Dem",
   "vdemLabel": {"one": "corrélation {r} sur {count} parti-année", "other": "corrélation {r} sur {count} parti-années"},
   "vdemScale": "HR V-Dem par 0,1 point de l'indice de démocratie électorale ; HR Polity2 par point.",
   "modelAria": "Modèle", "same": "même conclusion", "different": "conclusion différente"
  },
  "s05": {
   "title": "Le Cox face à l'apprentissage automatique",
   "lead": "Validation croisée groupée par pays ({folds} plis × {repeats} répétitions) ; écarts testés par le test t rééchantillonné corrigé (Nadeau & Bengio, 2003).",
   "plainNone": "Des méthodes plus souples, comme les forêts aléatoires ou le boosting, ne prédisent pas mieux que le modèle de Cox : aucun des {count} modèles comparés ne fait mieux que lui. Toutes les prédictions restent modestes : le C de Harrell du Cox vaut {c}, quand 0,5 correspond au hasard et 1 à une prédiction parfaite.",
   "plainBetter": "Selon les règles fixées à l'avance, au moins un des {count} modèles comparés prédit mieux que le modèle de Cox : {models}. Les prédictions restent modestes : le C de Harrell du Cox vaut {c}, quand 0,5 correspond au hasard et 1 à une prédiction parfaite.",
   "taskA": "Tâche A : survie par période au pouvoir", "taskB": "Tâche B : hasard annuel",
   "taskLabel": "{parties} · {falls}",
   "col": {"model": "Modèle", "meanSd": "{metric} (moyenne ± é.-t.)", "verdict": "Verdict", "variable": "Variable",
           "r2": "R² droite", "shape": "Forme", "covariate": "Covariable", "hrCox": "HR Cox", "sameSign": "Même sens"},
   "metric": {"harrell": "C de Harrell", "ibs": "Brier intégré ↓", "rocAuc": "ROC-AUC", "logLoss": "Perte log. ↓"},
   "task": "tâche {task}",
   "perm": "Ce que les modèles ont appris : importance par permutation", "permLabel": "● significatif dans le modèle de Cox",
   "permTipRank": "{factor} : rang {rank}", "permTipImportance": "importance {value} (é.-t. {sd})",
   "permTipP": "p dans le modèle de Cox : {p}",
   "linear": "Les effets sont-ils linéaires ?", "linearLabel": "dépendance partielle",
   "shap": "LightGBM va-t-il dans le même sens que le Cox ?", "shapLabel": "valeurs SHAP"
  },
  "country": {
   "title": "Les caractéristiques des pays changent-elles la donne ?",
   "lead": "Notebook 04_demographics. Même protocole que le banc d'essai : validation croisée groupée par pays ({folds} plis × {repeats} répétitions), mêmes partis pour tous les modèles comparés, règles de décision fixées avant les résultats.",
   "plainNone": "Nous avons ajouté au modèle, une à une, {tested} caractéristiques des pays : aucune n'améliore ses prédictions, et le modèle du simulateur ne change pas. Les données manquent pour tester {untestable} autres : {list}.",
   "plainKept": "Selon les règles fixées à l'avance, ces caractéristiques des pays améliorent le modèle : {list}. Elles décrivent des pays, pas des choix d'un parti : le simulateur ne les propose pas comme réglages.",
   "tested": "Variables testées",
   "testedLabel": "tâche A · hazard ratio pour l'unité indiquée",
   "col": {
    "block": "Bloc",
    "variable": "Variable",
    "unit": "Unité",
    "hr": "HR [IC 95 %]",
    "holm": "p (Holm)",
    "c1": "1. Holm",
    "c2": "2. Sens",
    "c3": "3. C-index",
    "c4": "4. Contrôle",
    "kept": "Retenue",
    "model": "Modèle",
    "cA": "C-index, tâche A",
    "aucB": "ROC-AUC, tâche B",
    "verdict": "Verdict (tâche A)",
    "falls": "Chutes (A / B)",
    "since": "Données depuis",
    "reduced": "HR, modèle réduit (tâche B)", "reading": "Lecture"
   },
   "testedNote": "Une variable est retenue seulement si les quatre conditions sont remplies : 1. effet significatif après la correction de Holm ; 2. même sens en tâche A (valeur à l'entrée) et en tâche B (valeur de l'année précédente) ; 3. gain de C-index en validation croisée (p corrigée < 0,05) ; 4. pour les blocs B et C, effet qui résiste au contrôle de la région ou du PIB par habitant. Un tiret signale une condition sans objet pour le bloc.",
   "prediction": "Prédiction : le modèle existant et les variables des pays",
   "predictionLabel": "mêmes partis dans chaque bloc",
   "m0": "modèle existant (M0)",
   "alone": "variables du bloc seules",
   "best": "M0 + {name} (meilleur ajout)",
   "blend": "mélange de M0 et du bloc",
   "verdict": {
    "ref": "référence",
    "better": "mieux que M0",
    "worse": "moins bien que M0",
    "none": "pas de différence nette"
   },
   "untestable": "Variables sans assez de données",
   "untestableLabel": "hors règles · descriptif",
   "tooFew": "trop peu de chutes",
   "link": {"none": "pas de lien net", "lower": "risque de chute plus faible", "higher": "risque de chute plus élevé"},
   "limits": "Limites de ce test"
  },
  "shocks": {
   "title": "Les chocs font-ils tomber les partis ?",
   "lead": "Notebook 05_shocks. Chaque choc de l'année précédente est ajouté seul au modèle time-varying existant (tâche B), avec des erreurs groupées par pays ; validation croisée groupée par pays ({folds} plis × {repeats} répétitions) ; règles de décision fixées avant les résultats.",
   "decision": "Décision pour chaque choc",
   "decisionLabel": "tâche B · hazard ratio pour l'unité indiquée",
   "decisionNote": "Un choc est retenu seulement si les trois conditions sont remplies : 1. effet significatif après la correction de Holm ; 2. gain de ROC-AUC en validation croisée (p corrigée < 0,05) ; 3. effet qui résiste au contrôle de l'époque (année calendaire) : même sens et p < 0,05.",
   "coverage": "Les chocs et leurs données",
   "coverageLabel": "valeur de l'année précédente",
   "prediction": "Prédiction : le modèle existant et les chocs",
   "predictionLabel": "mêmes parti-années pour tous les modèles",
   "limits": "Limites de ce test",
   "col": {
    "shock": "Choc",
    "unit": "Unité",
    "hr": "HR [IC 95 %]",
    "p": "p",
    "holm": "p (Holm)",
    "c1": "1. Holm",
    "auc": "ROC-AUC : écart (p)",
    "c2": "2. Prédiction",
    "period": "HR avec l'époque (p)",
    "c3": "3. Époque",
    "kept": "Retenu",
    "definition": "Définition",
    "obs": "Parti-années",
    "falls": "Chutes",
    "withShock": "Après un choc",
    "tested": "Testé",
    "model": "Modèle",
    "rocAuc": "ROC-AUC",
    "diff": "Écart avec M0 (p)",
    "verdict": "Verdict"
   },
   "model": {
    "m0": "modèle existant (M0)",
    "alone": "chocs seuls",
    "plus": "M0 + {name}",
    "blend": "mélange de M0 et des chocs"
   },
   "verdict": {
    "ref": "référence",
    "better": "mieux que M0",
    "worse": "moins bien que M0",
    "none": "pas de différence nette"
   }
  },
  "leaders": {
   "title": "Le parti et son dirigeant comptent-ils ?",
   "lead": "Notebook 06_party_leaders. Chaque caractéristique est ajoutée seule au modèle existant, à l'arrivée au pouvoir (tâche A, modèle statique) et l'année précédente (tâche B, modèle time-varying), avec des erreurs groupées par pays ; validation croisée groupée par pays ({folds} plis × {repeats} répétitions) ; règles de décision fixées avant les résultats.",
   "decision": "Décision pour chaque variable",
   "decisionLabel": "hazard ratio pour l'unité indiquée",
   "decisionNote": "Une variable est retenue seulement si les quatre conditions sont remplies : 1. effet significatif en tâche A après la correction de Holm ; 2. même sens en tâche B ; 3. gain de C-index en validation croisée (p corrigée < 0,05) ; 4. effet qui résiste aux contrôles de l'époque et du PIB : même sens et p < 0,05 en tâche A, même sens en tâche B.",
   "coverage": "Les variables et leurs données",
   "coverageLabel": "tâche A : à l'arrivée au pouvoir · tâche B : l'année précédente",
   "leader": "Quel dirigeant ?",
   "leaderLabel": "Archigos · table revue à la main",
   "prediction": "Prédiction : le modèle existant et les variables",
   "predictionLabel": "mêmes partis et parti-années pour tous les modèles",
   "limits": "Limites de ce test",
   "col": {
    "variable": "Variable",
    "hrA": "HR (A) [IC 95 %]",
    "p": "p (A)",
    "c1": "1. Holm (p)",
    "c2": "2. Même sens : HR (B)",
    "c3": "3. C-index : écart (p)",
    "c4": "4. Contrôles : HR (A)",
    "kept": "Retenue",
    "definition": "Définition",
    "partiesA": "Partis (A)",
    "fallsA": "Chutes (A)",
    "obsB": "Parti-années (B)",
    "fallsB": "Chutes (B)",
    "tested": "Testée",
    "rule": "Dirigeant de chaque parti-année (tâche B)",
    "obs": "Parti-années",
    "falls": "Chutes",
    "model": "Modèle",
    "cA": "C-index (tâche A)",
    "diffA": "Écart avec M0 (p)",
    "verdictA": "Verdict (A)",
    "aucB": "ROC-AUC (tâche B)",
    "diffB": "Écart avec M0 (p)",
    "verdictB": "Verdict (B)"
   },
   "rule": {
    "archigos": "dirigeant effectif d'Archigos au 31 décembre de l'année précédente",
    "first": "première année du parti : dirigeant de la table",
    "noLink": "parti sans lien : aucune valeur du dirigeant",
    "after": "après {year} (fin d'Archigos) : aucune valeur du dirigeant"
   },
   "model": {
    "m0": "modèle existant (M0)",
    "alone": "variables seules",
    "plus": "M0 + {name}",
    "blend": "mélange de M0 et des variables"
   },
   "verdict": {
    "ref": "référence",
    "better": "mieux que M0",
    "worse": "moins bien que M0",
    "none": "pas de différence nette"
   }
  },
  "s06": {
   "lead": "Chaque facteur comparé dans les trois modèles de Cox (statique, corrigé, time-varying) ; un effet est robuste s'il est significatif dans les trois.",
   "plain": {"one": "Un effet n'est jugé robuste que s'il est significatif dans les trois modèles de Cox, construits différemment. C'est le cas d'un seul facteur : {list}.", "other": "Un effet n'est jugé robuste que s'il est significatif dans les trois modèles de Cox, construits différemment. C'est le cas de {count} facteurs : {list}."},
   "plainNone": "Un effet n'est jugé robuste que s'il est significatif dans les trois modèles de Cox, construits différemment ; aucun facteur ne l'est."
  },
  "s07": {
   "plain": "Ces résultats décrivent des associations observées, pas des causes. Ils reposent sur {parties} seulement, dont {censored} encore au pouvoir en {year}, et certaines catégories en comptent très peu (stratégie clientéliste : {clientelist} dans le modèle statique).",
   "ml": "Limites propres au benchmark prédictif"
  },
  "s08": {
   "plain": "Toutes les sources sont publiques et citées ci-dessous dans leur langue d'origine ; les chiffres de cette page ont été recalculés par les notebooks le {date}.",
   "note": "Résultats exportés par notebooks/02_eda_and_data_processing.ipynb, final_panel.ipynb, 03_ml_survival.ipynb, 04_demographics.ipynb, 05_shocks.ipynb et 06_party_leaders.ipynb ; données du site construites le {date}."
  }
 },
 "sim": {
  "pageTitle": "Simulation de régime",
  "pageDescription": "Composez un régime autoritaire, ou relevez un défi : le modèle de Cox prédit sa durée au pouvoir.",
  "kicker": "Simulation · modèle de Cox corrigé",
  "title": "Combien de temps tiendra votre régime ?",
  "lead": "Modèle de Cox estimé sur {parties} autoritaires nommés de {countries} ({falls}, arrivées au pouvoir entre {from} et {to}). Choisissez les caractéristiques de votre parti au moment où il prend le pouvoir : chaque choix modifie son risque de chute.",
  "modelInfo": {"one": "Cox · {count} réplication", "other": "Cox · {count} réplications"},
  "params": "Paramètres du régime",
  "modeAria": "Mode de jeu", "modeFree": "Libre", "modeChallenge": "Défis",
  "field": {
   "origin": "01 · Origine du parti", "governance": "02 · Stratégie de gouvernance",
   "entry": "03 · Caractéristiques à l'entrée au pouvoir", "polity": "04 · Niveau démocratique à l'entrée (Polity2)",
   "horizon": "05 · Horizon de la prévision"
  },
  "refTag": "réf.",
  "lockedAria": "imposé par le défi", "lockedNote": "Paramètre imposé par le défi.",
  "switch": {"marxist": "Idéologie marxiste-léniniste", "conflict_entry": "Conflit armé à l'entrée au pouvoir"},
  "switchMeta": "{parties} · risque {effect}",
  "afterCut": "(après {cut})",
  "polityLow": "−10 · autocratie fermée", "polityHigh": "+10 · régime ouvert",
  "polityHelp": "Zone claire : 90 % des partis de l'échantillon ({range}). Chaque point de plus multiplie le risque de chute par {effect}.",
  "run": "Lancer la simulation", "submit": "Valider ma stratégie", "reset": "Profil de référence",
  "share": "Copier le lien",
  "shareCopied": "Lien copié : il ouvre ce profil, dans cette langue.",
  "shareFailed": "Copie impossible : copiez l'adresse de la page.",
  "short": {"marxist": "marxiste", "conflict": "conflit"},
  "paramRef": "profil de référence",
  "paramActive": {"one": "{count} levier actif", "other": "{count} leviers actifs"},
  "results": "Résultats",
  "medianLabel": "Durée médiane prévue",
  "medianReached": "La moitié des partis comparables a quitté le pouvoir après {years}.",
  "medianNotReached": "Médiane non atteinte : plus de la moitié des partis comparables sont encore au pouvoir après {years}.",
  "bandBeyond": "Bande à 95 % : au-delà de {years}.",
  "bandOpen": "Bande à 95 % : de {low} à plus de {years}.",
  "bandRange": "Bande à 95 % : {range} {unit}.",
  "atYears": "À {years}",
  "chartTitle": "Probabilité d'être encore au pouvoir",
  "chart": {
   "aria": "Courbe de survie prévue sur {years}", "cut": "{years} : effets tardifs", "median": "médiane : {years}",
   "target": "objectif : {years}", "tipHead": "Après {years}", "tipYours": "Votre régime : {pct} ({range})",
   "tipRef": "Profil de référence : {pct}", "tipHistory": "Historique (tous les partis) : {pct}"
  },
  "legend": {
   "yours": "Votre régime", "band": "Bande à 95 %", "ref": "Profil de référence",
   "history": "Historique (Kaplan-Meier, {count} partis)", "target": "Objectif du défi"
  },
  "leversTitle": "Leviers : effet de chaque choix sur le risque de chute",
  "lever": {
   "origin": "Origine : {value}", "governance": "Stratégie : {value}",
   "vs": "par rapport à : {value}", "vsNo": "par rapport à : non", "vsNoConflict": "par rapport à : pas de conflit",
   "vsMedian": "par rapport à la médiane {value}", "late": "≥ {cut} : {value}",
   "refNote": "Profil de référence : parti créé par un dictateur, stratégie fondée sur les politiques publiques, sans idéologie marxiste ni conflit, Polity2 à la médiane. Modifiez un paramètre pour voir son effet sur le risque de chute.",
   "combined": "Risque combiné par rapport au profil de référence : {early} pendant les {cut} premières années, {late} ensuite. À gauche de la ligne, le choix protège le régime ; à droite, il accélère sa chute."
  },
  "rankTitle": "Rang historique",
  "rank": {
   "label": "Partis historiques déjà tombés à cette durée",
   "reached": "Selon la courbe historique (Kaplan-Meier, {count} partis), {pct} des partis avaient quitté le pouvoir après {years}, la durée médiane prévue pour votre régime.",
   "notReached": "Votre régime a plus d'une chance sur deux de durer au-delà de {years} ; {pct} des partis historiques étaient déjà tombés à cette durée.",
   "plotAria": "Durées observées des partis de l'échantillon",
   "yourMedian": "votre médiane : {years}",
   "note": "Chaque point : un parti de l'échantillon et sa durée observée (cercle vide : encore au pouvoir en {year})."
  },
  "warningsTitle": "Fiabilité de la prédiction",
  "warn": {
   "smallGroup": "Seulement {n} partis de l'échantillon d'estimation ont {what} (seuil d'alerte : {threshold}) : la prédiction est peu précise pour ce choix.",
   "whatOrigin": "l'origine « {value} »", "whatGov": "la stratégie « {value} »",
   "what": {
    "marxist": {"yes": "une idéologie marxiste-léniniste", "no": "pas d'idéologie marxiste-léniniste"},
    "conflict_entry": {"yes": "un conflit armé à l'entrée au pouvoir", "no": "pas de conflit armé à l'entrée au pouvoir"}
   },
   "unseen": "Aucun parti de l'échantillon ne combine l'origine « {origin} » et la stratégie « {governance} » (parmi les {coded} partis dont la stratégie est codée) : la prédiction est une extrapolation.",
   "polity": "Le score Polity2 choisi ({value}) est en dehors de l'intervalle où se situent 90 % des partis de l'échantillon ({range}).",
   "horizon": "Horizon ramené de {requested} à {used}, la plus longue durée observée dans les données."
  },
  "analogsTitle": "Régimes réels les plus proches",
  "analog": {
   "count": {"one": "{count} parti comparé", "other": "{count} partis comparés"},
   "atlas": "voir sur l'atlas", "notCoded": "stratégie non codée", "fell": "chute en {year}", "still": "toujours au pouvoir",
   "note": "Partis réels dont les caractéristiques à l'entrée au pouvoir ressemblent le plus aux vôtres (origine, stratégie, idéologie, conflit, Polity2)."
  },
  "logTitle": "Journal des simulations", "logClear": "Effacer le journal",
  "log": {"empty": "Lancez une simulation pour l'ajouter au journal et comparer vos stratégies.", "reload": "Recharger ce profil"},
  "disclaimer": "Prédiction issue du modèle de Cox statique corrigé (final_panel.ipynb, section 6.3), calculée dans le navigateur à partir de src/cox_static_model.json ; bande à 95 % : {replicates} réplications d'un bootstrap par pays. Les résultats décrivent des associations observées entre {from} et {to}, pas des effets causaux ; pouvoir de discrimination modeste (C-index {cindex} en validation croisée). La stratégie « non codée » de l'ARPD n'est pas proposée : ce n'est pas une stratégie.",
  "ch": {
   "intro": "Chaque défi impose un ou plusieurs paramètres et fixe une durée à tenir. Composez le reste du régime, puis validez : le défi est réussi si la probabilité d'être encore au pouvoir à cette durée atteint 50 %.",
   "target": "{years}",
   "notPlayed": "pas encore joué",
   "bestAria": {"one": "Meilleur résultat : {count} étoile", "other": "Meilleur résultat : {count} étoiles"},
   "lockOrigin": "origine imposée : {value}", "lockGov": "stratégie imposée : {value}", "lockPolity": "Polity2 imposé : {value}",
   "cardLabel": "Défi en cours",
   "starsRule": "★ {a} · ★★ {b} · ★★★ {c}",
   "goal": "Objectif : être encore au pouvoir après {years}, avec une probabilité d'au moins 50 %.",
   "howTo": "Composez votre régime avec les paramètres libres, puis cliquez sur « Valider ma stratégie ».",
   "won": {"one": "Défi réussi : {count} étoile", "other": "Défi réussi : {count} étoiles"},
   "lost": "Défi manqué",
   "prob": "Probabilité d'être encore au pouvoir après {years} : {p} (bande à 95 % : {range}).",
   "history": "Parmi les partis réels, {pct} étaient encore au pouvoir après {years}.",
   "medianRank": "Durée médiane prévue : {median} ; à cette durée, {pct} des partis réels étaient déjà tombés.",
   "hint": "Piste : cherchez les leviers qui protègent le régime (barres à gauche de la ligne). Certains reposent sur peu de partis : voyez la fiabilité de la prédiction.",
   "hintMore": "Pour plus d'étoiles, combinez davantage de leviers protecteurs.",
   "hintCapped": "Pour plus d'étoiles, misez sur des choix mieux documentés : la fiabilité de la prédiction indique ceux qui reposent sur peu de partis."
  },
  "conf": {
   "label": "Confiance : {level}",
   "level": {"high": "élevée", "medium": "moyenne", "low": "faible"},
   "stars": {"one": "{count} étoile", "other": "{count} étoiles"},
   "tipHigh": "Chaque choix repose sur au moins {parties} de l'échantillon, cette combinaison d'origine et de stratégie a déjà été observée, et le score Polity2 est dans l'intervalle de 90 % des partis ({range}).",
   "tipLimit": "Dans un défi : {stars} au plus.",
   "reason": {
    "origin": "l'origine « {value} » repose sur {parties}",
    "governance": "la stratégie {value} repose sur {parties}",
    "switch": "« {value} » ne concerne que {parties}",
    "unseen": "aucun parti ne combine l'origine « {origin} » et la stratégie « {governance} »",
    "polity": "Polity2 {value} est hors de l'intervalle de 90 % des partis ({range})"
   },
   "possible": {"one": "{count} étoile possible", "other": "{count} étoiles possibles"},
   "limit": {"one": "{count}", "other": "{count}"},
   "capped": "{possible}, limitées à {limit} : {reasons}.",
   "rule": "Les étoiles dépendent aussi de la confiance de la prédiction : {medium} au plus si elle est moyenne, {low} si elle est faible (choix portés par peu de partis, combinaison jamais observée).",
   "challengeMax": "Ce défi rapporte {stars} au plus : {reasons}.",
   "challengeMaxShort": "{stars} au plus"
  },
  "challenges": {
   "president": {"title": "Le parti du président", "brief": "Votre parti a été créé par le dirigeant en place et gouverne par les politiques publiques, comme le profil de référence du modèle. Ces deux choix sont imposés : jouez sur le reste."},
   "coup": {"title": "Le coup d'État", "brief": "Votre parti est né d'une prise de pouvoir militaire : son origine est imposée. Dans le modèle corrigé, son risque de chute est plus élevé après 10 ans au pouvoir qu'au début."},
   "opening": {"title": "L'ouverture", "brief": "Vous arrivez au pouvoir dans un régime relativement ouvert : Polity2 est fixé à +6. Le modèle associe l'ouverture à un risque de chute plus élevé."},
   "war": {"title": "Né dans la guerre", "brief": "Votre parti prend le pouvoir pendant un conflit armé. Dans le modèle, ce conflit n'a pas d'effet net sur le risque de chute : tout se joue sur vos autres choix."},
   "independence": {"title": "L'héritier de l'indépendance", "brief": "Votre parti est issu de la lutte pour l'indépendance, une origine associée à une longue survie. Visez loin."}
  }
 },
 "home": {
  "pageTitle": "Partis autoritaires : pourquoi certains durent plus longtemps",
  "pageDescription": "Pourquoi certains partis autoritaires restent-ils plus longtemps au pouvoir ? Introduction, résultats clés en graphiques et sources des données.",
  "kicker": "Projet de statistique · analyse de survie",
  "title": "Pourquoi certains partis autoritaires restent-ils plus longtemps au pouvoir que d'autres ?",
  "lead": "Nous suivons les partis au pouvoir dans les régimes autoritaires, de leur arrivée au pouvoir jusqu'à leur chute. Ce site montre combien de temps ils durent et ce qui les fait durer ; il permet aussi d'explorer chaque pays, année par année, et de simuler un parti.",
  "ctaAtlas": "Explorer le globe",
  "ctaAnalyse": "Voir les résultats",
  "kpiTitle": "Chiffres clés",
  "kpi": {
   "median": "Durée médiane au pouvoir",
   "medianSub": "la moitié des partis tombe avant",
   "parties": "Partis étudiés",
   "countries": "Pays",
   "countriesSub": "sur tous les continents",
   "fallen": "Ont perdu le pouvoir",
   "inPower": "Encore au pouvoir",
   "inPowerSub": "en {year}"
  },
  "summaryTitle": "Ce qu'il faut retenir",
  "seeAnalysis": "Voir dans l'analyse",
  "f": {
   "survival": {
    "title": "Combien de temps ?",
    "text": "La moitié des partis perd le pouvoir en moins de {median}."
   },
   "factors": {
    "title": "Ce qui protège, ce qui fragilise",
    "text": "{best} divise le risque de chute par {k1} ; {worst} le multiplie par {k2}.",
    "none": "Aucun facteur n'a d'effet net sur la durée au pouvoir."
   },
   "prediction": {
    "title": "Peut-on prédire la chute ?",
    "text": "En partie seulement : {c} sur une échelle de 0,5 (hasard) à 1 (prédiction parfaite). L'apprentissage automatique ne fait pas nettement mieux que le modèle de Cox.",
    "textBetter": "En partie : {c} sur une échelle de 0,5 (hasard) à 1 (prédiction parfaite) ; l'apprentissage automatique fait un peu mieux."
   },
   "country": {
    "title": "Le pays compte-t-il ?",
    "text": "Pas de façon mesurable : aucune des {tested} caractéristiques des pays testées (démographie, ethnicité, religion, éducation…) n'améliore la prédiction.",
    "textKept": "Oui pour {list} : ces caractéristiques des pays améliorent la prédiction."
   },
   "shocks": {
    "title": "Les chocs comptent-ils ?",
    "text": "Pas de façon mesurable : ni les catastrophes, ni les guerres, ni les famines, ni les récessions ne changent nettement le risque de chute l'année suivante ({tested} chocs testés).",
    "textKept": "Oui pour {list} : après ce choc, le risque de chute change nettement l'année suivante."
   }
  },
  "exploreTitle": "Explorer",
  "tools": {
   "atlas": "Le globe des régimes, année par année de 1946 à 2024, avec une fiche pour chaque pays.",
   "analyse": "Le tableau de bord des résultats : durée au pouvoir, facteurs, qualité des prédictions.",
   "simulation": "Composez un parti et voyez combien de temps il resterait au pouvoir selon le modèle."
  },
  "sourcesTitle": "Sources des données",
  "sourcesMore": "Toutes les références et les licences"
 },
 "dash": {
  "kicker": "Analyse",
  "title": "Les résultats en un coup d'œil",
  "sub": "Chaque carte répond à une question par une phrase et un graphique. Les chiffres complets et les méthodes sont repliés sous « Voir le détail ».",
  "more": "Voir le détail",
  "kpi": {
   "median": "Durée médiane au pouvoir",
   "medianSub": "IC 95 % : {range} ans",
   "parties": "Partis étudiés",
   "fallen": "Ont perdu le pouvoir",
   "countries": "Pays",
   "cindex": "Qualité des prédictions",
   "cindexSub": "C-index : 0,5 = hasard, 1 = parfait"
  },
  "survival": {
   "title": "Combien de temps restent-ils au pouvoir ?",
   "answer": "La moitié des partis perd le pouvoir en moins de {median}, et {pct} y sont encore après {years}.",
   "all": "Tous",
   "longest": "durée la plus longue : {group}",
   "shortest": "durée la plus courte : {group}",
   "others": "autres groupes"
  },
  "factors": {
   "title": "Qu'est-ce qui les fait durer ?",
   "answer": "{best} divise le risque de chute par {k1} ; {worst} le multiplie par {k2}.",
   "answerNone": "Aucun facteur n'a d'effet net sur la durée au pouvoir.",
   "protect": "protège : risque plus faible",
   "harm": "fragilise : risque plus élevé",
   "none": "pas d'effet net",
   "note": "À autres facteurs égaux. Les origines sont comparées aux partis « {origin} », les stratégies à « {strategy} »."
  },
  "prediction": {
   "title": "Peut-on prédire leur chute ?",
   "answer": "En partie seulement : le modèle de Cox atteint {c} sur une échelle de 0,5 (hasard) à 1 (prédiction parfaite), et aucune méthode d'apprentissage automatique ne fait nettement mieux.",
   "answerBetter": "En partie : le modèle de Cox atteint {c} sur une échelle de 0,5 (hasard) à 1 (prédiction parfaite) ; {models} font un peu mieux.",
   "groupA": "Combien de temps le parti restera-t-il ? (C-index)",
   "groupB": "Tombera-t-il dans l'année ? (ROC-AUC)",
   "chance": "0,5 hasard",
   "perfect": "1 parfait"
  },
  "country": {
   "title": "Le pays compte-t-il ?",
   "answer": "Non : aucune des {tested} caractéristiques des pays testées n'améliore la prédiction (démographie, ethnicité, religion, emploi, éducation).",
   "answerKept": "Oui pour {list} : ces caractéristiques des pays améliorent la prédiction.",
   "m0": "modèle existant",
   "best": "avec la meilleure variable du bloc",
   "tip": "{variable} : C-index {pair}, {p} (test corrigé)",
   "noteNone": "Les petits gains visibles ici ne sont pas significatifs : ils restent dans la marge du hasard."
  },
  "shocks": {
   "title": "Les chocs font-ils tomber les partis ?",
   "answer": "Non : aucun des {tested} chocs testés (catastrophes, séismes, guerres, famines, récessions) ne change nettement le risque de chute l'année suivante.",
   "answerKept": "Oui pour {list} : après ce choc, le risque de chute change nettement l'année suivante.",
   "note": "Risque de chute l'année qui suit le choc, à autres facteurs égaux. Pour les catastrophes, l'effet correspond à 10 fois plus de morts par million d'habitants. En gris : pas d'effet net après la correction pour tests multiples (Holm).",
   "pHolm": "{p} après la correction de Holm"
  },
  "leaders": {
   "title": "Le parti et son dirigeant comptent-ils ?",
   "answer": "Non : aucune des {tested} caractéristiques testées (âge du parti ; âge, parcours et arrivée au pouvoir du dirigeant) ne change nettement le risque de chute.",
   "answerKept": "Oui pour {list} : à autres facteurs égaux, le risque de chute change nettement.",
   "note": "Risque de chute selon la valeur à l'arrivée au pouvoir, à autres facteurs égaux. Âges et expérience : effet de 10 ans de plus ; autres variables : « oui » plutôt que « non ». En gris : pas d'effet net après la correction pour tests multiples (Holm).",
   "pHolm": "{p} après la correction de Holm"
  },
  "data": {
   "title": "Sur quelles données ?",
   "answer": "{parties} dans {countries}, suivis jusqu'en {year}.",
   "steps": {
    "all": "régimes autoritaires recensés",
    "named": "dirigés par un parti (hors juntes militaires)",
    "model": "avec toutes les données du modèle",
    "falls": "parmi eux, ont perdu le pouvoir"
   }
  },
  "moreTitle": "Pour aller plus loin",
  "acc": {
   "conclusion": "Conclusion détaillée",
   "questions": "Questions de recherche",
   "limits": "Limites",
   "sources": "Sources et méthodes",
   "glossary": "Glossaire"
  }
 },
 "about": {
  "pageTitle": "À propos de l'Observatoire",
  "pageDescription": "Auteurs, méthode, sources et licences du site sur la survie des partis autoritaires.",
  "kicker": "À propos",
  "title": "Combien de temps durent les partis autoritaires, et pourquoi ?",
  "lead": "Ce site présente une analyse de survie des partis au pouvoir dans les régimes autoritaires, de 1946 à 2024, à partir de l'Autocratic Ruling Parties Dataset (ARPD) de Michael K. Miller, complété par V-Dem, Polity5, Archigos, REIGN, UCDP/PRIO et la base Maddison.",
  "authors": "Auteur",
  "pagesTitle": "Ce que montre le site",
  "pages": {
   "atlas": "Un globe en 3D : le type de régime de chaque pays, chaque année de 1946 à 2024, avec un dossier par pays et une vue en liste.",
   "analyse": "Les résultats des notebooks : courbes de survie, modèles de Cox, tests des hypothèses, robustesse et comparaison avec l'apprentissage automatique.",
   "simulation": "Un jeu : composez un régime, ou relevez un défi, et le modèle prédit combien de temps il resterait au pouvoir."
  },
  "methodTitle": "La méthode en cinq lignes",
  "method": [
   "Unité d'analyse : la période au pouvoir d'un parti autoritaire nommé de l'ARPD, de son arrivée au pouvoir à sa chute ou à la fin de l'observation ; les juntes sans parti sont exclues.",
   "Description de la survie au pouvoir par l'estimateur de Kaplan-Meier ; comparaison des groupes par le test du log-rank.",
   "Trois modèles de Cox : statique (situation à l'entrée au pouvoir), corrigé (effets différents avant et après 10 ans au pouvoir) et time-varying (situation de l'année précédente) ; erreurs standards groupées par pays.",
   "Vérification des hypothèses (test de Schoenfeld), test de robustesse avec V-Dem au lieu de Polity2, et comparaison prédictive avec l'apprentissage automatique en validation croisée groupée par pays.",
   "Trois tests complémentaires, avec des règles fixées avant les résultats, ajoutent au modèle existant des caractéristiques des pays (démographie, ethnicité, religion, emploi, éducation), des chocs de l'année précédente (catastrophes, guerres, famines, récessions) et des caractéristiques du parti et de son dirigeant (cartes 04 à 06 de la page Analyse).",
   "La simulation utilise le modèle de Cox statique corrigé, avec une bande à 95 % issue d'un bootstrap par pays. Les résultats décrivent des associations, pas des effets causaux."
  ],
  "sourcesTitle": "Sources des données",
  "sources": {
   "arpd": "Partis autoritaires : origine, accès au pouvoir, chute (ARPD)",
   "vdem": "Classification des régimes, indice de démocratie électorale, noms des dirigeants",
   "polity": "Score Polity2",
   "archigos": "Dirigeants (fusion des données ; test du parti et de son dirigeant)",
   "reign": "Types de régime (fusion des données)",
   "ucdp": "Conflits armés ; morts au combat depuis 1989 (test des chocs)",
   "maddison": "PIB par habitant ; récessions (test des chocs)",
   "naturalearth": "Frontières et noms des pays",
   "wpp": "Structure par âge de la population (test des caractéristiques des pays)",
   "wdi": "Espérance de vie, urbanisation, scolarisation, chômage (test des caractéristiques des pays)",
   "epr": "Exclusion ethnique du pouvoir (test des caractéristiques des pays)",
   "qog": "Fractionnalisation ethnique et religieuse, pour comparaison (test des caractéristiques des pays)",
   "clio": "Années moyennes d'études (test des caractéristiques des pays)",
   "afi": "Liberté académique (test des caractéristiques des pays)",
   "emdat": "Catastrophes naturelles et leurs victimes (test des chocs)",
   "noaa": "Grands séismes (test des chocs)",
   "prio": "Morts au combat avant 1989 (test des chocs)",
   "famine": "Famines d'au moins 100 000 morts (test des chocs)",
   "faostat": "Production alimentaire par habitant (test des chocs)",
   "lead": "Parcours des dirigeants avant le pouvoir : service militaire, passé rebelle, études, expérience politique (test du parti et de son dirigeant)",
   "wikidata": "Drapeaux datés, logos des partis, personnes et liens vers Wikipédia (fiche pays de l'Atlas)",
   "commons": "Images des drapeaux, logos et portraits (fiche pays de l'Atlas)",
   "wikipedia": "Premières phrases des articles sur les partis et les dirigeants (fiche pays de l'Atlas)"
  },
  "creditsTitle": "Crédits et licences",
  "credits": {
   "globe": "Rendu du globe en 3D",
   "three": "Moteur 3D utilisé par globe.gl",
   "naturalearth": "Frontières des pays",
   "vdem": "Indice de démocratie électorale, classes de régime et noms des dirigeants affichés sur le site",
   "fonts": "Polices du site",
   "wikidata": "Liens entre les données du site et les articles, dates des drapeaux",
   "commons": "Drapeaux, logos et portraits ; auteur et licence indiqués pour chaque image dans la fiche pays",
   "wikipedia": "Extraits des articles affichés dans la fiche pays, avec un lien vers l'article"
  },
  "licence": "Licence", "publicDomain": "Domaine public", "licencePerFile": "Licence propre à chaque fichier",
  "languagesTitle": "Langues",
  "languages": "Le site existe en français, en anglais et en arabe. Les textes générés à partir des résultats sont réécrits dans chaque langue avec les mêmes chiffres ; en arabe, les nombres s'écrivent en chiffres latins et les graphiques se lisent de gauche à droite. La terminologie arabe reste à relire par un locuteur natif.",
  "built": "Données du site construites le {date}."
 }
};
