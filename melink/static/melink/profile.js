(() => {
    const preview = document.querySelector(".profile-preview");
    for (const [inputId, selector, fallback] of [["display-name", ".profile-name", "Твоє ім’я"], ["short-bio", ".profile-job", ""], ["description", ".profile-description", ""]]) {
        const input = document.getElementById(inputId);
        const target = preview?.querySelector(selector);
        if (input && target) {
            const update = () => { target.textContent = input.value || fallback; };
            input.addEventListener("input", update);
            update();
        }
    }
    let photoUrl;
    document.getElementById("photo")?.addEventListener("change", event => {
        const file = event.target.files[0];
        if (!file || !preview) return;
        if (photoUrl) URL.revokeObjectURL(photoUrl);
        photoUrl = URL.createObjectURL(file);
        const image = document.createElement("img");
        image.className = "profile-avatar";
        image.alt = "Попередній перегляд фото";
        image.src = photoUrl;
        preview.querySelector(".profile-avatar").replaceWith(image);
    });
    document.querySelectorAll('input[name="theme"]').forEach(input => {
        input.addEventListener("change", () => { if (preview) preview.dataset.theme = input.value; });
    });
    document.getElementById("copy-link")?.addEventListener("click", async () => {
        const input = document.getElementById("public-url");
        const status = document.getElementById("copy-status");
        try {
            await navigator.clipboard.writeText(input.value);
            status.textContent = "Посилання скопійовано.";
        } catch {
            input.focus();
            input.select();
            status.textContent = "Натисни Ctrl+C або ⌘C, щоб скопіювати посилання.";
        }
    });
})();
