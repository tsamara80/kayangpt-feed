/**
 * UnblockU license checker (Cloudflare Worker, free plan is enough).
 *
 * The app calls POST /activate, /validate and /deactivate with JSON {key, device?, instance?}.
 * This worker asks your store whether the key is real and belongs to UnblockU,
 * and answers {ok:true, instance, email} or {ok:false, error}.
 *
 * Settings (Worker > Settings > Variables):
 *   PROVIDER          "lemonsqueezy" (default) or "gumroad"
 *   ALLOWED_ORIGINS   your app address, e.g. "https://app.unblocku.com" (comma-separate several; "*" allows any)
 *   LS_STORE_ID       Lemon Squeezy store ID   (recommended)
 *   LS_PRODUCT_ID     Lemon Squeezy product ID (recommended)
 *   GUMROAD_PRODUCT_ID  Gumroad product ID      (Gumroad only)
 *   MAX_ACTIVATIONS   devices per key on Gumroad (default 3). On Lemon Squeezy set the limit on the product.
 */
export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const allowed = (env.ALLOWED_ORIGINS || "*").split(",").map(s => s.trim()).filter(Boolean);
    const allowOrigin = allowed.includes("*") ? "*" : (allowed.includes(origin) ? origin : allowed[0] || "");
    const cors = {
      "Access-Control-Allow-Origin": allowOrigin,
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "Vary": "Origin"
    };
    const reply = (body, status = 200) =>
      new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
    if (request.method !== "POST") return reply({ ok: false, error: "method_not_allowed" }, 405);

    const action = new URL(request.url).pathname.replace(/^\/+|\/+$/g, "");
    if (!["activate", "validate", "deactivate"].includes(action)) return reply({ ok: false, error: "unknown_action" }, 404);

    let body;
    try { body = await request.json(); } catch { return reply({ ok: false, error: "bad_request" }, 400); }
    const key = String(body.key || "").trim();
    if (!key || key.length > 120) return reply({ ok: false, error: "missing_key" }, 400);

    try {
      const provider = String(env.PROVIDER || "lemonsqueezy").toLowerCase();
      const result = provider === "gumroad"
        ? await gumroad(action, key, body, env)
        : await lemonSqueezy(action, key, body, env);
      return reply(result);
    } catch (e) {
      return reply({ ok: false, error: "network" }, 502);
    }
  }
};

async function postForm(url, params) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams(params)
  });
  return res.json();
}

async function lemonSqueezy(action, key, body, env) {
  const base = "https://api.lemonsqueezy.com/v1/licenses/";

  if (action === "deactivate") {
    if (!body.instance) return { ok: true };
    const data = await postForm(base + "deactivate", { license_key: key, instance_id: String(body.instance) });
    return { ok: !!data.deactivated };
  }

  const data = action === "activate"
    ? await postForm(base + "activate", { license_key: key, instance_name: String(body.device || "UnblockU").slice(0, 80) })
    : await postForm(base + "validate", body.instance ? { license_key: key, instance_id: String(body.instance) } : { license_key: key });

  const good = action === "activate" ? data.activated : data.valid;
  if (!good) {
    const msg = String(data.error || "").toLowerCase();
    const status = data.license_key && data.license_key.status;
    if (msg.includes("limit")) return { ok: false, error: "limit_reached" };
    if (status === "disabled" || status === "expired" || msg.includes("disabled") || msg.includes("expired")) return { ok: false, error: "disabled" };
    return { ok: false, error: "invalid_key" };
  }

  // A real key from a different product in your store must not unlock UnblockU.
  const meta = data.meta || {};
  if (env.LS_STORE_ID && String(meta.store_id) !== String(env.LS_STORE_ID)) return { ok: false, error: "wrong_product" };
  if (env.LS_PRODUCT_ID && String(meta.product_id) !== String(env.LS_PRODUCT_ID)) return { ok: false, error: "wrong_product" };

  return { ok: true, instance: data.instance ? data.instance.id : (body.instance || null), email: meta.customer_email || "" };
}

async function gumroad(action, key, body, env) {
  // Gumroad has no per-device instances; "deactivate" just forgets the key in the app.
  if (action === "deactivate") return { ok: true };
  const data = await postForm("https://api.gumroad.com/v2/licenses/verify", {
    product_id: env.GUMROAD_PRODUCT_ID || "",
    license_key: key,
    increment_uses_count: action === "activate" ? "true" : "false"
  });
  if (!data.success) return { ok: false, error: "invalid_key" };
  const p = data.purchase || {};
  if (p.refunded || p.chargebacked || p.disputed) return { ok: false, error: "disabled" };
  const max = Number(env.MAX_ACTIVATIONS || 3);
  if (action === "activate" && Number(data.uses) > max) return { ok: false, error: "limit_reached" };
  return { ok: true, instance: null, email: p.email || "" };
}
