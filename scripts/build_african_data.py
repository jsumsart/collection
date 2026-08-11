import csv
import json
from html import escape
from pathlib import Path
from urllib.parse import quote


SOURCE = Path("/Users/Birittany/Documents/African Art/_data/africanart_mdl_medata.csv")
OUTPUT = Path("site-data/african-artworks.json")
RECORDS_DIR = Path("african-records")

FIELD_LABELS = [
    ("objectNumber", "Object Number"),
    ("title", "Title"),
    ("preferredTerm", "Preferred Term"),
    ("creator", "Creator"),
    ("culture", "Culture / Community"),
    ("date", "Date"),
    ("timePeriod", "Time Period"),
    ("location", "Geographic Location"),
    ("objectType", "Object Type"),
    ("materials", "Materials"),
    ("technique", "Technique"),
    ("functionUse", "Function / Use"),
    ("identifier", "Identifier"),
    ("source", "Source"),
    ("rights", "Rights"),
    ("rightsstatement", "Rights Statement"),
    ("attributionConfidence", "Attribution Confidence"),
]


def clean(value):
    return " ".join((value or "").split())


def display_value(value, default="Not recorded"):
    return clean(value).replace(";", ", ") or default


def encode_path(path):
    return quote(path, safe="/.-_")


def display_agent(record):
    if clean(record.get("creator")):
        return clean(record["creator"])
    if clean(record.get("culture")):
        return clean(record["culture"])
    if clean(record.get("objectType")):
        return clean(record["objectType"])
    return "Maker or culture not recorded"


def build_record(row, index):
    object_id = clean(row.get("Object name")) or f"african-{index:03d}"
    filename = clean(row.get("File name"))
    image = f"./african-thumbs/{filename}" if filename else "./assets/logo.png"
    return {
        "id": object_id,
        "objectNumber": clean(row.get("Identifier")) or object_id.upper(),
        "title": clean(row.get("Title")),
        "preferredTerm": clean(row.get("preferred_term")),
        "creator": clean(row.get("Creator")),
        "culture": clean(row.get("culture_community")),
        "date": clean(row.get("Date")),
        "timePeriod": clean(row.get("period_dynasty") or row.get("Coverage (time period)")),
        "location": clean(row.get("Geographic location")),
        "objectType": clean(row.get("object_type")),
        "materials": clean(row.get("materials")),
        "technique": clean(row.get("technique")),
        "functionUse": clean(row.get("function_use")),
        "description": clean(row.get("Description")),
        "subject": clean(row.get("Subject")),
        "identifier": clean(row.get("Identifier")),
        "source": clean(row.get("Source")),
        "type": clean(row.get("Resource type")),
        "format": clean(row.get("format") or row.get("Media format")),
        "language": clean(row.get("Language")),
        "rights": clean(row.get("Rights")),
        "rightsstatement": clean(row.get("Disclaimer")),
        "attributionConfidence": clean(row.get("attribution_confidence")),
        "latitude": clean(row.get("latitude")),
        "longitude": clean(row.get("longitude")),
        "collectionLabel": "African Art Collection",
        "image": image,
        "imageUrl": encode_path(image),
        "recordPath": f"./african-records/{object_id}.html",
    }


def render_meta_rows(record):
    rows = []
    for key, label in FIELD_LABELS:
        rows.append(
            f"""
            <div class="record-meta-row">
              <dt>{escape(label)}</dt>
              <dd>{escape(display_value(record.get(key)))}</dd>
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
    agent = escape(display_agent(record))
    description = escape(record["description"] or "Description not yet available.")
    image_alt = f"{record['title'] or 'Untitled'} from the Jackson State University African Art Collection"
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
  <title>{title} | JSU African Art Collection</title>
  <meta
    name="description"
    content="Object record for {title} in the Jackson State University African Art Collection."
  >
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link
    href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap"
    rel="stylesheet"
  >
  <link rel="icon" href="../favicon.ico">
  <link rel="stylesheet" href="../styles.css?v=20260811r">
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
          <p class="eyebrow">African Art Record</p>
          <h1>{title}</h1>
          <p class="record-creator">{agent}</p>
          <div class="record-summary-grid">
            <article>
              <span class="record-summary-label">Object Number</span>
              <span class="record-summary-value">{escape(display_value(record["objectNumber"]))}</span>
            </article>
            <article>
              <span class="record-summary-label">Date</span>
              <span class="record-summary-value">{escape(display_value(record["date"]))}</span>
            </article>
            <article>
              <span class="record-summary-label">Culture / Community</span>
              <span class="record-summary-value">{escape(display_value(record["culture"]))}</span>
            </article>
            <article>
              <span class="record-summary-label">Object Type</span>
              <span class="record-summary-value">{escape(display_value(record["objectType"]))}</span>
            </article>
          </div>
          <p class="record-description">{description}</p>
          <div class="hero-actions">
            <a class="button button-primary" href="../african-art.html">Return to African Art browse</a>
            {map_link}
          </div>
        </div>
      </section>

      <section class="record-detail-grid">
        <article class="record-panel">
          <p class="section-label">Collection Context</p>
          <h2>Catalog framing</h2>
          <p>
            This record is published as part of the Jackson State University African Art Collection
            and remains distinct from the Department of Art permanent collection browse path.
          </p>
          <p>{escape(display_value(record["attributionConfidence"], "Attribution notes are not currently published for this object."))}</p>
        </article>

        <article class="record-panel">
          <p class="section-label">Object Description</p>
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
