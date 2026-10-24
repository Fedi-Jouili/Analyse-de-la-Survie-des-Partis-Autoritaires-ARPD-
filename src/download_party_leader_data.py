"""Sources of notebooks/06_party_leaders.ipynb (characteristics of the ruling parties and of their leaders).

Run from the project root (internet; a few seconds):
    python src/download_party_leader_data.py

- LEAD (Leader Experience and Attribute Descriptions; Ellis, Horowitz & Stam 2015) has no download page of its own:
  its 11 variables (education, military service, combat, rebel group, war outcomes, political experience, health), one
  row per Archigos leader (obsid), are distributed in the R package peacesciencer (Miller 2022, GPL-2). data/LEAD.rda
  is downloaded from the package's GitHub repository at a fixed commit and converted to CSV with pyreadr. No licence is
  stated for the data themselves: data/raw/lead/ stays local (ignored by git) and the notebook exports results only.
- Archigos 4.1 is already in data/raw/arch_annual.csv: its version and SHA-256 are recorded, nothing is downloaded.
- V-Party, DPI 2023 and PLAD are not downloaded: even perfectly linked, none of them reaches the 120 falls required at
  entry into power. What was checked about them is recorded.

Everything is written to data/raw/party_leader_sources.json. Rules: one request at a time, at least one second apart;
the robots.txt of the host is read first and obeyed; on 429 or 503 the script waits as long as Retry-After asks; the
User-Agent names the project, without any personal data; no form, no login (a link that answers with an HTML page
instead of the file stops the script). A file whose SHA-256 differs from the one already recorded stops the script:
the source has changed and the change must be checked by hand.
"""
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
LEAD_DIR = RAW / "lead"
SOURCES = RAW / "party_leader_sources.json"
USER_AGENT = "ARPD-party-leaders/1.0 (student research project on authoritarian ruling parties; Python urllib)"
PAUSE = 1.0                # seconds between two requests

PEACESCIENCER = "https://github.com/svmiller/peacesciencer"
COMMIT = "2bb332117051fc00cbaaadde9a7470274a419119"    # 2023-03-22, the last commit that changed data/LEAD.rda
LEAD_URL = f"https://raw.githubusercontent.com/svmiller/peacesciencer/{COMMIT}/data/LEAD.rda"
LEAD_COLUMNS = ["obsid", "leveledu", "milservice", "combat", "rebel", "warwin", "warloss", "rebelwin", "rebelloss",
                "yrsexper", "physhealth", "mentalhealth"]

# Candidate sources checked on 2026-10-21 and left aside (control step of notebook 06)
NOT_USED = {
    "V-Party v2": {
        "url": "https://v-dem.net/data/v-party-dataset/",
        "formulaire": "oui : le téléchargement demande une adresse e-mail, le genre et un consentement (non rempli)",
        "version": "v2, février 2022",
        "licence": "non indiquée sur la page",
        "années": "1970-2019 (variables codées par des experts), partis ayant plus de 5 % des voix",
        "raison": "non testable : même parfaitement relié, au plus 106 chutes à l'entrée au pouvoir (moins de 120) "
                  "et 145 en tâche B (moins de 150)",
    },
    "DPI 2023": {
        "url": "https://data.iadb.org/dataset/the-database-of-political-institutions-dpi-2023",
        "formulaire": "non : liens directs (CSV, XLSX)",
        "version": "DPI 2023, publiée le 11 mars 2026 (https://doi.org/10.60966/8tx1xs4i)",
        "licence": "Creative Commons Attribution 4.0",
        "années": "1975-2023",
        "raison": "non testable : au plus 99 chutes à l'entrée au pouvoir et 133 en tâche B",
    },
    "PLAD v7": {
        "url": "https://doi.org/10.7910/DVN/YUS575",
        "formulaire": "non : Harvard Dataverse, sans questionnaire ni fichier restreint",
        "version": "7, avril 2024",
        "licence": "CC0 1.0",
        "années": "1989-2023",
        "raison": "non testable : au plus 68 chutes à l'entrée au pouvoir et 95 en tâche B",
    },
}

_last_request = [0.0]
_robots = {}


def fetch(url, obey_robots=True):
    """GET one URL, one request at a time; on 429 or 503, wait as long as Retry-After asks (at least 15 s, doubled at
    each new attempt)."""
    if obey_robots and not allowed(url):
        raise SystemExit(f"robots.txt interdit {url} : arrêt")
    for attempt in range(8):
        wait = _last_request[0] + PAUSE - time.time()
        if wait > 0:
            time.sleep(wait)
        _last_request[0] = time.time()
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                if obey_robots and "text/html" in response.headers.get("Content-Type", ""):
                    raise SystemExit(f"{url} renvoie une page HTML au lieu du fichier (formulaire ou connexion ?) : "
                                     "arrêt")
                return response.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 7:
                retry = e.headers.get("Retry-After")
                pause = max(int(retry) if retry and retry.isdigit() else 0, 15 * 2 ** attempt)
                print(f"    HTTP {e.code} (Retry-After : {retry or '-'}) : nouvel essai dans {pause} s")
                time.sleep(pause)
                continue
            raise
    raise SystemExit(f"pas de réponse de {url}")


