import csv
import json
from html import escape
from pathlib import Path
from urllib.parse import quote


SOURCE = Path("_data/jsuart_metadata.csv")
OUTPUT = Path("site-data/artworks.json")
RECORDS_DIR = Path("records")
PUBLIC_BASE_URL = "https://jsumsart.github.io/collection"
COLLECTION_NAME = "Jackson State University Department of Art Permanent Collection"

CATALOG_CAPTIONS = {
    "coll001": "Creator not presently known, Nineteenth-Century African American Portrait, n.d. Medium unknown, 19.6 x 15 in.",
    "coll002": "Creator not presently known, Nineteenth-Century African American Portrait, n.d. Medium unknown, 19.6 x 15 in.",
    "coll003": "Karl Griffin, Juanita, n.d. Oil on canvas, 31.5 x 23.5 in.",
    "coll004": "Thomas E. Eloby II, Self-Portrait, 1968. Ink on paper, 6.25 x 8.25 in.",
    "coll005": "Thomas E. Eloby II, Landscape, n.d. Oil on canvas, 36 x 24 in.",
    "coll008": "Brockford Gordon, Kneeling Football Player, n.d. Photograph on foam board.",
    "coll010": "Ronald O. Schnell, Landscape with a Bridge, n.d. Oil on canvas, 44 x 42 in.",
    "coll018": "Hargreaves Ntukwana, Figure with Jug, n.d. Mixed media on paper, 14.25 x 10 in.",
    "coll020": "Hargreaves Ntukwana, Figure with Small Bird, n.d. Mixed media on paper, 20 x 28.25 in.",
    "coll021": "Eli Kobeli, Musicians, n.d. Chalk on paper, 36 x 22.5 in.",
    "coll024": "Cliff Johnson, Haunted House, 1966. Medium unknown, 17 x 22.5 in.",
    "coll025": "Edward Colker, Sign and Symbol, 1967. Lithograph in color, ed. 106/210.",
    "coll030": "Anderson Macklin, Abstract Landscape, n.d. Oil on canvas, 23.5 x 36 in.",
    "coll034": "Dominic Azogini, Untitled (Sketch of a Man), c. 1980s. Medium unknown, 18 x 23 in.",
    "coll035": "Attma, Passage, c. 1980. Engraving.",
    "coll033": "Floyd Willis Coleman, Study #17, c. 1970s.",
    "coll036": "William Majors, Burning Bush, 1967. Etching in sepia, ed. 72/110.",
    "coll037": "Herbert Lewis Fink, The Foot Path, 1965. Etching, ed. 137/210, 17 1/8 x 21 3/8 in.",
    "coll042": "Robert R. Malone, Spring Night, 1966. Etching in color, ed. 123/210, 20 x 16 in.",
    "coll044": "Lewis Leon Lassiter, Las Cruces, 1991. Woodblock print, ed. 8/20, 9.5 x 10.5 in.",
    "coll053": "Floyd Willis Coleman, Mississippi Suite: Study, 1984. Pen and ink on paper, 16 x 23.5 in.",
    "coll054": "Brockford Gordon, Officer at the Flood, 1979. Photograph, 14 x 11 in.",
    "coll055": "Brockford Gordon, Jackson Flood, 1979. Photograph, 11 x 14 in.",
    "coll056": "Brockford Gordon, Sewing Machine, n.d. Photograph, 14 x 12 in.",
    "coll057": "Brockford Gordon, Eggs, n.d. Photograph, 10 x 8 in.",
    "coll058": "Brockford Gordon, Fig Leaf, n.d. Photograph, 10 x 8 in.",
    "coll059": "Karl Griffin, Connie, n.d. Oil on canvas, 36 x 24 in.",
    "coll060": "Karl Griffin, Nude Woman, n.d. Oil on canvas.",
    "coll061": "Karl Griffin, Figure Study, n.d. Gouache on paper, 15 x 22 in.",
    "coll063": "Lewis Leon Lassiter, Mannequins, 1990. Oil on canvas, 16 x 12 in.",
    "coll066": "C. W. Moore, Struggle, 1964. Print after larger acrylic painting on Masonite hardboard, 4 x 8 ft.",
    "coll067": "Godfrey Ndaba, Two Women (1), 1980. Chalk on paper, 12.6 x 37.85 in.",
    "coll068": "Godfrey Ndaba, Two Women (2), 1980. Chalk on paper, 12.6 x 37.85 in.",
    "coll070": "Lynette K. Stephenson, Untitled (Dress), c. mid-1990s.",
    "coll071": "Attributed to Hugh E. Stevens, Young Man, n.d. Oil on Masonite, 51 x 51.5 in.",
    "coll076": "Kojin Toneyama, Sunset, 1966. Lithograph in color, ed. 191/210, 17 x 21.75 in.",
    "coll084": "Chalmers W. Mayers Jr., Composition Number One, 1999. Acrylic and collage on board.",
}

