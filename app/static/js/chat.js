import { getJSON, postJSON } from "./api.js";

let lastChatId = 0;
let chatEnabled = true;
let messagesElement = null;
let inputElement = null;
let buttonElement = null;
let statusElement = null;
let pollHandle = null;

function setStatus(message = "") {
  if (statusElement) {
    statusElement.textContent = message;
  }
}

function applyEnabledState() {
  if (!inputElement || !buttonElement) {
    return;
  }

  inputElement.disabled = !chatEnabled;
  buttonElement.disabled = !chatEnabled;
  inputElement.placeholder = chatEnabled
    ? "Type a message..."
    : "Chat closes when the game ends.";
}

export function setChatEnabled(enabled) {
  chatEnabled = Boolean(enabled);
  applyEnabledState();

  if (!chatEnabled) {
    setStatus("Chat is closed because the game has finished.");
  } else if (statusElement?.textContent === "Chat is closed because the game has finished.") {
    setStatus("");
  }
}

function appendMessage(message, currentUserId) {
  if (!messagesElement) {
    return;
  }

  const row = document.createElement("div");
  row.className = "chat-message";

  const meta = document.createElement("div");
  meta.className = "chat-meta";

  const strong = document.createElement("strong");
  strong.textContent = message.display_name;

  const mine = document.createElement("span");
  mine.textContent = message.user_id === currentUserId ? " (you) " : " ";

  const timestamp = document.createElement("small");
  timestamp.textContent = message.created_at;

  meta.appendChild(strong);
  meta.appendChild(mine);
  meta.appendChild(timestamp);

  const body = document.createElement("div");
  body.className = "chat-body";
  body.textContent = message.body;

  row.appendChild(meta);
  row.appendChild(body);

  messagesElement.appendChild(row);
  messagesElement.scrollTop = messagesElement.scrollHeight;
  lastChatId = Math.max(lastChatId, message.id);
}

async function pollChat(gameId, currentUserId) {
  const data = await getJSON(`/games/${gameId}/chat?since_id=${lastChatId}`);
  if (!Array.isArray(data.messages)) {
    return;
  }

  for (const message of data.messages) {
    appendMessage(message, currentUserId);
  }
}

async function sendChat(gameId, currentUserId, body) {
  const message = await postJSON(`/games/${gameId}/chat`, { body });
  appendMessage(message, currentUserId);
}

function formatChatError(error) {
  const code = error?.data?.error;
  if (code === "empty") {
    return "Type a message before sending.";
  }
  if (code === "too_long") {
    return "Messages must be 500 characters or fewer.";
  }
  if (code === "game_finished") {
    return "Chat is closed because the game has finished.";
  }
  return error?.data?.message || error.message || "Unable to send chat right now.";
}

export function initChat(gameId, currentUserId) {
  messagesElement = document.getElementById("chat-messages");
  inputElement = document.getElementById("chat-input");
  buttonElement = document.getElementById("chat-send-button");
  statusElement = document.getElementById("chat-status");
  lastChatId = 0;

  if (!messagesElement || !inputElement || !buttonElement) {
    console.error("Chat elements not found.");
    return;
  }

  applyEnabledState();

  async function submitChat() {
    if (!chatEnabled) {
      setStatus("Chat is closed because the game has finished.");
      return;
    }

    const body = inputElement.value.trim();
    if (!body) {
      setStatus("Type a message before sending.");
      return;
    }

    setStatus("");
    buttonElement.disabled = true;

    try {
      await sendChat(gameId, currentUserId, body);
      inputElement.value = "";
    } catch (error) {
      console.error("Chat send failed:", error);
      setStatus(formatChatError(error));
      if (error?.data?.error === "game_finished") {
        setChatEnabled(false);
      }
    } finally {
      applyEnabledState();
    }
  }

  buttonElement.addEventListener("click", submitChat);

  inputElement.addEventListener("keydown", async (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      await submitChat();
    }
  });

  if (pollHandle) {
    window.clearInterval(pollHandle);
  }

  pollHandle = window.setInterval(() => {
    pollChat(gameId, currentUserId).catch((error) => {
      console.error("Chat poll failed:", error);
      setStatus("Unable to refresh chat right now.");
    });
  }, 3000);

  pollChat(gameId, currentUserId).catch((error) => {
    console.error("Initial chat load failed:", error);
    setStatus("Unable to load chat right now.");
  });
}
