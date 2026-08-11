import csv
import re
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET


CSV_PATH = Path("_data/jsuart_metadata.csv")
DOCX_PATH = Path("/Users/Birittany/Documents/Permanent Collection/JSUCatalogFinal.docx")
IMAGE_DIR = Path("/Users/Birittany/Downloads/drive-download-20260811T145531Z-1-001")
THUMB_PREFIX = "catalog-thumbs"
AUDIT_PATH = Path("_data/catalog_figure_audit.csv")

RIGHTS = "JSU"
RIGHTS_STATEMENT = (
    "All rights reserved. Reproduction or redistribution requires written permission from "
    "the Jackson State University Department of Art."
)
SOURCE = "JSU Department of Art collection catalog"

DATE_PATTERN = re.compile(
    r"(June \d{4}; negative \d{4}, printed \d{4}|April \d{4}|c\. mid-\d{4}s|c\. fifteenth century|c\. \d{4}s|c\. \d{4}|n\.d\.|\d{4})"
)
DIMENSIONS_PATTERN = re.compile(
    r"\d[\d\s/\.]*\s*x\s*\d[\d\s/\.]*(?:\s*x\s*\d[\d\s/\.]*)?\s*(?:in|ft)\.?(?:\s*;\s*image:\s*\d[\d\s/\.]*\s*x\s*\d[\d\s/\.]*(?:\s*x\s*\d[\d\s/\.]*)?\s*in\.?)?",
    re.IGNORECASE,
)
EDITION_PATTERN = re.compile(r"ed\.\s*[^,;]+", re.IGNORECASE)
DIMENSION_PATTERN = re.compile(r"\d")

# Existing record mappings where the catalog figure clearly corresponds to an existing public record.
FIGURE_TO_RECORD = {
    4: "coll048",
    5: "coll046",
    12: "coll045",
    18: "coll061",
    19: "coll059",
    20: "coll060",
    21: "coll003",
    25: "coll083",
    29: "coll071",
    32: "coll033",
    33: "coll053",
    34: "coll054",
    35: "coll055",
    36: "coll008",
    37: "coll057",
    38: "coll056",
    39: "coll058",
    40: "coll070",
    41: "coll030",
    44: "coll084",
    48: "coll039",
    53: "coll034",
    54: "coll062",
    55: "coll035",
    56: "coll001",
    57: "coll002",
    67: "coll082",
    68: "coll063",
    69: "coll043",
    70: "coll044",
    71: "coll004",
    72: "coll005",
    73: "coll069",
    74: "coll010",
    78: "coll024",
    79: "coll078",
    80: "coll066",
    82: "coll064",
    83: "coll065",
    84: "coll068",
    85: "coll067",
    86: "coll016",
    87: "coll020",
    88: "coll018",
    91: "coll021",
    92: "coll051",
    94: "coll038",
    95: "coll025",
    96: "coll036",
    97: "coll076",
    98: "coll042",
    99: "coll037",
}

# Figures that are documentary/contextual titles rather than maker-title object entries.
TITLE_ONLY_FIGURES = {
    1, 2, 3, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 22, 23, 24, 26, 27, 30, 42, 47, 66
}

FIGURE_OVERRIDES = {
    6: {
        "creator": "Photographer unknown",
        "title": "Vertis Hayes in front of the Carver Mural, Johnson Hall, Jackson State University",
        "medium": "Photograph",
        "dimensions": "",
    },
    7: {
        "creator": "Vertis Hayes",
        "title": "The Carver Mural",
        "medium": "Full-scale reproduction after original",
        "dimensions": "",
        "subject": "Mural",
    },
    8: {
        "creator": "",
        "title": "Detail of The Carver Mural",
        "medium": "Full-scale reproduction after original",
        "dimensions": "",
        "subject": "Mural",
    },
    15: {
        "creator": "",
        "title": "Maria Jones, Jackson State University",
        "medium": "Yearbook portrait",
    },
    16: {
        "creator": "",
        "title": "Lawrence A. Jones, Jackson State University",
        "medium": "Yearbook portrait",
    },
    25: {
        "title": "Vase",
        "medium": "Ceramic",
        "dimensions": "",
        "subject": "Ceramics",
    },
    79: {
        "creator": "Jerry and Terry Lynn (Twin)",
        "title": "Red Manse",
    },
}


def clean(value):
    return " ".join((value or "").split())


def load_rows():
    with CSV_PATH.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    return rows


