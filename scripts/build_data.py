import csv
import json
from html import escape
from pathlib import Path
from urllib.parse import quote


SOURCE = Path("_data/jsuart_metadata.csv")
OUTPUT = Path("site-data/artworks.json")
RECORDS_DIR = Path("records")

CATALOG_CAPTIONS = {
    "coll001": "Artist unknown, Nineteenth-Century African American Portrait, n.d. Medium unknown, 19.6 x 15 in.",
    "coll002": "Artist unknown, Nineteenth-Century African American Portrait, n.d. Medium unknown, 19.6 x 15 in.",
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
    ("objectNumber", "Object Number"),
    ("title", "Title"),
    ("creator", "Creator"),
    ("attribution", "Attribution"),
    ("date", "Date"),
    ("medium", "Medium"),
    ("dimensions", "Dimensions"),
    ("edition", "Edition"),
    ("subject", "Subject"),
    ("location", "Associated Place"),
    ("identifier", "Identifier"),
    ("source", "Source"),
    ("type", "Type"),
    ("format", "Format"),
    ("language", "Language"),
    ("rights", "Rights"),
    ("rightsstatement", "Rights Statement"),
]


def clean(value):
    return " ".join((value or "").split())


def format_value(value):
    return clean(value).replace(";", ", ")


def display_value(value, default="Not recorded"):
    return format_value(value) or default


def display_creator(record):
    creator = clean(record.get("creator"))
    attribution = clean(record.get("attribution"))
    if creator and attribution:
        return f"{attribution} {creator}"
    if creator:
        return creator
    return "Creator unknown"


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
        "objectNumber": object_id.upper(),
        "title": clean(row.get("title")),
        "creator": clean(row.get("creator")),
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
        "catalogCaption": CATALOG_CAPTIONS.get(object_id, ""),
        "image": image,
        "imageUrl": encode_path(image),
        "recordPath": f"./records/{object_id}.html",
    }


def render_meta_rows(record):
    rows = []
    for key, label in FIELD_LABELS:
        value = display_value(record.get(key))
        rows.append(
            f"""
            <div class="record-meta-row">
              <dt>{escape(label)}</dt>
              <dd>{escape(value)}</dd>
            </div>
            """.strip()
        )

    if record.get("latitude") and record.get("longitude"):
        rows.append(
            f"""
            <div class="record-meta-row">
              <dt>Coordinates</dt>
              <dd>{escape(record["latitude"])}, {escape(record["longitude"])}</dd>
            </div>
            """.strip()
        )

    return "\n".join(rows)


def render_record_page(record):
    title = escape(record["title"] or "Untitled")
    creator = escape(display_creator(record))
    image_alt = f"{record['title'] or 'Untitled'} by {display_creator(record)}"
    description = escape(record["description"] or "Description not yet available.")
    map_link = ""
    if record.get("latitude") and record.get("longitude"):
        map_link = (
            f'<a class="button button-secondary" '
            f'href="https://www.google.com/maps?q={escape(record["latitude"])},{escape(record["longitude"])}">'
            "View associated place"
            "</a>"
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
  <link rel="stylesheet" href="../styles.css?v=20260811k">
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
            <article>
              <span class="record-summary-label">Object Number</span>
              <span class="record-summary-value">{escape(record["objectNumber"])}</span>
            </article>
            <article>
              <span class="record-summary-label">Date</span>
              <span class="record-summary-value">{escape(display_value(record["date"]))}</span>
            </article>
            <article>
              <span class="record-summary-label">Medium</span>
              <span class="record-summary-value">{escape(display_value(record["medium"]))}</span>
            </article>
            <article>
              <span class="record-summary-label">Dimensions</span>
              <span class="record-summary-value">{escape(display_value(record["dimensions"]))}</span>
            </article>
          </div>
          <p class="record-description">{description}</p>
          <div class="hero-actions">
            <a class="button button-primary" href="../browse.html">Return to catalog</a>
            <a class="button button-secondary" href="../_data/jsuart_metadata.csv">Download CSV</a>
            {map_link}
          </div>
        </div>
      </section>

      <section class="record-detail-grid">
        <article class="record-panel">
          <p class="section-label">Catalog Note</p>
          <h2>Object context</h2>
          <p>
            This public-facing record is drawn from the working catalog and supporting collection files
            maintained for the Jackson State University Department of Art Permanent Collection.
          </p>
          <p>{escape(display_value(record["catalogCaption"], "No additional caption note is currently published for this object."))}</p>
        </article>

        <article class="record-panel">
          <p class="section-label">Collection Description</p>
          <h2>Interpretive description</h2>
          <p>{description}</p>
        </article>
      </section>

      <section class="record-metadata">
        <div>
          <p class="section-label">Metadata</p>
          <h2>Catalog fields</h2>
        </div>
        <dl class="record-meta-list">
          {render_meta_rows(record)}
        </dl>
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
