# AI workflow

Ho usato Codex in modalità Native, lavorando in sequenza nel worktree Git `feature/annunci-mvc`. Ho letto la trascrizione dell’assignment e lo scheletro, discusso e formalizzato il design, approvato un piano prima del codice e poi implementato offerte e seed, generazione LLM, API annunci, interfaccia e documentazione. Nella verifica finale ho confrontato anche gli screenshot originali forniti localmente; la pagina Sotion stessa mostrava solo il login. Una revisione statica indipendente tramite subagent ha individuato problemi di validazione, selezione UI, seed e alcuni disallineamenti minori; ho verificato i rilievi e applicato una fix pass.

## Pipeline

La job offer è l’unica fonte di fatti. Il backend costruisce un contesto ridotto che omette l’indirizzo civico; un prompt di sistema separa le istruzioni dai dati, adatta tono e campi al canale, vieta affermazioni non supportate e richiede un output strutturato. Pydantic e controlli applicativi validano i campi prima della persistenza. La prima bozza e l’annuncio vengono salvati nella stessa transazione, così un errore non lascia dati incompleti. L’editor consente poi al team di correggere il copy e creare ulteriori varianti.

Non c’è una seconda chiamata LLM di revisione né una pipeline di agenti: per questo prototipo schema e validazioni locali danno un confine più piccolo e leggibile. Il testo richiede comunque revisione umana prima della pubblicazione esterna.

## Strumenti

- Codex ha aiutato a leggere il progetto, progettare i confini, implementare codice e documentare scelte.
- Sono state usate le skill `using-superpowers`, `brainstorming`, `writing-plans` ed `executing-plans` per impostare il processo e approvare design e piano prima del codice; `receiving-code-review` per verificare tecnicamente i rilievi; `verification-before-completion` per basare le dichiarazioni finali su controlli effettivamente eseguiti.
- La documentazione ufficiale OpenAI è stata consultata per la Responses API e l’output JSON Schema rigoroso.
- Shell locale, Git e Docker Compose sono stati usati per navigare il worktree, compilare staticamente Python, controllare la sintassi JavaScript, ispezionare diff, validare `compose.yaml`, costruire l’immagine e gestire il branch.
- È stato usato un subagent per una revisione statica finale indipendente. Non sono stati usati MCP, strumenti di invio messaggi, generatori di immagini o chiamate OpenAI durante lo sviluppo.

Il prompt non ha versioni precedenti eseguite da confrontare: il repository iniziale non ne conteneva e non sono state fatte chiamate LLM durante lo sviluppo. Per questo `prompts.md` separa i vincoli finali dalle motivazioni progettuali, senza presentarle come risultati di benchmark.

## Verifica e limiti

Non sono stati aggiunti o eseguiti test automatici. I controlli statici sono compilazione Python (`./.venv312/bin/python -m compileall -q app`), sintassi JavaScript (`node --check app/views/static/app.js`) e `git diff --check`, oltre alle revisioni statiche dei confini di validazione, rollback e mapping delle route. `docker compose config --quiet` e `docker compose build app` sono terminati con successo. Ho tentato uno smoke check del seed locale con database temporaneo, ma `python -m app.seed` non ha terminato entro circa due minuti e l’ho interrotto mentre Python importava i moduli SQLAlchemy; non ho avviato il container, quindi l’avvio HTTP e gli endpoint non sono ancora verificati. Non è stata fatta una prova end-to-end con credenziali OpenAI: la generazione reale richiede una chiave e un modello abilitato sull’account.
