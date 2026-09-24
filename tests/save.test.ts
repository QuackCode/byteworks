import { describe, expect, it } from "vitest";
import { decodeSave, emptySave, encodeSave, STARTER } from "../src/engine/save";

describe("save v2", () => {
  it("starts with the welcome program", () => {
    const s = emptySave();
    expect(s.files["main.py"]).toBe(STARTER);
    expect(s.active).toBe("main.py");
    expect(s.world).toBeNull();
  });

  it("round-trips, including emoji in code", () => {
    const s = { ...emptySave(), files: { "main.py": "print('🏭 héllo')", "helpers.py": "" } };
    expect(decodeSave(encodeSave(s))).toEqual(s);
  });

  it("rejects junk, v1 codes and broken shapes", () => {
    expect(decodeSave("nope")).toBeNull();
    expect(decodeSave("BW1.e30=")).toBeNull();
    expect(decodeSave("BW2.!!!")).toBeNull();
    const bad = { ...emptySave(), active: "missing.py" };
    expect(decodeSave(encodeSave(bad as never))).toBeNull();
  });
});