def allowed(url):
    """The robots.txt of the host, read with the project's User-Agent. No robots.txt (404) allows everything; a
    robots.txt that cannot be read stops the script."""
    parts = urllib.parse.urlsplit(url)
    host = f"{parts.scheme}://{parts.netloc}"
    if host not in _robots:
        parser = urllib.robotparser.RobotFileParser(host + "/robots.txt")
        try:
            parser.parse(fetch(host + "/robots.txt", obey_robots=False).decode("utf-8", "replace").splitlines())
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                parser.allow_all = True
            else:
                raise SystemExit(f"robots.txt de {host} illisible (HTTP {e.code}) : arrêt")
        _robots[host] = parser
    return _robots[host].can_fetch(USER_AGENT, url)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def check_known(name, digest, record):
    """Stop if a file recorded earlier has changed."""
    if name in record and record[name]["sha256"] != digest:
        raise SystemExit(f"{name} : SHA-256 {digest} différent de celui enregistré le {record[name].get('downloaded')} "
                         f"({record[name]['sha256']}). La source a changé : à vérifier à la main avant de continuer.")


def main():
    print("Sources des partis et des dirigeants (notebook 06)")
    record = json.loads(SOURCES.read_text(encoding="utf-8")) if SOURCES.exists() else {}

    # ------------------------------------------------ LEAD, from peacesciencer at a fixed commit
    rda = LEAD_DIR / "LEAD.rda"
    if rda.exists() and "LEAD.rda" in record:
        check_known("LEAD.rda", sha256(rda.read_bytes()), record)
        print(f"  LEAD.rda déjà téléchargé le {record['LEAD.rda']['downloaded']}, SHA-256 inchangé")
    else:
        data = fetch(LEAD_URL)
        check_known("LEAD.rda", sha256(data), record)
        LEAD_DIR.mkdir(parents=True, exist_ok=True)
        rda.write_bytes(data)
        record["LEAD.rda"] = {
            "url": LEAD_URL,
            "dépôt": PEACESCIENCER,
            "commit": COMMIT,
            "date_du_commit": "2023-03-22",
            "downloaded": record.get("LEAD.rda", {}).get("downloaded", date.today().isoformat()),
            "bytes": len(data),
            "sha256": sha256(data),
            "version": "LEAD v1 (Ellis, Horowitz & Stam 2015) : les 11 variables du fichier de réplication des auteurs "
                       "(leaders_datapaper_replication_final_9_10_15.dta), une ligne par dirigeant d'Archigos (obsid), "
                       "reprises sans recodage par le paquet R peacesciencer",
            "années": "1875-2004",
            "licence": "aucune licence indiquée pour les données (le paquet peacesciencer est sous GPL-2) : fichiers "
                       "gardés en local (data/raw/lead/, ignoré par git), seuls des résultats sont exportés",
            "citation": "Ellis, C. M., Horowitz, M. C., & Stam, A. C. (2015). Introducing the LEAD Data Set. "
                        "International Interactions, 41(4), 718-741. https://doi.org/10.1080/03050629.2015.1016157 ; "
                        "Miller, S. V. (2022). peacesciencer: An R Package for Quantitative Peace Science Research. "
                        "Conflict Management and Peace Science, 39(6), 755-779.",
        }
        print(f"  LEAD.rda téléchargé : {len(data)} octets")

    import pyreadr
    lead = pyreadr.read_r(str(rda))["LEAD"]
    if list(lead.columns) != LEAD_COLUMNS or not lead["obsid"].is_unique:
        raise SystemExit(f"LEAD.rda : colonnes ou identifiants inattendus ({list(lead.columns)})")
    csv = LEAD_DIR / "LEAD.csv"
    lead.to_csv(csv, index=False)
    record["LEAD.csv"] = {"tiré_de": "LEAD.rda", "converti_avec": f"pyreadr {pyreadr.__version__}",
                          "lignes": len(lead), "colonnes": LEAD_COLUMNS, "bytes": csv.stat().st_size,
                          "sha256": sha256(csv.read_bytes())}
    print(f"  LEAD.csv : {len(lead)} dirigeants, {len(LEAD_COLUMNS) - 1} variables")

    # ------------------------------------------------ Archigos, already local
    arch = RAW / "arch_annual.csv"
    digest = sha256(arch.read_bytes())
    check_known("arch_annual.csv", digest, record)
    record["arch_annual.csv"] = {
        "url": "https://www.rochester.edu/college/faculty/hgoemans/data.htm",
        "downloaded": "déjà dans data/raw avant le notebook 06 (non téléchargé par ce script) ; l'origine exacte de "
                      "cette version annuelle en CSV n'est pas documentée dans le dépôt (la page des auteurs propose "
                      "Archigos_4.1_stata14.dta)",
        "bytes": arch.stat().st_size,
        "sha256": digest,
        "version": "Archigos 4.1 (données jusqu'au 31 décembre 2015), version annuelle : une ligne par dirigeant et "
                   "par année",
        "années": "1840-2015",
        "licence": "aucune licence indiquée ; les auteurs demandent de citer l'article",
        "citation": "Goemans, H. E., Gleditsch, K. S., & Chiozza, G. (2009). Introducing Archigos: A Data Set of "
                    "Political Leaders. Journal of Peace Research, 46(2), 269-283.",
    }
    print(f"  arch_annual.csv : SHA-256 {digest[:16]}…")

    record["sources_non_utilisées"] = NOT_USED
    record["user_agent"] = USER_AGENT
    SOURCES.write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  {SOURCES.relative_to(ROOT)} écrit")


if __name__ == "__main__":
    main()
