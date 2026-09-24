import { useEffect, useMemo, useRef } from "preact/hooks";
import { marked } from "marked";
import type { Level } from "../levels";
import { runner } from "../engine/runner";

// Every ```python block in a lesson becomes an editable "Try it" box with a Run button.
function attachTryIt(root: HTMLElement) {
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
    btn.textContent = "▶ Run";
    const out = document.createElement("pre");
    out.className = "tryit-out";
    out.hidden = true;
    btn.onclick = async () => {
      btn.disabled = true;
      out.hidden = false;
      out.classList.remove("err");
      out.textContent = runner.status === "ready" ? "Running…" : "Starting Python (first time takes a few seconds)…";
      try {
        const r = await runner.snippet(code.textContent ?? "");
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

export function Lesson({ level }: { level: Level }) {
  const ref = useRef<HTMLDivElement>(null);
  const html = useMemo(() => marked.parse(level.lesson, { async: false }) as string, [level.day]);

  useEffect(() => {
    if (ref.current) {
      attachTryIt(ref.current);
      ref.current.scrollTop = 0;
    }
  }, [html]);

  return (
    <article class="lesson panel">
      <div class="briefing">
        <div class="avatar" aria-hidden="true">👷</div>
        <div>
          <div class="briefing-name">Foreman Flo · Day {level.day}</div>
          <p>{level.briefing}</p>
        </div>
      </div>
      <div class="lesson-body" ref={ref} dangerouslySetInnerHTML={{ __html: html }} />
      <div class="bonus">
        <strong>⭐ Bonus challenge (optional):</strong> {level.bonus}
      </div>
    </article>
  );
}
