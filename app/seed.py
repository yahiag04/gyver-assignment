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
        "Carriera da Tecnico Fotovoltaico MT/BT: costruzione e avviamento di grandi impianti. "
        "Effettuerai sopralluoghi tecnici, raccoglierai informazioni e segnalerai criticità; "
        "supporterai il coordinamento di strutture, moduli FV, cablaggi DC/AC e quadri; "
        "verificherai disegni, avanzamento lavori e attività dei subappaltatori; eseguirai "
        "collaudi, test funzionali, avviamento e verifiche prestazionali; presidierai HSE e "
        "qualità e interverrai in campo per la manutenzione in caso di guasti."
    ),
    "location_and_hours": (
        "Trasferte giornaliere frequenti (senza indennità); sporadiche trasferte di più "
        "giorni (con indennità notturna)."
    ),
    "company_description": (
        "AB Group, multinazionale della cogenerazione e biogas, è stata fondata nel 1981 e "
        "ha sede a Orzinuovi (Brescia). È leader italiana nei settori cogenerazione, biogas "
        "e rinnovabili, conta oltre 1.700 dipendenti in 20 Paesi tra Europa, Nord e Sud "
        "America e ha un polo industriale di oltre 40.000 mq."
    ),
    "requirements_description": (
        "Diploma tecnico in elettrotecnica; almeno 3-4 anni di esperienza in installazione "
        "e avviamento di impianti FV; lettura di schemi elettrici e layout FV; conoscenza "
        "di inverter, BESS e strumentazione di verifica; esperienza su impianti oltre 100 "
        "kW e in media tensione."
    ),
    "compensation_package": (
        "RAL da 32.000 a 38.000 EUR in base all'esperienza; indennità di 60 EUR lordi a "
        "notte per trasferte multi-giorno; ticket da 13 EUR per giorno lavorato; ore di "
        "viaggio oltre le 8 giornaliere pagate all'85% della paga base come da CCNL; "
        "contratto a tempo indeterminato."
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
            {"channel": Channel.INDEED, "ad_format": AdFormat.TEXT, "status": AdStatus.READY,
             "location": "Via Artigianato, 27, 25034 Orzinuovi BS"},
            [
                {"variant_name": "Indeed sample", "title": "Tecnico elettricista fotovoltaico",
                 "body_text": "Assunzione diretta a tempo indeterminato in AB Group SpA.\n\nCoordina installazione, collaudo e manutenzione di impianti fotovoltaici industriali.",
                 "requirements": ["Fotovoltaico industriale", "Cabine secondarie - MT/BT"],
                 "compensation": "RAL da 32.000 a 38.000 EUR", "channel_fields": {"experience": "3-5 anni"},
                 "origin": ContentOrigin.MANUAL},
                {"variant_name": "Indeed alternative headline", "title": "Tecnico fotovoltaico industriale MT/BT",
                 "body_text": "Entra nel team che avvia e mantiene grandi impianti fotovoltaici. Contratto stabile, trasferte e indennità dedicate.",
                 "requirements": ["3-5 anni su impianti FV industriali", "Media tensione"],
                 "compensation": "RAL 32.000-38.000 EUR; 60 EUR lordi per notte fuori sede",
                 "channel_fields": {"experience": "3-5 anni"}, "origin": ContentOrigin.MANUAL},
            ],
        ),
        (
            "WhatsApp sample",
            {"channel": Channel.WHATSAPP, "ad_format": AdFormat.IMAGE_TEXT, "status": AdStatus.DRAFT,
             "location": "Orzinuovi (BS)"},
            [{"variant_name": "WhatsApp sample", "title": "Tecnico Fotovoltaico",
              "body_text": "Entra in AB Group: assunzione a tempo indeterminato per attività su impianti fotovoltaici industriali. Sede a Orzinuovi, con trasferte.",
              "requirements": ["Fotovoltaico industriale", "Media tensione"],
              "compensation": "RAL 32.000-38.000 EUR",
              "creative_text": "Tecnico Fotovoltaico · AB Group · Tempo indeterminato",
              "creative_brief": "Creatività verticale in proporzione A4 per anteprima completa in chat.",
              "origin": ContentOrigin.MANUAL}],
        ),
        (
            "Instagram square creative",
            {"channel": Channel.INSTAGRAM, "ad_format": AdFormat.IMAGE, "status": AdStatus.DRAFT,
             "location": "Brescia (BS)"},
            [{"variant_name": "Instagram square creative", "title": "Tecnico fotovoltaico",
              "requirements": ["Fotovoltaico industriale"],
              "creative_text": "Tecnico Fotovoltaico · Entra in una multinazionale · Impianti FV >100 kW",
              "creative_brief": "Creatività quadrata per Instagram, con focus sugli impianti industriali.",
              "origin": ContentOrigin.MANUAL}],
        ),
    ]

    for marker, ad_values, variant_values_list in samples:
        ad = session.scalar(
            select(Ad).join(AdVariant).where(
                Ad.job_offer_id == "jo_001", AdVariant.variant_name == marker,
            )
        )
        if ad is None:
            ad = Ad(job_offer_id="jo_001", **ad_values)
            session.add(ad)
        existing_names = {variant.variant_name for variant in ad.variants}
        for values in variant_values_list:
            if values["variant_name"] not in existing_names:
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
