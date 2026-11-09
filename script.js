(() => {
  "use strict";

  const form = document.getElementById("form");
  const input = document.getElementById("name");
  const errorEl = document.getElementById("error");
  const revealBtn = document.getElementById("reveal");
  const resultEl = document.getElementById("result");
  const greetingEl = document.getElementById("greeting");
  const messageEl = document.getElementById("message");
  const signatureEl = document.getElementById("signature");
  const anotherBtn = document.getElementById("another");
  const shareBtn = document.getElementById("share");
  const toastEl = document.getElementById("toast");

  const NAME_RE = /^\p{L}+(?:[ '’-]\p{L}+)*$/u;
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  let lastId = null;
  let current = null;
  let busy = false;
  let toastTimer = null;

  function validate(raw) {
    const name = raw.trim().replace(/\s+/g, " ");
    if (!name) return { error: "Entre ton prénom pour continuer." };
    if (name.length > 30) return { error: "Ton prénom ne doit pas dépasser 30 caractères." };
    if (!NAME_RE.test(name)) return { error: "Utilise seulement des lettres, espaces, tirets ou apostrophes." };
    return { name };
  }

  function showError(text) {
    errorEl.textContent = text;
    errorEl.hidden = false;
    input.setAttribute("aria-invalid", "true");
  }

  function clearError() {
    errorEl.hidden = true;
    errorEl.textContent = "";
    input.removeAttribute("aria-invalid");
  }

  function setBusy(state) {
    busy = state;
    revealBtn.disabled = state;
    anotherBtn.disabled = state;
  }

  function toast(text) {
    toastEl.textContent = text;
    toastEl.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove("show"), 2200);
  }

  async function requestMessage(name) {
    const res = await fetch("/api/message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, last: lastId }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || "Une erreur est survenue. Réessaie.");
    return data;
  }

  function render(data, firstTime) {
    greetingEl.textContent = data.greeting;
    messageEl.textContent = data.text;
    signatureEl.textContent = data.signature;
    resultEl.hidden = false;
    resultEl.classList.remove("revealed");
    void resultEl.offsetWidth; // relance l'animation
    resultEl.classList.add("revealed");
    if (firstTime) {
      resultEl.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
    }
  }

  async function load() {
    if (busy) return;
    const check = validate(input.value);
    if (check.error) {
      showError(check.error);
      input.focus();
      return;
    }
    clearError();
    setBusy(true);
    try {
      const firstTime = current === null;
      const data = await requestMessage(check.name);
      lastId = data.id;
      current = data;
      render(data, firstTime);
    } catch (err) {
      showError(err.message || "Impossible de contacter le serveur. Réessaie.");
    } finally {
      setBusy(false);
    }
  }

  async function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return;
    }
    const area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    document.execCommand("copy");
    area.remove();
  }

  async function share() {
    if (!current) return;
    const text = `${current.greeting}\n\n« ${current.text} »\n\n${current.signature}`;
    const url = window.location.origin;
    try {
      if (navigator.share) {
        await navigator.share({ title: "Riche’b te salue", text, url });
        return;
      }
      await copyText(`${text}\n${url}`);
      toast("Message copié, prêt à être partagé");
    } catch (err) {
      if (err && err.name === "AbortError") return; // partage annulé
      toast("Partage impossible");
    }
  }

  form.addEventListener("submit", (e) => { e.preventDefault(); load(); });
  anotherBtn.addEventListener("click", load);
  shareBtn.addEventListener("click", share);
  input.addEventListener("input", clearError);
})();
