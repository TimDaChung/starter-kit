// Dev-notes feedback channel for single-file HTML playtests.
// Players type a line starting with the prefix; it is stored instead of sent to the game.
const DEV_NOTES_KEY = "dev_notes";
const DEV_NOTES_PREFIX = "開發者表示：";

function readDevNotes() { return JSON.parse(localStorage.getItem(DEV_NOTES_KEY) || "[]"); }
function exportDevNotes() { return JSON.stringify(readDevNotes()); }
function clearDevNotes() { localStorage.removeItem(DEV_NOTES_KEY); }

function pushDevNote(text, context) {
  const notes = readDevNotes();
  notes.push({ ts: new Date().toISOString(), text: text.slice(DEV_NOTES_PREFIX.length).trim(), context: context || null });
  localStorage.setItem(DEV_NOTES_KEY, JSON.stringify(notes));
}

// Wire to the game input: intercepts prefixed text on Enter / send button, returns true when swallowed.
function attachDevNotesInterceptor(inputEl, sendBtn, getContext) {
  const tryIntercept = () => {
    const text = inputEl.value || "";
    if (!text.startsWith(DEV_NOTES_PREFIX)) return false;
    pushDevNote(text, getContext ? getContext() : null);
    inputEl.value = "";
    return true;
  };
  inputEl.addEventListener("keydown", (e) => { if (e.key === "Enter" && tryIntercept()) e.preventDefault(); });
  if (sendBtn) sendBtn.addEventListener("click", (e) => { if (tryIntercept()) e.stopImmediatePropagation(); }, true);
}
