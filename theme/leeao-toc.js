(() => {
  const main = document.querySelector("#mdbook-content main");
  if (!main) return;

  const title = main.querySelector(":scope > h1");
  const list = title?.nextElementSibling;
  if (!list || list.tagName !== "UL") return;

  const details = document.createElement("details");
  details.className = "leeao-page-toc";
  details.open = window.matchMedia("(min-width: 701px)").matches;

  const summary = document.createElement("summary");
  summary.textContent = `本页目录（${list.querySelectorAll("a").length}）`;
  details.append(summary, list);
  title.after(details);
})();
