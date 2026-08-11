const DATA_URL = document.body.dataset.collectionDataUrl || "./site-data/artworks.json";
const COLLECTION_VARIANT = document.body.dataset.collectionVariant || "department";
const gallery = document.querySelector("#gallery");
const resultsCount = document.querySelector("#results-count");
const searchInput = document.querySelector("#search-input");
const subjectFilter = document.querySelector("#subject-filter");
const creatorFilter = document.querySelector("#creator-filter");
const sortSelect = document.querySelector("#sort-select");
const cardTemplate = document.querySelector("#card-template");
const emptyState = document.querySelector("#empty-state");
const featuredImage = document.querySelector("#featured-image");
const featuredPrev = document.querySelector("#featured-prev");
const featuredNext = document.querySelector("#featured-next");
const FEATURED_RECORD_IDS = [
  "coll005",
  "coll009",
  "coll016",
  "coll025",
  "coll038",
  "coll055",
  "coll076",
  "coll083",
];

let artworks = [];
let featuredWorks = [];
let featuredIndex = 0;
let featuredTimer = null;

function getBrowsableArtworks(items) {
  if (COLLECTION_VARIANT !== "department") {
    return items;
  }

  return items.filter((item) => item.type !== "Documentation Image");
}

function getFieldValue(item, fieldName) {
  return item?.[fieldName] || "";
}

function displayCreator(item) {
  if (COLLECTION_VARIANT === "african") {
    return item.creator || item.culture || item.objectType || "Maker or culture not recorded";
  }

  if (item.attribution && item.creator) {
    return `${item.attribution} ${item.creator}`;
  }

  return item.creator || "Creator unknown";
}

async function loadArtworks() {
  const response = await fetch(DATA_URL);
  if (!response.ok) {
    throw new Error(`Unable to load collection data: ${response.status}`);
  }

  artworks = getBrowsableArtworks(await response.json());
  renderStats(artworks);
  setupFeaturedWorks(artworks);

  if (subjectFilter && creatorFilter && sortSelect && gallery) {
    populateFilter(subjectFilter, artworks.map((item) => getFieldValue(item, subjectFilter.dataset.field || "subject")));
    populateFilter(creatorFilter, artworks.map((item) => getFieldValue(item, creatorFilter.dataset.field || "creator")));
    renderCollection();
  }
}

function setupFeaturedWorks(items) {
  if (!featuredImage) {
    return;
  }

  const itemsById = new Map(items.map((item) => [item.id, item]));
  const curated = FEATURED_RECORD_IDS
    .map((id) => itemsById.get(id))
    .filter((item) => item && (item.imageUrl || item.image));

  const fallback = items.filter((item) => item.imageUrl || item.image);

  featuredWorks = curated.length ? curated : fallback.slice(0, 8);

  if (!featuredWorks.length) {
    return;
  }

  renderFeaturedWork(featuredIndex);

  if (featuredPrev && featuredNext) {
    featuredPrev.addEventListener("click", () => {
      stepFeaturedWork(-1);
      restartFeaturedTimer();
    });

    featuredNext.addEventListener("click", () => {
      stepFeaturedWork(1);
      restartFeaturedTimer();
    });
  }

  restartFeaturedTimer();
}

function restartFeaturedTimer() {
  if (featuredTimer) {
    window.clearInterval(featuredTimer);
  }

  if (featuredWorks.length < 2) {
    return;
  }

  featuredTimer = window.setInterval(() => {
    stepFeaturedWork(1);
  }, 5500);
}

function stepFeaturedWork(direction) {
  if (!featuredWorks.length) {
    return;
  }

  featuredIndex = (featuredIndex + direction + featuredWorks.length) % featuredWorks.length;
  renderFeaturedWork(featuredIndex);
}

function renderFeaturedWork(index) {
  const item = featuredWorks[index];

  if (!item) {
    return;
  }

  featuredImage.src = item.imageUrl || item.image;
  featuredImage.alt = item.title
    ? `${item.title} by ${displayCreator(item)}`
    : "Featured work from the JSU collection";
  featuredImage.onerror = () => {
    featuredImage.src = "./assets/logo.png";
    featuredImage.alt = "JSU Department of Art logo placeholder";
  };
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
  const artworkCount = document.querySelector("#artwork-count");
  const creatorCount = document.querySelector("#creator-count");
  const subjectCount = document.querySelector("#subject-count");

  if (!artworkCount || !creatorCount || !subjectCount) {
    return;
  }

  const creators = new Set(items.map((item) => item.creator).filter(Boolean));
  const subjects = new Set(items.map((item) => item.subject).filter(Boolean));
  artworkCount.textContent = items.length;
  creatorCount.textContent = creators.size;
  subjectCount.textContent = subjects.size;
}

