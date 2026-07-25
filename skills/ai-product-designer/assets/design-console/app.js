const state = {
  designSystems: [],
  projectTypes: [],
  requests: [],
  workspace: null,
  selectedDesignSystemId: "",
  selectedProjectTypeId: "",
  activeConsoleTab: "create",
  evidenceFiles: [],
  evidenceBatchId: crypto.randomUUID(),
};

const glyphs = {
  wireframe: "▤",
  mockup: "▣",
  slides: "▧",
  audit: "⌕",
  flow: "⌘",
  system: "◉",
  component: "◇",
  handoff: "⇢",
};

const elements = {
  designSystemGrid: document.querySelector("#design-system-grid"),
  designSystemPanelList: document.querySelector("#design-system-panel-list"),
  projectTypePanelList: document.querySelector("#project-type-panel-list"),
  designSystemLabel: document.querySelector("#selected-design-system-label"),
  projectTypeLabel: document.querySelector("#selected-project-type-label"),
  fidelity: document.querySelector("#fidelity"),
  fidelityHelp: document.querySelector("#fidelity-help"),
  evidenceDropzone: document.querySelector("#evidence-dropzone"),
  evidenceFiles: document.querySelector("#evidence-files"),
  evidenceFolder: document.querySelector("#evidence-folder"),
  evidenceFileList: document.querySelector("#evidence-file-list"),
  workspaceName: document.querySelector("#workspace-name"),
  workspacePath: document.querySelector("#workspace-path"),
  latestDownload: document.querySelector("#latest-download"),
  recentList: document.querySelector("#recent-list"),
  requestForm: document.querySelector("#request-form"),
  registerForm: document.querySelector("#register-form"),
  registerDialog: document.querySelector("#register-dialog"),
  runtimeBanner: document.querySelector("#runtime-banner"),
  runtimeTitle: document.querySelector("#runtime-title"),
  runtimeMessage: document.querySelector("#runtime-message"),
  createButton: document.querySelector(".create-button"),
  createStatusTitle: document.querySelector("#create-status-title"),
  createStatusNote: document.querySelector("#create-status-note"),
  toast: document.querySelector(".toast"),
};

let toastTimer;
bootstrap().catch((error) => showToast(error.message, true));

async function bootstrap() {
  const response = await fetch("/api/bootstrap");
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "初期データを取得できませんでした。");
  state.designSystems = data.designSystems;
  state.projectTypes = data.projectTypes;
  state.requests = data.requests;
  state.workspace = data.workspace;
  state.selectedDesignSystemId =
    state.designSystems.find((item) => item.id === state.workspace?.lastDesignSystemId && item.status !== "deprecated")?.id || "";
  state.selectedProjectTypeId =
    state.projectTypes.find((item) => item.availability === "ready")?.id ||
    state.projectTypes.find((item) => item.availability !== "planned")?.id ||
    "";
  render();
  window.setInterval(refreshRuntimeState, 2500);
}

function render() {
  elements.designSystemGrid.innerHTML = state.designSystems.length
    ? state.designSystems.map((item) => designSystemCard(item)).join("")
    : `<div class="empty-card">デザインシステムが未登録です。最初の1件を登録してください。</div>`;
  elements.designSystemPanelList.innerHTML = state.designSystems.length
    ? state.designSystems.map((item) => designSystemCard(item, true)).join("")
    : `<div class="empty-card">デザインシステムは未登録です。</div>`;
  elements.projectTypePanelList.innerHTML = state.projectTypes.map((item) => projectTypeCard(item)).join("");
  renderLabels();
  renderFidelity();
  renderRecent();
  renderWorkspace();
  renderConsoleTab();
  bindChoiceCards();
}

function designSystemCard(item, compact = false) {
  const selected = item.id === state.selectedDesignSystemId;
  const fileCount = item.inventory?.fileCount;
  return `
    <button class="choice-card ${selected ? "is-selected" : ""}" type="button" data-design-system-id="${escapeHtml(item.id)}">
      <span class="choice-glyph" aria-hidden="true">Aa</span>
      <h3>${escapeHtml(item.name)}</h3>
      ${compact ? "" : `<p>${escapeHtml(item.description || "説明はまだありません。")}</p>`}
      <span class="choice-meta">
        <span class="tag">${escapeHtml(designSystemStatusLabel(item.status))}</span>
        <span class="tag">${fileCount == null ? "ファイル数未取得" : `${escapeHtml(String(fileCount))}ファイル`}</span>
      </span>
    </button>
  `;
}