def write_rows(rows, fieldnames):
    with CSV_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def extract_figure_lines():
    with ZipFile(DOCX_PATH) as archive:
        xml = archive.read("word/document.xml")

    root = ET.fromstring(xml)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    lines = []
    for paragraph in root.findall(".//w:p", ns):
        text = "".join((node.text or "") for node in paragraph.findall(".//w:t", ns)).strip()
        if text.startswith("Fig. "):
            lines.append(text)
    return lines


def load_file_map():
    mapping = {}
    for path in sorted(IMAGE_DIR.glob("*")):
        if not path.is_file():
            continue
        match = re.match(r"fig-(\d+)_", path.name)
        if not match:
            continue
        mapping[int(match.group(1))] = path.name
    return mapping


def parse_line(line):
    match = re.match(r"Fig\.\s*(\d+)\.\s*(.+)", line)
    if not match:
        return None

    fig = int(match.group(1))
    body = match.group(2).strip()

    date_match = DATE_PATTERN.search(body)
    if date_match:
        prefix = body[: date_match.start()].rstrip(", ")
        date = date_match.group(0)
        after = body[date_match.end() :].lstrip(". ").strip()
    else:
        prefix = body.rstrip(". ")
        date = ""
        after = ""

    attribution = ""
    creator = ""
    title = prefix

    if fig in TITLE_ONLY_FIGURES:
        title = prefix
    else:
        if prefix.startswith("Attributed to "):
            attribution = "Attributed to"
            prefix = prefix[len("Attributed to ") :]
        if prefix.startswith("Artist unknown, "):
            creator = "Unknown"
            title = prefix.split(", ", 1)[1]
        elif prefix.startswith("Photographer unknown, "):
            creator = "Photographer unknown"
            title = prefix.split(", ", 1)[1]
        elif ", " in prefix:
            creator, title = prefix.split(", ", 1)
        else:
            title = prefix

    medium = ""
    dimensions = ""
    edition = ""
    if after:
        detail = clean(after).rstrip(".")
        edition_match = EDITION_PATTERN.search(detail)
        if edition_match:
            edition = clean(edition_match.group(0))
            detail = clean((detail[: edition_match.start()] + " " + detail[edition_match.end() :]).strip(" ,.;"))

        dimensions_match = DIMENSIONS_PATTERN.search(detail)
        if dimensions_match:
            dimensions = clean(dimensions_match.group(0).rstrip("."))
            detail = clean((detail[: dimensions_match.start()] + " " + detail[dimensions_match.end() :]).strip(" ,.;"))

        medium = clean(detail.strip(" ,.;"))

    entry = {
        "fig": fig,
        "title": clean(title),
        "creator": clean(creator),
        "date": clean(date),
        "attribution": clean(attribution),
        "medium": clean(medium),
        "dimensions": clean(dimensions),
        "edition": clean(edition),
        "line": line,
    }

    for key, value in FIGURE_OVERRIDES.get(fig, {}).items():
        entry[key] = value

    return entry


def default_subject(entry):
    if entry.get("subject"):
        return entry["subject"]
    title = entry["title"].lower()
    medium = entry["medium"].lower()
    if "photograph" in medium:
        return "Documentation"
    if "gelatin silver print" in medium:
        return "Photography"
    if "portrait" in title:
        return "Portraiture"
    if "landscape" in title:
        return "Landscape"
    if "mural" in title:
        return "Mural"
    if "ceramic" in medium:
        return "Ceramics"
    if "print" in medium or "woodcut" in medium or "etching" in medium or "lithograph" in medium or "engraving" in medium:
        return "Printmaking"
    return "Documentation" if entry["fig"] in TITLE_ONLY_FIGURES else ""


def default_type(entry):
    if "photograph" in entry["medium"].lower() or entry["fig"] in TITLE_ONLY_FIGURES:
        return "Documentation Image"
    return "Image;StillImage"


def format_for_file(file_name):
    suffix = Path(file_name).suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    return "image/png"


def accession_token(date_value):
    raw = clean(date_value)
    lowered = raw.lower()
    if not raw or lowered == "n.d.":
        return "2021"
    if "fifteenth century" in lowered:
        return "1400"
    match = re.search(r"(\d{4})", raw)
    if match:
        return match.group(1)
    return "2021"


def recompute_accessions(rows):
    counters = {}
    for row in rows:
        token = accession_token(row.get("date"))
        counters[token] = counters.get(token, 0) + 1
        row["accession_number"] = f"JSUART-{token}-{counters[token]:03d}"


def next_object_id(rows):
    max_id = max(int(row["objectid"].replace("coll", "")) for row in rows if row["objectid"].startswith("coll"))
    while True:
        max_id += 1
        yield f"coll{max_id:03d}"


