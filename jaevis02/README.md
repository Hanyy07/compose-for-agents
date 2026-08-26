# JAEVIS02

JAEVIS02 je samostatný osobní AI asistent. Běží jako jediná Docker Compose
služba, obsahuje jednoduché webové rozhraní i JSON API a nevyžaduje závislosti
instalované na hostitelském systému.

Bez nakonfigurovaného poskytovatele modelu se aplikace stále spustí a nabídne
stavové a nápovědní příkazy. Konverzační odpovědi aktivujete klíčem OpenAI.

## Spuštění

```sh
cd jaevis02
cp .env.example .env
# do .env volitelně doplňte OPENAI_API_KEY
docker compose up --build
```

Poté otevřete <http://localhost:8080>. Zdraví služby ověříte příkazem:

```sh
curl http://localhost:8080/health
```

## API

`POST /api/chat` přijímá zprávu a volitelný identifikátor konverzace:

```sh
curl http://localhost:8080/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"conversation_id":"moje-konverzace","message":"Ahoj"}'
```

Identifikátor může obsahovat pouze písmena, číslice, `_` a `-`. Historie je
uložena pouze v paměti běžícího procesu a po restartu se záměrně vymaže.

## Konfigurace

| Proměnná | Výchozí hodnota | Význam |
| --- | --- | --- |
| `OPENAI_API_KEY` | prázdná | Aktivuje odpovědi prostřednictvím OpenAI Responses API. |
| `OPENAI_MODEL` | `gpt-4.1-mini` | Model použitý po nastavení klíče. |
| `JAEVIS_PORT` | `8080` | Port vystavený na hostiteli Docker Compose. |

## Aktuální hranice

Záměrně jde o izolovaný základ projektu. Neobsahuje hlasový vstup, správu
uživatelů, perzistentní paměť ani automatické ovládání zařízení. Tyto funkce
vyžadují samostatné bezpečnostní a produktové požadavky; nemají být předstírány
jako součást tohoto startovního vydání.
