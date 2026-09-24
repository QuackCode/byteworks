import { useEffect, useRef } from "preact/hooks";
import { EditorView, basicSetup } from "codemirror";
import { keymap } from "@codemirror/view";
import { Prec } from "@codemirror/state";
import { indentWithTab } from "@codemirror/commands";
import { python } from "@codemirror/lang-python";
import { oneDark } from "@codemirror/theme-one-dark";

interface Props {
  value: string;
  docKey: string; // changing this swaps the document (e.g. a new day)
  onChange: (code: string) => void;
  onRun: () => void;
}

export function Editor({ value, docKey, onChange, onRun }: Props) {
  const host = useRef<HTMLDivElement>(null);
  const view = useRef<EditorView>();
  const handlers = useRef({ onChange, onRun });
  handlers.current = { onChange, onRun };

  useEffect(() => {
    view.current = new EditorView({
      parent: host.current!,
      doc: value,
      extensions: [
        basicSetup,
        python(),
        oneDark,
        EditorView.lineWrapping,
        // Highest precedence: basicSetup binds Mod-Enter to "insert blank line" otherwise
        Prec.highest(keymap.of([
          { key: "Mod-Enter", run: () => (handlers.current.onRun(), true) },
          indentWithTab,
        ])),
        EditorView.updateListener.of((u) => {
          if (u.docChanged) handlers.current.onChange(u.state.doc.toString());
        }),
      ],
    });
    return () => view.current?.destroy();
  }, []);

  // Load a different day's code, or reset to the starter code
  useEffect(() => {
    const v = view.current;
    if (v && v.state.doc.toString() !== value) {
      v.dispatch({ changes: { from: 0, to: v.state.doc.length, insert: value } });
    }
  }, [docKey]);

  return <div class="editor" ref={host} aria-label="Python code editor" />;
}
