#!/usr/bin/env python3
"""Build Swiss-format CVs (HTML + PDF) for Kornelia Kunstmann, one per target job.

Fill in PERSONAL below (empty fields are left out of the CV), then run:
    python3 cv/build_cvs.py
PDFs are printed with headless Chromium (override with CHROME=/path/to/chrome).
"""
import html
import os
import pathlib
import shutil
import subprocess

HERE = pathlib.Path(__file__).resolve().parent

# --- Personal details: fill in, then re-run. Empty values are omitted. --------
PERSONAL = {
    "name": "Kornelia Kunstmann",
    "address": "Küssnacht am Rigi, Schwyz",
    "phone": "",            # e.g. "+41 79 123 45 67"
    "email": "kornelia.stubicar@googlemail.com",
    "linkedin": "linkedin.com/in/kornelia-kunstmann-13258992",
    "birth_year": "",       # e.g. "1981" (common, but optional, in Swiss CVs)
    "nationality": "",      # e.g. "Deutsch"
    "permit": "",           # e.g. "Niederlassungsbewilligung C"
    "photo": "",            # path relative to cv/, e.g. "photo.jpg"
}

L = {
    "de": dict(profile="Profil", competencies="Kernkompetenzen", experience="Berufserfahrung",
               education="Ausbildung", languages="Sprachen", certs="Weiterbildung & Zertifikate",
               interests="Interessen", personal="Persönliche Angaben", born="Jahrgang",
               nationality="Nationalität", permit="Bewilligung", references="Referenzen auf Anfrage",
               target="Bewerbung als"),
    "en": dict(profile="Profile", competencies="Core Competencies", experience="Professional Experience",
               education="Education", languages="Languages", certs="Training & Certificates",
               interests="Interests", personal="Personal Details", born="Year of birth",
               nationality="Nationality", permit="Work permit", references="References available on request",
               target="Application for"),
}

LANGUAGES = {
    "de": [("Deutsch", "Muttersprache"), ("Englisch", "verhandlungssicher (C1)"),
           ("Französisch", "gute Kenntnisse (B2)"), ("Spanisch", "gute Kenntnisse (B2)")],
    "en": [("German", "Native"), ("English", "Full professional (C1)"),
           ("French", "Professional working (B2)"), ("Spanish", "Professional working (B2)")],
}

EDUCATION = {
    "de": [("2000 – 2006", "Dipl.-Ing. Luft- und Raumfahrttechnik", "Universität Stuttgart · Masterniveau (EQF 7)")],
    "en": [("2000 – 2006", "Dipl.-Ing. Aerospace Engineering", "University of Stuttgart · Master's level (EQF 7)")],
}

CERTS = {
    "de": [("2021", "Permaculture Design Certificate (PDC)", "Permaculture Research Institute"),
           ("", "Claude 101 (KI-Grundlagen)", "Anthropic")],
    "en": [("2021", "Permaculture Design Certificate (PDC)", "Permaculture Research Institute"),
           ("", "Claude 101 (AI fundamentals)", "Anthropic")],
}

INTERESTS = {
    "de": "Regeneratives Design und Permakultur, Raumfahrt und neue Technologien",
    "en": "Regenerative design and permaculture, space and emerging technologies",
}

