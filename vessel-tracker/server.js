require("dotenv").config();

const path = require("path");
const express = require("express");
const { WebSocketServer } = require("ws");

const PORT = process.env.PORT || 8787;
const MAPBOX_TOKEN = process.env.MAPBOX_TOKEN;
const SEAVANTAGE_USERNAME = process.env.SEAVANTAGE_USERNAME;
const SEAVANTAGE_PASSWORD = process.env.SEAVANTAGE_PASSWORD;
const SEAVANTAGE_BASE_URL = process.env.SEAVANTAGE_BASE_URL || "https://svmp.seavantage.com/api/v1";
const POLL_INTERVAL_MS = Number(process.env.SEAVANTAGE_POLL_INTERVAL_MS) || 15000;
// /ship/snapshot/:shipId requires a dateTime + a "range" whose unit isn't
// documented (assumed minutes) — how far back from dateTime a position report
// still counts as current. Widened default so a slightly-stale AIS report
// still comes back instead of a false "no data".
const SNAPSHOT_RANGE = Number(process.env.SEAVANTAGE_SNAPSHOT_RANGE) || 60;

const app = express();
app.use(express.static(path.join(__dirname, "public")));

app.get("/config", (_req, res) => {
  res.json({ mapboxToken: MAPBOX_TOKEN || null });
});

const server = app.listen(PORT, () => {
  console.log(`vessel-tracker listening on http://localhost:${PORT}`);
  if (!SEAVANTAGE_USERNAME || !SEAVANTAGE_PASSWORD) {
    console.warn("SEAVANTAGE_USERNAME/SEAVANTAGE_PASSWORD is not set — copy .env.example to .env and add your SeaVantage account.");
  }
  if (!MAPBOX_TOKEN) {
    console.warn("MAPBOX_TOKEN is not set — copy .env.example to .env and add your token.");
  }
});

const wss = new WebSocketServer({ server, path: "/ws" });

function authHeader() {
  const token = Buffer.from(`${SEAVANTAGE_USERNAME}:${SEAVANTAGE_PASSWORD}`).toString("base64");
  return `Basic ${token}`;
}

async function svGet(pathAndQuery) {
  const res = await fetch(`${SEAVANTAGE_BASE_URL}${pathAndQuery}`, {
    headers: { Authorization: authHeader(), Accept: "application/json" },
  });
  const body = await res.json().catch(() => null);
  if (!res.ok || (body && body.error)) {
    const message = (body && (body.error_message || body.message)) || `HTTP ${res.status}`;
    const err = new Error(message);
    err.status = res.status;
    throw err;
  }
  return body;
}

function isoNow() {
  return new Date().toISOString().replace(/\.\d+Z$/, "Z");
}

// SVMP has no "get position by MMSI" endpoint. You resolve MMSI/IMO/name to a
// shipId once via /ship/search, then poll /ship/snapshot/:shipId for that
// one ship's latest position, worldwide — no bounding box needed. This cache
// avoids re-searching on every poll tick.
const shipIdCache = new Map();

async function resolveShipId(mmsi) {
  if (shipIdCache.has(mmsi)) return shipIdCache.get(mmsi);
  const body = await svGet(`/ship/search?keyword=${encodeURIComponent(mmsi)}`);
  const candidates = body.response || [];
  const match = candidates.find((s) => String(s.mmsi) === String(mmsi)) || candidates[0];
  if (!match) return null;
  shipIdCache.set(mmsi, match.shipId);
  return match.shipId;
}

async function fetchShipPosition(shipId) {
  const body = await svGet(`/ship/snapshot/${shipId}?dateTime=${encodeURIComponent(isoNow())}&range=${SNAPSHOT_RANGE}`);
  return body.response || body;
}

function toPositionMessage(ship) {
  const p = ship.position || {};
  return {
    type: "position",
    mmsi: String(p.mmsi ?? ship.mmsi ?? ""),
    shipName: (p.shipName ?? ship.shipName ?? "").trim(),
    lat: p.latitude,
    lon: p.longitude,
    sog: p.speedOverGround,
    cog: p.courseOverGround,
    heading: p.trueHeading,
    timeUtc: p.timestamp,
  };
}

wss.on("connection", (client) => {
  let pollTimer = null;

  const stopPolling = () => {
    if (pollTimer) clearInterval(pollTimer);
    pollTimer = null;
  };

  const startTrackingMmsi = async (mmsi) => {
    stopPolling();

    if (!SEAVANTAGE_USERNAME || !SEAVANTAGE_PASSWORD) {
      client.send(JSON.stringify({ type: "error", message: "Server has no SEAVANTAGE_USERNAME/SEAVANTAGE_PASSWORD configured (.env)." }));
      return;
    }

    client.send(JSON.stringify({ type: "status", message: `Looking up MMSI ${mmsi} on SeaVantage...` }));
    let shipId;
    try {
      shipId = await resolveShipId(mmsi);
    } catch (err) {
      client.send(JSON.stringify({ type: "error", message: "SeaVantage ship search failed: " + err.message }));
      return;
    }
    if (!shipId) {
      client.send(JSON.stringify({ type: "error", message: `MMSI ${mmsi} not found on SeaVantage.` }));
      return;
    }

    const poll = async () => {
      try {
        const ship = await fetchShipPosition(shipId);
        if (!ship || !ship.position || typeof ship.position.latitude !== "number") {
          client.send(JSON.stringify({ type: "status", message: `Waiting for a recent position report for MMSI ${mmsi}...` }));
          return;
        }
        client.send(JSON.stringify(toPositionMessage(ship)));
      } catch (err) {
        client.send(JSON.stringify({ type: "error", message: "SeaVantage API error: " + err.message }));
      }
    };

    client.send(JSON.stringify({ type: "status", message: `Subscribed. Polling MMSI ${mmsi} every ${POLL_INTERVAL_MS / 1000}s...` }));
    await poll();
    pollTimer = setInterval(poll, POLL_INTERVAL_MS);
  };

  client.on("message", (raw) => {
    let msg;
    try {
      msg = JSON.parse(raw.toString());
    } catch {
      return;
    }

    if (msg.type === "stop") {
      stopPolling();
      return;
    }

    if (msg.type === "track" && msg.mmsi) {
      startTrackingMmsi(String(msg.mmsi));
      return;
    }
  });

  client.on("close", stopPolling);
});