function projectTypeCard(item, compact = false) {
  const selected = item.id === state.selectedProjectTypeId;
  const planned = item.availability === "planned";
  const availability = availabilityLabel(item.availability);
  return `
    <button class="choice-card ${selected ? "is-selected" : ""} ${planned ? "is-disabled" : ""}" type="button" data-project-type-id="${escapeHtml(item.id)}" ${planned ? "disabled" : ""}>
      <span class="choice-glyph" aria-hidden="true">${glyphs[item.icon] || "◇"}</span>
      <h3>${escapeHtml(compact ? item.shortName : item.name)}</h3>
      ${compact ? "" : `<p>${escapeHtml(item.description)}</p>`}
      <span class="choice-meta">
        <span class="tag availability-${escapeHtml(item.availability || "beta")}">${escapeHtml(availability)}</span>
        <span class="tag">${escapeHtml(item.artifact)}</span>
      </span>
      ${compact ? "" : `<small class="availability-note">${escapeHtml(item.availabilityNote || "")}</small>`}
    </button>
  `;
}

function renderLabels() {
  const designSystem = selectedDesignSystem();
  const projectType = selectedProjectType();
  const hasDesignSystems = state.designSystems.length > 0;
  elements.designSystemLabel.textContent = designSystem?.name || (hasDesignSystems ? "選択してください" : "未登録");
  elements.projectTypeLabel.textContent = projectType?.name || "選択してください";
  elements.createButton.disabled = !designSystem || !projectType;
  if (!hasDesignSystems) {
    elements.createStatusTitle.textContent = "デザインシステムを登録してください";
    elements.createStatusNote.textContent = "「デザインシステム」タブから最初の1件を登録すると制作を開始できます。";
  } else if (!designSystem) {
    elements.createStatusTitle.textContent = "デザインシステムを選択してください";
    elements.createStatusNote.textContent = "登録済みのデザインシステムから、この制作で使用するものを選択してください。";
  } else {
    elements.createStatusTitle.textContent = "依頼内容と出力設定を確認してください";
    elements.createStatusNote.textContent = "選択した資料は案件フォルダへコピーし、移動後も参照できる状態で保存します。";
  }
}

function renderFidelity() {
  const projectType = selectedProjectType();
  const values = projectType?.fidelity || ["mid"];
  elements.fidelity.innerHTML = values
    .map((value) => `<option value="${escapeHtml(value)}" ${value === projectType?.defaultFidelity ? "selected" : ""}>${escapeHtml(fidelityLabel(value))}</option>`)
    .join("");
  renderFidelityHelp();
}

function renderRecent() {
  elements.recentList.innerHTML = state.requests.length
    ? state.requests
        .map(
          (item) => `
            <article class="recent-item">
              <div class="recent-main"><strong>${escapeHtml(item.title)}</strong><span class="recent-location">${escapeHtml(item.locations?.workspace || `work/${item.id}`)}</span></div>
              <div class="recent-meta"><span>${escapeHtml(item.designSystem?.name || "")}</span><span>${escapeHtml(item.projectType?.name || "")}</span><span>${escapeHtml(formatDate(item.updatedAt || item.createdAt))}</span></div>
              <div class="request-status status-${escapeHtml(item.status || "queued")}"><span></span>${escapeHtml(requestStatusLabel(item.status))}</div>
              <div class="recent-actions">
                ${item.status === "ready" && item.result?.entrypoint ? `<a href="${escapeHtml(item.result.previewUrl || `/preview/${encodeURIComponent(item.id)}/`)}" target="_blank" rel="noreferrer">プレビュー</a>` : ""}
                ${item.status === "ready" ? `<a href="${escapeHtml(item.result?.downloadUrl || `/api/requests/${encodeURIComponent(item.id)}/export`)}">ZIP</a>` : ""}
                ${item.status === "ready" ? `<button type="button" data-copy-revision="${escapeHtml(item.id)}">修正依頼をコピー</button>` : ""}
              </div>
            </article>
          `,
        )
        .join("")
    : `<div class="empty-card">まだ案件設定はありません。</div>`;
  renderLatestDownload();
  renderRuntimeBanner();
  bindRecentActions();
}

