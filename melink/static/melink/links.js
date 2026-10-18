(() => {
    const editor = document.querySelector('.links-editor');
    if (!editor) return;
    const list = editor.querySelector('.links-list');
    const add = editor.querySelector('.add-link-button');
    const preview = editor.querySelector('.social-links');
    const template = list.querySelector('.link-card').cloneNode(true);
    const status = document.getElementById('links-status');
    let next = Math.max(...Array.from(list.querySelectorAll('input[type="text"]'), input => Number(input.name.split('_')[1]))) + 1;
    const iconFor = value => {
        try {
            const host = new URL(value).hostname.replace(/^www\./, '');
            const sites = {'github.com': 'github', 'instagram.com': 'instagram', 't.me': 'telegram', 'telegram.me': 'telegram', 'youtube.com': 'youtube', 'youtu.be': 'youtube', 'linkedin.com': 'linkedin', 'facebook.com': 'facebook', 'x.com': 'x', 'twitter.com': 'x', 'tiktok.com': 'tiktok', 'wa.me': 'whatsapp'};
            return sites[host] || 'website';
        } catch { return 'website'; }
    };
    const update = () => {
        preview.replaceChildren();
        list.querySelectorAll('.link-card').forEach(card => {
            const title = card.querySelector('input[type="text"]').value.trim();
            const url = card.querySelector('input[type="url"]').value.trim();
            const icon = editor.dataset.iconBase + iconFor(url) + '.svg';
            card.querySelector('.link-icon').src = icon;
            if (!card.querySelector('input[type="checkbox"]').checked || !title || !url) return;
            let parsed;
            try { parsed = new URL(url); } catch { return; }
            if (!['http:', 'https:'].includes(parsed.protocol)) return;
            const anchor = document.createElement('a');
            anchor.href = url;
            anchor.target = '_blank';
            anchor.rel = 'noopener noreferrer';
            const image = document.createElement('img');
            image.src = icon;
            image.alt = '';
            const label = document.createElement('b');
            label.textContent = title;
            const arrow = document.createElement('span');
            arrow.textContent = '↗';
            arrow.setAttribute('aria-hidden', 'true');
            anchor.append(image, label, arrow);
            preview.append(anchor);
        });
        if (!preview.children.length) {
            const empty = document.createElement('p');
            empty.className = 'empty-links';
            empty.textContent = 'Посилань поки немає.';
            preview.append(empty);
        }
        add.disabled = list.children.length >= 20;
    };
    list.addEventListener('input', update);
    list.addEventListener('change', update);
    list.addEventListener('click', event => {
        const button = event.target.closest('.icon-button');
        if (!button) return;
        const card = button.closest('.link-card');
        const focusTarget = card.nextElementSibling?.querySelector('input') || card.previousElementSibling?.querySelector('input') || add;
        card.remove();
        update();
        focusTarget.focus();
        status.textContent = 'Посилання видалено. Натисни «Продовжити», щоб зберегти зміни.';
    });
    add.addEventListener('click', () => {
        if (list.children.length >= 20) return;
        const card = template.cloneNode(true);
        for (const input of card.querySelectorAll('input')) {
            const field = input.name.split('_').pop();
            input.name = `link_${next}_${field}`;
            if (input.type === 'checkbox') input.checked = true;
            else {
                input.value = '';
                input.id = `link-${next}-${field}`;
                card.querySelector(`label[for$="-${field}"]`).htmlFor = input.id;
            }
        }
        next += 1;
        list.append(card);
        update();
        card.querySelector('input').focus();
        status.textContent = 'Додано нове посилання.';
    });
    update();
})();
