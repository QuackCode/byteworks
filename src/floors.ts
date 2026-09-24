export interface FloorInfo { id: string; label: string; name: string; icon: string; color: string; unlock: string | null }

// Bottom to top. `unlock` is the upgrade that opens the floor (null = open from the start).
export const FLOORS: FloorInfo[] = [
  { id: "RAM", label: "G", name: "RAM Floor", icon: "🧠", color: "#4cc38a", unlock: null },
  { id: "CPU", label: "1", name: "CPU Floor", icon: "🔲", color: "#5aa9ff", unlock: "floor_cpu" },
  { id: "SSD", label: "2", name: "SSD Floor", icon: "💾", color: "#b18cff", unlock: "floor_ssd" },
  { id: "BOARD", label: "3", name: "Motherboard Floor", icon: "🟩", color: "#3fd0c9", unlock: "floor_board" },
  { id: "GPU", label: "4", name: "GPU Floor", icon: "🎮", color: "#ff7a59", unlock: "floor_gpu" },
  { id: "ASSEMBLY", label: "5", name: "Final Assembly", icon: "🖥️", color: "#ff5c8a", unlock: "floor_assembly" },
];

export const PART_ICON: Record<string, string> = { RAM: "🧠", CPU: "🔲", SSD: "💾", BOARD: "🟩", GPU: "🎮", COMPUTER: "🖥️" };
export const PARTS_ORDER = ["RAM", "CPU", "SSD", "BOARD", "GPU", "COMPUTER"];

// Keep equal to WIN_COMPUTERS in src/python/game/balance.py (a Python test checks this).
export const WIN_COMPUTERS = 10;
