import { describe, expect, it } from "vitest";
import { decodeSave, emptySave, encodeSave } from "../src/engine/save";
import { isDayUnlocked, isFloorComplete, isFloorUnlocked, nextDay } from "../src/engine/progress";
import type { Level } from "../src/levels";

const lvl = (day: number, floor: number) => ({ day, floor }) as Level;
const levels = [lvl(1, 0), lvl(2, 0), lvl(3, 1), lvl(4, 1)];

describe("save codes", () => {
  it("round-trips progress and code, including non-ASCII text", () => {
    const save = { ...emptySave(), completed: [1, 2], code: { "1": 'print("héllo 🏭")' } };
    expect(decodeSave(encodeSave(save))).toEqual(save);
  });

  it("rejects junk", () => {
    expect(decodeSave("hello")).toBeNull();
    expect(decodeSave("BW1.!!!")).toBeNull();
    expect(decodeSave("BW1." + btoa('{"v":2}'))).toBeNull();
  });
});

describe("progress", () => {
  it("unlocks days in order", () => {
    expect(isDayUnlocked(1, [])).toBe(true);
    expect(isDayUnlocked(2, [])).toBe(false);
    expect(isDayUnlocked(2, [1])).toBe(true);
  });

  it("unlocks a floor when its first day unlocks", () => {
    expect(isFloorUnlocked(levels, 1, [1])).toBe(false);
    expect(isFloorUnlocked(levels, 1, [1, 2])).toBe(true);
    expect(isFloorComplete(levels, 0, [1, 2])).toBe(true);
  });

  it("picks the next unfinished day", () => {
    expect(nextDay(levels, [])?.day).toBe(1);
    expect(nextDay(levels, [1, 2])?.day).toBe(3);
    expect(nextDay(levels, [1, 2, 3, 4])?.day).toBe(4);
  });
});
