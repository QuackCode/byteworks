import { useState } from "preact/hooks";
import { decodeSave, encodeSave, type Save } from "../engine/save";

interface Props {
  save: Save;
  running: boolean;
  onLoad: (save: Save) => void;
  onResetAll: () => void;
  onClose: () => void;
}

export function SaveDialog({ save, running, onLoad, onResetAll, onClose }: Props) {
  const [importText, setImportText] = useState("");
  const [msg, setMsg] = useState("");
  const [confirmWipe, setConfirmWipe] = useState(false);
  const code = encodeSave(save);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setMsg("Copied! Paste it somewhere safe.");
    } catch {
      setMsg("Couldn't copy automatically. Select the code and copy it yourself.");
    }
  };

  const load = () => {
    const loaded = decodeSave(importText);
    if (!loaded) return setMsg("That save code doesn't look right. Make sure you copied all of it.");
    onLoad(loaded);
    setMsg("Loaded! Your factory is back.");
  };

  return (
    <div class="modal-backdrop" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div class="modal panel" role="dialog" aria-modal="true" aria-labelledby="save-title">
        <h2 id="save-title">💾 Your save</h2>
        <p>Progress saves automatically in this browser. To carry on from another computer, copy your save code and load it there.</p>
        {running && <p class="modal-msg">Stop your program first to load or reset a save.</p>}
        <label class="field-label">Your save code</label>
        <textarea readOnly rows={3} value={code} onFocus={(e) => (e.target as HTMLTextAreaElement).select()} />
        <button class="btn primary small" onClick={copy}>Copy save code</button>

        <label class="field-label">Load a save code</label>
        <textarea rows={3} placeholder="Paste a code starting with BW2." value={importText}
          onInput={(e) => setImportText((e.target as HTMLTextAreaElement).value)} />
        <button class="btn small" onClick={load} disabled={running || !importText.trim()}>Load save</button>

        {msg && <p class="modal-msg" role="status">{msg}</p>}

        <div class="modal-foot">
          {confirmWipe ? (
            <>
              <span>Delete ALL progress?</span>
              <button class="btn danger small" onClick={() => { onResetAll(); setConfirmWipe(false); setMsg("Progress reset."); }}>Yes, delete</button>
              <button class="btn small" onClick={() => setConfirmWipe(false)}>Cancel</button>
            </>
          ) : (
            <button class="btn ghost small" disabled={running} onClick={() => setConfirmWipe(true)}>Reset all progress</button>
          )}
          <span class="spacer" />
          <button class="btn small" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
}