# Experience: (dates, title, employer · place, [bullets]). Bullets are drafted from the
# LinkedIn profile (titles, headline, skills) — review and add figures before sending.
EXPERIENCE = {
    "de": [
        ("02/2024 – 06/2026", "Head Documentation", "RUAG AG · Emmen LU", [
            "Führung der Dokumentationsorganisation mit bis zu 35 FTE, inkl. Budget-, Ressourcen- und Personalverantwortung",
            "Steuerung der technischen Dokumentation in einem regulierten Luftfahrtumfeld",
            "Treiber von Change Management, Prozessstandardisierung und Operational Excellence in der Organisation",
        ]),
        ("01/2022 – 01/2024", "Senior Business Development Manager", "RUAG AG · Emmen LU", [
            "Identifikation, Entwicklung und Akquisition neuer Geschäftsmöglichkeiten mit Kunden und Partnern",
            "Ausarbeitung von Angeboten, Verhandlungen und Aufbau von Kooperationen mit Kunden und Partnern",
        ]),
        ("01/2021 – 12/2021", "Lead Digital Transformation", "RUAG AG · Emmen LU", [
            "Leitung von Digitalisierungsinitiativen und Begleitung der Organisation durch den Wandel",
        ]),
        ("06/2019 – 12/2020", "Business Process Manager", "RUAG AG · Emmen LU", [
            "Analyse, Modellierung und Optimierung von Geschäftsprozessen entlang der Wertschöpfungskette",
        ]),
        ("04/2018 – 04/2019", "Space Science and Technology Advisor", "Swiss Space Center · Zürich", [
            "Beratung zu Raumfahrtwissenschaft und -technologie, Schnittstelle zwischen Industrie, Hochschulen und Behörden",
        ]),
        ("04/2017 – 03/2018", "Research Associate / Aerospace Engineer", "ETH Zürich / inspire AG · Zürich", [
            "Forschung zu additiver Fertigung (3D-Druck) und Raumfahrtanwendungen",
        ]),
        ("06/2011 – 03/2017", "Senior Project Manager", "maxon motor group · Sachseln OW", [
            "Gesamtverantwortung für komplexe Kundenprojekte im Bereich Präzisionsantriebe, u. a. für Luft- und Raumfahrt",
            "Steuerung von Kosten, Terminen, Qualität und Risiken in interdisziplinären Teams und mit Lieferanten",
        ]),
        ("02/2010 – 05/2011", "Technical Officer", "European Space Agency (ESA)", [
            "Technische Begleitung und Überwachung von Raumfahrtprojekten und Industrieaufträgen",
        ]),
        ("09/2006 – 01/2010", "Entwicklungsingenieurin", "Deutsches Zentrum für Luft- und Raumfahrt (DLR)", [
            "Entwicklung, Auslegung und Test von Luft- und Raumfahrtsystemen",
        ]),
    ],
    "en": [
        ("02/2024 – 06/2026", "Head Documentation", "RUAG AG · Emmen, Switzerland", [
            "Led the documentation organisation of up to 35 FTE, with budget, resource and people responsibility",
            "Steered technical documentation in a regulated aviation environment",
            "Drove change management, process standardisation and operational excellence across the organisation",
        ]),
        ("01/2022 – 01/2024", "Senior Business Development Manager", "RUAG AG · Emmen, Switzerland", [
            "Identified, developed and won new business with customers and partners",
            "Prepared proposals, led negotiations and built partnerships with customers and partners",
        ]),
        ("01/2021 – 12/2021", "Lead Digital Transformation", "RUAG AG · Emmen, Switzerland", [
            "Led digitalisation initiatives and guided the organisation through the change",
        ]),
        ("06/2019 – 12/2020", "Business Process Manager", "RUAG AG · Emmen, Switzerland", [
            "Analysed, modelled and improved end-to-end business processes",
        ]),
        ("04/2018 – 04/2019", "Space Science and Technology Advisor", "Swiss Space Center · Zurich", [
            "Advised on space science and technology; interface between industry, academia and public bodies",
        ]),
        ("04/2017 – 03/2018", "Research Associate / Aerospace Engineer", "ETH Zurich / inspire AG · Zurich", [
            "Research on additive manufacturing (3D printing) for space applications",
        ]),
        ("06/2011 – 03/2017", "Senior Project Manager", "maxon motor group · Sachseln, Switzerland", [
            "End-to-end responsibility for complex customer projects in precision drive systems, incl. aerospace",
            "Managed cost, schedule, quality and risk across cross-functional teams and suppliers",
        ]),
        ("02/2010 – 05/2011", "Technical Officer", "European Space Agency (ESA)", [
            "Technical oversight of space projects and industrial contracts",
        ]),
        ("09/2006 – 01/2010", "Development Engineer", "German Aerospace Center (DLR)", [
            "Design, analysis and testing of aerospace systems",
        ]),
    ],
}

