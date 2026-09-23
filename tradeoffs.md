# Decisioni e trade-off

## Scelte

- **Python e FastAPI:** lo scheletro disponibile usava già Python, SQLAlchemy e FastAPI. Continuare con lo stack riduce setup e consente a chi revisiona l’assignment di concentrarsi sul modello dati e sul flusso.
- **SQLite:** basta per un prototipo locale e rende il seed immediato. `create_all` crea le tabelle, ma non sostituisce migrazioni se il modello cambia dopo la prima esecuzione.
- **Docker Compose:** offre un avvio riproducibile con volumi separati per database e upload, ma espone l’app solo su localhost e non configura autenticazione, TLS o un database server: è packaging per demo locale, non deployment pubblico.
- **Annuncio e variante separati:** canale, formato, stato e luogo appartengono all’annuncio; il copy, i campi del canale e la creative appartengono alla variante. Questo permette copy alternativi per uno stesso annuncio e luoghi diversi per annunci della stessa offerta.
- **JSON per `channel_fields`:** evita un campo SQL per ogni canale, mantenendo flessibile l’output. Le varianti LLM usano campi consentiti e prevedibili; questa scelta non impone uno schema tipizzato distinto per ogni job board.
- **HTTPX diretto verso Responses:** evita un SDK aggiuntivo e mantiene il confine provider in un file. La richiesta usa JSON Schema rigoroso e il progetto fa comunque validazione locale. `gpt-5.6-terra` è il default documentato come equilibrio tra capacità e costo; account e modelli abilitati possono variare, quindi resta configurabile.
- **Una sola chiamata sincrona:** semplice da seguire e sufficiente per l’uso dimostrativo; richieste lente occupano il worker e non ci sono job queue o retry automatici.

## Ambiguità interpretate

- Ogni `Ad` rappresenta una pubblicazione/canale/formato/luogo; una variante rappresenta una versione del contenuto di quell’annuncio. Un annuncio Indeed e uno WhatsApp per la stessa offerta sono record distinti.
- “Immagine” descrive una creative con testo e brief; l’app non compone grafiche. È possibile caricare PNG, JPEG o WebP esistenti, associati a una variante, con limite configurabile.
- Lo stato `published` è solo un valore del workflow interno. Non esistono credenziali né integrazioni per pubblicare davvero sui canali.
- La job offer fornisce i fatti interni; il luogo di pubblicazione è invece inserito o confermato dal team Delivery. Il modello non riceve via e numero civico dell’offerta.
- I benefici e gli importi devono provenire dall’offerta. Se un dato non è disponibile, il prompt chiede di ometterlo anziché inventarlo.

## Cosa resta fuori

- Autenticazione, autorizzazioni, audit trail, migrazioni e supporto per più istanze concorrenti.
- Pubblicazione su Indeed, social o WhatsApp, metriche di performance e test A/B reali.
- Generazione o ridimensionamento di immagini: l’LLM propone solo testo e brief; l’asset arriva da un file già prodotto.
- Cronologia di ogni modifica: una PATCH cambia la variante esistente e marca `origin=manual`; per conservare ogni revisione servirebbe una tabella di versioni.
- Pulizia automatica delle immagini sostituite: la nuova associazione è transazionale rispetto al record, ma il vecchio file può restare nella directory upload.
- Modalità offline per la generazione: senza chiave si possono consultare e modificare i dati esistenti, ma non creare varianti LLM.

## Priorità con un giorno in più

1. **Verifiche automatiche mirate:** aggiungere test con database temporaneo e provider simulato per creazione atomica/rollback, filtri combinati, modifica parziale, ownership delle varianti, upload e risposte LLM incomplete. La priorità è ridurre il rischio di regressioni senza dipendere da una chiave o da chiamate fatturabili.
2. **Valutazione della qualità dei copy:** raccogliere output reali per canali e formati, poi rivederli con una persona del team Delivery usando una checklist su fedeltà ai fatti, leggibilità, lunghezza e campi richiesti. Non automatizzerei la pubblicazione né considererei un output plausibile come approvato.
3. **Rafforzamento per uso condiviso:** aggiungere autenticazione e autorizzazioni, migrazioni SQL, limiti di concorrenza e storage oggetti per le immagini. Questi cambi dipendono dall’ambiente di deploy e non sono necessari per una demo locale.

Il prototipo resta deliberatamente locale: l’upload di asset e la UI editoriale vanno oltre il minimo backend, ma rendono ispezionabile il flusso creativo. Per rispettare strettamente un timebox, avrei mantenuto prima il seed, i casi d’uso backend e la UI essenziale; hardening e integrazioni restano fuori.

## Limiti da tenere presenti

Il provider riceve i dati dell’offerta per poter generare il copy. `store=false` evita la persistenza dello stato della Response, ma non rappresenta una promessa universale di zero retention. Il modello configurato deve essere abilitato sull’account e supportare Responses con JSON Schema rigoroso. Il contenuto deve essere revisionato da una persona prima dell’uso esterno.
