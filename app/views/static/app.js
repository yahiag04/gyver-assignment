const $ = (selector) => document.querySelector(selector);
const state = { offers: [], ads: [], selectedAd: null, selectedVariantId: null };
const channelLabels = { indeed: "Indeed", whatsapp: "WhatsApp", instagram: "Instagram", tiktok: "TikTok" };
const formatLabels = { text: "Solo testo", image: "Solo immagine", image_text: "Immagine e testo" };
const statusLabels = { draft: "Bozza", ready: "Pronto", published: "Pubblicato", archived: "Archiviato" };
const channelFieldNames = ["experience", "employment_type", "schedule", "application_url"];
let listRequestSequence = 0;

function notify(message, kind = "info") {
  const notice = $("#notice");
  notice.textContent = message;
  notice.dataset.kind = kind;
}

async function api(path, options = {}) {
  const isFormData = options.body instanceof FormData;
  const response = await fetch(path, {
    ...options,
    headers: { ...(options.body && !isFormData ? { "Content-Type": "application/json" } : {}), ...options.headers },
  });
  let data = null;
  if (response.status !== 204) {
    try { data = await response.json(); } catch { data = null; }
  }
  if (!response.ok) {
    const detail = data?.detail;
    const message = Array.isArray(detail) ? detail.map((item) => item.msg).join(" · ") : detail;
    throw new Error(message || `Richiesta non riuscita (${response.status})`);
  }
  return data;
}

function option(value, label) {
  const node = document.createElement("option");
  node.value = value;
  node.textContent = label;
  return node;
}

function populateOffers() {
  const createSelect = $("#create-offer");
  const filterSelect = $("#filter-offer");
  createSelect.replaceChildren();
  filterSelect.replaceChildren(option("", "Tutte le offerte"));
  for (const offer of state.offers) {
    const label = `${offer.title} · ${offer.company_name}`;
    createSelect.append(option(offer.id, label));
    filterSelect.append(option(offer.id, label));
  }
}

function textElement(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  element.textContent = text;
  return element;
}

function renderAds() {
  const list = $("#ads-list");
  list.replaceChildren();
  $("#ads-count").textContent = String(state.ads.length);
  if (!state.ads.length) {
    list.append(textElement("p", "empty-list", "Nessun annuncio con questi filtri."));
    $("#detail").hidden = true;
    $("#empty-detail").hidden = false;
    state.selectedAd = null;
    return;
  }
  for (const ad of state.ads) {
    const title = ad.variants[0]?.title || channelLabels[ad.channel] || "Annuncio";
    const offer = state.offers.find((item) => item.id === ad.job_offer_id);
    const button = document.createElement("button");
    button.type = "button";
    button.className = "ad-card";
    button.setAttribute("aria-current", String(state.selectedAd?.id === ad.id));
    button.append(
      textElement("span", "ad-card-title", title),
      textElement("span", "ad-card-meta", `${channelLabels[ad.channel] || ad.channel} · ${formatLabels[ad.format] || ad.format}`),
      textElement("span", "ad-card-location", offer ? `${offer.title} · ${offer.company_name}` : ad.job_offer_id),
      textElement("span", "ad-card-location", ad.location),
      textElement("span", `status-pill status-${ad.status}`, statusLabels[ad.status] || ad.status),
    );
    button.addEventListener("click", () => selectAd(ad.id));
    list.append(button);
  }
}

function renderBadges(ad) {
  const badges = $("#ad-badges");
  badges.replaceChildren();
  for (const label of [channelLabels[ad.channel], formatLabels[ad.format], statusLabels[ad.status]]) {
    badges.append(textElement("span", "badge", label || ""));
  }
}

function activeVariant() {
  return state.selectedAd?.variants.find((variant) => variant.id === state.selectedVariantId) || null;
}

