// Events the Python side sends back for the factory animation.
export type FactoryEvent =
  | { type: "power_on" }
  | { type: "display"; text: string }
  | { type: "part"; label: string; result: "ship" | "reject" | "crash" };

export interface CheckResult {
  passed: boolean;
  message: string;
  stdout: string;
  error: string | null;
  events: FactoryEvent[];
}

export interface SnippetResult {
  stdout: string;
  error: string | null;
}
