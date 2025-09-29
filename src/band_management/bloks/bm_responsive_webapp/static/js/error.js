(function () {
  document.body.addEventListener("htmx:responseError", function (event) {
    const error_banner = document.getElementById("error-message");
    const xhr = event.detail.xhr;
    const status = xhr.status;
    let message = `An error occurred (${status})`;

    try {
      const data = JSON.parse(xhr.responseText);
      if (data.message) {
        message = data.message;
      }
    } catch (e) {
      // no error
      message = "Something wrong happen";
    }


    error_banner.innerHTML = `
      <div class="notification is-danger">
        <button class="delete"></button>
        ${message}
      </div>
    `;
    error_banner.querySelector(".delete").addEventListener("click", () => {
      error_banner.innerHTML = "";
    });
  });

})();