function renderWorkspace() {
  elements.workspaceName.textContent = state.workspace?.name || "作業フォルダ";
  elements.workspacePath.textContent = state.workspace?.path || "";
}

function renderLatestDownload() {
  const latestReady = state.requests.find((item) => item.status === "ready");
  elements.latestDownload.hidden = !latestReady;
  if (latestReady) {
    elements.latestDownload.href =
      latestReady.result?.downloadUrl ||
      `/api/requests/${encodeURIComponent(latestReady.id)}/export`;
  }
}

function renderRuntimeBanner() {
  const active = state.requests.find(
    (item) => item.id === state.workspace?.activeRequestId && ["queued", "generating"].includes(item.status),
  ) || state.requests.find((item) => ["queued", "generating"].includes(item.status));
  elements.runtimeBanner.hidden = !active;
  if (!active) return;
  elements.runtimeTitle.textContent = active.status === "generating" ? "Codexが制作しています" : "制作開始を待っています";
  elements.runtimeMessage.textContent = `${active.title} · ${active.statusMessage || "この画面で進捗を自動更新します。"}`;
}

function bindRecentActions() {
  for (const button of document.querySelectorAll("[data-copy-revision]")) {
    button.addEventListener("click", async () => {
      const request = state.requests.find((item) => item.id === button.dataset.copyRevision);
      if (!request) return;
      const text = [
        "$ai-product-designer",
        `作業フォルダ: ${state.workspace?.path || ""}`,
        `案件ID: ${request.id}`,
        "以下の内容で既存の制作物を修正してください:",
        "",
      ].join("\n");
      await navigator.clipboard.writeText(text);
      showToast("修正依頼をコピーしました。チャットへ貼り付けて、修正内容を追記してください。");
    });
  }
}

function renderConsoleTab() {
  for (const button of document.querySelectorAll("[data-console-tab]")) {
    const selected = button.dataset.consoleTab === state.activeConsoleTab;
    button.setAttribute("aria-selected", String(selected));
  }
  document.querySelector("#create-panel").hidden = state.activeConsoleTab !== "create";
  document.querySelector("#design-systems-panel").hidden = state.activeConsoleTab !== "design-systems";
  document.querySelector("#recent-panel").hidden = state.activeConsoleTab !== "recent";
}

function bindChoiceCards() {
  for (const button of document.querySelectorAll("[data-design-system-id]")) {
    button.addEventListener("click", () => {
      state.selectedDesignSystemId = button.dataset.designSystemId;
      closePanels();
      render();
    });
  }
  for (const button of document.querySelectorAll("[data-project-type-id]")) {
    button.addEventListener("click", () => {
      if (button.disabled) return;
      state.selectedProjectTypeId = button.dataset.projectTypeId;
      closePanels();
      render();
    });
  }
}

elements.fidelity.addEventListener("change", renderFidelityHelp);

document.querySelector("#choose-files").addEventListener("click", (event) => {
  event.stopPropagation();
  elements.evidenceFiles.click();
});
document.querySelector("#choose-folder").addEventListener("click", (event) => {
  event.stopPropagation();
  elements.evidenceFolder.click();
});
for (const eventName of ["dragenter", "dragover"]) {
  elements.evidenceDropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    elements.evidenceDropzone.classList.add("is-dragging");
  });
}
for (const eventName of ["dragleave", "drop"]) {
  elements.evidenceDropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    elements.evidenceDropzone.classList.remove("is-dragging");
  });
}
elements.evidenceDropzone.addEventListener("drop", async (event) => {
  try {
    addEvidenceFiles(await filesFromDataTransfer(event.dataTransfer));
  } catch (error) {
    showToast(`資料を読み込めませんでした: ${error.message}`, true);
  }
});
elements.evidenceFiles.addEventListener("change", () => {
  addEvidenceFiles([...elements.evidenceFiles.files].map((file) => ({ file, relativePath: file.name })));
  elements.evidenceFiles.value = "";
});
elements.evidenceFolder.addEventListener("change", () => {
  addEvidenceFiles(
    [...elements.evidenceFolder.files].map((file) => ({
      file,
      relativePath: file.webkitRelativePath || file.name,
    })),
  );
  elements.evidenceFolder.value = "";
});
elements.evidenceFileList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-remove-evidence]");
  if (!button) return;
  state.evidenceFiles = state.evidenceFiles.filter((item) => item.key !== button.dataset.removeEvidence);
  renderEvidenceFiles();
});

