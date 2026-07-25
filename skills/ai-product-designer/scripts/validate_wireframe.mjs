#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
const input = args.find((arg) => !arg.startsWith("--"));
const allowGoogleFonts = args.includes("--allow-google-fonts");
if (!input) {
  console.error("Usage: node validate_wireframe.mjs <index.html> [--allow-google-fonts]");
  process.exit(2);
}

const htmlPath = path.resolve(input);
const root = path.dirname(htmlPath);
const html = fs.readFileSync(htmlPath, "utf8");
const findings = [];

function check(id, pass, message, severity = "error") {
  findings.push({ id, pass: Boolean(pass), severity, message });
}

check("document-title", /<title>\s*[^<]+\s*<\/title>/i.test(html), "Document has a non-empty title.");
check("document-lang", /<html[^>]+\blang=["'][^"']+["']/i.test(html), "HTML declares a language.");
check("viewport", /<meta[^>]+name=["']viewport["']/i.test(html), "Document declares a viewport.");
check("main-landmark", /<main(?:\s|>)/i.test(html), "Document has a main landmark.");
check("scope-status", /data-design-status=/i.test(html), "Document declares design status.");
check("visible-focus", /:focus-visible/i.test(html) || linkedFiles(html, root, "stylesheet").some(hasFocusVisible), "Visible focus styles are defined.");
check(
  "template-resolved",
  !/data-template-state=["']unresolved["']/i.test(html)
    && !/data-template-placeholder(?:=|\s|>)/i.test(html),
  "No unresolved scaffold markers remain.",
);
check(
  "review-status",
  /data-design-status=["'](?:review-ready|visually-inspected)["']/i.test(html),
  "Artifact status is review-ready or visually-inspected.",
);
check(
  "design-directions",
  /data-design-direction=["'][^"']+["']/i.test(html),
  "Artifact contains at least one marked design direction.",
);
const screenTags = [...html.matchAll(/<[^>]*\bdata-wireframe-screen\b[^>]*>/gi)].map((match) => match[0]);
check(
  "wireframe-screens",
  screenTags.length > 0,
  "Artifact contains at least one marked wireframe screen.",
);
const untracedScreens = screenTags.filter(
  (tag) => !/\bdata-screen-id=["'][^"']+["']/i.test(tag)
    || !/\bdata-requirement-ids=["'][^"']+["']/i.test(tag),
);
check(
  "screen-traceability",
  untracedScreens.length === 0,
  untracedScreens.length
    ? `${untracedScreens.length} screen(s) lack data-screen-id or data-requirement-ids.`
    : "Every screen has an ID and requirement trace.",
);
const starterCopy = [
  "Design exploration",
  "State the design hypothesis",
  "Replace with",
  "画面タイトル",
  "ここに画面を実装",
].filter((marker) => html.toLocaleLowerCase().includes(marker.toLocaleLowerCase()));
check(
  "starter-copy",
  starterCopy.length === 0,
  starterCopy.length
    ? `Starter copy remains: ${starterCopy.join(", ")}`
    : "No known starter copy remains.",
);

const remotePattern = /(?:https?:)?\/\/[^\s"'<>]+/gi;
const remoteRefs = [...html.matchAll(remotePattern)].map((match) => match[0]);
for (const css of linkedFiles(html, root, "stylesheet")) {
  remoteRefs.push(...(fs.readFileSync(css, "utf8").match(remotePattern) ?? []));
}
for (const script of linkedFiles(html, root, "script")) {
  remoteRefs.push(...(fs.readFileSync(script, "utf8").match(remotePattern) ?? []));
}
const uniqueRemoteRefs = [...new Set(remoteRefs)];
const approvedFontRefs = allowGoogleFonts
  ? uniqueRemoteRefs.filter(isGoogleFontReference)
  : [];
const prohibitedRemoteRefs = uniqueRemoteRefs.filter((ref) => !approvedFontRefs.includes(ref));
check(
  "offline-dependencies",
  prohibitedRemoteRefs.length === 0,
  prohibitedRemoteRefs.length
    ? `Unapproved remote references found: ${prohibitedRemoteRefs.join(", ")}`
    : "No unapproved remote references found.",
);
check(
  "approved-google-fonts",
  approvedFontRefs.length === 0,
  approvedFontRefs.length
    ? `Approved Google Fonts network dependency: ${approvedFontRefs.join(", ")}`
    : "No Google Fonts network dependency found.",
  "warning",
);

const localRefs = [
  ...attributeValues(html, "link", "href"),
  ...attributeValues(html, "script", "src"),
  ...attributeValues(html, "img", "src"),
].filter(isLocalFileReference);
const missing = localRefs.filter((ref) => !fs.existsSync(path.resolve(root, stripQuery(ref))));
check(
  "local-files",
  missing.length === 0,
  missing.length ? `Missing local files: ${missing.join(", ")}` : "Referenced local files exist.",
);

const interactiveWithoutLabel = [...html.matchAll(/<(button|a)\b([^>]*)>([\s\S]*?)<\/\1>/gi)]
  .filter((match) => stripTags(match[3]).trim() === "" && !/aria-label=["'][^"']+["']/i.test(match[2]));
check(
  "control-labels",
  interactiveWithoutLabel.length === 0,
  interactiveWithoutLabel.length
    ? `${interactiveWithoutLabel.length} interactive element(s) have no text or aria-label.`
    : "Buttons and links have detectable labels.",
  "warning",
);

const failures = findings.filter((item) => !item.pass);
const errorCount = failures.filter((item) => item.severity === "error").length;
const warningCount = failures.filter((item) => item.severity === "warning").length;
for (const item of findings) {
  console.log(`${item.pass ? "PASS" : item.severity === "warning" ? "WARN" : "FAIL"} ${item.id}: ${item.message}`);
}
console.log(`\n${findings.length - failures.length}/${findings.length} checks passed; ${warningCount} warning(s); ${errorCount} error(s).`);
process.exit(errorCount > 0 ? 1 : 0);

function attributeValues(source, tag, attribute) {
  const tagPattern = new RegExp(`<${tag}\\b[^>]*\\b${attribute}=["']([^"']+)["'][^>]*>`, "gi");
  return [...source.matchAll(tagPattern)].map((match) => match[1]);
}

function linkedFiles(source, base, kind) {
  const refs = kind === "stylesheet"
    ? attributeValues(source, "link", "href").filter((ref) => ref.endsWith(".css"))
    : attributeValues(source, "script", "src").filter((ref) => ref.endsWith(".js"));
  return refs.filter(isLocalFileReference).map((ref) => path.resolve(base, stripQuery(ref))).filter(fs.existsSync);
}

function hasFocusVisible(file) {
  return /:focus-visible/i.test(fs.readFileSync(file, "utf8"));
}

function isLocalFileReference(ref) {
  return !/^(?:[a-z]+:)?\/\//i.test(ref) && !ref.startsWith("data:") && !ref.startsWith("#");
}

function stripQuery(ref) {
  return ref.split(/[?#]/, 1)[0];
}

function stripTags(value) {
  return value.replace(/<[^>]+>/g, " ");
}

function isGoogleFontReference(ref) {
  try {
    const normalized = ref.startsWith("//") ? `https:${ref}` : ref;
    const hostname = new URL(normalized).hostname;
    return hostname === "fonts.googleapis.com" || hostname === "fonts.gstatic.com";
  } catch {
    return false;
  }
}
