# Annunci Gyver: design

## Obiettivo

Completare lo scheletro esistente in una piccola applicazione utilizzabile per il flusso Delivery descritto nell’assignment: consultare offerte e annunci, creare più annunci per offerta e canale, generare varianti con un LLM, modificarle manualmente e filtrare i risultati. Il progetto deve essere facile da avviare, mostrare dati dimostrativi e spiegare le scelte e i limiti.

## Architettura

Si mantiene lo stack già avviato: FastAPI, SQLAlchemy, SQLite e una pagina HTML con JavaScript vanilla. I confini restano semplici e verificabili:

- i modelli SQLAlchemy persistono job offer, annunci e varianti;
- i repository contengono le query e le operazioni di persistenza;
- i servizi coordinano i casi d’uso, validazione e transazioni;
- i controller espongono API REST;
- un adapter LLM dedicato gestisce la richiesta al provider, il prompt e la validazione dell’output;
- la UI consuma le API senza accedere direttamente ai dati.

La generazione usa i campi interni dell’offerta come contesto e richiede un oggetto JSON aderente allo schema della variante. Il servizio valida il risultato prima di creare record; errori di rete, credenziali mancanti, JSON non valido e campi mancanti vengono restituiti come errori API leggibili e non lasciano annunci parziali nel database. Le modifiche manuali aggiornano i campi della variante e ne marcano l’origine come manuale.

## Modello dati e API

La job offer conserva il contenuto denso originario. Ogni annuncio appartiene a una singola offerta e memorizza canale, formato, stato e luogo di pubblicazione, che può essere scelto indipendentemente dalla sede dell’offerta. Un annuncio contiene una o più varianti. Ogni variante conserva titolo, testo, requisiti, compenso, campi specifici del canale, testo/brief della creative, eventuale percorso immagine, origine e timestamp.

Le API supportano:

- elenco e dettaglio delle job offer;
- elenco e dettaglio annunci, con filtri combinabili per `job_offer_id` e `channel`;
- creazione di un annuncio con generazione iniziale di una variante;
- aggiunta di ulteriori varianti generate allo stesso annuncio;
- aggiornamento manuale dei metadati dell’annuncio e dei campi della variante;
- stato di salute e pagina applicativa.

Le forme dei payload vengono definite con schemi Pydantic. Gli enum ammessi sono i canali (`indeed`, `tiktok`, `instagram`, `whatsapp`), i formati (`text`, `image`, `image_text`) e gli stati (`draft`, `ready`, `published`, `archived`). L’output per job board espone i campi di pubblicazione separati dal testo; i canali social e WhatsApp possono contenere brief e testo creative.

## UI e dati dimostrativi

La pagina mostra annunci con canale, formato, stato, luogo e offerta. Consente filtro per offerta/canale, creazione scegliendo offerta, canale, formato e luogo, consultazione delle varianti, generazione di una nuova variante e modifica/salvataggio del copy. L’interfaccia segnala caricamento ed errori API e non richiede una build frontend.

Il seed è ripetibile: crea l’offerta di esempio dell’assignment e pochi annunci/varianti rappresentativi senza duplicare record. Le immagini non sono generate: il modello supporta il percorso di un’immagine caricata e l’upload è limitato dal limite configurato. Il flusso principale resta completo anche con annunci solo testuali.

## Configurazione e documentazione

`OPENAI_API_KEY` e `OPENAI_MODEL` configurano il provider. Senza chiave si possono consultare e modificare i dati persistiti, ma la generazione restituisce un errore esplicito. Le impostazioni database e upload restano configurabili via ambiente. Nessuna credenziale o dato sensibile viene incluso.

La consegna documenta avvio, seed e percorso UI in `README.md`; componenti, schema e flusso dati in `architecture.md`; prompt finale, vincoli e gestione output invalido in `prompts.md`; uso degli strumenti AI in `ai-workflows.md`; decisioni e semplificazioni in `tradeoffs.md`.

## Fuori scope e semplificazioni

- Nessuna pubblicazione diretta su Indeed, TikTok, Instagram o WhatsApp; lo stato descrive il workflow interno.
- Nessuna autenticazione, ruoli o collaborazione concorrente.
- SQLite e `create_all` sono sufficienti per il prototipo; non si introduce un sistema di migrazioni.
- Le varianti sono versioni modificabili collegate all’annuncio; non si implementano esperimenti o metriche di performance.
- Non si promette generazione pixel-perfect di asset grafici. Si salvano brief/testi e si può associare un’immagine già disponibile.
- Le chiamate LLM sono sincrone e senza job queue o retry automatici, per mantenere l’applicazione minima.
