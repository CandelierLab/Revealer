document.addEventListener("DOMContentLoaded", () => {
  const currentPage = document.querySelector(".sidebar-tree .current-page");
  const tocRoot = document.querySelector(".toc-tree > ul > li:first-child > ul");

  if (currentPage && tocRoot && tocRoot.children.length) {
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "toctree-checkbox";
    checkbox.id = "revealer-current-page-sections";
    checkbox.checked = true;

    const label = document.createElement("label");
    label.setAttribute("for", checkbox.id);
    label.setAttribute("aria-label", "Toggle page sections");
    label.innerHTML = '<span class="icon"><svg><use href="#svg-arrow-right"></use></svg></span>';

    const clonedToc = tocRoot.cloneNode(true);
    clonedToc.classList.add("revealer-sidebar-sections");

    currentPage.classList.add("has-children", "revealer-current-page");
    currentPage.appendChild(checkbox);
    currentPage.appendChild(label);
    currentPage.appendChild(clonedToc);
  }
});