FIELD_LABELS = [
    ("creator", "Artist / Maker"),
    ("title", "Title"),
    ("date", "Date"),
    ("medium", "Medium"),
    ("dimensions", "Dimensions"),
    ("objectNumber", "Accession Number"),
    ("collection", "Collection"),
    ("subject", "Subject / Keywords"),
]

UNKNOWN_CREATOR_LABEL = "Creator not presently known"


def clean(value):
    return " ".join((value or "").split())


def normalize_unknown_creator(value):
    cleaned = clean(value)
    if cleaned.lower() in {"unknown", "creator unknown"}:
        return UNKNOWN_CREATOR_LABEL
    return cleaned


def format_value(value):
    return clean(value).replace(";", ", ")


def display_value(value, default="Not recorded"):
    return format_value(value) or default


def has_public_value(value):
    return bool(format_value(value))


def normalize_creator_name(value):
    creator = normalize_unknown_creator(value)
    if "," not in creator:
        return creator
    parts = [part.strip() for part in creator.split(",") if part.strip()]
    if len(parts) < 2:
        return creator
    return " ".join(parts[1:] + [parts[0]])


def display_creator(record):
    creator = normalize_creator_name(record.get("creator"))
    attribution = clean(record.get("attribution"))
    if creator and attribution:
        return f"{attribution} {creator}"
    if creator:
        return creator
    return UNKNOWN_CREATOR_LABEL


def object_information_rows(record):
    rows = []
    for key, label in FIELD_LABELS:
        value = record.get(key)
        if has_public_value(value):
            rows.append((label, format_value(value)))
    rows.append(("Acquisition Information", "Not yet documented."))
    return rows


def render_object_information(record):
    rows = []
    for label, value in object_information_rows(record):
        rows.append(
            f"""
            <div class="record-meta-row">
              <dt>{escape(label)}</dt>
              <dd>{escape(value)}</dd>
            </div>
            """.strip()
        )
    return "\n".join(rows)


def build_research_note(record):
    note_parts = []
    creator = display_creator(record)
    if creator == UNKNOWN_CREATOR_LABEL:
        note_parts.append("The creator is not presently known.")
    if has_public_value(record.get("attribution")):
        note_parts.append("The current attribution reflects the existing departmental catalog and may be refined through further research.")
    if has_public_value(record.get("date")):
        date_value = format_value(record.get("date"))
        if date_value.lower() == "n.d.":
            note_parts.append("A date for the work has not yet been documented.")
        elif date_value.lower().startswith("c."):
            note_parts.append("The date is approximate.")

    note_parts.append("The title, attribution, date, and medium shown here reflect current collection documentation.")
    note_parts.append("Additional research into collection history, acquisition, and related scholarship is ongoing.")
    return " ".join(note_parts)


