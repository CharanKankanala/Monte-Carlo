import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(
    new Request("http://localhost/", { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders the Multi-Asset Risk Lab shell", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<title>Multi-Asset Risk Lab<\/title>/i);
  assert.match(html, /Portfolio decisions/);
  assert.match(html, /Walk-forward wealth/);
  assert.match(html, /Research governance/i);
  assert.doesNotMatch(html, /codex-preview|Starter Project|Your site is taking shape|ChatGPT|OpenAI/i);
});

test("ships the production research payload", async () => {
  const payload = JSON.parse(await readFile(new URL("../public/results.json", import.meta.url), "utf8"));
  assert.equal(payload.meta.paths, 10_000);
  assert.equal(Object.keys(payload.meta.assets).length, 9);
  assert.ok(payload.meta.observations > 3_000);
  assert.ok(payload.performance.length >= 6);
  assert.deepEqual(
    new Set(payload.models.map((model) => model.model)),
    new Set(["moving_block_bootstrap", "garch_regime_t_copula"]),
  );
  assert.ok(payload.wealth.length > 400);
});
