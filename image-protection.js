const protectedImageSelector = [
  ".featured-preview-frame img",
  ".card-media img",
  ".record-media-panel img",
].join(", ");

function isProtectedImage(target) {
  return target instanceof Element && Boolean(target.closest(protectedImageSelector));
}

document.addEventListener("contextmenu", (event) => {
  if (isProtectedImage(event.target)) {
    event.preventDefault();
  }
});

document.addEventListener("dragstart", (event) => {
  if (isProtectedImage(event.target)) {
    event.preventDefault();
  }
});