def build_about_text(record):
    title = format_value(record.get("title")) or "This work"
    creator = display_creator(record)
    if creator == UNKNOWN_CREATOR_LABEL:
        return (
            f"{title} is part of the {COLLECTION_NAME}. "
            "Research into the work, its context, and its collection history is ongoing."
        )
    return (
        f"{title} by {creator} is part of the {COLLECTION_NAME}. "
        "Research into the work, its context, and its collection history is ongoing."
    )


def build_rights_text(record):
    rights_holder = format_value(record.get("rights")) or "the Jackson State University Department of Art"
    return {
        "copyright_status": "Copyright status has not yet been determined.",
        "digital_image": f"Digital image courtesy of {COLLECTION_NAME}.",
        "reproduction": f"For information concerning image use and reproduction, contact {rights_holder}.",
    }


def build_citation(record):
    parts = []
    creator = display_creator(record)
    title = format_value(record.get("title"))
    date = format_value(record.get("date"))
    medium = format_value(record.get("medium"))
    accession = format_value(record.get("objectNumber"))
    if creator:
        parts.append(creator)
    if title:
        parts.append(title)
    if date:
        parts.append(date)
    if medium:
        parts.append(medium)
    parts.append(COLLECTION_NAME)
    if accession:
        parts.append(accession)
    return ", ".join(parts) + "."


def normalize_id(raw_id, index):
    return clean(raw_id) or f"record-{index:03d}"


def encode_path(path):
    return quote(path, safe="/.-_")


def build_record(row, index):
    object_id = normalize_id(row.get("objectid"), index)
    filename = clean(row.get("filename"))
    image = f"./objects/{filename}" if filename else "./assets/logo.png"
    return {
        "id": object_id,
        "objectNumber": clean(row.get("accession_number")) or object_id.upper(),
        "title": clean(row.get("title")),
        "creator": normalize_creator_name(row.get("creator")),
        "attribution": clean(row.get("attribution")),
        "date": clean(row.get("date")),
        "medium": clean(row.get("medium")),
        "dimensions": clean(row.get("dimensions")),
        "edition": clean(row.get("edition")),
        "description": clean(row.get("description")),
        "subject": clean(row.get("subject")),
        "location": clean(row.get("location")),
        "latitude": clean(row.get("latitude")),
        "longitude": clean(row.get("longitude")),
        "source": clean(row.get("source")),
        "identifier": clean(row.get("identifier")),
        "type": clean(row.get("type")),
        "format": clean(row.get("format")),
        "language": clean(row.get("language")),
        "rights": clean(row.get("rights")),
        "rightsstatement": clean(row.get("rightsstatement")),
        "collection": COLLECTION_NAME,
        "catalogCaption": CATALOG_CAPTIONS.get(object_id, ""),
        "image": image,
        "imageUrl": encode_path(image),
        "recordPath": f"./records/{object_id}.html",
    }


def render_record_page(record):
    title = escape(record["title"] or "Untitled")
    creator = escape(display_creator(record))
    image_alt = f"{record['title'] or 'Untitled'} by {display_creator(record)}"
    description = escape(record["description"]) if has_public_value(record.get("description")) else ""
    rights = build_rights_text(record)
    citation = escape(build_citation(record))
    citation_url = f"{PUBLIC_BASE_URL}/records/{record['id']}.html"
    about_text = escape(build_about_text(record))
    research_note = escape(build_research_note(record))

    summary_items = [
        ("Date", record.get("date")),
        ("Medium", record.get("medium")),
        ("Dimensions", record.get("dimensions")),
        ("Accession Number", record["objectNumber"]),
    ]
    summary_markup = "\n".join(
        f"""
            <article>
              <span class="record-summary-label">{escape(label)}</span>
              <span class="record-summary-value">{escape(format_value(value))}</span>
            </article>
        """.rstrip()
        for label, value in summary_items
        if has_public_value(value)
    )

    description_panel = (
        f"""
        <article class="record-panel">
          <p class="section-label">Description</p>
          <h2>Object description</h2>
          <p>{description}</p>
        </article>
        """.strip()
        if description
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} | JSU Department of Art Permanent Collection</title>
  <meta
    name="description"
    content="Object record for {title} in the Jackson State University Department of Art Permanent Collection."
  >
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link
    href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap"
    rel="stylesheet"
  >
  <link rel="icon" href="../favicon.ico">
  <link rel="stylesheet" href="../styles.css?v=20260811z">
  <script src="../image-protection.js?v=20260811c" defer></script>
