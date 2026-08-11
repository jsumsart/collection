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
const paginationTop = document.querySelector("#pagination-top");
const paginationBottom = document.querySelector("#pagination-bottom");
const paginationStatusTop = document.querySelector("#pagination-status-top");
const paginationStatusBottom = document.querySelector("#pagination-status-bottom");
const paginationPrevTop = document.querySelector("#pagination-prev-top");
const paginationPrevBottom = document.querySelector("#pagination-prev-bottom");
const paginationNextTop = document.querySelector("#pagination-next-top");
const paginationNextBottom = document.querySelector("#pagination-next-bottom");
const featuredImage = document.querySelector("#featured-image");
const featuredPrev = document.querySelector("#featured-prev");
const featuredNext = document.querySelector("#featured-next");
const PAGE_SIZE = COLLECTION_VARIANT === "african" ? 24 : 9999;
const FEATURED_RECORD_IDS = [
  "coll046",
  "coll016",
  "coll025",
  "coll038",
  "coll055",
  "coll076",
  "coll083"
];
const FEATURED_IMAGE_OVERRIDES = {
  coll005: "./assets/featured/coll005.png?v=20260811d",
  coll016: "./assets/featured/coll016.png?v=20260811d",
  coll025: "./assets/featured/coll025.png?v=20260811d",
  coll038: "./assets/featured/coll038.png?v=20260811d",
  coll046: "./assets/featured/coll046.png?v=20260811d",
  coll055: "./assets/featured/coll055.png?v=20260811d",
  coll076: "./assets/featured/coll076.png?v=20260811d",
  coll083: "./assets/featured/coll083.png?v=20260811d",
};
const UNKNOWN_CREATOR_LABEL = "Creator not presently known";
const AFRICAN_CULTURE_CAVEATS = [
  "attribution uncertain",
  "attribution probable",
  "probable attribution",
  "attribution tentative",
  "attribution high",
  "attribution probable but not documented",
  "attribution probable but cautious",
  "likely",
  "possibly",
  "tentative",
  "probable",
  "uncertain",
];

let artworks = [];
let featuredWorks = [];
let featuredIndex = 0;
let featuredTimer = null;
let currentPage = 1;

function normalizeCreatorName(value = "") {
  const creator = value.trim();

  if (creator.toLowerCase() === "unknown" || creator.toLowerCase() === "creator unknown") {
    return UNKNOWN_CREATOR_LABEL;
  }

  if (!creator.includes(",")) {
    return creator;
  }

  const parts = creator
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean);

  if (parts.length < 2) {
    return creator;
  }

  return `${parts.slice(1).join(" ")} ${parts[0]}`.replace(/\s+/g, " ").trim();
}

function getBrowsableArtworks(items) {
  if (COLLECTION_VARIANT !== "department") {
    return items;
  }

  return items.filter((item) => item.type !== "Documentation Image");
}

function getFieldValue(item, fieldName) {
  return item?.[fieldName] || "";
}

