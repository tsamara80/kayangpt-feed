# UnblockU: selling it for $9

How it works for a buyer:

1. They open your app and run **1 free round**.
2. To run another, they hit the paywall. They tap **Buy for $9**, which opens your Lemon Squeezy checkout.
3. Lemon Squeezy emails them a **license key**. They paste it into the app and tap **Unlock this device**.
4. The app asks your **license checker** (a small free Cloudflare Worker) whether the key is real. If it is, the app unlocks on that device.
5. About once a week the app checks the key again, so refunded keys stop working. If the buyer is offline, they keep access.

You need about 30 minutes and 3 accounts: Lemon Squeezy (payments), Cloudflare (license checker) and a host for the app.

---

## Files

| File | What it is |
|---|---|
| `index.html` | **The app you host.** One file, no server needed. |
| `license-worker/worker.js` | The license checker you paste into Cloudflare. |
| `app.html` | The preview version (demo keys). It's the source `index.html` is built from. |
| `build.py` | Rebuilds `index.html` from `app.html` after changes. |

---

## Step 1: Lemon Squeezy (payments and license keys)

Lemon Squeezy is the "merchant of record": it charges the card, handles sales tax and VAT in every country, sends the receipt and creates the license key.

1. Sign up at lemonsqueezy.com, create your store and set up payouts. Check that a payout method works for your country before you launch.
2. **Products → New product**
   - Name: `UnblockU`
   - Pricing: **Single payment**, `$9`
   - Turn on **Generate license keys**
     - Activation limit: `3` (one buyer, 3 devices)
     - Expiry: never
   - Optional: in the confirmation settings, add a button that links to your app address, so buyers can go straight to the app after paying.
3. Publish the product and copy its **checkout link** (Share → checkout URL).
4. Note your **store ID** and the **product ID**. Both appear in the dashboard; the product ID is shown on the product page. The checker uses them so keys from your other products can't unlock UnblockU.

Lemon Squeezy puts the license key in the receipt email automatically.

## Step 2: Cloudflare Worker (the license checker)

It's free and needs no code knowledge, just copy and paste.

1. Sign up at dash.cloudflare.com.
2. **Workers & Pages → Create → Create Worker**. Name it `unblocku-license` and click **Deploy**.
3. Click **Edit code**, delete everything, paste the full contents of `license-worker/worker.js`, then click **Deploy**.
4. Go to **Settings → Variables and Secrets** and add:

   | Name | Value |
   |---|---|
   | `LS_STORE_ID` | your store ID |
   | `LS_PRODUCT_ID` | your UnblockU product ID |
   | `ALLOWED_ORIGINS` | your app address, e.g. `https://app.unblocku.com` |

5. Copy the Worker address. It looks like `https://unblocku-license.YOURNAME.workers.dev`.

## Step 3: Put your two links in the app

Open `index.html` in any text editor, search for `OWNER SETTINGS`, and replace the two placeholders:

```js
checkoutUrl: "https://YOURSTORE.lemonsqueezy.com/buy/....",
licenseApi:  "https://unblocku-license.YOURNAME.workers.dev",
price: "$9",
freeRounds: 1
```

If you change the price in Lemon Squeezy, change `price` here too. `freeRounds` sets how many rounds a visitor gets before the paywall.

## Step 4: Host it

`index.html` is the whole app. Any of these works:

- **Cloudflare Pages** (same account as the Worker): Workers & Pages → Create → Pages → upload the file.
- **Netlify Drop**: drag the `unblocku` folder onto app.netlify.com/drop.
- **Your own site**: upload `index.html` to a subdomain such as `app.tareqsamara.com`.

Then make sure `ALLOWED_ORIGINS` in the Worker matches the final address exactly (https, no trailing slash).

## Step 5: Test before you announce

1. Open the app in a private window and run the free round. On the second round you should see the paywall.
2. In Lemon Squeezy, create a **100% discount code**, buy UnblockU with it, and paste the key from the email. The app should unlock.
3. Paste a random key. You should see "That key wasn't found."
4. Refund your test order. Within a week (or right away if you clear the "license" data and paste the key again), the key stops working.

---

## Using Gumroad instead

Create the product on Gumroad with **Generate a unique license key per sale** turned on. In the Worker variables, set:

| Name | Value |
|---|---|
| `PROVIDER` | `gumroad` |
| `GUMROAD_PRODUCT_ID` | your Gumroad product ID |
| `MAX_ACTIVATIONS` | `3` |
| `ALLOWED_ORIGINS` | your app address |

Put your Gumroad checkout link in `checkoutUrl`. One difference: on Gumroad, "Remove from this device" doesn't give the activation back, so if a buyer gets a new phone you may need to reset the count by hand in Gumroad.

---

## What this protects, and what it doesn't

This setup fits a $9 product. It stops casual sharing, refunds and fake keys. It does **not** stop someone technical who edits the app's code, because the whole app runs in the browser. Also:

- Clearing browser data gives a visitor another free round.
- A buyer can share their key with up to 2 other people (the activation limit).

If UnblockU grows and copying becomes a real problem, the next step is to move the hook library to the server and send it only to unlocked devices. Wait until the sales numbers justify that.

## Changing hooks or text later

Edit `app.html` (the preview), then run `python3 build.py` to rebuild `index.html`.

So rebuilding never wipes your links, save them once in `store-links.json` next to `build.py`:

```json
{ "checkoutUrl": "https://YOURSTORE.lemonsqueezy.com/buy/....",
  "licenseApi": "https://unblocku-license.YOURNAME.workers.dev" }
```
