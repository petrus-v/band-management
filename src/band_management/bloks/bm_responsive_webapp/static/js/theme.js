(function () {
  const dark = document.getElementById("btn-dark-mode");
  const light = document.getElementById("btn-light-mode");
  const body = document.querySelector("body");

  const ensure_theme = function (theme) {
    document.cookie =
      "theme=" + theme + "; SameSite=Strict; Secure; Max-Age: 3600";

    if (body.dataset.theme !== theme) {
      body.dataset.theme = theme;
      if (theme === "dark") {
        light.classList.remove("is-outlined");
        light.classList.add("is-light");
        dark.classList.add("is-outlined");
        dark.classList.remove("is-light");
      } else {
        dark.classList.remove("is-outlined");
        dark.classList.add("is-light");
        light.classList.add("is-outlined");
        light.classList.remove("is-light");
      }
    }
  };
  dark.addEventListener("click", () => ensure_theme("dark"));
  light.addEventListener("click", () => ensure_theme("light"));
  let systemTheme = "dark";
  if (window.matchMedia) {
    // Check if the dark-mode Media-Query matches
    if (window.matchMedia("(prefers-color-scheme: light)").matches) {
      systemTheme = "light";
    }

    window
      .matchMedia("(prefers-color-scheme: dark)")
      .addEventListener("change", (event) => {
        const newTheme = event.matches ? "dark" : "light";
        ensure_theme(newTheme);
      });
  }

  const cookieTheme = document.cookie
    .split("; ")
    .find((row) => row.startsWith("theme="))
  ?.split("=")[1];
  console.log("cookie theme", cookieTheme);
  if (cookieTheme) {
    ensure_theme(cookieTheme);
  } else {
    ensure_theme(systemTheme);
  }
})();
