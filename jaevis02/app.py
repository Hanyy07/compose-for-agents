"""JAEVIS02: a small, self-contained personal-assistant web service."""

from __future__ import annotations

import json
import os
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

MAX_MESSAGE_LENGTH = 4_000
CONVERSATION_ID = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")
SYSTEM_PROMPT = """You are JAEVIS02, a helpful personal AI assistant.
Reply in the language used by the user. Be concise, accurate, and explicit about
uncertainty. Never claim that you performed actions outside this chat."""


def local_response(message: str) -> str:
    """Offer useful behavior when no model provider is configured."""
    normalized = message.strip().lower()
    if normalized in {"/help", "help", "pomoc"}:
        return (
            "JAEVIS02 je připraven. Nastavte OPENAI_API_KEY pro odpovědi modelu. "
            "Příkazy: /help, /status."
        )
    if normalized in {"/status", "status"}:
        return "Služba JAEVIS02 běží. Poskytovatel modelu není nakonfigurován."
    return (
        "Pro konverzační odpověď nastavte OPENAI_API_KEY v souboru .env. "
        "Do té doby použijte /help nebo /status."
    )


class Assistant:
    def __init__(self) -> None:
        self.history: dict[str, list[dict[str, str]]] = {}
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    def reply(self, conversation_id: str, message: str) -> str:
        if not self.api_key:
            return local_response(message)

        history = self.history.setdefault(conversation_id, [])
        history.append({"role": "user", "content": message})
        history[:] = history[-12:]
        try:
            answer = self._request_model(history)
        except (HTTPError, URLError, TimeoutError, ValueError) as error:
            return f"Model není momentálně dostupný ({error}). Zkuste to prosím znovu."
        history.append({"role": "assistant", "content": answer})
        return answer

    def _request_model(self, history: list[dict[str, str]]) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "instructions": SYSTEM_PROMPT,
                "input": history,
            }
        ).encode()
        request = Request(
            "https://api.openai.com/v1/responses",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urlopen(request, timeout=30) as response:
            data = json.load(response)
        text = data.get("output_text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("model returned no text")
        return text.strip()


ASSISTANT = Assistant()


class JaevisHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._json(HTTPStatus.OK, {"status": "ok", "service": "jaevis02"})
            return
        if self.path in {"/", "/index.html"}:
            self._html()
            return
        self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/chat":
            self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= MAX_MESSAGE_LENGTH + 256:
                raise ValueError("invalid request size")
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise ValueError("request body must be a JSON object")
            message = body.get("message", "")
            conversation_id = body.get("conversation_id", "default")
            if not isinstance(message, str) or not 0 < len(message.strip()) <= MAX_MESSAGE_LENGTH:
                raise ValueError("message must contain 1–4000 characters")
            if not isinstance(conversation_id, str) or not CONVERSATION_ID.fullmatch(conversation_id):
                raise ValueError("invalid conversation_id")
            message = message.strip()
        except (json.JSONDecodeError, ValueError, UnicodeDecodeError) as error:
            self._json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
            return

        self._json(
            HTTPStatus.OK,
            {"conversation_id": conversation_id, "reply": ASSISTANT.reply(conversation_id, message)},
        )

    def _json(self, status: HTTPStatus, body: dict[str, str]) -> None:
        encoded = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _html(self) -> None:
        content = b"""<!doctype html><html lang="cs"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>JAEVIS02</title><style>
body{font:16px system-ui;margin:auto;max-width:720px;padding:2rem;background:#101522;color:#e9edf7}
#chat{min-height:280px;padding:1rem;background:#192131;border-radius:12px;white-space:pre-wrap}
form{display:flex;gap:.5rem;margin-top:1rem}input{flex:1;padding:.8rem}button{padding:.8rem 1rem}
.user{color:#8dd3ff}.assistant{color:#b7f3c4}</style>
<h1>JAEVIS02</h1><p>Samostatný osobní AI asistent</p><main id="chat"></main>
<form><input aria-label="Zpráva" placeholder="Napište zprávu…" required><button>Odeslat</button></form>
<script>
const chat=document.querySelector('#chat'), form=document.querySelector('form'), input=document.querySelector('input');
const add=(role,text)=>{const p=document.createElement('p');p.className=role;p.textContent=`${role==='user'?'Vy':'JAEVIS02'}: ${text}`;chat.append(p);chat.scrollTop=chat.scrollHeight};
form.onsubmit=async e=>{e.preventDefault();const message=input.value.trim();if(!message)return;add('user',message);input.value='';
try{const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message})});const data=await r.json();add('assistant',data.reply||data.error)}catch{add('assistant','Nelze se připojit ke službě.')}}
</script></html>"""
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format: str, *args: object) -> None:
        print(f"JAEVIS02 | {format % args}")


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    print(f"JAEVIS02 listening on http://0.0.0.0:{port}")
    ThreadingHTTPServer(("0.0.0.0", port), JaevisHandler).serve_forever()
