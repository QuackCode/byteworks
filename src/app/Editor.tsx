import { useEffect, useRef } from "preact/hooks";
import { EditorView, basicSetup } from "codemirror";
import { Decoration, keymap, type DecorationSet } from "@codemirror/view";
import { EditorState, Prec, StateEffect, StateField, type Extension } from "@codemirror/state";
import { indentWithTab } from "@codemirror/commands";
import { python } from "@codemirror/lang-python";
import { oneDark } from "@codemirror/theme-one-dark";

// The line the drone is carrying out right now (null = nothing running here)
const setRunningLine = StateEffect.define<number | null>();
const runningLineMark = Decoration.line({ class: "cm-running-line" });
const runningLine = StateField.define<DecorationSet>({
  create: () => Decoration.none,
  update(marks, tr) {
    marks = marks.map(tr.changes);
    for (const e of tr.effects) {
      if (e.is(setRunningLine)) {
        const n = e.value;
        marks = n !== null && n >= 1 && n <= tr.state.doc.lines
          ? Decoration.set([runningLineMark.range(tr.state.doc.line(n).from)])
          : Decoration.none;
      }
    }
    return marks;
  },
  provide: (f) => EditorView.decorations.from(f),
});

interface Props {
  value: string;
  runningLine?: number | null;
  docKey: string; // changing this swaps in a fresh document (another window, or a loaded save)
  onChange: (code: string) => void;
  onRun: () => void;
}

export function Editor({ value, docKey, onChange, onRun, runningLine: line = null }: Props) {
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
      runningLine,
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

  // Highlight the running line, and keep it in view while the program runs
  useEffect(() => {
    const v = view.current;
    if (!v) return;
    const effects: StateEffect<unknown>[] = [setRunningLine.of(line)];
    if (line !== null && line >= 1 && line <= v.state.doc.lines) {
      effects.push(EditorView.scrollIntoView(v.state.doc.line(line).from, { y: "nearest" }));
    }
    v.dispatch({ effects });
  }, [line, docKey]);

  return <div class="editor" ref={host} aria-label="Python code editor" />;
}
