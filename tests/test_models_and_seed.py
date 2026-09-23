from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.session import Base
from app.models import Ad, AdVariant, JobOffer
from app.models.enums import AdFormat, AdStatus, Channel, ContentOrigin
from app.repositories.ad_repository import AdRepository
from app.repositories.job_offer_repository import JobOfferRepository
from app.seed import seed_database


def make_session(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'models.db'}")
    Base.metadata.create_all(engine)
    return Session(engine)


def test_offer_ads_and_variants_persist_and_can_be_filtered(tmp_path):
    with make_session(tmp_path) as session:
        offer = JobOffer(
            id="jo_test",
            title="Tecnico elettricista",
            company_name="AB Group SpA",
            status="active",
            location={"locality": "Orzinuovi", "province": "Brescia"},
            contract_type="Tempo indeterminato",
            min_exp_years=3,
            max_exp_years=5,
            ral_min=32000,
            ral_max=38000,
            currency="EUR",
            required_skills=["Fotovoltaico industriale"],
            role_description="Descrizione interna",
            location_and_hours="Trasferte giornaliere",
            company_description="Multinazionale",
            requirements_description="Diploma tecnico",
            compensation_package="RAL 32-38k",
        )
        session.add(offer)
        session.commit()

        repository = AdRepository(session)
        indeed = repository.create_ad(
            job_offer_id=offer.id,
            channel=Channel.INDEED,
            ad_format=AdFormat.TEXT,
            location="Orzinuovi (BS)",
            status=AdStatus.DRAFT,
        )
        repository.create_variant(
            ad_id=indeed.id,
            variant_name="Prima versione",
            title="Tecnico fotovoltaico",
            body_text="Annuncio Indeed",
            origin=ContentOrigin.MANUAL,
        )
        repository.create_ad(
            job_offer_id=offer.id,
            channel=Channel.WHATSAPP,
            ad_format=AdFormat.IMAGE_TEXT,
            location="Milano",
            status=AdStatus.READY,
        )
        session.commit()

        assert JobOfferRepository(session).get_job_offer("jo_test").required_skills == [
            "Fotovoltaico industriale"
        ]
        assert len(repository.get_ad(indeed.id).variants) == 1
        assert [ad.channel for ad in repository.list_ads(job_offer_id="jo_test")] == [
            Channel.INDEED,
            Channel.WHATSAPP,
        ]
        assert [ad.channel for ad in repository.list_ads(channel=Channel.WHATSAPP)] == [
            Channel.WHATSAPP
        ]


def test_enum_values_are_restricted_to_supported_domain_values():
    import pytest
    from pydantic import ValidationError

    from app.schemas.ad import AdCreate

    with pytest.raises(ValidationError):
        AdCreate(job_offer_id="jo_001", channel="linkedin", format="text")


def test_seed_is_idempotent_and_creates_assignment_examples(tmp_path):
    with make_session(tmp_path) as session:
        seed_database(session)
        seed_database(session)

        offers = JobOfferRepository(session).list_job_offers()
        ads = AdRepository(session).list_ads(job_offer_id="jo_001")

        assert [offer.id for offer in offers] == ["jo_001"]
        assert len(ads) == 3
        assert {(ad.channel, ad.ad_format) for ad in ads} == {
            (Channel.INDEED, AdFormat.TEXT),
            (Channel.WHATSAPP, AdFormat.IMAGE_TEXT),
            (Channel.INSTAGRAM, AdFormat.IMAGE),
        }
        assert {ad.channel: len(ad.variants) for ad in ads} == {
            Channel.INDEED: 2,
            Channel.WHATSAPP: 1,
            Channel.INSTAGRAM: 1,
        }
        assert any(variant.variant_name == "Indeed alternative headline" for ad in ads for variant in ad.variants)
