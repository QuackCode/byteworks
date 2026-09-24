import { useEffect, useMemo, useRef } from "preact/hooks";
import { marked } from "marked";
import type { UnlockInfo } from "../engine/types";
import { attachTryIt } from "./tryit";

const files = import.meta.glob("../help/*.md", { query: "?raw", import: "default", eager: true }) as Record<string, string>;
const PAGES: Record<string, string> = Object.fromEntries(
  Object.entries(files).map(([path, text]) => [path.split("/").pop()!.replace(/\.md$/, ""), text]),
);
const titleOf = (id: string) => (PAGES[id] ?? "# ?").split("\n")[0].replace(/^# /, "");

interface Props {
  helpId: string; tree: UnlockInfo[]; owned: Set<string>; questsDone: Set<string>; running: boolean;
  onPick: (helpId: string) => void; onClose: () => void;
}

export function HelpPanel({ helpId, tree, owned, questsDone, running, onPick, onClose }: Props) {
  const body = useRef<HTMLDivElement>(null);
  const runningRef = useRef(running);
  runningRef.current = running;
  const topics = ["start", ...tree.filter((u) => u.help && owned.has(u.id)).map((u) => u.help!)];
  const html = useMemo(() => marked.parse(PAGES[helpId] ?? PAGES.start, { async: false }) as string, [helpId]);

  useEffect(() => {
    if (!body.current) return;
    attachTryIt(body.current, () => !runningRef.current);
    body.current.scrollTop = 0;
  }, [html]);

  return (
    <aside class="drawer panel" role="dialog" aria-label="Help">
      <div class="drawer-head">
        <h2>📖 Help</h2>
        <button class="btn small" onClick={onClose}>Close</button>
      </div>
      <nav class="help-topics">
        {topics.map((id) => (
          <button key={id} class={`chip ${id === helpId ? "on" : ""}`} onClick={() => onPick(id)}>{titleOf(id)}</button>
        ))}
      </nav>
      {questBanner(helpId, tree, questsDone)}
      <div class="help-body" ref={body} dangerouslySetInnerHTML={{ __html: html }} />
    </aside>
  );
}

/** The quest on this help page (if any) and which upgrade it opens up. */
function questBanner(helpId: string, tree: UnlockInfo[], questsDone: Set<string>) {
  const gated = tree.find((u) => u.quest?.page === helpId);
  if (!gated?.quest) return null;
  const done = questsDone.has(gated.quest.id);
  return (
    <div class={`quest-banner ${done ? "done" : ""}`} role="status">
      <strong>{done ? "✓ Quest complete" : "🎯 Quest"}</strong>
      <span>{gated.quest.title}</span>
      <small>{done ? `You can buy ${gated.title} once you have the parts.` : `Finish it to be able to buy ${gated.title}.`}</small>
    </div>
  );
}
