import { readFileSync } from "node:fs";
import { R5 } from "../src/dynamic_lift.mjs";
import { runSourceGeometry } from "../src/source_geometry.mjs";
const input = JSON.parse(readFileSync(new URL("../inputs/HD_NATIVE100K_PARA_SLICE.json", import.meta.url), "utf8"));
console.log(JSON.stringify(runSourceGeometry(R5,input),null,2));
