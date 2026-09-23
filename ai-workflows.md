# AI workflow

Ho usato Codex in modalità Native, lavorando in sequenza nel worktree Git `feature/annunci-mvc`. Ho prima letto la traccia e lo scheletro esistente, poi ho formalizzato il design e il piano prima di completare offerte e seed, generazione LLM, API annunci, interfaccia e documentazione.

## Pipeline

La job offer è l’unica fonte di fatti. Il backend costruisce un contesto ridotto che omette l’indirizzo civico; un prompt di sistema separa le istruzioni dai dati, adatta tono e campi al canale, vieta affermazioni non supportate e richiede un output strutturato. Pydantic e controlli applicativi validano i campi prima della persistenza. La prima bozza e l’annuncio vengono salvati nella stessa transazione, così un errore non lascia dati incompleti. L’editor consente poi al team di correggere il copy e creare ulteriori varianti.

Non c’è una seconda chiamata LLM di revisione né una pipeline di agenti: per questo prototipo schema e validazioni locali danno un confine più piccolo e leggibile. Il testo richiede comunque revisione umana prima della pubblicazione esterna.

## Strumenti

- Codex ha aiutato a leggere il progetto, progettare i confini, implementare codice e documentare scelte.
- Sono state usate le skill `brainstorming`, `writing-plans` ed `executing-plans` per approvare design e piano prima del codice.
- La documentazione ufficiale OpenAI è stata consultata per la Responses API e l’output JSON Schema rigoroso.
- Shell locale e Git sono stati usati per navigare il worktree, compilare staticamente Python, controllare la sintassi JavaScript e rivedere le modifiche.
- Non sono stati usati MCP, subagent, strumenti di invio messaggi o generatori di immagini.

Il prompt non ha versioni precedenti eseguite da confrontare: il repository iniziale non ne conteneva e non sono state fatte chiamate LLM durante lo sviluppo. Per questo `prompts.md` separa i vincoli finali dalle motivazioni progettuali, senza presentarle come risultati di benchmark.

## Verifica e limiti

Per vincolo della sessione, non sono stati aggiunti o eseguiti test automatici. I controlli svolti sono compilazione sintattica Python, controllo della sintassi JavaScript, `git diff --check` e revisione manuale dei confini di validazione, rollback e mapping delle route. Non è stata fatta una prova end-to-end con credenziali OpenAI: la generazione reale richiede una chiave e un modello abilitato sull’account.