function normalizeAfricanCultureLabel(value = "") {
  if (COLLECTION_VARIANT !== "african") {
    return value;
  }

  let normalized = String(value || "").trim();

  if (!normalized) {
    return "";
  }

  normalized = normalized
    .replace(/\bDemocratic Republic of the Congo\b/gi, "")
    .replace(/\bnorthern Cameroon\b/gi, "")
    .replace(/\bcoastal Guinea region\b/gi, "")
    .replace(/\beastern Congo peoples\b/gi, "Lega peoples")
    .replace(/\beastern Central African peoples\b/gi, "Central African peoples")
    .replace(/\bWest Central African peoples\b/gi, "Central or West-Central African peoples")
    .replace(/\bWest-Central African peoples\b/gi, "Central or West-Central African peoples")
    .replace(/\bWest or Central African peoples\b/gi, "West or Central African peoples");

  normalized = normalized
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean)
    .filter((part) => {
      const lower = part.toLowerCase();
      return !AFRICAN_CULTURE_CAVEATS.some((phrase) => lower.includes(phrase));
    })[0] || normalized;

  normalized = normalized
    .replace(/\bor related .*$/i, "")
    .replace(/\bstyle\b/gi, "")
    .replace(/\bpeoples\b/gi, "peoples")
    .replace(/\s*-\s*/g, " ")
    .replace(/\s{2,}/g, " ")
    .trim();

  normalized = normalized.replace(/\s+or\s+$/i, "").trim();

  const cleanupMap = [
    [/^central or central or west central african peoples$/i, "Central or West-Central African peoples"],
    [/^central or west central african peoples$/i, "Central or West-Central African peoples"],
    [/^unidentified central or central or west central african peoples$/i, "Central or West-Central African peoples"],
    [/^unidentified west or central african peoples$/i, "West or Central African peoples"],
    [/^unidentified west african peoples$/i, "West African peoples"],
    [/^unidentified east or central african peoples$/i, "East or Central African peoples"],
    [/^unidentified african peoples$/i, "African peoples"],
    [/^central african$/i, "Central African peoples"],
    [/^west african$/i, "West African peoples"],
    [/^eastern congolese peoples$/i, "Lega"],
    [/^lega peoples$/i, "Lega"],
    [/^luba peoples$/i, "Luba"],
    [/^dan peoples$/i, "Dan"],
    [/^yoruba peoples$/i, "Yoruba"],
    [/^suku peoples$/i, "Suku"],
    [/^pende peoples$/i, "Pende"],
    [/^baule peoples$/i, "Baule"],
    [/^dan we$/i, "Dan or We"],
    [/^dan or we related peoples$/i, "Dan or We"],
    [/^songye or luba peoples$/i, "Songye or Luba"],
    [/^hemba or luba hemba$/i, "Hemba or Luba-Hemba"],
    [/^hemba or luba related peoples$/i, "Hemba or Luba"],
    [/^fon or ewe fon$/i, "Fon or Ewe-Fon"],
    [/^mbete or kota mbete$/i, "Mbete or Kota-Mbete"],
    [/^namji\/namchi or dowayo peoples$/i, "Namji/Namchi or Dowayo"],
    [/^baga\/nalu\/landuma$/i, "Baga/Nalu/Landuma"],
    [/^chokwe or pende related central african peoples$/i, "Chokwe or Pende"],
    [/^kete or kuba related peoples$/i, "Kete or Kuba"],
    [/^kuba or closely related kasai region group$/i, "Kuba"],
    [/^kuba or kuba influenced central african peoples$/i, "Kuba"],
    [/^kasai region or central african peoples$/i, "Kasai region or Central African"],
    [/^pende or central african$/i, "Pende or Central African"],
    [/^mangbetu or central african$/i, "Mangbetu or Central African"],
    [/^luba or central african$/i, "Luba or Central African"],
  ];

  for (const [pattern, replacement] of cleanupMap) {
    if (pattern.test(normalized)) {
      return replacement;
    }
  }

  return normalized;
}

function normalizeAfricanObjectTypeLabel(value = "") {
  if (COLLECTION_VARIANT !== "african") {
    return value;
  }

  const normalized = String(value || "")
    .split("/")
    .map((part) => part.trim())
    .filter(Boolean)[0] || "";

  const lower = normalized.toLowerCase();

  if (lower.includes("helmet mask")) {
    return "Helmet mask";
  }

  if (lower.includes("face mask")) {
    return "Face mask";
  }

  if (lower.includes("maskette")) {
    return "Maskette";
  }

  if (lower.includes("mask")) {
    return "Mask";
  }

  if (lower.includes("power figure")) {
    return "Power figure";
  }

  if (lower.includes("standing female figure") || lower.includes("standing figure")) {
    return "Standing figure";
  }

  if (lower.includes("female figure")) {
    return "Female figure";
  }

  if (lower.includes("mother-and-child") || lower.includes("maternity figure")) {
    return "Maternity figure";
  }

  if (lower.includes("ancestor figure")) {
    return "Ancestor figure";
  }

  if (lower.includes("reliquary")) {
    return "Reliquary figure";
  }

  if (lower.includes("staff")) {
    return "Staff";
  }

  if (lower.includes("spoon")) {
    return "Spoon";
  }

  if (lower.includes("headdress")) {
    return "Headdress";
  }

  if (lower.includes("figure")) {
    return "Figure";
  }

  return normalized.replace(/\s{2,}/g, " ").trim();
}

