"""Idempotent demo data for the assignment's supplied job offer."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import Base, create_database
from app.models.ad import Ad
from app.models.ad_variant import AdVariant
from app.models.enums import AdFormat, AdStatus, Channel, ContentOrigin
from app.models.job_offer import JobOffer


OFFER = {
    "id": "jo_001",
    "title": "Tecnico elettricista fotovoltaico",
    "company_name": "AB Group SpA",
    "status": "active",
    "source_created_at": datetime.fromisoformat("2026-02-08T20:05:13+00:00"),
    "location": {
        "street_name": "Via Artigianato", "street_number": "27", "postal_code": "25034",
        "locality": "Orzinuovi", "province": "Brescia", "province_code": "BS",
        "region": "Lombardia", "country_code": "IT",
    },
    "contract_type": "Tempo indeterminato",
    "min_exp_years": 3,
    "max_exp_years": 5,
    "ral_min": 32000,
    "ral_max": 38000,
    "currency": "EUR",
    "required_skills": ["Fotovoltaico industriale", "Cabine secondarie - MT/BT"],
    "role_description": (
        "**Carriera da Tecnico Fotovoltaico MT/BT – Costruisci una carriera nella costruzione "
        "e avviamento di grandi impianti**\n\n"
        "Entra all'interno della divisione dell'azienda specializzata nella realizzazione e "
        "manutenzione di grandi impianti fotovoltaici. Ti occuperai di:\n\n"
        "- Effettuare sopralluoghi tecnici in cantiere, raccogliere informazioni dal campo e "
        "definire lo stato di fatto, segnalare criticità tecniche e operative, proporre soluzioni "
        "tecniche da condividere con PM ed Engineering e redigere i report di sopralluogo\n"
        "- Supportare il coordinamento delle attività di montaggio delle strutture, moduli FV, "
        "cablaggi DC/AC e quadri elettrici effettuati da terze parti\n"
        "- Verificare la corretta esecuzione delle attività secondo disegni e indicazioni ricevute "
        "e segnalare scostamenti dal programma lavori\n"
        "- Eseguire le attività di collaudo attraverso verifiche preliminari, test funzionali, "
        "avviamento impianto e verifiche prestazionali\n"
        "- Supportare la verifica tecnica delle attività dei subappaltatori, segnalando non "
        "conformità o criticità e compilando le check list\n"
        "- Verificare il rispetto delle regole HSE sulle attività presidiate e segnalare situazioni "
        "di rischio, supportando il controllo qualità delle installazioni\n"
        "- Eseguire interventi in campo per la manutenzione in caso di guasti tecnici"
    ),
    "location_and_hours": (
        "- Trasferte giornaliere frequenti (senza indennità)\n"
        "- Sporadiche trasferte di più giorni (con indennità notturna)"
    ),
    "company_description": (
        "AB Group – multinazionale della cogenerazione e biogas\n\n"
        "- Fondato nel 1981 con sede centrale a Orzinuovi (Brescia), il Gruppo AB è l'azienda "
        "leader italiana nei settori della cogenerazione, biogas e rinnovabili\n"
        "- L'azienda conta oltre 1.700 dipendenti ed è presente in 20 Paesi tra Europa, Nord e "
        "Sud America\n"
        "- Il polo industriale principale si trova a Orzinuovi, su oltre 40.000 mq"
    ),
    "requirements_description": (
        "- Possiedi un diploma tecnico in elettrotecnica\n"
        "- Hai maturato almeno 3-4 anni di esperienza in installazione e avviamento di impianti FV\n"
        "- Sai leggere schemi elettrici e layout FV\n"
        "- Conosci inverter, BESS e strumentazione di verifica impianti FV\n"
        "- Hai maturato esperienza su impianti FV sopra i 100 kW\n"
        "- Hai esperienza su impianti di media tensione"
    ),
    "compensation_package": (
        "- RAL da 32.000 a 38.000 € in base all'esperienza\n"
        "- Indennità di 60 € lordi a notte per le trasferte multi-giorno\n"
        "- Ticket da 13 € per ogni giorno lavorato\n"
        "- Ore di viaggio oltre le 8 ore giornaliere pagate all'85% della paga base come da CCNL\n"
        "- Contratto a tempo indeterminato"
    ),
}


def seed_database(session: Session) -> None:
    offer = session.get(JobOffer, "jo_001")
    if offer is None:
        offer = JobOffer(**OFFER)
        session.add(offer)
        session.flush()

    samples = [
        (
            "Indeed sample",
            "seed-ad-indeed-001",
            {"channel": Channel.INDEED, "ad_format": AdFormat.TEXT, "status": AdStatus.READY,
             "location": "Via Artigianato, 27, 25034 Orzinuovi BS"},
            [
                {"id": "seed-variant-indeed-001", "variant_name": "Indeed sample", "title": "Tecnico elettricista fotovoltaico",
                 "body_text": "Assunzione diretta a tempo indeterminato in AB Group SpA.\n\nCoordina installazione, collaudo e manutenzione di impianti fotovoltaici industriali.",
                 "requirements": ["Fotovoltaico industriale", "Cabine secondarie - MT/BT"],
                 "compensation": "RAL da 32.000 a 38.000 EUR", "channel_fields": {"experience": "3-5 anni"},
                 "origin": ContentOrigin.MANUAL},
                {"id": "seed-variant-indeed-002", "variant_name": "Indeed alternative headline", "title": "Tecnico fotovoltaico industriale MT/BT",
                 "body_text": "Entra nel team che avvia e mantiene grandi impianti fotovoltaici. Contratto stabile, trasferte e indennità dedicate.",
                 "requirements": ["3-5 anni su impianti FV industriali", "Media tensione"],
                 "compensation": "RAL 32.000-38.000 EUR; 60 EUR lordi per notte fuori sede",
                 "channel_fields": {"experience": "3-5 anni"}, "origin": ContentOrigin.MANUAL},
            ],
        ),
        (
            "WhatsApp sample",
            "seed-ad-whatsapp-001",
            {"channel": Channel.WHATSAPP, "ad_format": AdFormat.IMAGE_TEXT, "status": AdStatus.DRAFT,
             "location": "Orzinuovi (BS)"},
            [{"id": "seed-variant-whatsapp-001", "variant_name": "WhatsApp sample", "title": "Tecnico Fotovoltaico",
              "body_text": "Entra in AB Group: assunzione a tempo indeterminato per attività su impianti fotovoltaici industriali. Sede a Orzinuovi, con trasferte.",
              "requirements": ["Fotovoltaico industriale", "Media tensione"],
              "compensation": "RAL 32.000-38.000 EUR",
              "creative_text": "Tecnico Fotovoltaico · AB Group · Tempo indeterminato",
              "creative_brief": "Creatività verticale in proporzione A4 per anteprima completa in chat.",
              "origin": ContentOrigin.MANUAL}],
        ),
        (
            "Instagram square creative",
            "seed-ad-instagram-001",
            {"channel": Channel.INSTAGRAM, "ad_format": AdFormat.IMAGE, "status": AdStatus.DRAFT,
             "location": "Brescia (BS)"},
            [{"id": "seed-variant-instagram-001", "variant_name": "Instagram square creative", "title": "Tecnico fotovoltaico",
              "requirements": ["Fotovoltaico industriale"],
              "creative_text": "Tecnico Fotovoltaico · Entra in una multinazionale · Impianti FV >100 kW",
              "creative_brief": "Creatività quadrata per Instagram, con focus sugli impianti industriali.",
              "origin": ContentOrigin.MANUAL}],
        ),
    ]

    for marker, seed_ad_id, ad_values, variant_values_list in samples:
        ad = session.get(Ad, seed_ad_id)
        if ad is None:
            ad = session.scalar(
                select(Ad).join(AdVariant).where(
                    Ad.job_offer_id == "jo_001", AdVariant.variant_name == marker,
                )
            )
        if ad is None:
            ad = session.scalar(
                select(Ad).where(
                    Ad.job_offer_id == "jo_001",
                    Ad.channel == ad_values["channel"],
                    Ad.ad_format == ad_values["ad_format"],
                    Ad.location == ad_values["location"],
                )
            )
        if ad is None:
            ad = Ad(id=seed_ad_id, job_offer_id="jo_001", **ad_values)
            session.add(ad)
        existing_ids = {variant.id for variant in ad.variants}
        existing_names = {variant.variant_name for variant in ad.variants}
        existing_titles = {variant.title for variant in ad.variants}
        for values in variant_values_list:
            if (values["id"] not in existing_ids
                    and values["variant_name"] not in existing_names
                    and values["title"] not in existing_titles):
                ad.variants.append(AdVariant(**values))
    session.commit()


def main() -> None:
    settings = get_settings()
    engine, session_factory = create_database(settings.database_url)
    from app import models  # noqa: F401 — register metadata before create_all

    Base.metadata.create_all(bind=engine)
    try:
        with session_factory() as session:
            seed_database(session)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
