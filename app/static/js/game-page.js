import { getJSON, postJSON } from "./api.js";
import { createBoardController } from "./board.js";
import { replaceLeaderboard } from "./leaderboard.js";
import { startPoller } from "./poller.js";
import { initChat, setChatEnabled } from "./chat.js";

const initialState = JSON.parse(document.getElementById("initial-state").textContent);
const boardElement = document.getElementById("board");
const moveListElement = document.getElementById("move-list");
const statusBannerElement = document.getElementById("status-banner");
const claimDrawButton = document.getElementById("claim-draw-button");
const syncIndicator = document.getElementById("sync-indicator");
const leaderboardBody = document.getElementById("leaderboard-body");
const promotionModal = document.getElementById("promotion-modal");

let state = initialState;

const board = createBoardController({
  root: boardElement,
  promotionModal,
  onMoveRequest: submitMove,
});

function renderMoveList() {
  moveListElement.innerHTML = "";
  for (const move of state.moves) {
    const item = document.createElement("li");
    item.textContent = `${move.move_number}. ${move.san}`;
    moveListElement.appendChild(item);
  }
}

function renderStatus() {
  let message = `${state.players.white} vs ${state.players.black} · ${state.turn} to move`;
  if (state.status !== "active") {
    message = `Finished · ${state.result_code}${state.termination ? ` · ${state.termination}` : ""}`;
  } else if (state.your_turn) {
    message += " · your turn";
  }
  if (state.can_claim_draw && state.status === "active") {
    message += ` · draw claim available${state.draw_claim_reason ? ` (${state.draw_claim_reason.replaceAll("_", " ")})` : ""}`;
  }
  statusBannerElement.textContent = message;
  claimDrawButton.disabled = !(state.can_claim_draw && state.your_turn && state.status === "active");
}

function applyState(nextState) {
  state = nextState;
  board.render(state);
  renderMoveList();
  renderStatus();
  setChatEnabled(state.status === "active");
  syncIndicator.textContent = "Synced";
}

async function submitMove({ from, to, promotion }) {
  syncIndicator.textContent = "Saving move…";
  try {
    const result = await postJSON(`/games/${window.FLASK_CHESS.gameId}/moves`, {
      from,
      to,
      promotion,
      expected_version: state.version,
    });
    applyState(result.state);
    replaceLeaderboard(leaderboardBody, result.leaderboard_html);
  } catch (error) {
    syncIndicator.textContent = error.data?.message || error.message;
    await refreshState(true);
  }
}

async function claimDraw() {
  syncIndicator.textContent = "Claiming draw…";
  try {
    const result = await postJSON(`/games/${window.FLASK_CHESS.gameId}/claim-draw`, {
      expected_version: state.version,
    });
    applyState(result.state);
    replaceLeaderboard(leaderboardBody, result.leaderboard_html);
  } catch (error) {
    syncIndicator.textContent = error.data?.message || error.message;
    await refreshState(true);
  }
}

async function refreshState(force = false) {
  const url = force
    ? `/games/${window.FLASK_CHESS.gameId}/state`
    : `/games/${window.FLASK_CHESS.gameId}/state?since_version=${state.version}`;
  try {
    const payload = await getJSON(url);
    if (!payload.changed && !force) {
      return;
    }
    applyState(payload.state);
    replaceLeaderboard(leaderboardBody, payload.leaderboard_html);
  } catch (error) {
    syncIndicator.textContent = error.message;
  }
}

claimDrawButton.addEventListener("click", claimDraw);
initChat(window.FLASK_CHESS.gameId, window.FLASK_CHESS.currentUserId);
applyState(initialState);
startPoller(() => refreshState(false), window.FLASK_CHESS.pollIntervalMs);
