const params = new URLSearchParams(window.location.search);
const focusedDirection = params.get("direction");
const directionIds = [...document.querySelectorAll("[data-design-direction]")]
  .map((element) => element.getAttribute("data-design-direction"));

if (focusedDirection && directionIds.includes(focusedDirection)) {
  document.body.dataset.focusDirection = focusedDirection;
  document.body.classList.add("is-focus-mode");
  document
    .querySelector(`[data-design-direction="${CSS.escape(focusedDirection)}"]`)
    ?.classList.add("is-focused");
}

const updateCurrentDirection = () => {
  const target = document.body.dataset.focusDirection || window.location.hash.slice(1);
  document.querySelectorAll(".direction-index a").forEach((link) => {
    const isCurrent = link.getAttribute("href") === `#${target}`;
    if (isCurrent) {
      link.setAttribute("aria-current", "true");
    } else {
      link.removeAttribute("aria-current");
    }
  });
};

window.addEventListener("hashchange", updateCurrentDirection);
updateCurrentDirection();