function normalizeFilterValue(fieldName, value = "") {
  if (COLLECTION_VARIANT !== "african") {
    return fieldName === "creator" ? normalizeCreatorName(value) : value;
  }

  if (fieldName === "culture") {
    return normalizeAfricanCultureLabel(value);
  }

  if (fieldName === "objectType") {
    return normalizeAfricanObjectTypeLabel(value);
  }

  if (fieldName === "creator") {
    return normalizeCreatorName(value);
  }

  return value;
}

function hasDisplayValue(value) {
  return Boolean(String(value || "").trim());
}

function displayCreator(item) {
  if (COLLECTION_VARIANT === "african") {
    return normalizeCreatorName(item.creator) || item.culture || item.objectType || "Maker or culture not recorded";
  }

  if (item.attribution && item.creator) {
    return `${item.attribution} ${normalizeCreatorName(item.creator)}`;
  }

  return normalizeCreatorName(item.creator) || UNKNOWN_CREATOR_LABEL;
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
    populateFilter(
      subjectFilter,
      artworks.map((item) => normalizeFilterValue(subjectFilter.dataset.field || "subject", getFieldValue(item, subjectFilter.dataset.field || "subject")))
    );
    populateFilter(
      creatorFilter,
      artworks.map((item) => normalizeFilterValue(creatorFilter.dataset.field || "creator", getFieldValue(item, creatorFilter.dataset.field || "creator")))
    );
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

  featuredImage.src = FEATURED_IMAGE_OVERRIDES[item.id] || item.imageUrl || item.image;
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
  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  currentPage = Math.min(currentPage, totalPages);
  const paginated = paginateArtworks(filtered, currentPage);
  renderGallery(paginated);
  updatePagination(filtered.length, totalPages);
  emptyState.hidden = filtered.length !== 0;
  resultsCount.textContent =
    "Use the search and filters above to refine the records displayed below.";
}

function paginateArtworks(items, page) {
  if (COLLECTION_VARIANT !== "african") {
    return items;
  }

  const start = (page - 1) * PAGE_SIZE;
  return items.slice(start, start + PAGE_SIZE);
}

