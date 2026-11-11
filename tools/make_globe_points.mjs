// Generate land dot coordinates for the 404 globe: [lat*10, lon*10, ...] (Int)
import fs from "fs";
import { feature } from "topojson-client";
import { geoContains } from "d3-geo";
const topo = JSON.parse(fs.readFileSync(new URL("./node_modules/world-atlas/land-110m.json", import.meta.url)));
const land = feature(topo, topo.objects.land);
const out = [];
const step = 1.6; // degrees between rows
for (let lat = -58; lat <= 82; lat += step) {
  const n = Math.max(1, Math.round((360 * Math.cos(lat * Math.PI / 180)) / step));
  for (let i = 0; i < n; i++) {
    const lon = -180 + (i + (Math.round(lat / step) % 2) * 0.5) * (360 / n);
    if (geoContains(land, [lon, lat])) out.push(Math.round(lat * 10), Math.round(lon * 10));
  }
}
fs.writeFileSync(process.argv[2], "window.GLOBE_LAND=[" + out.join(",") + "];\n");
console.log(out.length / 2, "points");
