# Instagram Doomscrolling Detector 🚨

A small automation project to gently remind myself (via Telegram) whenever I open Instagram and start doomscrolling.

This project uses **MacroDroid** (Android automation app), **n8n** (automation workflow tool), and **Telegram Bot API**.  
Just a fun personal experiment to build awareness about my screen time. 📱

---

## How It Works

- **MacroDroid** detects when Instagram is launched on my phone.
- After a 15-minutes delay, it checks if Instagram is still in the foreground.
- If yes, **MacroDroid** sends an HTTP POST request (Webhook) to an **n8n** workflow URL.
- **n8n** checks the incoming webhook, processes the request, and sends a random GIF/message to me via a **Telegram Bot**.

---

## Tools Used

- [MacroDroid](https://www.macrodroid.com/) (Android automation app)
- [n8n](https://n8n.io/) (Self-hosted via Cloud/VPS or locally)
- [Telegram Bot](https://core.telegram.org/bots#botfather) (via BotFather)
- [Ngrok](https://ngrok.com/) (optional, for exposing local n8n webhook to the internet)

---

## Setup Instructions

### 1. MacroDroid Setup

- **Trigger:** Application Launched → Select Instagram.
- **Action Flow:**
  - Wait 15 minutes
  - If (App in Foreground = Instagram)
    - HTTP Request (POST) → Send a request to your n8n webhook URL  
      (example: `https://your-ngrok-url/webhook/instagram-doomscroll`)
  - End If

> **Note:**  
> Use the "Wait 15 minutes" action to avoid sending false signals if you accidentally open and close Instagram quickly.

---

### 2. n8n Workflow Setup

- **Trigger Node:** Webhook (HTTP POST)
  - Create a new webhook in n8n.
  - Set it to expect POST requests.

- **Check Node:** (Optional but good practice)
  - You can add a small IF node to check for any specific values in the payload if needed (in my case, it's simple and unconditional).

- **Telegram Node:**
  - Configure a Send Message node.
  - Set it to send a GIF, sticker, or a simple text message through your Telegram bot to your chat ID.

> **Tip:**  
> You can use the `sendAnimation` method in Telegram to send a GIF directly if you want it to be more fun.

---

### 3. Telegram Bot Setup

- Create a bot using **BotFather** on Telegram.
- Get your bot token.
- In n8n’s Telegram node, paste your token and set the message/chat parameters.
- You can hardcode your chat ID or set it dynamically based on the incoming webhook data.

---

## Things to Note

- If you're hosting n8n locally, use **ngrok** to expose your local server for MacroDroid to hit the webhook URL.
- You can customize the message content to randomize between multiple GIFs, motivational texts, or memes.
- Be careful with webhook security if making it public.
![WhatsApp Image 2025-04-26 at 19 39 21_3d414d6a](https://github.com/user-attachments/assets/e16f3a2f-8906-4130-bccc-1351525041ca)

---
ScreenShots:![WhatsApp Image 2025-04-26 at 19 39 22_85c5d51f](https://github.com/user-attachments/assets/7be75017-5ba2-4f1e-bcc5-fde932a5d41f)

![WhatsApp Image 2025-04-26 at 19 45 53_b6e51bfa](https://github.com/user-attachments/assets/d24d42de-a5fe-4e37-b250-db2b9885db71)![Screenshot 2025-04-26 193633](https://github.com/user-attachments/assets/a2e74b01-d615-4f35-9441-fb08b10d0538)



## Why I Made This

I wanted a non-intrusive, funny way to catch myself when I mindlessly open Instagram.  
Instead of using strict blockers, this approach nudges me gently without being annoying.

---