for (const button of document.querySelectorAll("[data-open-panel]")) {
  button.addEventListener("click", () => {
    const target = document.getElementById(button.dataset.openPanel);
    const wasHidden = target.hidden;
    closePanels();
    target.hidden = !wasHidden;
  });
}
for (const button of document.querySelectorAll("[data-console-tab]")) {
  button.addEventListener("click", () => {
    state.activeConsoleTab = button.dataset.consoleTab;
    renderConsoleTab();
  });
}
for (const button of document.querySelectorAll("[data-close-panel]")) {
  button.addEventListener("click", closePanels);
}
for (const button of document.querySelectorAll("[data-open-dialog]")) {
  button.addEventListener("click", () => {
    closePanels();
    elements.registerDialog.showModal();
  });
}
for (const button of document.querySelectorAll("[data-close-dialog]")) {
  button.addEventListener("click", () => elements.registerDialog.close());
}
elements.registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(elements.registerForm);
  const payload = Object.fromEntries(formData.entries());
  try {
    const response = await fetch("/api/design-systems", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "登録できませんでした。");
    state.designSystems.push(data.item);
    state.selectedDesignSystemId = data.item.id;
    elements.registerForm.reset();
    elements.registerDialog.close();
    render();
    showToast(`${data.item.name} を登録しました。`);
  } catch (error) {
    showToast(error.message, true);
  }
});

elements.requestForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const submitButton = elements.requestForm.querySelector(".create-button");
  const originalButtonText = submitButton.innerHTML;
  submitButton.disabled = true;
  try {
    submitButton.textContent = state.evidenceFiles.length ? "資料を保存しています…" : "案件を準備しています…";
    const uploadedEvidencePaths = await uploadEvidenceFiles();
    const payload = {
      title: document.querySelector("#title").value.trim(),
      prompt: document.querySelector("#prompt").value.trim(),
      designSystemId: state.selectedDesignSystemId,
      projectTypeId: state.selectedProjectTypeId,
      fidelity: elements.fidelity.value,
      compareDirections: Number(document.querySelector("#compare-directions").value),
      viewports: [...document.querySelectorAll('[name="viewport"]:checked')].map((item) => item.value),
      interactive: document.querySelector("#interactive").checked,
      allowGoogleFonts: document.querySelector("#google-fonts").checked,
      evidencePaths: document
        .querySelector("#evidence-paths")
        .value.split("\n")
        .map((item) => item.trim())
        .filter(Boolean),
      uploadedEvidencePaths,
    };
    submitButton.textContent = "制作フォルダを作成しています…";
    const response = await fetch("/api/requests", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "案件設定を作成できませんでした。");
    state.requests.unshift(data.request);
    if (state.workspace) state.workspace.activeRequestId = data.request.id;
    renderRecent();
    state.activeConsoleTab = "recent";
    renderConsoleTab();
    state.evidenceFiles = [];
    state.evidenceBatchId = crypto.randomUUID();
    renderEvidenceFiles();
    showToast("制作を開始しました。制作履歴で進捗を確認できます。");
  } catch (error) {
    showToast(error.message, true);
  } finally {
    submitButton.innerHTML = originalButtonText;
    renderLabels();
  }
});

function selectedDesignSystem() {
  return state.designSystems.find((item) => item.id === state.selectedDesignSystemId);
}

function selectedProjectType() {
  return state.projectTypes.find((item) => item.id === state.selectedProjectTypeId);
}

function closePanels() {
  for (const panel of document.querySelectorAll(".floating-panel")) panel.hidden = true;
}

function fidelityLabel(value) {
  return { "n/a": "対象外", low: "低：構成確認", mid: "中：UI検討", high: "高：完成イメージ" }[value] || value;
}

function renderFidelityHelp() {
  const descriptions = {
    "n/a": "この制作タイプでは仕上がりレベルを指定しません。",
    low: "画面構成、情報の順序、導線を確認します。配色や細かな見た目は作り込みません。",
    mid: "構成に加えて、実際の文言、配色、余白、コンポーネントの状態まで検討します。",
    high: "デザインシステムに沿って、実装に近い見た目とレスポンシブ・状態差分まで表現します。",
  };
  elements.fidelityHelp.textContent = descriptions[elements.fidelity.value] || "";
}

function availabilityLabel(value) {
  return { ready: "利用可能", beta: "Beta", planned: "準備中" }[value] || "Beta";
}

