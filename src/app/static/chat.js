(() => {
  const byId = (id) => document.getElementById(id);
  const qs = (sel) => document.querySelector(sel);
  const qsa = (sel) => Array.from(document.querySelectorAll(sel));
  const norm = (s) => (s || "").trim().toLowerCase();

  const first = (...getters) => {
    for (const g of getters) {
      try {
        const v = g();
        if (v) return v;
      } catch {}
    }
    return null;
  };

  function setText(el, text) {
    if (el) el.textContent = text;
  }

  function safeHtml(str) {
    return (str ?? "").toString();
  }

  const el = {
    chat: () =>
      first(
        () => byId("chat"),
        () => byId("messages"),
        () => qs('[data-role="chat"]'),
        () => qs("#chatArea"),
        () => qs(".chatArea"),
        () => qs(".chat"),
        () => {
          const candidates = qsa("div").filter((d) => {
            const r = d.getBoundingClientRect?.();
            if (!r) return false;
            const style = getComputedStyle(d);
            const scrollish = style.overflowY === "auto" || style.overflowY === "scroll";
            return scrollish && r.width > 300 && r.height > 200;
          });
          return candidates.sort((a, b) => b.getBoundingClientRect().height - a.getBoundingClientRect().height)[0] || null;
        }
      ),

    input: () =>
      first(
        () => byId("input"),
        () => byId("message"),
        () => byId("messageInput"),
        () => byId("prompt"),
        () => qs('textarea[data-role="input"]'),
        () => qs('input[data-role="input"]'),
        () => {
          const inputs = qsa("textarea, input[type='text']").filter((x) => !x.disabled);
          if (!inputs.length) return null;
          return inputs.sort((a, b) => b.getBoundingClientRect().top - a.getBoundingClientRect().top)[0];
        }
      ),

    send: () =>
      first(
        () => byId("send"),
        () => byId("sendBtn"),
        () => byId("btnSend"),
        () => qs('[data-role="send"]'),
        () => qsa("button").find((b) => norm(b.textContent) === "send")
      ),

    newBtn: () =>
      first(
        () => byId("new"),
        () => byId("newChat"),
        () => byId("btnNew"),
        () => qs('[data-role="new"]'),
        () => qsa("button").find((b) => norm(b.textContent) === "new")
      ),

    status: () =>
      first(
        () => byId("status"),
        () => byId("pillStatus"),
        () => byId("authStatus"),
        () => qs('[data-role="status"]')
      ),

    loginBtn: () =>
      first(
        () => byId("loginBtn"),
        () => byId("login"),
        () => byId("btnLogin"),
        () => qsa("button").find((b) => norm(b.textContent) === "login")
      ),

    email: () =>
      first(
        () => byId("email"),
        () => byId("emailInput"),
        () => byId("loginEmail"),
        () => qsa("input").find((i) => (i.type || "").toLowerCase() === "email")
      ),

    modelSelect: () =>
      first(
        () => byId("modelSelect"),
        () => qs('[data-role="model-select"]'),
        () => qs("select")
      ),

    convList: () =>
      first(
        () => byId("conversationList"),
        () => byId("conversations"),
        () => qs('[data-role="conversations"]'),
        () => qs('[data-role="conversation-list"]'),
        () => {
          const convoHeader = qsa("*").find((n) => norm(n.textContent) === "conversations");
          if (!convoHeader) return null;
          let p = convoHeader.parentElement;
          for (let i = 0; i < 5 && p; i++) {
            const listCandidate =
              p.querySelector('[data-list="conversations"]') ||
              p.querySelector(".conversation-list") ||
              p.querySelector("ul") ||
              p;
            if (listCandidate) return listCandidate;
            p = p.parentElement;
          }
          return null;
        }
      ),
  };

  function setStatus(text) {
    const s = el.status();
    if (s) s.textContent = text;
  }

  function disableSend(disabled) {
    const btn = el.send();
    const input = el.input();
    const modelSelect = el.modelSelect();
    if (btn) btn.disabled = disabled;
    if (input) input.disabled = disabled;
    if (modelSelect) modelSelect.disabled = disabled;
  }

  function hideAuthUIHard() {
    // hide known elements
    const loginBtn = el.loginBtn();
    const email = el.email();
    if (loginBtn) loginBtn.style.display = "none";
    if (email) email.style.display = "none";

    const killTexts = new Set(["signed out", "signed in", "missing supabase config", "login"]);
    qsa("button, span, div, p").forEach((n) => {
      const t = norm(n.textContent);
      if (!t) return;
      if (killTexts.has(t)) n.style.display = "none";
    });

    qsa("div").forEach((d) => {
      const kids = Array.from(d.children || []);
      if (kids.length < 2) return;
      const texts = kids.map((k) => norm(k.textContent));
      const hasSigned =
        texts.some((x) => x === "signed out") || texts.some((x) => x === "signed in");
      if (hasSigned) d.style.display = "none";
    });
  }

  function applyScrollFixes() {
    const chat = el.chat();
    if (chat) {
      chat.style.overflowY = "auto";
      chat.style.scrollBehavior = "smooth";
      chat.style.minHeight = "0";

      chat.style.maxHeight = "calc(100vh - 260px)";
      chat.style.paddingRight = "6px"; // room for scrollbar
    }

    const list = el.convList();
    if (list) {
      list.style.overflowY = "auto";
      list.style.minHeight = "0";
      list.style.maxHeight = "calc(100vh - 220px)";
      list.style.paddingRight = "6px";
    }
  }

  function scrollToBottom() {
    const c = el.chat();
    if (!c) return;
    c.scrollTop = c.scrollHeight;
  }

  function addBubble(role, text, meta = "") {
    const c = el.chat();
    if (!c) return;

    const row = document.createElement("div");
    row.className = `msg ${role}`;
    row.style.margin = "10px 0";

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;

    row.appendChild(bubble);

    if (meta) {
      const m = document.createElement("div");
      m.className = "meta";
      m.textContent = meta;
      m.style.opacity = "0.75";
      m.style.fontSize = "12px";
      m.style.marginTop = "6px";
      row.appendChild(m);
    }

    c.appendChild(row);
    scrollToBottom();
  }

  function getConversationId() {
    return window.__conversationId || null;
  }
  function setConversationId(id) {
    window.__conversationId = id;
  }

  function getSelectedModel() {
    return el.modelSelect()?.value || null;
  }

  async function api(path, opts = {}) {
    const res = await fetch(path, opts);
    const ct = res.headers.get("content-type") || "";
    const isJson = ct.includes("application/json");
    const body = isJson ? await res.json().catch(() => ({})) : await res.text().catch(() => "");
    if (!res.ok) {
      const msg = typeof body === "string" ? body : JSON.stringify(body);
      throw new Error(`${res.status} ${res.statusText} — ${msg}`);
    }
    return body;
  }

  async function fetchConversations() {
    const endpoints = ["/api/conversations", "/api/conversations/list"];
    let lastErr = null;

    for (const ep of endpoints) {
      try {
        const data = await api(ep);
        const conversations =
          Array.isArray(data) ? data :
          Array.isArray(data?.conversations) ? data.conversations :
          Array.isArray(data?.data) ? data.data :
          [];
        return conversations;
      } catch (e) {
        lastErr = e;
      }
    }
    throw lastErr || new Error("Unable to fetch conversations");
  }

  async function fetchMessages(conversationId) {
    const endpoints = [
      `/api/conversations/${conversationId}/messages`,
      `/api/messages?conversation_id=${encodeURIComponent(conversationId)}`
    ];
    let lastErr = null;

    for (const ep of endpoints) {
      try {
        const data = await api(ep);
        const messages =
          Array.isArray(data) ? data :
          Array.isArray(data?.messages) ? data.messages :
          Array.isArray(data?.data) ? data.data :
          [];
        return messages;
      } catch (e) {
        lastErr = e;
      }
    }
    throw lastErr || new Error("Unable to fetch messages");
  }

  async function createConversation() {
    try {
      const data = await api("/api/conversations", { method: "POST" });
      const id = data?.conversation_id || data?.id;
      if (!id) throw new Error("No conversation id returned");
      return id;
    } catch (e) {
      console.warn("createConversation fallback:", e.message);
      return null;
    }
  }

  async function fetchModels() {
    return api("/api/models");
  }

  function populateModelSelect(catalog) {
    const select = el.modelSelect();
    if (!select) return;

    const models = Array.isArray(catalog?.models) ? catalog.models : [];
    const defaultModel = catalog?.default_model || "";

    select.innerHTML = "";

    if (!models.length) {
      const option = document.createElement("option");
      option.value = defaultModel;
      option.textContent = defaultModel || "No models available";
      select.appendChild(option);
      select.disabled = true;
      return;
    }

    let selectedValue = null;
    for (const model of models) {
      const option = document.createElement("option");
      option.value = model.id;
      option.textContent = model.installed === false ? `${model.label} (not installed)` : model.label;
      option.title = model.description || "";
      option.disabled = model.installed === false;
      if (!selectedValue && option.disabled === false) {
        selectedValue = model.id;
      }
      if (model.id === defaultModel && option.disabled === false) {
        selectedValue = model.id;
      }
      select.appendChild(option);
    }

    select.disabled = false;
    select.value = selectedValue || defaultModel || select.options[0]?.value || "";
  }

  async function loadModels() {
    try {
      const catalog = await fetchModels();
      populateModelSelect(catalog);
    } catch (e) {
      console.error("loadModels failed:", e);
      const select = el.modelSelect();
      if (select) {
        const hasUsableOptions = Array.from(select.options).some((option) => option.value);
        if (hasUsableOptions) {
          return;
        }
        select.innerHTML = "";
        const option = document.createElement("option");
        option.value = "";
        option.textContent = "Model list unavailable";
        select.appendChild(option);
        select.disabled = true;
      }
    }
  }

  function renderConversationList(conversations) {
    const list = el.convList();
    if (!list) return;

    let items = list.querySelector(".__convItems");
    if (!items) {
      items = document.createElement("div");
      items.className = "__convItems";
      items.style.display = "flex";
      items.style.flexDirection = "column";
      items.style.gap = "10px";
      items.style.marginTop = "12px";
      list.appendChild(items);
    }

    items.innerHTML = "";

    if (!conversations.length) {
      const empty = document.createElement("div");
      empty.style.opacity = "0.7";
      empty.style.fontSize = "13px";
      empty.textContent = "No conversations yet.";
      items.appendChild(empty);
      return;
    }

    conversations.forEach((c) => {
      const id = c.id || c.conversation_id || c.uuid;
      const created = c.created_at || c.createdAt || c.created;
      const label = c.title || (id ? `Conversation ${String(id).slice(0, 8)}` : "Conversation");

      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "convItem";
      btn.dataset.id = id;

      btn.style.textAlign = "left";
      btn.style.padding = "10px 12px";
      btn.style.borderRadius = "12px";
      btn.style.border = "1px solid rgba(255,255,255,0.08)";
      btn.style.background = "rgba(255,255,255,0.04)";
      btn.style.color = "inherit";
      btn.style.cursor = "pointer";

      btn.innerHTML = `
        <div style="font-size:13px; font-weight:600;">${safeHtml(label)}</div>
        <div style="font-size:11px; opacity:.65; margin-top:4px;">
          ${created ? new Date(created).toLocaleString() : ""}
        </div>
      `;

      const current = getConversationId();
      if (current && id && String(current) === String(id)) {
        btn.style.border = "1px solid rgba(120,150,255,0.35)";
        btn.style.background = "rgba(120,150,255,0.08)";
      }

      btn.onclick = () => openConversation(id);
      items.appendChild(btn);
    });
  }

  async function loadConversations({ autoOpenLatest = true } = {}) {
    setStatus("Loading…");
    try {
      const conversations = await fetchConversations();
      renderConversationList(conversations);

      if (autoOpenLatest && !getConversationId() && conversations[0]) {
        const id = conversations[0].id || conversations[0].conversation_id || conversations[0].uuid;
        if (id) await openConversation(id);
      } else {
        setStatus("Ready");
      }
    } catch (e) {
      console.error("loadConversations failed:", e);
      setStatus("Ready");
    }
  }

  async function openConversation(id) {
    if (!id) return;
    setStatus("Loading…");
    try {
      const chat = el.chat();
      if (chat) chat.innerHTML = "";

      setConversationId(id);

      const messages = await fetchMessages(id);
      if (!messages.length) {
        addBubble("bot", "No messages yet. Send one to begin.");
        setStatus("Ready");
        await loadConversations({ autoOpenLatest: false });
        return;
      }

      for (const m of messages) {
        const role = (m.role || m.sender || "assistant") === "user" ? "user" : "bot";
        addBubble(role, m.content || m.message || "");
      }

      setStatus("Ready");
      await loadConversations({ autoOpenLatest: false });
      scrollToBottom();
    } catch (e) {
      console.error("openConversation failed:", e);
      addBubble("bot", `Error loading conversation: ${e.message}`);
      setStatus("Ready");
    }
  }

  async function handleNew() {
    setStatus("Creating…");
    try {
      const id = await createConversation();
      if (id) {
        setConversationId(id);
        await openConversation(id);
      } else {
        setConversationId(null);
        const chat = el.chat();
        if (chat) chat.innerHTML = "";
        addBubble("bot", "New chat started. Send a message to begin.");
        setStatus("Ready");
      }
      await loadConversations({ autoOpenLatest: false });
    } catch (e) {
      console.error("handleNew failed:", e);
      setStatus("Ready");
    }
  }

  async function handleSend() {
    const input = el.input();
    const text = (input?.value || "").trim();
    if (!text) return;

    addBubble("user", text);
    if (input) input.value = "";

    disableSend(true);
    setStatus("Thinking…");

    try {
      if (!getConversationId()) {
        const id = await createConversation();
        if (id) setConversationId(id);
      }

      const payload = {
        message: text,
        conversation_id: getConversationId(),
        model: getSelectedModel(),
      };

      const data = await api("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (data?.conversation_id) setConversationId(data.conversation_id);

      const metaParts = [];
      if (data?.model) metaParts.push(`model=${data.model}`);
      if (data?.env) metaParts.push(`env=${data.env}`);
      if (data?.request_id) metaParts.push(`id=${data.request_id}`);

      addBubble("bot", data.reply || data.response || "(no reply)", metaParts.join(" • "));
      setStatus("Ready");
      await loadConversations({ autoOpenLatest: false });
      scrollToBottom();
    } catch (e) {
      console.error("send failed:", e);
      addBubble("bot", `Send failed: ${e.message}`);
      setStatus("Ready");
    } finally {
      disableSend(false);
    }
  }

  function wireEvents() {
    const sendBtn = el.send();
    const input = el.input();
    const newBtn = el.newBtn();

    if (sendBtn) {
      sendBtn.type = "button";
      sendBtn.addEventListener("click", handleSend);
    }

    if (input) {
      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          handleSend();
        }
      });
    }

    if (newBtn) {
      newBtn.type = "button";
      newBtn.addEventListener("click", handleNew);
    }
  }

  (async function init() {
    hideAuthUIHard();
    applyScrollFixes();
    wireEvents();

    disableSend(false);
    setStatus("Ready");

    await loadModels();
    await loadConversations({ autoOpenLatest: true });
    scrollToBottom();
  })();
})();
