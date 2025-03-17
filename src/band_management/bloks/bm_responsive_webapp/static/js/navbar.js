// The following code is based off a toggle menu by @Bradcomp
// source: https://gist.github.com/Bradcomp/a9ef2ef322a8e8017443b626208999c1
(function () {
  // side bar
  const sidebar = document.getElementById("sideBarMenuLeft");
  const overlay = document.querySelector(".overlay");
  const sidebarBtn = document.querySelector("#aside-burger");

  sidebarBtn.addEventListener("click", function () {
    sidebar.classList.toggle("active");
    overlay.classList.toggle("active");
  });

  overlay.addEventListener("click", function () {
    sidebar.classList.remove("active");
    overlay.classList.remove("active");
  });

  // navbar
  var burger = document.querySelector("#top-burger");
  var menu = document.querySelector("#" + burger.dataset.target);
  const header = document.querySelector("body > header");
  const footer = document.querySelector("body > footer");
  const mainContainer = document.querySelector("#main-container");
  const setMainContainerMarginHeight = function () {
    mainContainer.style.marginTop =
      header.firstElementChild.clientHeight + 10 + "px";
    if (footer && footer.firstElementChild) {
      mainContainer.style.marginBottom =
        footer.firstElementChild.clientHeight + 10 + "px";
    }
  };
  burger.addEventListener("click", function () {
    burger.classList.toggle("is-active");
    menu.classList.toggle("is-active");
    setMainContainerMarginHeight();
  });
  setMainContainerMarginHeight();
})();
