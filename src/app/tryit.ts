import { game } from "../engine/game";

/** Turn every Python example block (language-python) inside `root` into an editable box with a Run button. */
export function attachTryIt(root: HTMLElement, canRun: () => boolean) {
  root.querySelectorAll("pre > code.language-python").forEach((code) => {
    const pre = code.parentElement!;
    if (pre.parentElement?.classList.contains("tryit")) return;
    const box = document.createElement("div");
    box.className = "tryit";
    pre.replaceWith(box);
    box.appendChild(pre);
    code.setAttribute("contenteditable", "plaintext-only");
    code.setAttribute("spellcheck", "false");
    const bar = document.createElement("div");
    bar.className = "tryit-bar";
    const btn = document.createElement("button");
    btn.className = "btn small";
    btn.textContent = "▶ Try it";
    const out = document.createElement("pre");
    out.className = "tryit-out";
    out.hidden = true;
    btn.onclick = async () => {
      out.hidden = false;
      out.classList.remove("err");
      if (!canRun()) {
        out.textContent = "Stop your drone program first. Python can only do one thing at a time.";
        return;
      }
      btn.disabled = true;
      out.textContent = "Running…";
      try {
        const r = await game.snippet(code.textContent ?? "");
        out.textContent = (r.stdout || "") + (r.error ? (r.stdout ? "\n" : "") + r.error : "") || "(no output)";
        out.classList.toggle("err", !!r.error);
      } catch (e) {
        out.textContent = String(e);
        out.classList.add("err");
      } finally {
        btn.disabled = false;
      }
    };
    bar.append(btn);
    box.append(bar, out);
  });
}