function renderCollection() {
  const filtered = sortArtworks(filterArtworks());
  renderGallery(filtered);
  emptyState.hidden = filtered.length !== 0;
  resultsCount.textContent =
    filtered.length === 0
      ? "0 records shown"
      : `${filtered.length} record${filtered.length === 1 ? "" : "s"} shown`;
}

function filterArtworks() {
  const query = searchInput.value.trim().toLowerCase();
  const primaryValue = subjectFilter.value;
  const secondaryValue = creatorFilter.value;
  const primaryField = subjectFilter.dataset.field || "subject";
  const secondaryField = creatorFilter.dataset.field || "creator";
  const queryFields =
    COLLECTION_VARIANT === "department"
      ? ["creator", "attribution"]
      : [
          "objectNumber",
          "title",
          "creator",
          "culture",
          "subject",
          "objectType",
          "materials",
          "location",
          "description",
          "identifier",
        ];

  return artworks.filter((item) => {
    if (primaryValue && getFieldValue(item, primaryField) !== primaryValue) {
      return false;
    }

    if (secondaryValue && getFieldValue(item, secondaryField) !== secondaryValue) {
      return false;
    }

    if (!query) {
      return true;
    }

    const haystack = queryFields
      .map((field) => item[field])
      .join(" ")
      .toLowerCase();

    return haystack.includes(query);
  });
}

function sortArtworks(items) {
  const sorted = [...items];
  const mode = sortSelect.value;
  const secondaryField = creatorFilter?.dataset.field || "creator";

  sorted.sort((left, right) => {
    if (mode === "title-desc") {
      return compareText(right.title, left.title);
    }

    if (mode === "secondary-asc") {
      return compareText(getFieldValue(left, secondaryField), getFieldValue(right, secondaryField))
        || compareText(left.title, right.title);
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
    const card = buildCard(
      item,
      COLLECTION_VARIANT === "african"
        ? {
            kicker: item.objectNumber || "African Art Record",
            description: item.description || "Description coming soon.",
            meta: [
              ["Date", item.date || "Not recorded"],
              ["Culture", item.culture || "Not recorded"],
              ["Place", item.location || "Not recorded"],
              ["Object Type", item.objectType || "Not recorded"],
            ],
          }
        : {
            kicker: item.objectNumber || "Collection Record",
            description: item.description || "Description coming soon.",
            meta: [
              ["Date", item.date || "Not recorded"],
              ["Medium", item.medium || "Not recorded"],
              ["Dimensions", item.dimensions || "Not recorded"],
              ["Location", item.location || "Not recorded"],
              ["Object Type", item.type || "Not recorded"],
            ],
          }
    );
    fragment.append(card);
  }

  gallery.append(fragment);
}

function buildCard(item, config) {
  const card = cardTemplate.content.firstElementChild.cloneNode(true);
  const cardLink = card.querySelector(".card-link");
  const image = card.querySelector("img");
  image.src = item.imageUrl || item.image;
  image.alt = item.title ? `${item.title} by ${displayCreator(item)}` : "Artwork from the JSU collection";
  image.addEventListener("error", () => {
    image.src = "./assets/logo.png";
    image.alt = "JSU Department of Art logo placeholder";
  });

  cardLink.href = item.recordPath;
  cardLink.setAttribute(
    "aria-label",
    `Open record for ${item.title || "Untitled"} by ${displayCreator(item)}`
  );

  card.querySelector(".card-kicker").textContent = config.kicker;
  card.querySelector("h3").textContent = item.title || "Untitled";
  card.querySelector(".card-creator").textContent = displayCreator(item);
  card.querySelector(".card-description").textContent = config.description;

  const meta = card.querySelector(".card-meta");
  for (const [label, value] of config.meta) {
    meta.append(metaRow(label, value));
  }

  return card;
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

if (searchInput && subjectFilter && creatorFilter && sortSelect) {
  searchInput.addEventListener("input", renderCollection);
  subjectFilter.addEventListener("change", renderCollection);
  creatorFilter.addEventListener("change", renderCollection);
  sortSelect.addEventListener("change", renderCollection);
}

loadArtworks().catch((error) => {
  console.error(error);
  if (resultsCount && emptyState) {
    resultsCount.textContent = "The collection data could not be loaded.";
    emptyState.hidden = false;
    emptyState.querySelector("h2").textContent = "Collection data is temporarily unavailable";
    emptyState.querySelector("p").textContent = "Please refresh the page or try again later.";
  }
});
