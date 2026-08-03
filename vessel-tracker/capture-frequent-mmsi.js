const WebSocket = require("ws");
const ws = new WebSocket("ws://localhost:8787/ws");
const counts = new Map();

ws.on("open", () => ws.send(JSON.stringify({ type: "track-live" })));

ws.on("message", (raw) => {
  const data = JSON.parse(raw.toString());
  if (data.type === "position" && data.mmsi) {
    const key = data.mmsi + " - " + (data.shipName || "?");
    counts.set(key, (counts.get(key) || 0) + 1);
  }
});

setTimeout(() => {
  ws.close();
  const sorted = [...counts.entries()].sort((a, b) => b[1] - a[1]);
  sorted.forEach(([k, v]) => console.log(v, k));
  process.exit(0);
}, 30000);
