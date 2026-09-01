export function replaceLeaderboard(root, html) {
  if (root && typeof html === "string") {
    root.innerHTML = html;
  }
}
