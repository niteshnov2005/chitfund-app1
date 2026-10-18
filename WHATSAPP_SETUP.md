# WhatsApp Receipt Sending — Setup Guide

This uses Meta's official **WhatsApp Cloud API** (free tier: 1,000 conversations/month,
no per-message cost within that). It works on your cloud-hosted Flask app because it's
a plain HTTPS API call — no browser or QR scan needed on the server.

## 1. Create the free Meta credentials

1. Go to https://developers.facebook.com/ and log in / create a developer account.
2. Create a new App → type "Business".
3. Inside the app dashboard, add the **WhatsApp** product.
4. Under **WhatsApp → API Setup** you'll immediately see:
   - A **temporary access token** (valid ~24 hours — fine for testing, see step 3 for a permanent one).
   - A **Phone number ID** (this is a test number Meta gives you for free).
5. Still on that page, under "To", add the phone numbers you want to test with
   (your own number and a few members' numbers). **On the free test number, you can
   only message numbers you've explicitly added here** — this is a Meta restriction,
   not a bug in the app.

## 2. Set the environment variables on your host

Wherever you deploy (Render, Railway, Cloud Run, etc.), set:

```
WHATSAPP_TOKEN=<your access token>
WHATSAPP_PHONE_NUMBER_ID=<your phone number id>
```

Restart/redeploy the app after setting these.

## 3. (Recommended) Get a permanent token + your own number

The token from step 1 expires in 24 hours. For a real deployment:
1. In Meta Business Settings → System Users, create a system user, generate a
   **permanent token** with `whatsapp_business_messaging` permission.
2. To message *any* number (not just pre-approved test numbers), you'll need to
   go through **Business Verification** and add your own WhatsApp Business phone
   number under WhatsApp Manager. This is free but takes Meta a few days to approve.

## 4. Using it in the app

On the **View Receipts** page, each member card now has a phone number field and a
**Send** button. Enter the member's WhatsApp number (with country code, e.g.
`91XXXXXXXXXX`) once — it's saved automatically for next time. A **"Send All via
WhatsApp"** button in the top bar sends receipts to every member who has a saved
number.

Numbers are stored in `member_phones.json` next to your other data files.

## Known limitations

- Free Meta test numbers can only message pre-approved recipients (step 1). For
  sending to all your real members without pre-approval, you need Business
  Verification (still free, just takes review time).
- If your host uses an ephemeral filesystem (e.g. Cloud Run's `/tmp`), like your
  `payment_records.json` already does, `member_phones.json` will reset on
  redeploy unless you back it up the same way you back up your Excel data.
