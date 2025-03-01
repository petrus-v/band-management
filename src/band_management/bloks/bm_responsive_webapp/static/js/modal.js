function openModal($el) {
    const $target = document.getElementById($el.dataset.target);
    $target.classList.add('is-active');
}

function closeModal($el) {
    const $target = document.getElementById($el.dataset.target);
    $target.classList.remove("is-active");
}
