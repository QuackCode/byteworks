import { describe, expect, it } from "vitest";
import { lookOf, moveDuration, svgRow } from "../src/app/floorMath";

describe("tile looks", () => {
  it("shows growth progress", () => {
    const look = lookOf(["CPU", 200, false, null, 100], 150);
    expect(look).toEqual({ part: "CPU", ready: false, progress: 0.5, faulty: false, score: null });
  });
  it("hides a faulty board until it's ready", () => {
    expect(lookOf(["BOARD", 200, true, null, 100], 150).faulty).toBe(false);
    expect(lookOf(["BOARD", 200, true, null, 100], 250).faulty).toBe(true);
  });
  it("shows GPU scores and handles empty tiles", () => {
    expect(lookOf(["GPU", 0, false, 7, 0], 5).score).toBe(7);
    expect(lookOf([null, 0, false, null, 0], 5)).toEqual({ part: null, ready: false, progress: 0, faulty: false, score: null });
  });
});

describe("drone movement", () => {
  const at = (x: number, y: number, floor = "RAM") => ({ floor, x, y });
  it("slides one step", () => expect(moveDuration(at(0, 0), at(1, 0), 200)).toBe(200));
  it("jumps when moving more than one square", () => expect(moveDuration(at(2, 0), at(0, 0), 200)).toBe(0));
  it("jumps when changing floor or on first draw", () => {
    expect(moveDuration(at(0, 0), at(0, 0, "CPU"), 200)).toBe(0);
    expect(moveDuration(null, at(0, 0), 200)).toBe(0);
  });
  it("puts North at the top", () => expect(svgRow(0, 3)).toBe(2));
});