function renderVariantEditor(ad) {
  const variant = activeVariant();
  const form = $("#variant-form");
  const list = $("#variants-list");
  list.replaceChildren();
  for (const item of ad.variants) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "variant-tab";
    button.setAttribute("aria-pressed", String(item.id === state.selectedVariantId));
    button.append(
      textElement("span", "variant-tab-name", item.variant_name),
      textElement("span", "variant-tab-origin", item.origin === "llm" ? "Generata" : "Manuale"),
    );
    button.addEventListener("click", () => {
      state.selectedVariantId = item.id;
      renderDetail(ad);
    });
    list.append(button);
  }
  if (!variant) {
    form.hidden = true;
    return;
  }

  form.hidden = false;
  $("#variant-editor-title").textContent = variant.variant_name;
  $("#variant-origin").textContent = variant.origin === "llm"
    ? "Contenuto generato · puoi modificarlo" : "Contenuto modificato manualmente";
  form.elements.namedItem("variant_name").value = variant.variant_name;
  form.elements.namedItem("title").value = variant.title;
  form.elements.namedItem("body_text").value = variant.body_text || "";
  form.elements.namedItem("requirements").value = (variant.requirements || []).join("\n");
  form.elements.namedItem("compensation").value = variant.compensation || "";
  form.elements.namedItem("creative_text").value = variant.creative_text || "";
  form.elements.namedItem("creative_brief").value = variant.creative_brief || "";
  for (const field of channelFieldNames) {
    form.elements.namedItem(`field_${field}`).value = variant.channel_fields?.[field] || "";
  }
  const imageOnly = ad.format === "image";
  const hasCreative = imageOnly || ad.format === "image_text";
  $("#body-field").hidden = imageOnly;
  $("#creative-fields").hidden = !hasCreative;
  $("#image-asset").hidden = !hasCreative;
  const imagePreview = $("#creative-image");
  imagePreview.hidden = !variant.image_path;
  if (variant.image_path) imagePreview.src = variant.image_path;
  else imagePreview.removeAttribute("src");
  form.elements.namedItem("image_file").value = "";
  form.elements.namedItem("body_text").required = !imageOnly;
  form.elements.namedItem("creative_text").required = hasCreative;
  form.elements.namedItem("creative_brief").required = hasCreative;
}

function renderDetail(ad) {
  state.selectedAd = ad;
  $("#detail").hidden = false;
  $("#empty-detail").hidden = true;
  $("#detail-title").textContent = activeVariant()?.title || ad.variants[0]?.title || "Annuncio";
  renderBadges(ad);
  const offer = state.offers.find((item) => item.id === ad.job_offer_id);
  $("#detail-offer").textContent = offer ? `${offer.title} · ${offer.company_name}` : ad.job_offer_id;
  $("#metadata-form").elements.namedItem("location").value = ad.location;
  $("#metadata-form").elements.namedItem("status").value = ad.status;
  renderVariantEditor(ad);
  renderAds();
}

async function selectAd(adId) {
  try {
    const ad = await api(`/api/ads/${encodeURIComponent(adId)}`);
    state.selectedVariantId = ad.variants[0]?.id || null;
    renderDetail(ad);
    notify("Annuncio caricato.");
  } catch (error) {
    notify(error.message, "error");
  }
}

async function loadAds() {
  const sequence = ++listRequestSequence;
  const params = new URLSearchParams();
  const offerId = $("#filter-offer").value;
  const channel = $("#filter-channel").value;
  if (offerId) params.set("job_offer_id", offerId);
  if (channel) params.set("channel", channel);
  try {
    const suffix = params.size ? `?${params.toString()}` : "";
    const ads = await api(`/api/ads${suffix}`);
    if (sequence !== listRequestSequence) return;
    state.ads = ads;
    const selectedIsVisible = state.selectedAd && ads.some((ad) => ad.id === state.selectedAd.id);
    if (selectedIsVisible) {
      const fresh = await api(`/api/ads/${encodeURIComponent(state.selectedAd.id)}`);
      if (sequence !== listRequestSequence) return;
      state.selectedVariantId = fresh.variants.some((variant) => variant.id === state.selectedVariantId)
        ? state.selectedVariantId : fresh.variants[0]?.id || null;
      renderDetail(fresh);
    } else {
      state.selectedAd = null;
      $("#detail").hidden = true;
      $("#empty-detail").hidden = false;
    }
    renderAds();
  } catch (error) {
    if (sequence === listRequestSequence) notify(error.message, "error");
  }
}

