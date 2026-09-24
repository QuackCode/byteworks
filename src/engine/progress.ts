import type { Level } from "../levels";

// Day N unlocks when Day N-1 is complete. A floor unlocks when its first day does.
export function isDayUnlocked(day: number, completed: number[]): boolean {
  return day === 1 || completed.includes(day - 1);
}

export function daysOnFloor(levels: Level[], floor: number): Level[] {
  return levels.filter((l) => l.floor === floor);
}

export function isFloorUnlocked(levels: Level[], floor: number, completed: number[]): boolean {
  const days = daysOnFloor(levels, floor);
  return days.length > 0 && isDayUnlocked(days[0].day, completed);
}

export function isFloorComplete(levels: Level[], floor: number, completed: number[]): boolean {
  const days = daysOnFloor(levels, floor);
  return days.length > 0 && days.every((l) => completed.includes(l.day));
}

/** The next day to play: the first unlocked day that isn't complete yet. */
export function nextDay(levels: Level[], completed: number[]): Level | undefined {
  return levels.find((l) => !completed.includes(l.day) && isDayUnlocked(l.day, completed)) ?? levels.at(-1);
}