function designSystemStatusLabel(value) {
  return { active: "利用中", evaluation: "評価中", deprecated: "利用終了" }[value] || value;
}

function formatDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("ja-JP", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(value));
}

function requestStatusLabel(value) {
  return {
    queued: "制作待ち",
    generating: "制作中",
    ready: "完成",
    error: "要確認",
  }[value] || "制作待ち";
}

async function refreshRuntimeState() {
  try {
    const response = await fetch("/api/bootstrap");
    if (!response.ok) return;
    const data = await response.json();
    state.requests = data.requests;
    state.workspace = data.workspace;
    renderRecent();
    renderWorkspace();
  } catch {
    // The local server may be restarting. Keep the last visible state.
  }
}

function addEvidenceFiles(entries) {
  const byPath = new Map(state.evidenceFiles.map((item) => [item.relativePath, item]));
  for (const entry of entries) {
    if (!entry?.file || entry.file.size === 0 || entry.file.size > 50 * 1024 * 1024) {
      if (entry?.file?.size === 0) showToast(`${entry.file.name} は空のファイルです。`, true);
      if (entry?.file?.size > 50 * 1024 * 1024) showToast(`${entry.file.name} は50MBを超えるため追加できません。`, true);
      continue;
    }
    const relativePath = normalizeClientPath(entry.relativePath || entry.file.name);
    if (!relativePath) continue;
    byPath.set(relativePath, {
      file: entry.file,
      relativePath,
      key: `${relativePath}:${entry.file.size}:${entry.file.lastModified}`,
    });
  }
  state.evidenceFiles = [...byPath.values()];
  renderEvidenceFiles();
}

function renderEvidenceFiles() {
  elements.evidenceFileList.innerHTML = state.evidenceFiles
    .map(
      (item) => `
        <div class="evidence-file-item">
          <div><strong>${escapeHtml(item.file.name)}</strong><small>${escapeHtml(item.relativePath)}</small></div>
          <span class="evidence-file-size">${escapeHtml(formatBytes(item.file.size))}</span>
          <button type="button" data-remove-evidence="${escapeHtml(item.key)}" aria-label="${escapeHtml(item.file.name)}を外す">×</button>
        </div>
      `,
    )
    .join("");
}

async function uploadEvidenceFiles() {
  const paths = [];
  for (const item of state.evidenceFiles) {
    const params = new URLSearchParams({
      batch: state.evidenceBatchId,
      path: item.relativePath,
    });
    const response = await fetch(`/api/reference-files?${params}`, {
      method: "POST",
      headers: { "Content-Type": item.file.type || "application/octet-stream" },
      body: item.file,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || `${item.file.name}を保存できませんでした。`);
    paths.push(data.path);
  }
  return paths;
}

async function filesFromDataTransfer(dataTransfer) {
  const items = [...(dataTransfer?.items || [])];
  const entries = items.map((item) => item.webkitGetAsEntry?.()).filter(Boolean);
  if (!entries.length) {
    return [...(dataTransfer?.files || [])].map((file) => ({ file, relativePath: file.name }));
  }
  const files = [];
  for (const entry of entries) await collectDroppedEntry(entry, "", files);
  return files;
}

async function collectDroppedEntry(entry, parentPath, output) {
  const relativePath = normalizeClientPath(`${parentPath}/${entry.name}`);
  if (entry.isFile) {
    const file = await new Promise((resolve, reject) => entry.file(resolve, reject));
    output.push({ file, relativePath });
    return;
  }
  if (!entry.isDirectory) return;
  const reader = entry.createReader();
  while (true) {
    const children = await new Promise((resolve, reject) => reader.readEntries(resolve, reject));
    if (!children.length) break;
    for (const child of children) await collectDroppedEntry(child, relativePath, output);
  }
}

function normalizeClientPath(value) {
  const parts = String(value)
    .replaceAll("\\", "/")
    .split("/")
    .filter((part) => part && part !== "." && part !== "..");
  return parts.join("/");
}

function formatBytes(value) {
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${Math.round(value / 1024)} KB`;
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

function showToast(message, error = false) {
  window.clearTimeout(toastTimer);
  elements.toast.textContent = message;
  elements.toast.classList.toggle("is-error", error);
  elements.toast.classList.add("is-visible");
  toastTimer = window.setTimeout(() => elements.toast.classList.remove("is-visible"), 2600);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
