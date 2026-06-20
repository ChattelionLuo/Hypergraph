function initDrawer() {
  const toggle = document.querySelector(".menu-toggle");
  const drawer = document.querySelector(".site-drawer");
  const closers = document.querySelectorAll("[data-close-drawer]");
  if (!toggle || !drawer) return;

  const setOpen = (open) => {
    document.body.classList.toggle("drawer-open", open);
    toggle.setAttribute("aria-expanded", String(open));
  };

  toggle.addEventListener("click", () => {
    setOpen(!document.body.classList.contains("drawer-open"));
  });
  closers.forEach((closer) => closer.addEventListener("click", () => setOpen(false)));
  drawer.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => setOpen(false)));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") setOpen(false);
  });
}

initDrawer();
