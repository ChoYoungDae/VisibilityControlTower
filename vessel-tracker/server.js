require("dotenv").config();

const path = require("path");
const express = require("express");
const { WebSocketServer, WebSocket } = require("ws");

const PORT = process.env.PORT || 8787;
const AISSTREAM_API_KEY = process.env.AISSTREAM_API_KEY;
const MAPBOX_TOKEN = process.env.MAPBOX_TOKEN;
const AISSTREAM_URL = "wss://stream.aisstream.io/v0/stream";

// aisstream.io's FiltersShipMMSI parameter hasn't reliably returned results in testing,
// and there's effectively no receiver coverage in Korean waters (confirmed via manual
// probing — 0 messages over 60s+ with and without filters). Region-based BoundingBoxes
// subscriptions do work reliably. So for a live "does the connection actually work" demo,
// we subscribe to known-busy straits with real coverage and show whichever real vessel
// reports next, rather than waiting on one specific MMSI that may never be heard from.
const LIVE_DEMO_BBOXES = [
  [[50.5, 0.5], [51.3, 2.0]],   // Dover Strait / English Channel
  [[1.0, 103.5], [1.5, 104.2]], // Singapore Strait
];

const app = express();
app.use(express.static(path.join(__dirname, "public")));

app.get("/config", (_req, res) => {
  res.json({ mapboxToken: MAPBOX_TOKEN || null });
});

const server = app.listen(PORT, () => {
  console.log(`vessel-tracker listening on http://localhost:${PORT}`);
  if (!AISSTREAM_API_KEY) {
    console.warn("AISSTREAM_API_KEY is not set — copy .env.example to .env and add your key.");
  }
  if (!MAPBOX_TOKEN) {
    console.warn("MAPBOX_TOKEN is not set — copy .env.example to .env and add your token.");
  }
});

const wss = new WebSocketServer({ server, path: "/ws" });

