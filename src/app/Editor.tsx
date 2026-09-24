import { useEffect, useRef } from "preact/hooks";
import { EditorView, basicSetup } from "codemirror";
import { keymap } from "@codemirror/view";
import { EditorState, Prec, type Extension } from "@codemirror/state";
import { indentWithTab } from "@codemirror/commands";
import { python } from "@codemirror/lang-python";
import { oneDark } from "@codemirror/theme-one-dark";

interface Props {
  value: string;
  docKey: string; // changing this swaps in a fresh document (another window, or a loaded save)
  onChange: (code: string) => void;
  onRun: () => void;
}

export function Editor({ value, docKey, onChange, onRun }: Props) {
  const host = useRef<HTMLDivElement>(null);
  const view = useRef<EditorView>();
  const handlers = useRef({ onChange, onRun });
  handlers.current = { onChange, onRun };

  const extensions = useRef<Extension[]>([]);

  useEffect(() => {
    extensions.current = [
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
    ];
    view.current = new EditorView({
      parent: host.current!,
      state: EditorState.create({ doc: value, extensions: extensions.current }),
    });
    return () => view.current?.destroy();
  }, []);

  // Switching window (or loading a save) swaps in a brand-new state with its own undo history,
  // so Ctrl+Z can never pull another window's code into this one.
  useEffect(() => {
    view.current?.setState(EditorState.create({ doc: value, extensions: extensions.current }));
  }, [docKey]);

  return <div class="editor" ref={host} aria-label="Python code editor" />;
}