function updatePagination(totalItems, totalPages) {
  if (COLLECTION_VARIANT !== "african" || !paginationTop || !paginationBottom) {
    return;
  }

  const shouldShow = totalItems > PAGE_SIZE;
  paginationTop.hidden = !shouldShow;
  paginationBottom.hidden = !shouldShow;

  if (!shouldShow) {
    return;
  }

  const statusText = `Page ${currentPage} of ${totalPages}`;
  paginationStatusTop.textContent = statusText;
  paginationStatusBottom.textContent = statusText;

  const atStart = currentPage <= 1;
  const atEnd = currentPage >= totalPages;
  paginationPrevTop.disabled = atStart;
  paginationPrevBottom.disabled = atStart;
  paginationNextTop.disabled = atEnd;
  paginationNextBottom.disabled = atEnd;
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
      const normalizedPrimary = normalizeFilterValue(primaryField, getFieldValue(item, primaryField));
      if (normalizedPrimary !== primaryValue) {
        return false;
      }
    }

    if (secondaryValue) {
      const creatorValue = normalizeFilterValue(secondaryField, getFieldValue(item, secondaryField));
      if (creatorValue !== secondaryValue) {
        return false;
      }
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

  function compareSecondary(left, right, descending = false) {
    const leftValue = normalizeFilterValue(secondaryField, getFieldValue(left, secondaryField));
    const rightValue = normalizeFilterValue(secondaryField, getFieldValue(right, secondaryField));
    const leftUnknown = !leftValue || leftValue === UNKNOWN_CREATOR_LABEL;
    const rightUnknown = !rightValue || rightValue === UNKNOWN_CREATOR_LABEL;

    if (leftUnknown !== rightUnknown) {
      return leftUnknown ? 1 : -1;
    }

    return descending
      ? compareText(rightValue, leftValue) || compareText(left.title, right.title)
      : compareText(leftValue, rightValue) || compareText(left.title, right.title);
  }

  sorted.sort((left, right) => {
    if (mode === "title-desc") {
      return compareText(right.title, left.title);
    }

    if (mode === "secondary-asc") {
      return compareSecondary(left, right, false);
    }

    if (mode === "secondary-desc") {
      return compareSecondary(left, right, true);
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
            meta: [
              item.culture || "",
              item.objectType || "",
              item.date || "",
            ],
          }
        : {
            kicker: item.objectNumber || "Collection Record",
            meta: [
              item.date || "",
              item.medium || "",
              item.location || "",
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
  const titleElement = card.querySelector("h3");
  const creatorElement = card.querySelector(".card-creator");
  const description = card.querySelector(".card-description");
  const meta = card.querySelector(".card-meta");
  image.src = item.imageUrl || item.image;
  image.alt = item.title ? `${item.title} by ${displayCreator(item)}` : "Artwork from the JSU collection";
  image.addEventListener("error", () => {
    image.src = "./assets/logo.png";
    image.alt = "JSU Department of Art logo placeholder";
  });

  if (COLLECTION_VARIANT === "african") {
    const staticCard = document.createElement("div");
    staticCard.className = "card-link card-link-static";
    while (cardLink.firstChild) {
      staticCard.append(cardLink.firstChild);
    }
    cardLink.replaceWith(staticCard);
  } else {
    cardLink.href = item.recordPath;
    cardLink.setAttribute(
      "aria-label",
      `Open record for ${item.title || "Untitled"} by ${displayCreator(item)}`
    );
  }

  card.querySelector(".card-kicker").textContent = config.kicker;
  titleElement.textContent = item.title || "Untitled";
  creatorElement.textContent = displayCreator(item);

  if (COLLECTION_VARIANT === "african") {
    if (hasDisplayValue(item.description)) {
      description.textContent = item.description;
    } else {
      description.remove();
    }

    const detailPairs = [
      ["Date", item.date],
      ["Culture / Community", item.culture],
      ["Object Type", item.objectType],
      ["Materials", item.materials],
      ["Geographic Location", item.location],
    ].filter(([, value]) => hasDisplayValue(value));

    if (detailPairs.length) {
      meta.innerHTML = detailPairs
        .map(
          ([label, value]) => `
            <div>
              <dt>${escapeHtml(label)}</dt>
              <dd>${escapeHtml(value)}</dd>
            </div>
          `
        )
        .join("");
    } else {
      meta.remove();
    }
  } else {
    description.remove();

    const compactMeta = config.meta.filter(hasDisplayValue);

    if (compactMeta.length) {
      const summary = document.createElement("p");
      summary.className = "card-summary";
      summary.textContent = compactMeta.join(" | ");
      meta.replaceWith(summary);
    } else {
      meta.remove();
    }
  }

  return card;
}

function setPage(page) {
  currentPage = Math.max(1, page);
  renderCollection();
  window.scrollTo({ top: 0, behavior: "smooth" });
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
  searchInput.addEventListener("input", () => {
    currentPage = 1;
    renderCollection();
  });
  subjectFilter.addEventListener("change", () => {
    currentPage = 1;
    renderCollection();
  });
  creatorFilter.addEventListener("change", () => {
    currentPage = 1;
    renderCollection();
  });
  sortSelect.addEventListener("change", () => {
    currentPage = 1;
    renderCollection();
  });
}

if (COLLECTION_VARIANT === "african") {
  paginationPrevTop?.addEventListener("click", () => setPage(currentPage - 1));
  paginationPrevBottom?.addEventListener("click", () => setPage(currentPage - 1));
  paginationNextTop?.addEventListener("click", () => setPage(currentPage + 1));
  paginationNextBottom?.addEventListener("click", () => setPage(currentPage + 1));
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
