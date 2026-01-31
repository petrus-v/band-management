(function () {
    const uuidv7 = () => {
        return 'tttttttt-tttt-7xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            const r = Math.trunc(Math.random() * 16);
            const v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        }).replace(/^[t]{8}-[t]{4}/, function () {
            const unixtimestamp = Date.now().toString(16).padStart(12, '0');
            return unixtimestamp.slice(0, 8) + '-' + unixtimestamp.slice(8);
        });
    };

    const setupQuill = (element) => {
        const inputName = element.getAttribute('data-input');
        let hiddenInput;
        if (inputName) {
            hiddenInput = document.querySelector(`input[name="${inputName}"]`);
        } else {
            // For music comments, find the specific input for comments
            hiddenInput = element.parentElement.querySelector('input[name="event_music_comments"]');
        }

        const quill = new Quill(element, {
            theme: 'snow',
            modules: {
                toolbar: [
                    ['bold', 'italic', 'underline', 'strike'],
                    [{ 'list': 'ordered' }, { 'list': 'bullet' }],
                    ['clean']
                ]
            }
        });

        quill.on('text-change', () => {
            hiddenInput.value = quill.root.innerHTML;
        });
    };

    const removeMusic = (event) => {
        event.target.parentElement.parentElement.remove();
    };

    var deleteButtons = document.querySelectorAll(".remove-music");
    for (var i = 0; i < deleteButtons.length; i++) {
        deleteButtons[i].addEventListener("click", removeMusic);
    }

    const editors = document.querySelectorAll('.quill-editor');
    editors.forEach(setupQuill);

    const addButton = document.getElementById("add-music");
    addButton.addEventListener("click", (event) => {
        const music_uuid = document.getElementById('selected-music-uuid').value;
        const music_title = document.getElementById('music-search').value;
        if (!music_uuid || !music_title) {
            return;
        }
        const music_template = document.getElementById("music-template");
        const clone = music_template.content.cloneNode(true);

        clone.querySelector(".music-description").textContent = music_title;
        clone.querySelector(".music-uuid").value = music_uuid;
        clone.querySelector(".event-music-uuid").value = uuidv7();
        clone.querySelector(".remove-music").addEventListener("click", removeMusic);

        // Setup Quill for the newly added music comment
        const newEditor = clone.querySelector(".quill-editor");

        document.getElementById("musics-list").appendChild(clone);

        // Quill must be initialized AFTER it's in the DOM
        const addedElement = document.getElementById("musics-list").lastElementChild;
        setupQuill(addedElement.querySelector(".quill-editor"));

        event.preventDefault();
    });
})();