def make_new_row(object_id, entry, thumb_name):
    return {
        "objectid": object_id,
        "accession_number": "",
        "filename": f"{THUMB_PREFIX}/{thumb_name}",
        "youtubeid": "",
        "vimeoid": "",
        "title": entry["title"],
        "creator": entry["creator"],
        "date": entry["date"],
        "attribution": entry["attribution"],
        "medium": entry["medium"],
        "dimensions": entry["dimensions"],
        "edition": entry["edition"],
        "description": "Documentation image or catalog figure included in the public-facing JSU art database.",
        "subject": default_subject(entry),
        "location": "",
        "latitude": "",
        "longitude": "",
        "source": SOURCE,
        "identifier": f"Fig. {entry['fig']}",
        "type": default_type(entry),
        "format": format_for_file(thumb_name),
        "language": "",
        "rights": RIGHTS,
        "rightsstatement": RIGHTS_STATEMENT,
    }


def update_existing_row(row, entry, thumb_name):
    overrides = FIGURE_OVERRIDES.get(entry["fig"], {})
    row["filename"] = f"{THUMB_PREFIX}/{thumb_name}"
    if entry["title"] or "title" in overrides:
        row["title"] = entry["title"]
    if entry["creator"] or "creator" in overrides:
        row["creator"] = entry["creator"]
    if entry["date"] or "date" in overrides:
        row["date"] = entry["date"]
    if entry["attribution"] or "attribution" in overrides:
        row["attribution"] = entry["attribution"]
    if entry["medium"] or "medium" in overrides:
        row["medium"] = entry["medium"]
    if entry["dimensions"] or "dimensions" in overrides:
        row["dimensions"] = entry["dimensions"]
    if entry["edition"] or "edition" in overrides:
        row["edition"] = entry["edition"]
    row["source"] = SOURCE
    row["identifier"] = f"Fig. {entry['fig']}"
    row["format"] = format_for_file(thumb_name)
    row["rights"] = RIGHTS
    row["rightsstatement"] = RIGHTS_STATEMENT
    if "subject" in overrides:
        row["subject"] = overrides["subject"]
    elif not clean(row.get("subject")):
        row["subject"] = default_subject(entry)


def main():
    rows = load_rows()
    by_id = {row["objectid"]: row for row in rows}
    by_identifier = {clean(row.get("identifier")): row for row in rows if clean(row.get("identifier"))}
    fieldnames = list(rows[0].keys())
    figure_lines = extract_figure_lines()
    file_map = load_file_map()
    object_id_source = next_object_id(rows)
    audit_rows = []

    for line in figure_lines:
        entry = parse_line(line)
        if not entry:
            continue
        fig = entry["fig"]
        file_name = file_map.get(fig)
        if not file_name:
            continue

        matched_id = FIGURE_TO_RECORD.get(fig)
        existing_by_identifier = by_identifier.get(f"Fig. {fig}")
        category = "context" if fig in TITLE_ONLY_FIGURES else "object"
        if matched_id and matched_id in by_id:
            update_existing_row(by_id[matched_id], entry, file_name)
            audit_rows.append({
                "fig": fig,
                "file": file_name,
                "objectid": matched_id,
                "action": "updated existing",
                "category": category,
                "title": entry["title"],
            })
            continue

        if existing_by_identifier:
            update_existing_row(existing_by_identifier, entry, file_name)
            audit_rows.append({
                "fig": fig,
                "file": file_name,
                "objectid": existing_by_identifier["objectid"],
                "action": "updated imported",
                "category": category,
                "title": entry["title"],
            })
            continue

        new_id = next(object_id_source)
        new_row = make_new_row(new_id, entry, file_name)
        rows.append(new_row)
        by_id[new_id] = new_row
        by_identifier[f"Fig. {fig}"] = new_row
        audit_rows.append({
            "fig": fig,
            "file": file_name,
            "objectid": new_id,
            "action": "added new",
            "category": category,
            "title": entry["title"],
        })

    recompute_accessions(rows)
    write_rows(rows, fieldnames)

    with AUDIT_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["fig", "file", "objectid", "action", "category", "title"])
        writer.writeheader()
        writer.writerows(audit_rows)

    print(f"Updated {len([r for r in audit_rows if r['action'] == 'updated existing'])} existing records")
    print(f"Added {len([r for r in audit_rows if r['action'] == 'added new'])} new records")
    print(f"Wrote audit to {AUDIT_PATH}")


if __name__ == "__main__":
    main()
