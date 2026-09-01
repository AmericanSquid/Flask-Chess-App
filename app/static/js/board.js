const PIECES = {
  P: "♙",
  N: "♘",
  B: "♗",
  R: "♖",
  Q: "♕",
  K: "♔",
  p: "♟",
  n: "♞",
  b: "♝",
  r: "♜",
  q: "♛",
  k: "♚",
};

function maybeReverse(items, orientation) {
  return orientation === "black" ? [...items].reverse() : items;
}

function isPromotionMove(pieceSymbol, targetSquare) {
  if (!pieceSymbol) return false;
  const rank = targetSquare.slice(1);
  return (pieceSymbol === "P" && rank === "8") || (pieceSymbol === "p" && rank === "1");
}

function readBoardCell(state, square) {
  for (const row of state.board) {
    for (const cell of row) {
      if (cell.square === square) return cell;
    }
  }
  return null;
}

function ownPiece(state, square) {
  const cell = readBoardCell(state, square);
  if (!cell?.piece || !state.player_color) return false;
  return state.player_color === "white" ? cell.piece === cell.piece.toUpperCase() : cell.piece === cell.piece.toLowerCase();
}

function choosePromotion(modal) {
  modal.classList.remove("hidden");
  modal.setAttribute("aria-hidden", "false");
  return new Promise((resolve) => {
    const buttons = modal.querySelectorAll("[data-promotion]");
    const cleanup = () => {
      modal.classList.add("hidden");
      modal.setAttribute("aria-hidden", "true");
      buttons.forEach((button) => button.removeEventListener("click", handleClick));
    };
    const handleClick = (event) => {
      cleanup();
      const value = event.currentTarget.dataset.promotion || null;
      resolve(value || null);
    };
    buttons.forEach((button) => button.addEventListener("click", handleClick));
  });
}

export function createBoardController({ root, promotionModal, onMoveRequest }) {
  let state = null;
  let selectedSquare = null;

  async function handleSquareClick(square) {
    if (!state || !state.your_turn || state.status !== "active") return;

    if (selectedSquare) {
      if (square === selectedSquare) {
        selectedSquare = null;
        render(state);
        return;
      }

      const legalTargets = state.legal_moves[selectedSquare] || [];
      if (legalTargets.includes(square)) {
        const movingCell = readBoardCell(state, selectedSquare);
        let promotion = null;
        if (isPromotionMove(movingCell?.piece, square)) {
          promotion = await choosePromotion(promotionModal);
          if (!promotion) {
            selectedSquare = null;
            render(state);
            return;
          }
        }
        const from = selectedSquare;
        selectedSquare = null;
        render(state);
        onMoveRequest({ from, to: square, promotion });
        return;
      }

      if (ownPiece(state, square)) {
        selectedSquare = square;
        render(state);
        return;
      }

      selectedSquare = null;
      render(state);
      return;
    }

    if (ownPiece(state, square)) {
      selectedSquare = square;
      render(state);
    }
  }

  function render(nextState) {
    state = nextState;
    root.innerHTML = "";

    const rows = maybeReverse(state.board, state.orientation);
    for (const row of rows) {
      const orientedRow = maybeReverse(row, state.orientation);
      for (const cell of orientedRow) {
        const fileIndex = cell.square.charCodeAt(0) - 97;
        const rankIndex = Number(cell.square.slice(1)) - 1;
        const isDark = (fileIndex + rankIndex) % 2 === 1;
        const button = document.createElement("button");
        button.type = "button";
        button.className = `square ${isDark ? "dark" : "light"}`;
        button.dataset.square = cell.square;
        button.textContent = cell.piece ? PIECES[cell.piece] : "";
        if (selectedSquare === cell.square) {
          button.classList.add("selected");
        }
        const legalTargets = selectedSquare ? state.legal_moves[selectedSquare] || [] : [];
        if (legalTargets.includes(cell.square)) {
          button.classList.add("legal");
        }
        button.addEventListener("click", () => handleSquareClick(cell.square));
        root.appendChild(button);
      }
    }
  }

  return { render };
}
