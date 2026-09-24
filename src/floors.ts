export interface Floor {
  id: number;
  label: string; // shown on the elevator buttons
  name: string;
  part: string;
  icon: string;
  color: string;
}

// One floor per computer part. Each level's meta.json says which floor it belongs to.
export const FLOORS: Floor[] = [
  { id: 0, label: "G", name: "Control Room", part: "Power & control", icon: "⚡", color: "#f5b841" },
  { id: 1, label: "1", name: "RAM Floor", part: "RAM sticks", icon: "🧠", color: "#4cc38a" },
  { id: 2, label: "2", name: "CPU Floor", part: "Processors", icon: "🔲", color: "#5aa9ff" },
  { id: 3, label: "3", name: "Storage Floor", part: "SSDs", icon: "💾", color: "#b18cff" },
  { id: 4, label: "4", name: "Motherboard Floor", part: "Motherboards", icon: "🟩", color: "#3fd0c9" },
  { id: 5, label: "5", name: "GPU Floor", part: "Graphics cards", icon: "🎮", color: "#ff7a59" },
  { id: 6, label: "6", name: "Shipping & Orders", part: "Orders & delivery", icon: "📦", color: "#e2c275" },
  { id: 7, label: "7", name: "Final Assembly", part: "Complete computers", icon: "🖥️", color: "#ff5c8a" },
];
