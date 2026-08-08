const DATA_URL = "./site-data/artworks.json";
const gallery = document.querySelector("#gallery");
const catalogBody = document.querySelector("#catalog-body");
const resultsCount = document.querySelector("#results-count");
const searchInput = document.querySelector("#search-input");
const subjectFilter = document.querySelector("#subject-filter");
const creatorFilter = document.querySelector("#creator-filter");
const sortSelect = document.querySelector("#sort-select");
const cardTemplate = document.querySelector("#card-template");
const emptyState = document.querySelector("#empty-state");

let artworks = [];

async function loadArtworks() {
  const response = await fetch(DATA_URL);
  if (!response.ok) {
    throw new Error(`Unable to load collection data: ${response.status}`);
  }

  artworks = await response.json();
  populateFilter(subjectFilter, artworks.map((item) => item.subject));
  populateFilter(creatorFilter, artworks.map((item) => item.creator));
  renderStats(artworks);
  renderCollection();
}

function populateFilter(select, values) {
  const items = [...new Set(values.filter(Boolean))].sort((left, right) =>
    left.localeCompare(right, undefined, { sensitivity: "base" })
  );

  for (const item of items) {
    const option = document.createElement("option");
    option.value = item;
    option.textContent = item;
    select.append(option);
  }
}

function renderStats(items) {
  const creators = new Set(items.map((item) => item.creator).filter(Boolean));
  const subjects = new Set(items.map((item) => item.subject).filter(Boolean));
  document.querySelector("#artwork-count").textContent = items.length;
  document.querySelector("#creator-count").textContent = creators.size;
  document.querySelector("#subject-count").textContent = subjects.size;
}

function renderCollection() {
  const filtered = sortArtworks(filterArtworks());
  renderGallery(filtered);
  renderTable(filtered);
  emptyState.hidden = filtered.length !== 0;
  resultsCount.textContent =
    filtered.length === 0
      ? "0 records shown"
      : `${filtered.length} record${filtered.length === 1 ? "" : "s"} shown`;
}

function filterArtworks() {
  const query = searchInput.value.trim().toLowerCase();
  const subject = subjectFilter.value;
  const creator = creatorFilter.value;

  return artworks.filter((item) => {
    if (subject && item.subject !== subject) {
      return false;
    }

    if (creator && item.creator !== creator) {
      return false;
    }

    if (!query) {
      return true;
    }

    const haystack = [
      item.objectNumber,
      item.title,
      item.creator,
      item.subject,
      item.location,
      item.description,
      item.identifier,
    ]
      .join(" ")
      .toLowerCase();

    return haystack.includes(query);
  });
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
    const cardLink = card.querySelector(".card-link");
    const image = card.querySelector("img");
    image.src = item.image;
    image.alt = item.title ? `${item.title} by ${item.creator || "Unknown"}` : "Artwork from the JSU collection";
    image.addEventListener("error", () => {
      image.src = "./assets/logo.png";
      image.alt = "JSU Department of Art logo placeholder";
    });

    cardLink.href = item.recordPath;
    cardLink.setAttribute(
      "aria-label",
      `Open record for ${item.title || "Untitled"} by ${item.creator || "Unknown creator"}`
    );

    card.querySelector(".card-kicker").textContent = item.objectNumber || "Collection Record";
    card.querySelector("h3").textContent = item.title || "Untitled";
    card.querySelector(".card-creator").textContent = item.creator || "Creator unknown";
    card.querySelector(".card-description").textContent = item.description || "Description coming soon.";

    const meta = card.querySelector(".card-meta");
    meta.append(
      metaRow("Date", item.date || "Not recorded"),
      metaRow("Subject", item.subject || "Not recorded"),
      metaRow("Location", item.location || "Not recorded"),
      metaRow("Rights", item.rights || "Not recorded")
    );

    fragment.append(card);
  }

  gallery.append(fragment);
}

function renderTable(items) {
  catalogBody.innerHTML = "";
  const fragment = document.createDocumentFragment();

  for (const item of items) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${escapeHtml(item.objectNumber || "Not recorded")}</td>
      <td><a class="record-table-link" href="${escapeHtml(item.recordPath)}">${escapeHtml(item.title || "Untitled")}</a></td>
      <td>${escapeHtml(item.creator || "Creator unknown")}</td>
      <td>${escapeHtml(item.date || "Not recorded")}</td>
      <td>${escapeHtml(item.subject || "Not recorded")}</td>
      <td>${escapeHtml(item.location || "Not recorded")}</td>
    `;
    fragment.append(row);
  }

  catalogBody.append(fragment);
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

function escapeHtml(value = "") {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

searchInput.addEventListener("input", renderCollection);
subjectFilter.addEventListener("change", renderCollection);
creatorFilter.addEventListener("change", renderCollection);
sortSelect.addEventListener("change", renderCollection);

loadArtworks().catch((error) => {
  console.error(error);
  resultsCount.textContent = "The collection data could not be loaded.";
  emptyState.hidden = false;
  emptyState.querySelector("h2").textContent = "Collection data is temporarily unavailable";
  emptyState.querySelector("p").textContent = "Please refresh the page or try again later.";
});