</head>
<body class="record-page">
  <a class="skip-link" href="#record-main">Skip to record</a>
  <div class="page-shell">
    <header class="site-header record-header">
      <a class="brand" href="../index.html" aria-label="JSU Art home">
        <img class="brand-mark" src="../assets/logo.png" alt="JSU Department of Art logo">
        <span class="brand-lockup">
          <span class="brand-kicker">Jackson State University</span>
          <span class="brand-title">Department of Art Permanent Collection</span>
        </span>
      </a>
      <nav class="site-nav" aria-label="Primary">
        <a href="../index.html">Home</a>
        <a href="../browse.html">Browse</a>
        <a href="../african-art.html">African Art</a>
        <a href="../about.html">About</a>
      </nav>
    </header>

    <main id="record-main" class="record-shell">
      <section class="record-hero">
        <div class="record-media-panel">
          <img src="../{escape(record["imageUrl"][2:])}" alt="{escape(image_alt)}">
        </div>
        <div class="record-intro">
          <p class="eyebrow">Object Record</p>
          <h1>{title}</h1>
          <p class="record-creator">{creator}</p>
          <div class="record-summary-grid">
            {summary_markup}
          </div>
          <div class="hero-actions">
            <a class="button button-primary" href="../browse.html">Back to Collection</a>
          </div>
        </div>
      </section>

      <section class="record-detail-grid">
        {description_panel}
        <article class="record-panel">
          <p class="section-label">About the Work</p>
          <h2>Collection context</h2>
          <p>{about_text}</p>
        </article>
      </section>

      <section class="record-metadata">
        <div>
          <p class="section-label">Object Information</p>
          <h2>Recorded object details</h2>
        </div>
        <dl class="record-meta-list">
          {render_object_information(record)}
        </dl>
      </section>

      <section class="record-detail-grid">
        <article class="record-panel">
          <p class="section-label">Research Notes</p>
          <h2>Current state of research</h2>
          <p>{research_note}</p>
        </article>

        <article class="record-panel">
          <p class="section-label">Rights and Reproduction</p>
          <h2>Use and permissions</h2>
          <p><strong>Copyright status:</strong> {escape(rights["copyright_status"])}</p>
          <p>{escape(rights["digital_image"])}</p>
          <p>{escape(rights["reproduction"])}</p>
        </article>
      </section>

      <section class="record-detail-grid">
        <article class="record-panel">
          <p class="section-label">Cite This Record</p>
          <h2>Suggested citation</h2>
          <p>{citation}</p>
          <p><a class="inline-link" href="{citation_url}">{citation_url}</a></p>
        </article>

        <article class="record-panel">
          <p class="section-label">Digital Collection Project</p>
          <h2>Project credit</h2>
          <p>
            Digitization and database development led by Dr. Brittany Myburgh and Dr. Detrice Roberts,
            with support from the Africana Digital Humanities Lab at Jackson State University.
          </p>
        </article>
      </section>
    </main>
  </div>
</body>
</html>
"""


def main():
    records = []
    with SOURCE.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for index, row in enumerate(reader, start=1):
            records.append(build_record(row, index))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(records, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    RECORDS_DIR.mkdir(parents=True, exist_ok=True)
    for existing in RECORDS_DIR.glob("*.html"):
        existing.unlink()

    for record in records:
        output_path = RECORDS_DIR / f"{record['id']}.html"
        output_path.write_text(render_record_page(record), encoding="utf-8")

    print(f"Wrote {len(records)} records to {OUTPUT} and {RECORDS_DIR}")


if __name__ == "__main__":
    main()
