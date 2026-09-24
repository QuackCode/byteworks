import { describe, expect, it } from "vitest";
import { cleanUrl, freshUrl } from "../src/engine/update";

describe("update check", () => {
  const page = "https://quackcode.github.io/byteworks/";
  it("does nothing when the page is already the latest build", () => {
    expect(freshUrl(page, "abc", "abc")).toBeNull();
  });
  it("reloads a stale page on a fresh URL the browser hasn't cached", () => {
    expect(freshUrl(page, "old", "new")).toBe(page + "?v=new");
  });
  it("never loops if the fresh URL still served an old copy", () => {
    expect(freshUrl(page + "?v=new", "old", "new")).toBeNull();
  });
  it("tidies the ?v= marker off the address afterwards", () => {
    expect(cleanUrl(page + "?v=new")).toBe(page);
    expect(cleanUrl(page)).toBeNull();
  });
});