VARIANTS = [
    {
        "slug": "cv_rychiger_director_project_management",
        "lang": "de",
        "target": "Director Project Management · Rychiger AG, Steffisburg",
        "headline": "Dipl.-Ing. Luft- und Raumfahrttechnik · Program & Project Management · Führungskraft (35 FTE)",
        "profile": (
            "Ingenieurin und Führungskraft mit rund 20 Jahren Erfahrung in Projekt- und Programmmanagement "
            "für technisch anspruchsvolle Produkte – bei DLR, ESA, maxon und RUAG. Bei maxon habe ich sechs "
            "Jahre lang komplexe internationale Kundenprojekte verantwortet, bei RUAG Geschäftsprozesse "
            "optimiert, die digitale Transformation geleitet und zuletzt eine Organisation mit bis zu 35 FTE "
            "geführt. Ich entwickle Projektorganisationen weiter, begleite Teams durch Veränderungen und "
            "setze KI und Digitalisierung pragmatisch ein."
        ),
        "competencies": [
            "Multiprojekt- & Portfoliomanagement", "Führung & Coaching von Projektleitenden",
            "Internationale Kundenprojekte", "Kosten-, Termin- & Risikosteuerung",
            "Projekt- & Prozessstandards", "Reporting an die Geschäftsleitung",
            "Change Management", "KI & Digitalisierung",
        ],
    },
    {
        "slug": "cv_axpo_process_excellence_manager",
        "lang": "de",
        "target": "Process Excellence Manager · Axpo Group, Baden",
        "headline": "Dipl.-Ing. Luft- und Raumfahrttechnik · Process Excellence & Transformation · Führungskraft (35 FTE)",
        "profile": (
            "Ingenieurin mit Schwerpunkt Prozess- und Organisationsentwicklung: Bei RUAG habe ich als "
            "Business Process Manager End-to-End-Prozesse analysiert und optimiert, als Lead Digital "
            "Transformation Digitalisierungsinitiativen geleitet und als Head Documentation eine Organisation "
            "mit bis zu 35 FTE durch Veränderungen geführt. Ich moderiere Workshops und Management-Dialoge, "
            "entwickle Operating Models und Governance weiter und verbinde strategisches Denken mit "
            "pragmatischer Umsetzung."
        ),
        "competencies": [
            "Process Excellence & End-to-End-Prozesse", "Operating Models & Governance",
            "Organisationsentwicklung", "Change Management",
            "Digitale Transformation", "Workshop- & Management-Moderation",
            "Operational Excellence", "Stakeholder-Management",
        ],
    },
    {
        "slug": "cv_johnson_controls_director_pm_opex",
        "lang": "en",
        "target": "Director, Project Management & Operational Excellence, EMEA · Johnson Controls, Neuhausen",
        "headline": "Executive Leader (35 FTE) · Program Management & Operational Excellence · Dipl.-Ing. Aerospace Engineering",
        "profile": (
            "Executive leader and aerospace engineer with ~20 years across DLR, ESA, maxon and RUAG. I have "
            "led an organisation of up to 35 FTE, run complex customer projects end to end, and driven process "
            "management, digital transformation and change programmes. I bring structured project governance, "
            "standardised processes and KPI-driven continuous improvement, and work in German, English, French "
            "and Spanish across international teams."
        ),
        "competencies": [
            "Operational Excellence & Continuous Improvement", "Project & Program Governance",
            "Process Standardisation", "Change Management",
            "Digital Transformation", "KPI & Risk Management",
            "People Leadership (35 FTE)", "Cross-functional Stakeholder Management",
        ],
    },
]

CSS = """
@page { size: A4; margin: 14mm 15mm 14mm 15mm; }
:root { --ink:#1d2433; --muted:#5b6475; --accent:#1f4e79; --rule:#d5dbe5; }
* { box-sizing: border-box; }
body { margin:0; background:#fff; color:var(--ink); font: 9.6pt/1.42 "Inter","Helvetica Neue",Arial,sans-serif; }
.page { max-width: 180mm; margin: 0 auto; }
header { display:flex; justify-content:space-between; gap:8mm; border-bottom:2px solid var(--accent); padding-bottom:4mm; }
h1 { font-size: 22pt; margin:0; letter-spacing:.2px; }
.headline { color:var(--accent); font-weight:600; margin-top:1.5mm; }
.target { color:var(--muted); font-size:8.8pt; margin-top:1.5mm; }
.photo { width:32mm; height:40mm; object-fit:cover; border-radius:2px; flex:none; }
.contact { display:flex; flex-wrap:wrap; gap:1mm 5mm; margin-top:2.5mm; font-size:8.8pt; color:var(--muted); }
.cols { display:grid; grid-template-columns: 1fr 55mm; gap: 8mm; margin-top: 5mm; }
h2 { font-size: 10.5pt; text-transform: uppercase; letter-spacing: 1px; color: var(--accent);
     border-bottom: 1px solid var(--rule); padding-bottom: 1mm; margin: 0 0 2.5mm; }
section { margin-bottom: 5mm; }
.job { margin-bottom: 3.2mm; break-inside: avoid; }
.job-head { display:flex; justify-content:space-between; gap:4mm; }
.job-title { font-weight: 700; }
.dates { color: var(--muted); white-space: nowrap; font-size: 8.8pt; }
.org { color: var(--muted); font-size: 8.8pt; }
ul { margin: 1mm 0 0; padding-left: 4.5mm; }
li { margin: .4mm 0; }
.side p, .side li { font-size: 8.9pt; }
.tags { list-style:none; padding:0; margin:0; }
.tags li { padding: .8mm 0; border-bottom: 1px dotted var(--rule); }
.kv { display:grid; grid-template-columns: auto 1fr; gap: .8mm 3mm; font-size: 8.9pt; }
.kv dt { color: var(--muted); } .kv dd { margin:0; }
.foot { color: var(--muted); font-size: 8.5pt; margin-top: 2mm; }
@media screen { body { background:#eef1f5; } .page { background:#fff; padding:14mm 15mm; margin:8mm auto;
  box-shadow:0 1px 4px rgba(0,0,0,.12); max-width:210mm; } }
@media (max-width: 700px) { .cols { grid-template-columns: 1fr; } header { flex-direction: column-reverse; }
  .page { padding: 16px; margin: 0; } }
"""


