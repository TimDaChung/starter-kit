// Legacy adapter: seth-reward-demo predates the DEMO_API contract.
(() => {
  const buttons = () => [...document.querySelectorAll('#force-btns .force')];
  window.DEMO_API = {
    scenarios: buttons().map((b, i) => ({ id: String(i), name: b.textContent.trim() })),
    play(id) {
      return new Promise((resolve) => {
        buttons()[+id].click();
        const t = setInterval(() => { if (!running) { clearInterval(t); resolve(); } }, 100);
      });
    },
    pause() { setPauseUI(true); },
    resume() { setPauseUI(false); },
  };
  const original = hudPhase;
  hudPhase = function (label, sub, dur) {
    window.dispatchEvent(new CustomEvent('demo:phase', { detail: { name: sub.replace(/（[\d.]+s）$/, ''), ms: dur } }));
    return original(label, sub, dur);
  };
})();
