# Gyver Annunci

Piccola applicazione FastAPI per il team Delivery: parte da una job offer interna, crea annunci per Indeed, WhatsApp, Instagram o TikTok, genera copy e varianti con un LLM e permette di modificarli prima della pubblicazione.

## Requisiti

- Python 3.12 o successivo.
- Una chiave OpenAI per generare nuovi annunci o varianti. Senza chiave si possono consultare e modificare gli annunci dimostrativi già salvati.

## Installazione

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Imposta `OPENAI_API_KEY` nel file `.env` per abilitare la generazione. La chiave si crea dalla [dashboard API di OpenAI](https://platform.openai.com/api-keys). Non inserirla nei file sorgente o nei commit. `OPENAI_MODEL` deve essere un modello abilitato per il tuo account che supporta Responses e output JSON Schema strutturato; il nome si può cambiare nel `.env`. Il default `gpt-5.6-terra` è presente nella [documentazione ufficiale dei modelli](https://platform.openai.com/docs/models/gpt-4-turbo-and-gpt-4).

## Configurazione

| Variabile | Default | Uso |
| --- | --- | --- |
| `OPENAI_API_KEY` | vuoto | Credenziale server-side per generare copy e varianti. |
| `OPENAI_MODEL` | `gpt-5.6-terra` | Modello usato dall’endpoint Responses. Verifica che sia abilitato sul tuo account. |
| `OPENAI_TIMEOUT_SECONDS` | `45` | Timeout della chiamata LLM, da 1 a 120 secondi. |
| `DATABASE_URL` | `sqlite:///./data/gyver.db` | URL SQLAlchemy del database. |
| `UPLOAD_DIR` | `uploads` | Directory locale per le immagini delle creative. |
| `MAX_UPLOAD_MB` | `8` | Limite di upload in megabyte, configurabile da 1 a 30. |
| `APP_PORT` | `8000` | Porta locale pubblicata da Docker Compose; non cambia la porta interna del container. |

Il progetto invia al provider i dati dell’offerta necessari a scrivere l’annuncio. La richiesta imposta `store=false`; questo evita la persistenza dello stato della risposta da parte dell’endpoint, ma non equivale a una garanzia di zero retention per ogni configurazione dell’account. Valuta i dati che inserisci e le policy applicabili al tuo account.

## Database e dati dimostrativi

Inizializza il database e inserisci i dati di esempio:

```bash
python -m app.seed
```

Il comando crea lo schema e inserisce l’offerta `jo_001` con annunci Indeed, WhatsApp e Instagram. È ripetibile: non duplica i record dimostrativi già presenti. Il database SQLite viene creato sotto `data/` ed è escluso da Git; puoi rilanciare il seed per ricostruirlo.

## Avvio

```bash
uvicorn app.main:app --reload
```

- Interfaccia: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- API e schema interattivo: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health check: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

Non serve un processo frontend separato né una build JavaScript.

## Avvio con Docker

Servono Docker Engine/Desktop e Docker Compose v2. Per preparare la configurazione locale e, se vuoi generare copy, impostare la chiave:

```bash
cp .env.example .env
```

`OPENAI_API_KEY` è facoltativa per consultare e modificare gli annunci demo; serve per creare annunci o generare nuove varianti. Avvia il seed una volta, poi il servizio:

```bash
docker compose run --rm app python -m app.seed
docker compose up --build -d
```

Apri [http://127.0.0.1:8000](http://127.0.0.1:8000); `/api/health` è il controllo di stato. La porta locale si cambia con `APP_PORT` nel file `.env`. Database e immagini sono persistiti in volumi Docker separati (`gyver_data` e `gyver_uploads`); ricreare il container non li cancella. Per fermare il servizio usa `docker compose down`. Evita `docker compose down -v` se vuoi conservare i dati: rimuove anche i volumi.

Il container gira come utente non root e la porta è pubblicata solo su localhost. Questo setup è per sviluppo/demo locale, non aggiunge autenticazione e non è una configurazione di produzione.

## Percorso completo

1. Avvia il seed e il server; nella pagina **Annunci** trovi i record dimostrativi.
2. Scegli la job offer, il canale e il formato nel modulo **Crea un annuncio**. Puoi specificare un luogo di pubblicazione diverso dalla sede dell’offerta.
3. Premi **Crea e genera copy**. Il backend salva insieme la bozza e la prima variante solo dopo aver ricevuto e validato l’output LLM.
4. Seleziona l’annuncio, consulta le varianti e modifica titolo, testo, requisiti, compenso, campi del canale o creative. **Salva modifiche** aggiorna la variante e ne registra l’origine manuale.
5. Premi **Genera variante** per creare un’altra versione per lo stesso annuncio.
6. Per i formati con immagine puoi associare un file PNG, JPEG o WebP. Il server verifica il tipo, la firma del file e il limite configurato; l’anteprima viene servita dalla directory `UPLOAD_DIR`.

Senza `OPENAI_API_KEY` le operazioni di lettura, filtro e modifica funzionano sui dati presenti. La creazione generativa restituisce un errore esplicito finché non configuri la chiave.

## API principali

- `GET /api/job-offers` e `GET /api/job-offers/{id}`: offerte disponibili.
- `GET /api/ads?job_offer_id=...&channel=...`: lista filtrabile.
- `GET /api/ads/{id}`: dettaglio con varianti.
- `POST /api/ads`: crea un annuncio e genera la prima variante.
- `POST /api/ads/{id}/variants`: aggiunge una variante generata.
- `PATCH /api/ads/{id}`: modifica luogo o stato.
- `PATCH /api/ads/{id}/variants/{variant_id}`: modifica il contenuto.
- `POST /api/ads/{id}/variants/{variant_id}/image`: associa un’immagine multipart nel campo `image`.

Errori di validazione restituiscono `422`; risorse inesistenti `404`; credenziali/provider non disponibili `503`; risposta LLM non valida `502`; file immagine troppo grande `413` o non valido `415`.