def e(s):
    return html.escape(s, quote=True)


def render(v):
    lang, t, p = v["lang"], L[v["lang"]], PERSONAL
    contact = [x for x in (p["address"], p["phone"], p["email"], p["linkedin"]) if x]
    photo = f'<img class="photo" src="{e(p["photo"])}" alt="">' if p["photo"] else ""

    jobs = "".join(
        f'<div class="job"><div class="job-head"><span class="job-title">{e(title)}</span>'
        f'<span class="dates">{e(d)}</span></div><div class="org">{e(org)}</div>'
        f'<ul>{"".join(f"<li>{e(b)}</li>" for b in bullets)}</ul></div>'
        for d, title, org, bullets in EXPERIENCE[lang])
    edu = "".join(f'<div class="job"><div class="job-head"><span class="job-title">{e(a)}</span>'
                  f'<span class="dates">{e(d)}</span></div><div class="org">{e(b)}</div></div>'
                  for d, a, b in EDUCATION[lang])
    certs = "".join(f'<li>{e(a)}<br><span class="org">{e(b)}{" · " + e(d) if d else ""}</span></li>'
                    for d, a, b in CERTS[lang])
    langs = "".join(f"<dt>{e(a)}</dt><dd>{e(b)}</dd>" for a, b in LANGUAGES[lang])
    pers = [(t["born"], p["birth_year"]), (t["nationality"], p["nationality"]), (t["permit"], p["permit"])]
    pers_html = "".join(f"<dt>{e(a)}</dt><dd>{e(b)}</dd>" for a, b in pers if b)
    pers_section = f'<section><h2>{t["personal"]}</h2><dl class="kv">{pers_html}</dl></section>' if pers_html else ""
    comps = "".join(f"<li>{e(c)}</li>" for c in v["competencies"])

    return f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CV {e(p["name"])}</title><style>{CSS}</style></head>
<body><div class="page">
<header><div><h1>{e(p["name"])}</h1><div class="headline">{e(v["headline"])}</div>
<div class="contact">{"".join(f"<span>{e(c)}</span>" for c in contact)}</div>
<div class="target">{t["target"]}: {e(v["target"])}</div></div>{photo}</header>
<div class="cols">
<main>
<section><h2>{t["profile"]}</h2><p>{e(v["profile"])}</p></section>
<section><h2>{t["experience"]}</h2>{jobs}</section>
<section><h2>{t["education"]}</h2>{edu}</section>
</main>
<aside class="side">
<section><h2>{t["competencies"]}</h2><ul class="tags">{comps}</ul></section>
<section><h2>{t["languages"]}</h2><dl class="kv">{langs}</dl></section>
<section><h2>{t["certs"]}</h2><ul class="tags">{certs}</ul></section>
{pers_section}
<section><h2>{t["interests"]}</h2><p>{e(INTERESTS[lang])}</p></section>
<p class="foot">{t["references"]}</p>
</aside></div></div></body></html>
"""


def find_chrome():
    for c in (os.environ.get("CHROME"), "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
              shutil.which("chromium"), shutil.which("google-chrome"), shutil.which("chrome")):
        if c and os.path.exists(c):
            return c
    raise SystemExit("Chromium not found; set CHROME=/path/to/chrome")


def main():
    out = HERE
    chrome = find_chrome()
    for v in VARIANTS:
        html_path = out / f"{v['slug']}.html"
        html_path.write_text(render(v), encoding="utf-8")
        pdf_path = out / f"{v['slug']}.pdf"
        subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf_path}", html_path.as_uri()],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{html_path.name} -> {pdf_path.name}")


if __name__ == "__main__":
    main()