function formValues(form) {
  return Object.fromEntries(new FormData(form).entries());
}

function equalValue(left, right) {
  if (left && right && typeof left === "object" && typeof right === "object") {
    const leftKeys = Object.keys(left).sort();
    const rightKeys = Object.keys(right).sort();
    return leftKeys.length === rightKeys.length
      && leftKeys.every((key, index) => key === rightKeys[index] && equalValue(left[key], right[key]));
  }
  return left === right;
}

$("#create-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const button = form.querySelector("button[type=submit]");
  button.disabled = true;
  notify("Generazione in corso…");
  try {
    const values = formValues(form);
    const payload = { job_offer_id: values.job_offer_id, channel: values.channel, format: values.format };
    if (values.location.trim()) payload.location = values.location.trim();
    const ad = await api("/api/ads", { method: "POST", body: JSON.stringify(payload) });
    await loadAds();
    await selectAd(ad.id);
    notify("Annuncio creato e copy generato.", "success");
  } catch (error) {
    notify(error.message, "error");
  } finally {
    button.disabled = false;
  }
});

$("#filter-offer").addEventListener("change", loadAds);
$("#filter-channel").addEventListener("change", loadAds);

$("#generate-variant").addEventListener("click", async (event) => {
  if (!state.selectedAd) return;
  const adId = state.selectedAd.id;
  const button = event.currentTarget;
  button.disabled = true;
  notify("Generazione della variante in corso…");
  try {
    const variant = await api(`/api/ads/${encodeURIComponent(adId)}/variants`, {
      method: "POST", body: JSON.stringify({}),
    });
    if (state.selectedAd?.id === adId) {
      const ad = await api(`/api/ads/${encodeURIComponent(adId)}`);
      if (state.selectedAd?.id === adId) {
        state.selectedVariantId = variant.id;
        renderDetail(ad);
      }
    }
    notify("Nuova variante generata.", "success");
  } catch (error) {
    notify(error.message, "error");
  } finally {
    button.disabled = false;
  }
});

$("#upload-image").addEventListener("click", async (event) => {
  const ad = state.selectedAd;
  const variant = activeVariant();
  const file = $("#variant-form").elements.namedItem("image_file").files[0];
  if (!ad || !variant) return;
  if (!file) {
    notify("Seleziona un'immagine prima di caricarla.", "error");
    return;
  }
  const button = event.currentTarget;
  button.disabled = true;
  notify("Caricamento immagine in corso…");
  try {
    const formData = new FormData();
    formData.append("image", file);
    await api(`/api/ads/${encodeURIComponent(ad.id)}/variants/${encodeURIComponent(variant.id)}/image`, {
      method: "POST", body: formData,
    });
    const updated = await api(`/api/ads/${encodeURIComponent(ad.id)}`);
    state.selectedVariantId = variant.id;
    renderDetail(updated);
    notify("Immagine associata alla variante.", "success");
  } catch (error) {
    notify(error.message, "error");
  } finally {
    button.disabled = false;
  }
});

