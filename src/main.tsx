import { render } from "preact";
import { App } from "./app/App";
import "./app/styles.css";
import { reloadIfOutdated } from "./engine/update";

reloadIfOutdated();   // an old cached copy of the page swaps itself for the latest version
render(<App />, document.getElementById("app")!);
