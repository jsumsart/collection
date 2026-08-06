import csv
import json
from pathlib import Path


SOURCE = Path("_data/jsuart_metadata.csv")
OUTPUT = Path("site-data/artworks.json")

CATALOG_CAPTIONS = {
    "coll003": "Karl Griffin, Juanita, n.d. Oil on canvas, 31.5 x 23.5 in.",
    "coll004": "Thomas E. Eloby II, Self-Portrait, 1968. Ink on paper, 6.25 x 8.25 in.",
    "coll005": "Thomas E. Eloby II, Landscape, n.d. Oil on canvas, 36 x 24 in.",
    "coll008": "Brockford Gordon, Kneeling Football Player, n.d. Photograph on foam board.",
    "coll010": "Ronald O. Schnell, Landscape with a Bridge, n.d. Oil on canvas, 44 x 42 in.",
    "coll021": "Eli Kobeli, Musicians, n.d. Chalk on paper, 36 x 22.5 in.",
    "coll024": "Cliff Johnson, Haunted House, 1966. Medium unknown, 17 x 22.5 in.",
    "coll025": "Edward Colker, Sign and Symbol, 1967. Lithograph in color, ed. 106/210.",
    "coll030": "Anderson Macklin, Abstract Landscape, n.d. Oil on canvas, 23.5 x 36 in.",
    "coll033": "Floyd Willis Coleman, Study #17, c. 1970s.",
    "coll036": "William Majors, Burning Bush, 1967. Etching in sepia, ed. 72/110.",
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
}


def clean(value):
    return " ".join((value or "").split())


def main():
    rows = []
    with SOURCE.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            filename = clean(row.get("filename"))
            image = f"./objects/{filename}" if filename else "./assets/logo.png"
            rows.append(
                {
                    "id": clean(row.get("objectid")),
                    "title": clean(row.get("title")),
                    "creator": clean(row.get("creator")),
                    "date": clean(row.get("date")),
                    "description": clean(row.get("description")),
                    "subject": clean(row.get("subject")),
                    "location": clean(row.get("location")),
                    "source": clean(row.get("source")),
                    "type": clean(row.get("type")),
                    "format": clean(row.get("format")),
                    "rights": clean(row.get("rights")),
                    "rightsstatement": clean(row.get("rightsstatement")),
                    "catalogCaption": CATALOG_CAPTIONS.get(clean(row.get("objectid")), ""),
                    "image": image,
                }
            )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(rows, indent=2, ensure_ascii=True) + "\n")
    print(f"Wrote {len(rows)} records to {OUTPUT}")


if __name__ == "__main__":
    main()