$("#metadata-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.selectedAd) return;
  const form = event.currentTarget;
  const button = form.querySelector("button[type=submit]");
  button.disabled = true;
  try {
    const values = formValues(form);
    const payload = {};
    if (values.location.trim() !== state.selectedAd.location) payload.location = values.location.trim();
    if (values.status !== state.selectedAd.status) payload.status = values.status;
    if (!Object.keys(payload).length) {
      notify("Non ci sono modifiche da salvare.");
      return;
    }
    const ad = await api(`/api/ads/${encodeURIComponent(state.selectedAd.id)}`, {
      method: "PATCH", body: JSON.stringify(payload),
    });
    const previousVariantId = state.selectedVariantId;
    state.selectedAd = ad;
    state.ads = state.ads.map((item) => item.id === ad.id
      ? { ...item, location: ad.location, status: ad.status, variants: ad.variants }
      : item);
    state.selectedVariantId = ad.variants.some((variant) => variant.id === previousVariantId)
      ? previousVariantId : ad.variants[0]?.id || null;
    renderDetail(ad);
    notify("Dettagli aggiornati.", "success");
  } catch (error) {
    notify(error.message, "error");
  } finally {
    button.disabled = false;
  }
});

$("#delete-ad").addEventListener("click", async (event) => {
  const ad = state.selectedAd;
  if (!ad) return;
  const title = activeVariant()?.title || "questo annuncio";
  if (!window.confirm(`Eliminare definitivamente “${title}” e tutte le sue varianti?`)) return;

  const button = event.currentTarget;
  button.disabled = true;
  try {
    await api(`/api/ads/${encodeURIComponent(ad.id)}`, { method: "DELETE" });
    state.ads = state.ads.filter((item) => item.id !== ad.id);
    state.selectedAd = null;
    state.selectedVariantId = null;
    renderAds();
    notify("Annuncio eliminato.", "success");
  } catch (error) {
    notify(error.message, "error");
  } finally {
    button.disabled = false;
  }
});

$("#variant-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const ad = state.selectedAd;
  const variant = activeVariant();
  if (!ad || !variant) return;
  const form = event.currentTarget;
  if (!form.reportValidity()) return;
  const button = form.querySelector("button[type=submit]");
  button.disabled = true;
  try {
    const values = formValues(form);
    const channelFields = { ...(variant.channel_fields || {}) };
    for (const key of channelFieldNames) {
      const value = values[`field_${key}`].trim();
      if (value) channelFields[key] = value;
      else delete channelFields[key];
    }
    const payload = {
      variant_name: values.variant_name.trim(),
      title: values.title.trim(),
      requirements: values.requirements.split("\n").map((item) => item.trim()).filter(Boolean),
      compensation: values.compensation.trim() || null,
      channel_fields: channelFields,
    };
    if (ad.format !== "image") payload.body_text = values.body_text.trim();
    if (ad.format === "image" || ad.format === "image_text") {
      payload.creative_text = values.creative_text.trim();
      payload.creative_brief = values.creative_brief.trim();
    }
    const current = {
      variant_name: variant.variant_name,
      title: variant.title,
      requirements: variant.requirements || [],
      compensation: variant.compensation,
      channel_fields: variant.channel_fields || {},
    };
    if (ad.format !== "image") current.body_text = variant.body_text || "";
    if (ad.format === "image" || ad.format === "image_text") {
      current.creative_text = variant.creative_text || "";
      current.creative_brief = variant.creative_brief || "";
    }
    for (const [key, value] of Object.entries(payload)) {
      if (equalValue(value, current[key])) delete payload[key];
    }
    if (!Object.keys(payload).length) {
      notify("Non ci sono modifiche da salvare.");
      return;
    }
    await api(`/api/ads/${encodeURIComponent(ad.id)}/variants/${encodeURIComponent(variant.id)}`, {
      method: "PATCH", body: JSON.stringify(payload),
    });
    await loadAds();
    notify("Variante aggiornata.", "success");
  } catch (error) {
    notify(error.message, "error");
  } finally {
    button.disabled = false;
  }
});

async function start() {
  try {
    state.offers = await api("/api/job-offers");
    populateOffers();
    await loadAds();
    if (!state.ads.length) notify("Nessun annuncio presente. Creane uno dalla job offer.");
  } catch (error) {
    notify(error.message, "error");
  }
}

start();
