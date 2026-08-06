const DATA_URL = "./site-data/artworks.json";
const gallery = document.querySelector("#gallery");
const resultsCount = document.querySelector("#results-count");
const searchInput = document.querySelector("#search-input");
const subjectFilter = document.querySelector("#subject-filter");
const sortSelect = document.querySelector("#sort-select");
const cardTemplate = document.querySelector("#card-template");
const detailDialog = document.querySelector("#detail-dialog");
const detailClose = document.querySelector("#detail-close");

let artworks = [];

async function loadArtworks() {
  const response = await fetch(DATA_URL);
  if (!response.ok) {
    throw new Error(`Unable to load collection data: ${response.status}`);
  }

  artworks = await response.json();
  populateSubjectFilter(artworks);
  renderStats(artworks);
  renderGallery(artworks);
}

function populateSubjectFilter(items) {
  const subjects = [...new Set(items.map((item) => item.subject).filter(Boolean))].sort();
  for (const subject of subjects) {
    const option = document.createElement("option");
    option.value = subject;
    option.textContent = subject;
    subjectFilter.append(option);
  }
}

function renderStats(items) {
  const creators = new Set(items.map((item) => item.creator).filter(Boolean));
  const subjects = new Set(items.map((item) => item.subject).filter(Boolean));
  document.querySelector("#artwork-count").textContent = items.length;
  document.querySelector("#creator-count").textContent = creators.size;
  document.querySelector("#subject-count").textContent = subjects.size;
}

function filterArtworks() {
  const query = searchInput.value.trim().toLowerCase();
  const subject = subjectFilter.value;
  const filtered = artworks.filter((item) => {
    if (subject && item.subject !== subject) {
      return false;
    }

    if (!query) {
      return true;
    }

    const haystack = [
      item.title,
      item.creator,
      item.subject,
      item.location,
      item.description,
    ]
      .join(" ")
      .toLowerCase();

    return haystack.includes(query);
  });

  renderGallery(sortArtworks(filtered));
}

function sortArtworks(items) {
  const sorted = [...items];
  const mode = sortSelect.value;

  sorted.sort((left, right) => {
    if (mode === "title-desc") {
      return compareText(right.title, left.title);
    }

    if (mode === "creator-asc") {
      return compareText(left.creator, right.creator) || compareText(left.title, right.title);
    }

    if (mode === "date-asc") {
      return compareNumber(parseYear(left.date), parseYear(right.date)) || compareText(left.title, right.title);
    }

    if (mode === "date-desc") {
      return compareNumber(parseYear(right.date), parseYear(left.date)) || compareText(left.title, right.title);
    }

    return compareText(left.title, right.title);
  });

  return sorted;
}

function renderGallery(items) {
  gallery.innerHTML = "";
  const fragment = document.createDocumentFragment();

  for (const item of items) {
    const card = cardTemplate.content.firstElementChild.cloneNode(true);
    const image = card.querySelector("img");
    image.src = item.image;
    image.alt = item.title ? `${item.title} by ${item.creator || "Unknown"}` : "Artwork from the JSU collection";

    card.querySelector(".card-kicker").textContent = item.subject || "Collection Work";
    card.querySelector("h3").textContent = item.title || "Untitled";
    card.querySelector(".card-creator").textContent = item.creator || "Creator unknown";
    card.querySelector(".card-description").textContent = item.description || "Description coming soon.";

    const meta = card.querySelector(".card-meta");
    meta.append(
      metaRow("Date", item.date || "Unknown"),
      metaRow("Location", item.location || "Unknown"),
      metaRow("Rights", item.rights || "JSU")
    );

    card.addEventListener("click", () => openDetail(item));
    card.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openDetail(item);
      }
    });

    fragment.append(card);
  }

  gallery.append(fragment);
  resultsCount.textContent = `${items.length} work${items.length === 1 ? "" : "s"} shown`;
}

function metaRow(label, value) {
  const wrapper = document.createElement("div");
  const dt = document.createElement("dt");
  const dd = document.createElement("dd");
  dt.textContent = label;
  dd.textContent = value;
  wrapper.append(dt, dd);
  return wrapper;
}

function openDetail(item) {
  document.querySelector("#detail-image").src = item.image;
  document.querySelector("#detail-image").alt = item.title || "Artwork detail";
  document.querySelector("#detail-subject").textContent = item.subject || "Collection Work";
  document.querySelector("#detail-title").textContent = item.title || "Untitled";
  document.querySelector("#detail-creator").textContent = item.creator || "Creator unknown";
  document.querySelector("#detail-description").textContent = item.description || "Description coming soon.";
  const detailCaption = document.querySelector("#detail-caption");
  if (item.catalogCaption) {
    detailCaption.hidden = false;
    detailCaption.textContent = item.catalogCaption;
  } else {
    detailCaption.hidden = true;
    detailCaption.textContent = "";
  }

  const meta = document.querySelector("#detail-meta");
  meta.innerHTML = "";
  meta.append(
    metaRow("Date", item.date || "Unknown"),
    metaRow("Location", item.location || "Unknown"),
    metaRow("Source", item.source || "JSU Permanent Collection"),
    metaRow("Type", item.type || "Still Image"),
    metaRow("Format", item.format || "Image"),
    metaRow("Rights", item.rights || "JSU"),
    metaRow("Rights Statement", item.rightsstatement || "All rights reserved.")
  );

  detailDialog.showModal();
}

function compareText(left = "", right = "") {
  return left.localeCompare(right, undefined, { sensitivity: "base" });
}

function compareNumber(left, right) {
  return left - right;
}

function parseYear(value = "") {
  const match = value.match(/\d{4}/);
  return match ? Number(match[0]) : Number.MAX_SAFE_INTEGER;
}

searchInput.addEventListener("input", filterArtworks);
subjectFilter.addEventListener("change", filterArtworks);
sortSelect.addEventListener("change", filterArtworks);
detailClose.addEventListener("click", () => detailDialog.close());
detailDialog.addEventListener("click", (event) => {
  const bounds = detailDialog.getBoundingClientRect();
  const inDialog =
    bounds.top <= event.clientY &&
    event.clientY <= bounds.top + bounds.height &&
    bounds.left <= event.clientX &&
    event.clientX <= bounds.left + bounds.width;
  if (!inDialog) {
    detailDialog.close();
  }
});

loadArtworks().catch((error) => {
  console.error(error);
  resultsCount.textContent = "The collection data could not be loaded.";
});