wss.on("connection", (client) => {
  let upstream = null;

  const closeUpstream = () => {
    if (upstream && upstream.readyState === WebSocket.OPEN) upstream.close();
    upstream = null;
  };

  client.on("message", (raw) => {
    let msg;
    try {
      msg = JSON.parse(raw.toString());
    } catch {
      return;
    }

    if (msg.type === "stop") {
      closeUpstream();
      return;
    }

    if (msg.type === "track-live") {
      closeUpstream();

      if (!AISSTREAM_API_KEY) {
        client.send(JSON.stringify({ type: "error", message: "Server has no AISSTREAM_API_KEY configured (.env)." }));
        return;
      }

      client.send(JSON.stringify({ type: "status", message: "Connecting to aisstream.io (live region feed)..." }));
      const ws = new WebSocket(AISSTREAM_URL);
      upstream = ws;

      ws.on("open", () => {
        if (upstream !== ws) return;
        ws.send(JSON.stringify({
          APIKey: AISSTREAM_API_KEY,
          BoundingBoxes: LIVE_DEMO_BBOXES,
          FilterMessageTypes: ["PositionReport"],
        }));
        client.send(JSON.stringify({ type: "status", message: "Subscribed to live traffic (Dover Strait + Singapore Strait). Waiting for the next real report..." }));
      });

      ws.on("message", (data) => {
        if (upstream !== ws) return;
        let payload;
        try {
          payload = JSON.parse(data.toString());
        } catch {
          return;
        }
        if (payload.MessageType !== "PositionReport") return;

        const meta = payload.MetaData || payload.Metadata || {};
        const report = (payload.Message && payload.Message.PositionReport) || {};
        const lat = report.Latitude ?? meta.Latitude ?? meta.latitude;
        const lon = report.Longitude ?? meta.Longitude ?? meta.longitude;
        if (typeof lat !== "number" || typeof lon !== "number") return;

        client.send(JSON.stringify({
          type: "position",
          mmsi: String(meta.MMSI ?? meta.mmsi ?? ""),
          shipName: (meta.ShipName ?? meta.ship_name ?? "").trim(),
          lat,
          lon,
          sog: report.Sog,
          cog: report.Cog,
          heading: report.TrueHeading,
          timeUtc: meta.time_utc ?? meta.Time_Utc,
        }));
      });

      ws.on("error", (err) => {
        if (upstream !== ws) return;
        client.send(JSON.stringify({ type: "error", message: "aisstream.io connection error: " + err.message }));
      });

      ws.on("close", () => {
        if (upstream !== ws) return;
        client.send(JSON.stringify({ type: "status", message: "aisstream.io connection closed." }));
      });

      return;
    }

    // Subscribes to the same known-good region BoundingBoxes as "track-live"
    // (aisstream.io's global FiltersShipMMSI subscription has proven unreliable —
    // see the comment on the "track" handler below — but a target MMSI known to
    // be sailing through Dover/Singapore does show up in the region feed), and
    // forwards only reports matching msg.mmsi.
    if (msg.type === "track-in-region" && msg.mmsi) {
      closeUpstream();

      if (!AISSTREAM_API_KEY) {
        client.send(JSON.stringify({ type: "error", message: "Server has no AISSTREAM_API_KEY configured (.env)." }));
        return;
      }

      client.send(JSON.stringify({ type: "status", message: `Connecting to aisstream.io for MMSI ${msg.mmsi} (region feed)...` }));
      const targetMmsi = String(msg.mmsi);
      const ws = new WebSocket(AISSTREAM_URL);
      upstream = ws;

      ws.on("open", () => {
        if (upstream !== ws) return;
        ws.send(JSON.stringify({
          APIKey: AISSTREAM_API_KEY,
          BoundingBoxes: LIVE_DEMO_BBOXES,
          FilterMessageTypes: ["PositionReport"],
        }));
        client.send(JSON.stringify({ type: "status", message: `Subscribed. Waiting for position reports for MMSI ${targetMmsi}...` }));
      });

      ws.on("message", (data) => {
        if (upstream !== ws) return;
        let payload;
        try {
          payload = JSON.parse(data.toString());
        } catch {
          return;
        }
        if (payload.MessageType !== "PositionReport") return;

        const meta = payload.MetaData || payload.Metadata || {};
        const report = (payload.Message && payload.Message.PositionReport) || {};
        const lat = report.Latitude ?? meta.Latitude ?? meta.latitude;
        const lon = report.Longitude ?? meta.Longitude ?? meta.longitude;
        if (typeof lat !== "number" || typeof lon !== "number") return;

        const reportedMmsi = String(meta.MMSI ?? meta.mmsi ?? "");
        if (reportedMmsi !== targetMmsi) return;

        client.send(JSON.stringify({
          type: "position",
          mmsi: reportedMmsi,
          shipName: (meta.ShipName ?? meta.ship_name ?? "").trim(),
          lat,
          lon,
          sog: report.Sog,
          cog: report.Cog,
          heading: report.TrueHeading,
          timeUtc: meta.time_utc ?? meta.Time_Utc,
        }));
      });

      ws.on("error", (err) => {
        if (upstream !== ws) return;
        client.send(JSON.stringify({ type: "error", message: "aisstream.io connection error: " + err.message }));
      });

      ws.on("close", () => {
        if (upstream !== ws) return;
        client.send(JSON.stringify({ type: "status", message: "aisstream.io connection closed." }));
      });

      return;
    }

    if (msg.type === "track" && msg.mmsi) {
      closeUpstream();

      if (!AISSTREAM_API_KEY) {
        client.send(JSON.stringify({ type: "error", message: "Server has no AISSTREAM_API_KEY configured (.env)." }));
        return;
      }

      client.send(JSON.stringify({ type: "status", message: `Connecting to aisstream.io for MMSI ${msg.mmsi}...` }));
      const targetMmsi = String(msg.mmsi);
      const ws = new WebSocket(AISSTREAM_URL);
      upstream = ws;

      // Each handler below closes over `ws` (this specific socket), not the
      // outer `upstream` variable — otherwise a fast-follow "track"/"stop"
      // reassigns/nulls `upstream` before this socket's "open" fires, and
      // upstream.send() throws on null and crashes the process.
      ws.on("open", () => {
        if (upstream !== ws) return;
        ws.send(JSON.stringify({
          APIKey: AISSTREAM_API_KEY,
          BoundingBoxes: [[[-90, -180], [90, 180]]],
          FiltersShipMMSI: [targetMmsi],
          FilterMessageTypes: ["PositionReport"],
        }));
        client.send(JSON.stringify({ type: "status", message: `Subscribed. Waiting for position reports for MMSI ${targetMmsi}...` }));
      });

      ws.on("message", (data) => {
        if (upstream !== ws) return;
        let payload;
        try {
          payload = JSON.parse(data.toString());
        } catch {
          return;
        }
        if (payload.MessageType !== "PositionReport") return;

        const meta = payload.MetaData || payload.Metadata || {};
        const report = (payload.Message && payload.Message.PositionReport) || {};

        // aisstream.io's live payloads don't match their own docs' casing
        // (MetaData uses lowercase latitude/longitude in practice) — prefer
        // Message.PositionReport, which has always come back capitalized.
        const lat = report.Latitude ?? meta.Latitude ?? meta.latitude;
        const lon = report.Longitude ?? meta.Longitude ?? meta.longitude;
        if (typeof lat !== "number" || typeof lon !== "number") return;

        // Belt-and-suspenders: FiltersShipMMSI hasn't reliably filtered in
        // testing, so also filter server-side before forwarding to the client.
        const reportedMmsi = String(meta.MMSI ?? meta.mmsi ?? "");
        if (reportedMmsi !== targetMmsi) return;

        client.send(JSON.stringify({
          type: "position",
          mmsi: reportedMmsi,
          shipName: (meta.ShipName ?? meta.ship_name ?? "").trim(),
          lat,
          lon,
          sog: report.Sog,
          cog: report.Cog,
          heading: report.TrueHeading,
          timeUtc: meta.time_utc ?? meta.Time_Utc,
        }));
      });

      ws.on("error", (err) => {
        if (upstream !== ws) return;
        client.send(JSON.stringify({ type: "error", message: "aisstream.io connection error: " + err.message }));
      });

      ws.on("close", () => {
        if (upstream !== ws) return;
        client.send(JSON.stringify({ type: "status", message: "aisstream.io connection closed." }));
      });
    }
  });

  client.on("close", closeUpstream);
});
