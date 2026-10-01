const i18n = {
    en: { nav_home: "Home", nav_queue: "Live Queue Monitor" },
    hi: { nav_home: "मुख्य पृष्ठ", nav_queue: "लाइव कतार मॉनिटर" },
    gu: { nav_home: "મુખ્ય પૃષ્ઠ", nav_queue: "લાઈવ કતાર મોનિટર" }
};

function changeLanguage(lang) {
    const dict = i18n[lang] || i18n.en;
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (dict[key]) el.textContent = dict[key];
    });
}

function toggleLowBandwidth() {
    document.body.classList.toggle('low-bandwidth');
    const label = document.getElementById('bw-label');
    if (document.body.classList.contains('low-bandwidth')) {
        label.textContent = "Low-BW (Active)";
    } else {
        label.textContent = "Low-BW Mode";
    }
}

