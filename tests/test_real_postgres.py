"""
Teste pe PostgreSQL REAL — nu FakeDB, nu mock.

Sarite automat (skip) daca DATABASE_URL nu e setat, ca dezvoltarea
locala fara o baza de date pornita sa nu esueze. In CI, DATABASE_URL
e setat explicit (v. .github/workflows/tests.yml), deci aceste teste
chiar ruleaza acolo.

Fiecare test isi creeaza propriii utilizatori/date (email-uri unice,
uuid4), fara sa depinda de seed-ul separat (002_seed_minimal.sql) —
doar KPI-urile sunt asigurate idempotent la inceput, fiindca
MissionEngine/FollowUpEngine/PartnerEngine au nevoie de ele pentru
persistenta scorurilor.
"""

import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import psycopg.errors
import pytest

from src.data.db import get_connection
from src.engines.rule.rule_engine import RuleEngine
from src.engines.mission.mission_engine import MissionEngine, MissionAccessDeniedError
from src.agents.mission.mission_agent import MissionAgent
from src.engines.followup.followup_engine import FollowUpEngine, FollowUpAccessDeniedError
from src.agents.followup.followup_agent import FollowUpAgent
from src.engines.partner.partner_engine import PartnerEngine, PartnerAccessDeniedError
from src.agents.partner.partner_agent import PartnerAgent
from src.agents.contact.contact_agent import ContactAgent
from src.engines.contact.contact_engine import Contact, ContactEngine
from src.engines.objection.objection_engine import Objection, ObjectionEngine, ObjectionNotFoundError
from src.agents.conversation.conversation_agent import ConversationAgent
from src.engines.conversation.conversation_engine import (
    Conversation, ConversationEngine, ConversationAccessDeniedError,
)


pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"),
    reason="Necesita DATABASE_URL (PostgreSQL real) — sarit fara DB configurat.",
)


@pytest.fixture(scope="module", autouse=True)
def ensure_kpis_seeded():
    """Asigura cei 13 KPI, idempotent — nu presupune ca 002_seed_minimal.sql a rulat deja."""
    kpis = [
        ("DIS", "Daily Impact Score"), ("CRH", "Customer Relationship Health"),
        ("PDI", "Partner Development Index"), ("PIP", "Partner Integration Progress"),
        ("OAS", "Onboarding Activation Success"), ("ERI", "Experience Reuse Index"),
        ("LRI", "Leadership Readiness Index"), ("MEI", "Mentoring Effectiveness Index"),
        ("TDI", "Team Development Index"), ("AMS", "Autonomy Maturity Score"),
        ("PES", "Presentation Effectiveness Score"), ("ORE", "Objection Resolution Effectiveness"),
        ("OPI", "Overall Performance Index"),
    ]
    with get_connection() as conn:
        with conn.cursor() as cur:
            for code, name in kpis:
                cur.execute(
                    "INSERT INTO kpis (metric_code, name, status) VALUES (%s, %s, 'PROPOSED') "
                    "ON CONFLICT (metric_code) DO NOTHING",
                    (code, name),
                )


def _create_user(prefix: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, full_name, role) VALUES (%s, %s, 'LEADER') RETURNING id",
                (f"{prefix}-{uuid4()}@nicmar.local", f"Test {prefix}"),
            )
            return cur.fetchone()[0]


class TestMissionOnRealPostgres:

    def test_full_lifecycle(self):
        """Event -> RuleEngine -> MissionEngine -> Agent -> KPI, pe PostgreSQL real."""
        owner_id = _create_user("mission")
        rule_engine = RuleEngine()
        mission_engine = MissionEngine(rule_engine=rule_engine)
        agent = MissionAgent(mission_engine=mission_engine)

        assert rule_engine.evaluate(owner_id).decision_outcome == "MISSION_READY"

        mission = mission_engine.generate_mission(owner_id, title="Test PostgreSQL real")
        assert mission.status == "GENERATED"
        assert rule_engine.evaluate(owner_id).decision_outcome == "MISSION_BLOCKED"

        mission = mission_engine.assign_mission(mission.id, owner_id)
        mission = agent.confirm_and_start(mission.id, owner_id, confirmed=True)
        mission = agent.confirm_completion(mission.id, owner_id)
        assert mission.status == "COMPLETED"

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM scores WHERE entity_id = %s", (mission.id,))
                assert cur.fetchone()[0] == 1

    def test_security_isolation(self):
        """Lider A nu poate accesa misiunea Liderului B, pe PostgreSQL real."""
        owner_a = _create_user("mission-a")
        owner_b = _create_user("mission-b")
        rule_engine = RuleEngine()
        mission_engine = MissionEngine(rule_engine=rule_engine)

        mission_b = mission_engine.generate_mission(owner_b, title="Confidential B")
        with pytest.raises(MissionAccessDeniedError):
            mission_engine.assign_mission(mission_b.id, owner_a)


class TestFollowUpOnRealPostgres:

    def test_full_lifecycle(self):
        """Event -> RuleEngine -> FollowUpEngine -> Agent -> KPI, pe PostgreSQL real."""
        owner_id = _create_user("followup")
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO contacts (owner_id, full_name, status) "
                    "VALUES (%s, %s, 'ACTIVE') RETURNING id",
                    (owner_id, "Contact Test"),
                )
                contact_id = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO conversations (owner_id, contact_id, channel, status) "
                    "VALUES (%s, %s, 'WHATSAPP', 'FOLLOWUP_NEEDED') RETURNING id",
                    (owner_id, contact_id),
                )
                conversation_id = cur.fetchone()[0]

        rule_engine = RuleEngine()
        followup_engine = FollowUpEngine(rule_engine=rule_engine)
        agent = FollowUpAgent(followup_engine=followup_engine)

        assert rule_engine.evaluate_followup(conversation_id).decision_outcome == "FOLLOWUP_READY"

        followup = followup_engine.create_from_trigger(owner_id, contact_id, conversation_id)
        assert followup.status == "PENDING"

        followup = agent.confirm_completion(followup.id, owner_id, confirmed=True)
        assert followup.status == "COMPLETED"
        assert agent.get_recent_dis_score(owner_id) == 1.0

    def test_security_isolation(self):
        """Lider A nu poate accesa follow-up-ul Liderului B, pe PostgreSQL real."""
        owner_a = _create_user("followup-a")
        owner_b = _create_user("followup-b")
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO contacts (owner_id, full_name, status) "
                    "VALUES (%s, %s, 'ACTIVE') RETURNING id",
                    (owner_b, "Contact B"),
                )
                contact_b = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO conversations (owner_id, contact_id, channel, status) "
                    "VALUES (%s, %s, 'WHATSAPP', 'FOLLOWUP_NEEDED') RETURNING id",
                    (owner_b, contact_b),
                )
                conversation_b = cur.fetchone()[0]

        rule_engine = RuleEngine()
        followup_engine = FollowUpEngine(rule_engine=rule_engine)
        fu_b = followup_engine.create_from_trigger(owner_b, contact_b, conversation_b)

        with pytest.raises(FollowUpAccessDeniedError):
            followup_engine.complete_followup(fu_b.id, owner_a, confirmed=True)


class TestPartnerOnRealPostgres:

    def test_full_lifecycle(self):
        """Event -> RuleEngine -> PartnerEngine -> Agent -> KPI, pe PostgreSQL real."""
        owner_id = _create_user("partner")
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO contacts (owner_id, full_name, status) "
                    "VALUES (%s, %s, 'CONVERTED') RETURNING id",
                    (owner_id, "Contact Partner"),
                )
                contact_id = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO partners (owner_id, contact_id, status) "
                    "VALUES (%s, %s, 'ACTIVATED') RETURNING id",
                    (owner_id, contact_id),
                )
                partner_id = cur.fetchone()[0]

        rule_engine = RuleEngine()
        partner_engine = PartnerEngine(rule_engine=rule_engine)
        agent = PartnerAgent(partner_engine=partner_engine)

        assert rule_engine.evaluate_partner_diagnostic(partner_id).decision_outcome == "PARTNER_READY"

        diagnostic = agent.request_diagnostic(partner_id, owner_id, "ENCOURAGEMENT")
        assert diagnostic.diagnostic_type == "ENCOURAGEMENT"

        agent.confirm_and_send(partner_id, owner_id, confirmed=True)
        scores = agent.get_recent_scores(owner_id)
        assert scores.get("PDI") == 1
        assert scores.get("PIP") == 1

    def test_security_isolation(self):
        """Lider A nu poate genera diagnostic pentru partenerul Liderului B, pe PostgreSQL real."""
        owner_a = _create_user("partner-a")
        owner_b = _create_user("partner-b")
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO contacts (owner_id, full_name, status) "
                    "VALUES (%s, %s, 'CONVERTED') RETURNING id",
                    (owner_b, "Contact Partner B"),
                )
                contact_b = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO partners (owner_id, contact_id, status) "
                    "VALUES (%s, %s, 'ACTIVATED') RETURNING id",
                    (owner_b, contact_b),
                )
                partner_b = cur.fetchone()[0]

        rule_engine = RuleEngine()
        partner_engine = PartnerEngine(rule_engine=rule_engine)

        with pytest.raises(PartnerAccessDeniedError):
            partner_engine.generate_diagnostic(partner_b, owner_a, "CLARITY")


class TestContactAgentOnRealPostgres:
    """
    Valideaza SQL-ul real al ContactAgent (LEFT JOIN LATERAL, PostgreSQL
    specific) - singurul punct ramas neverificat dupa GREEN pe mock,
    conform auditului tehnic din 20-contact-agent-contract.md.
    """

    def test_left_join_lateral_ruleaza_fara_eroare_si_izoleaza_owner(self):
        """
        Verifica intai ca sintaxa LEFT JOIN LATERAL e valida pe Postgres
        real (nu doar plauzibila) si ca filtrarea owner_id functioneaza
        end-to-end, nu doar in mock.
        """
        owner_a = _create_user("contact-a")
        owner_b = _create_user("contact-b")
        agent = ContactAgent()

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO contacts (owner_id, full_name, status) "
                    "VALUES (%s, %s, 'ACTIVE') RETURNING id",
                    (owner_a, "Contact Lider A"),
                )
                contact_a = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO contacts (owner_id, full_name, status) "
                    "VALUES (%s, %s, 'ACTIVE') RETURNING id",
                    (owner_b, "Contact Lider B"),
                )
                contact_b = cur.fetchone()[0]

        result_a = agent.list_prioritized_contacts(owner_a)
        result_ids_a = [c.contact_id for c in result_a]

        assert contact_a in result_ids_a
        assert contact_b not in result_ids_a

    def test_archived_exclus_pe_date_reale(self):
        owner_id = _create_user("contact-archived")
        agent = ContactAgent()

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO contacts (owner_id, full_name, status) "
                    "VALUES (%s, %s, 'ARCHIVED') RETURNING id",
                    (owner_id, "Contact Arhivat"),
                )
                contact_archived = cur.fetchone()[0]

        result = agent.list_prioritized_contacts(owner_id)
        result_ids = [c.contact_id for c in result]

        assert contact_archived not in result_ids

    def test_sortare_completa_pe_date_reale(self):
        """
        Cele 3 grupuri, verificate impreuna pe date reale: FollowUp
        scadent -> fara FollowUp -> restul (updated_at DESC). Aceasta e
        testarea reala a LEFT JOIN LATERAL - subquery-ul trebuie sa
        aduca exact ultimul FollowUp per contact, nu un JOIN simplu
        care ar duplica randuri daca un contact are mai multe FollowUp.
        """
        owner_id = _create_user("contact-sortare")
        now = datetime.now(timezone.utc)
        past = now - timedelta(days=2)
        future = now + timedelta(days=3)
        agent = ContactAgent()

        with get_connection() as conn:
            with conn.cursor() as cur:
                # Contact cu FollowUp scadent (PENDING, scheduled_at in trecut).
                cur.execute(
                    "INSERT INTO contacts (owner_id, full_name, status) "
                    "VALUES (%s, %s, 'ACTIVE') RETURNING id",
                    (owner_id, "Contact Scadent"),
                )
                contact_scadent = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO follow_ups (owner_id, contact_id, status, scheduled_at) "
                    "VALUES (%s, %s, 'PENDING', %s)",
                    (owner_id, contact_scadent, past),
                )
                # Acelasi contact primeste si un FollowUp mai vechi, COMPLETED -
                # LEFT JOIN LATERAL trebuie sa aduca doar cel mai recent
                # (scheduled_at DESC), altfel testul de mai jos ar produce
                # randuri duplicate pentru acelasi contact.
                cur.execute(
                    "INSERT INTO follow_ups (owner_id, contact_id, status, scheduled_at) "
                    "VALUES (%s, %s, 'COMPLETED', %s)",
                    (owner_id, contact_scadent, past - timedelta(days=10)),
                )

                # Contact fara niciun FollowUp.
                cur.execute(
                    "INSERT INTO contacts (owner_id, full_name, status) "
                    "VALUES (%s, %s, 'ACTIVE') RETURNING id",
                    (owner_id, "Contact Fara FollowUp"),
                )
                contact_fara_followup = cur.fetchone()[0]

                # Contact cu FollowUp PENDING dar viitor - nu e scadent, cade in Grupul 3.
                cur.execute(
                    "INSERT INTO contacts (owner_id, full_name, status) "
                    "VALUES (%s, %s, 'ACTIVE') RETURNING id",
                    (owner_id, "Contact Viitor"),
                )
                contact_viitor = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO follow_ups (owner_id, contact_id, status, scheduled_at) "
                    "VALUES (%s, %s, 'PENDING', %s)",
                    (owner_id, contact_viitor, future),
                )

        result = agent.list_prioritized_contacts(owner_id)
        result_ids = [c.contact_id for c in result]

        # Fara duplicate - dovada ca LEFT JOIN LATERAL aduce un singur rand per contact.
        assert len(result_ids) == len(set(result_ids))

        assert result_ids.index(contact_scadent) < result_ids.index(contact_fara_followup)
        assert result_ids.index(contact_fara_followup) < result_ids.index(contact_viitor)

        scadent_summary = next(c for c in result if c.contact_id == contact_scadent)
        assert scadent_summary.last_followup_status == "PENDING"

    def test_converted_client_pe_date_reale(self):
        owner_id = _create_user("contact-client")
        agent = ContactAgent()

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO contacts (owner_id, full_name, status) "
                    "VALUES (%s, %s, 'CONVERTED') RETURNING id",
                    (owner_id, "Contact Devenit Client"),
                )
                contact_id = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO clients (owner_id, contact_id, status) "
                    "VALUES (%s, %s, 'ACTIVE')",
                    (owner_id, contact_id),
                )

        result = agent.list_prioritized_contacts(owner_id)
        summary = next(c for c in result if c.contact_id == contact_id)

        assert summary.converted_to == "client"
        assert summary.pdi is None
        assert summary.pip is None

    def test_converted_partner_cu_scor_real_persistat(self):
        """
        Foloseste fluxul real PartnerEngine (nu insert manual in scores)
        pentru a persista PDI/PIP, apoi verifica ca ContactAgent le
        citeste corect - dovada end-to-end ca cele doua interogari
        (contacte + scoruri) functioneaza impreuna pe Postgres real.
        """
        owner_id = _create_user("contact-partner")

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO contacts (owner_id, full_name, status) "
                    "VALUES (%s, %s, 'CONVERTED') RETURNING id",
                    (owner_id, "Contact Devenit Partener"),
                )
                contact_id = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO partners (owner_id, contact_id, status) "
                    "VALUES (%s, %s, 'ACTIVATED') RETURNING id",
                    (owner_id, contact_id),
                )
                partner_id = cur.fetchone()[0]

        rule_engine = RuleEngine()
        partner_engine = PartnerEngine(rule_engine=rule_engine)
        partner_agent = PartnerAgent(partner_engine=partner_engine)
        partner_agent.request_diagnostic(partner_id, owner_id, "CLARITY")
        partner_agent.confirm_and_send(partner_id, owner_id, confirmed=True)

        contact_agent = ContactAgent()
        result = contact_agent.list_prioritized_contacts(owner_id)
        summary = next(c for c in result if c.contact_id == contact_id)

        assert summary.converted_to == "partner"
        assert summary.pdi == 1.0
        assert summary.pip == 1.0

    def test_pdi_pip_per_partener_individual_pe_date_reale(self):
        """
        Testul critic al corecturii de granularitate (contract sectiunea
        3.1, CONFIRMATA 17 august 2026), pe PostgreSQL real - nu mock.

        Scenariu exact confirmat:
            Partner A -> PDI 10
            Partner B -> PDI 90
            Contact A (convertit in Partner A) -> trebuie sa primeasca 10
            Contact B (convertit in Partner B) -> trebuie sa primeasca 90

        Scorurile sunt inserate direct in `scores` (nu prin PartnerEngine,
        care scrie doar placeholder 1.0 fix) - ca sa testam explicit
        valori diferite intre cei doi Parteneri, pe date reale.
        """
        owner_id = _create_user("contact-pdi-granular")

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM kpis WHERE metric_code = 'PDI'")
                pdi_kpi_id = cur.fetchone()[0]

                cur.execute(
                    "INSERT INTO contacts (owner_id, full_name, status) "
                    "VALUES (%s, %s, 'CONVERTED') RETURNING id",
                    (owner_id, "Contact A"),
                )
                contact_a = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO partners (owner_id, contact_id, status) "
                    "VALUES (%s, %s, 'ACTIVATED') RETURNING id",
                    (owner_id, contact_a),
                )
                partner_a = cur.fetchone()[0]

                cur.execute(
                    "INSERT INTO contacts (owner_id, full_name, status) "
                    "VALUES (%s, %s, 'CONVERTED') RETURNING id",
                    (owner_id, "Contact B"),
                )
                contact_b = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO partners (owner_id, contact_id, status) "
                    "VALUES (%s, %s, 'ACTIVATED') RETURNING id",
                    (owner_id, contact_b),
                )
                partner_b = cur.fetchone()[0]

                cur.execute(
                    "INSERT INTO scores (kpi_id, entity_type, entity_id, score_value, engine_source) "
                    "VALUES (%s, 'partner', %s, %s, 'TEST-MANUAL')",
                    (pdi_kpi_id, partner_a, 10.0),
                )
                cur.execute(
                    "INSERT INTO scores (kpi_id, entity_type, entity_id, score_value, engine_source) "
                    "VALUES (%s, 'partner', %s, %s, 'TEST-MANUAL')",
                    (pdi_kpi_id, partner_b, 90.0),
                )

        contact_agent = ContactAgent()
        result = contact_agent.list_prioritized_contacts(owner_id)

        summary_a = next(c for c in result if c.contact_id == contact_a)
        summary_b = next(c for c in result if c.contact_id == contact_b)

        assert summary_a.pdi == 10.0
        assert summary_b.pdi == 90.0

    def test_converted_fara_client_fara_partner_pe_date_reale(self):
        """
        Caz de date inconsistente pe Postgres real: Contact cu status
        CONVERTED, dar fara niciun rand corespunzator in clients sau
        partners. LEFT JOIN + CASE trebuie sa produca NULL, nu eroare.
        """
        owner_id = _create_user("contact-inconsistent")

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO contacts (owner_id, full_name, status) "
                    "VALUES (%s, %s, 'CONVERTED') RETURNING id",
                    (owner_id, "Contact Fara Client Sau Partner"),
                )
                contact_id = cur.fetchone()[0]

        agent = ContactAgent()
        result = agent.list_prioritized_contacts(owner_id)
        summary = next(c for c in result if c.contact_id == contact_id)

        assert summary.converted_to is None
        assert summary.pdi is None
        assert summary.pip is None


class TestObjectionEngineOnRealPostgres:
    """
    Valideaza fluxul complet ObjectionEngine pe PostgreSQL real: creare
    obiectie (create_objection, Decizia 2A), clasificare, submit_response
    cu persistare reala, izolare owner_id, si BLOCK care nu scrie nimic.
    """

    def _create_objection(self, owner_id, category, text):
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO objections (owner_id, objection_category, objection_text) "
                    "VALUES (%s, %s, %s) RETURNING id",
                    (owner_id, category, text),
                )
                return cur.fetchone()[0]

    def _create_conversation(self, owner_id):
        """Creeaza un contact + o conversatie reala, pentru testele cu conversation_id valid."""
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO contacts (owner_id, full_name, status) "
                    "VALUES (%s, %s, 'ACTIVE') RETURNING id",
                    (owner_id, "Contact Test Objection"),
                )
                contact_id = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO conversations (owner_id, contact_id, channel, status) "
                    "VALUES (%s, %s, 'WHATSAPP', 'ACTIVE') RETURNING id",
                    (owner_id, contact_id),
                )
                return cur.fetchone()[0]

    def test_submit_response_persista_real_pe_postgres(self):
        owner_id = _create_user("objection-submit")
        objection_id = self._create_objection(owner_id, "PRET", "Mi se pare cam scump.")

        engine = ObjectionEngine()
        result = engine.submit_response(
            objection_id=objection_id,
            owner_id=owner_id,
            objection_category="PRET",
            objection_text="Mi se pare cam scump.",
            response_text="Înțeleg, chiar poate părea o investiție la prima vedere.",
            response_variant_used="CALDA",
        )

        assert result.persisted is True
        assert result.validation.level == "PASS"

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT response_text, response_variant_used FROM objections WHERE id = %s",
                    (objection_id,),
                )
                row = cur.fetchone()

        assert row[0] == "Înțeleg, chiar poate părea o investiție la prima vedere."
        assert row[1] == "CALDA"

    def test_submit_response_block_nu_scrie_nimic_pe_postgres(self):
        owner_id = _create_user("objection-block")
        objection_id = self._create_objection(owner_id, "PRET", "e scump")

        engine = ObjectionEngine()
        result = engine.submit_response(
            objection_id=objection_id,
            owner_id=owner_id,
            objection_category="PRET",
            objection_text="e scump",
            response_text="Îți garantez că vei câștiga bani.",
            response_variant_used="CALDA",
        )

        assert result.persisted is False
        assert result.validation.level == "BLOCK"

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT response_text FROM objections WHERE id = %s", (objection_id,))
                row = cur.fetchone()

        assert row[0] is None

    def test_submit_response_izoleaza_owner_id_pe_postgres(self):
        """Liderul B nu poate persista un raspuns pe obiectia liderului A."""
        owner_a = _create_user("objection-owner-a")
        owner_b = _create_user("objection-owner-b")
        objection_id = self._create_objection(owner_a, "TIMP", "nu am timp")

        engine = ObjectionEngine()
        with pytest.raises(ObjectionNotFoundError):
            engine.submit_response(
                objection_id=objection_id,
                owner_id=owner_b,
                objection_category="TIMP",
                objection_text="nu am timp",
                response_text="Înțeleg, poți începe cu 10 minute pe zi.",
                response_variant_used="DIRECTA",
            )

    def test_clasificare_si_variante_pe_postgres_end_to_end(self):
        """Flux complet: text liber -> clasificare -> variante -> submit."""
        owner_id = _create_user("objection-e2e")
        objection_text = "Nu am timp."
        objection_id = self._create_objection(owner_id, "TIMP", objection_text)

        engine = ObjectionEngine()
        category = engine.classify(objection_text)
        assert category == "TIMP"

        variants = engine.get_variants(category)
        assert set(variants.keys()) == {"CALDA", "DIRECTA", "INTREBARE"}

        result = engine.submit_response(
            objection_id=objection_id,
            owner_id=owner_id,
            objection_category=category,
            objection_text=objection_text,
            response_text=variants["DIRECTA"],
            response_variant_used="DIRECTA",
        )

        assert result.persisted is True
        assert result.validation.level == "PASS"

    # ------------------------------------------------------------------
    # get_objection() — Decizia 8A, 25-get-objection-contract.md
    # ------------------------------------------------------------------

    def test_get_objection_returneaza_date_reale_pe_postgres(self):
        """get_objection() citeste corect din PostgreSQL real, pentru owner-ul corect."""
        owner_id = _create_user("get-objection-happy")
        engine = ObjectionEngine()

        created = engine.create_objection(
            owner_id=owner_id, objection_text="e scump", objection_category="PRET",
        )

        fetched = engine.get_objection(objection_id=created.id, owner_id=owner_id)

        assert fetched == created

    def test_get_objection_izoleaza_owner_id_pe_postgres(self):
        """
        User A creeaza o obiectie. User B incearca get_objection(id_A, user_B)
        -> ObjectionNotFoundError, verificat pe PostgreSQL real, nu mockat.
        """
        owner_a = _create_user("get-objection-owner-a")
        owner_b = _create_user("get-objection-owner-b")
        engine = ObjectionEngine()

        objection_a = engine.create_objection(
            owner_id=owner_a, objection_text="nu am timp", objection_category="TIMP",
        )

        with pytest.raises(ObjectionNotFoundError):
            engine.get_objection(objection_id=objection_a.id, owner_id=owner_b)

    def test_get_objection_id_inexistent_ridica_eroare_pe_postgres(self):
        """objection_id complet inexistent -> ObjectionNotFoundError, pe PostgreSQL real."""
        owner_id = _create_user("get-objection-inexistent")
        engine = ObjectionEngine()

        with pytest.raises(ObjectionNotFoundError):
            engine.get_objection(objection_id=uuid4(), owner_id=owner_id)

    # ------------------------------------------------------------------
    # create_objection() — Decizia 2A, 20-2A-create-objection-contract.md
    # ------------------------------------------------------------------

    def test_create_objection_insert_real_toate_campurile(self):
        """INSERT real -> gen_random_uuid() -> RETURNING -> Objection complet."""
        owner_id = _create_user("objection-create")
        engine = ObjectionEngine()

        objection = engine.create_objection(
            owner_id=owner_id,
            objection_text="Mi se pare cam scump.",
            objection_category="PRET",
        )

        assert isinstance(objection, Objection)
        assert objection.id is not None
        assert objection.owner_id == owner_id
        assert objection.conversation_id is None
        assert objection.objection_category == "PRET"
        assert objection.objection_text == "Mi se pare cam scump."
        assert objection.resolution_status == "OPEN"

        # Verificare independenta, direct din DB — nu ne bazam doar pe RETURNING
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT owner_id, conversation_id, objection_category, "
                    "objection_text, resolution_status FROM objections WHERE id = %s",
                    (objection.id,),
                )
                row = cur.fetchone()

        assert row == (owner_id, None, "PRET", "Mi se pare cam scump.", "OPEN")

    def test_create_objection_conversation_id_none_acceptat_de_postgres(self):
        """conversation_id=None -> coloana e efectiv NULL in DB, nu doar in Python."""
        owner_id = _create_user("objection-create-noconv")
        engine = ObjectionEngine()

        objection = engine.create_objection(
            owner_id=owner_id,
            objection_text="Nu am incredere in structura.",
            objection_category="INCREDERE_STRUCTURA",
        )

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT conversation_id FROM objections WHERE id = %s",
                    (objection.id,),
                )
                assert cur.fetchone()[0] is None

    def test_create_objection_cu_conversation_id_real(self):
        """conversation_id valid -> INSERT reuseste, FK respectat."""
        owner_id = _create_user("objection-create-conv")
        conversation_id = self._create_conversation(owner_id)
        engine = ObjectionEngine()

        objection = engine.create_objection(
            owner_id=owner_id,
            objection_text="Ma mai gandesc.",
            objection_category="AMANARE",
            conversation_id=conversation_id,
        )

        assert objection.conversation_id == conversation_id

    def test_create_objection_owner_invalid_ridica_fk_violation_real(self):
        """owner_id inexistent -> psycopg.errors.ForeignKeyViolation propaga efectiv din Postgres."""
        engine = ObjectionEngine()

        with pytest.raises(psycopg.errors.ForeignKeyViolation):
            engine.create_objection(
                owner_id=uuid4(),  # nu exista in users
                objection_text="e scump",
                objection_category="PRET",
            )

    def test_create_objection_conversation_invalid_ridica_fk_violation_real(self):
        """conversation_id inexistent -> psycopg.errors.ForeignKeyViolation propaga efectiv din Postgres."""
        owner_id = _create_user("objection-create-badconv")
        engine = ObjectionEngine()

        with pytest.raises(psycopg.errors.ForeignKeyViolation):
            engine.create_objection(
                owner_id=owner_id,
                objection_text="e scump",
                objection_category="PRET",
                conversation_id=uuid4(),  # nu exista in conversations
            )

    def test_create_objection_apeluri_identice_creeaza_doua_randuri_pe_postgres(self):
        """Fara deduplicare (Decizia 2A): doua apeluri identice -> doua randuri reale distincte."""
        owner_id = _create_user("objection-create-dup")
        engine = ObjectionEngine()

        first = engine.create_objection(
            owner_id=owner_id, objection_text="e scump", objection_category="PRET",
        )
        second = engine.create_objection(
            owner_id=owner_id, objection_text="e scump", objection_category="PRET",
        )

        assert first.id != second.id

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) FROM objections "
                    "WHERE owner_id = %s AND objection_category = 'PRET' AND objection_text = 'e scump'",
                    (owner_id,),
                )
                assert cur.fetchone()[0] == 2


class TestConversationAgentOnRealPostgres:
    """
    Valideaza orchestrarea completa ConversationAgent -> ObjectionEngine pe
    PostgreSQL real. Componentele individuale (classify, create_objection,
    get_variants, submit_response) sunt deja acoperite in
    TestObjectionEngineOnRealPostgres — aici verificam ca legarea lor prin
    ConversationAgent produce exact aceeasi persistenta reala, capat la capat.
    """

    def test_flux_complet_analiza_variante_confirmare_pas_pas(self):
        """
        analyze_objection -> prepare_response_options -> confirm_response,
        cu PASS, verificat direct din tabela objections dupa fiecare pas.
        """
        owner_id = _create_user("conv-agent-flow")
        agent = ConversationAgent(objection_engine=ObjectionEngine(), conversation_engine=ConversationEngine())

        # Pasul 1 — analiza, fara nicio scriere
        analysis = agent.analyze_objection("Nu am timp.")
        assert analysis.detected_category == "TIMP"
        assert analysis.needs_manual_selection is False

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM objections WHERE owner_id = %s", (owner_id,))
                assert cur.fetchone()[0] == 0  # analiza nu a scris nimic

        # Pasul 2 — creare reala + variante
        prep = agent.prepare_response_options(
            owner_id=owner_id,
            objection_text="Nu am timp.",
            objection_category=analysis.detected_category,
        )
        assert prep.objection.id is not None
        assert prep.objection.resolution_status == "OPEN"
        assert set(prep.variants.keys()) == {"CALDA", "DIRECTA", "INTREBARE"}

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT objection_category, response_text FROM objections WHERE id = %s",
                    (prep.objection.id,),
                )
                row = cur.fetchone()
                assert row == ("TIMP", None)  # creat, dar fara raspuns inca

        # Pasul 3 — confirmare, cu scalari (objection_id + owner_id), Decizia 8A
        confirmation = agent.confirm_response(
            objection_id=prep.objection.id,
            owner_id=owner_id,
            response_text=prep.variants["DIRECTA"],
            response_variant_used="DIRECTA",
        )
        assert confirmation.persisted is True
        assert confirmation.validation_level == "PASS"
        assert confirmation.reason is None

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT response_text, response_variant_used FROM objections WHERE id = %s",
                    (prep.objection.id,),
                )
                row = cur.fetchone()
                assert row == (prep.variants["DIRECTA"], "DIRECTA")

    def test_confirm_response_block_nu_scrie_nimic_prin_agent(self):
        """BLOCK, prin orchestrarea agentului -> nimic persistat, la fel ca ObjectionEngine direct."""
        owner_id = _create_user("conv-agent-block")
        agent = ConversationAgent(objection_engine=ObjectionEngine(), conversation_engine=ConversationEngine())

        prep = agent.prepare_response_options(
            owner_id=owner_id, objection_text="e scump", objection_category="PRET",
        )

        confirmation = agent.confirm_response(
            objection_id=prep.objection.id,
            owner_id=owner_id,
            response_text="Îți garantez că vei câștiga bani.",
            response_variant_used="CALDA",
        )

        assert confirmation.persisted is False
        assert confirmation.validation_level == "BLOCK"
        assert confirmation.reason is not None

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT response_text FROM objections WHERE id = %s", (prep.objection.id,))
                assert cur.fetchone()[0] is None

    def test_confirm_response_izoleaza_owner_id_prin_agent(self):
        """
        Liderul B nu poate confirma un raspuns pe obiectia liderului A, prin
        agent — acum verificat direct la nivelul real de securitate
        (get_objection() cu owner_id gresit), nu simuland un obiect manual.
        """
        owner_a = _create_user("conv-agent-owner-a")
        owner_b = _create_user("conv-agent-owner-b")
        agent = ConversationAgent(objection_engine=ObjectionEngine(), conversation_engine=ConversationEngine())

        prep = agent.prepare_response_options(
            owner_id=owner_a, objection_text="nu am timp", objection_category="TIMP",
        )

        with pytest.raises(ObjectionNotFoundError):
            agent.confirm_response(
                objection_id=prep.objection.id,
                owner_id=owner_b,
                response_text="Înțeleg, poți începe cu 10 minute pe zi.",
                response_variant_used="DIRECTA",
            )


class TestContactEngineOnRealPostgres:
    """
    Valideaza ContactEngine.create_contact() pe PostgreSQL real —
    Decizia 42, 42-contact-events-contract.md. Gol de testare
    identificat la audit: pana acum exista doar TestContactAgentOnRealPostgres
    (read-only, alta componenta) — zero acoperire reala pentru scrierea
    efectiva a unui Contact.
    """

    def test_creeaza_contact_pe_postgres_real(self):
        owner_id = _create_user("contact-engine-create")
        engine = ContactEngine()

        contact = engine.create_contact(owner_id=owner_id, full_name="Contact Real Postgres")

        assert isinstance(contact, Contact)
        assert contact.owner_id == owner_id
        assert contact.full_name == "Contact Real Postgres"
        assert contact.status == "NEW"

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT owner_id, full_name, status FROM contacts WHERE id = %s",
                    (contact.id,),
                )
                row = cur.fetchone()
        assert row == (owner_id, "Contact Real Postgres", "NEW")

    def test_evenimentul_contact_created_e_scris_in_events(self):
        """Contract 42, criteriul 3."""
        owner_id = _create_user("contact-engine-event")
        engine = ContactEngine()

        contact = engine.create_contact(owner_id=owner_id, full_name="Contact Event Test")

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT event_name, target_object FROM events WHERE target_object_id = %s",
                    (contact.id,),
                )
                row = cur.fetchone()
        assert row == ("ContactCreated", "contact")


class TestConversationEngineOnRealPostgres:
    """
    Valideaza ConversationEngine ("Conversation Writer") pe PostgreSQL
    real — Decizia 29, 29-conversation-writer-contract.md. Nu are nicio
    legatura cu ConversationAgent (Objection).
    """

    def _create_contact(self, owner_id):
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO contacts (owner_id, full_name, status) "
                    "VALUES (%s, %s, 'ACTIVE') RETURNING id",
                    (owner_id, "Contact Test ConversationEngine"),
                )
                return cur.fetchone()[0]

    def test_creeaza_conversatie_noua_pe_postgres_real(self):
        owner_id = _create_user("conv-engine-create")
        contact_id = self._create_contact(owner_id)
        engine = ConversationEngine()

        conversation = engine.get_or_create_conversation(owner_id=owner_id, contact_id=contact_id)

        assert isinstance(conversation, Conversation)
        assert conversation.owner_id == owner_id
        assert conversation.contact_id == contact_id
        assert conversation.channel == "WHATSAPP"
        assert conversation.status == "INITIATED"

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT owner_id, contact_id, channel, status FROM conversations WHERE id = %s",
                    (conversation.id,),
                )
                row = cur.fetchone()
        assert row == (owner_id, contact_id, "WHATSAPP", "INITIATED")

    def test_apel_repetat_returneaza_aceeasi_conversatie_idempotency(self):
        """Doua apeluri pentru acelasi contact -> ACEEASI conversatie, nu doua randuri."""
        owner_id = _create_user("conv-engine-idempotent")
        contact_id = self._create_contact(owner_id)
        engine = ConversationEngine()

        first = engine.get_or_create_conversation(owner_id=owner_id, contact_id=contact_id)
        second = engine.get_or_create_conversation(owner_id=owner_id, contact_id=contact_id)

        assert first.id == second.id

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) FROM conversations WHERE owner_id = %s AND contact_id = %s",
                    (owner_id, contact_id),
                )
                assert cur.fetchone()[0] == 1

    def test_user_b_nu_poate_crea_conversatie_pe_contactul_lui_user_a(self):
        """
        User A creeaza un contact. User B incearca
        get_or_create_conversation(contact_id_A, owner_B) ->
        ConversationAccessDeniedError, verificat pe PostgreSQL real.
        """
        owner_a = _create_user("conv-engine-owner-a")
        owner_b = _create_user("conv-engine-owner-b")
        contact_id_a = self._create_contact(owner_a)
        engine = ConversationEngine()

        with pytest.raises(ConversationAccessDeniedError):
            engine.get_or_create_conversation(owner_id=owner_b, contact_id=contact_id_a)

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) FROM conversations WHERE contact_id = %s", (contact_id_a,),
                )
                assert cur.fetchone()[0] == 0  # nimic scris pentru incercarea lui B

    def test_contact_id_inexistent_ridica_access_denied_pe_postgres(self):
        owner_id = _create_user("conv-engine-no-contact")
        engine = ConversationEngine()

        with pytest.raises(ConversationAccessDeniedError):
            engine.get_or_create_conversation(owner_id=owner_id, contact_id=uuid4())

    def test_conversatie_rezolvata_nu_blocheaza_creare_noua(self):
        """
        O conversatie RESOLVED nu conteaza ca 'deschisa' — un apel nou
        pentru acelasi contact creeaza o conversatie noua, distincta.
        """
        owner_id = _create_user("conv-engine-resolved")
        contact_id = self._create_contact(owner_id)
        engine = ConversationEngine()

        first = engine.get_or_create_conversation(owner_id=owner_id, contact_id=contact_id)

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE conversations SET status = 'RESOLVED' WHERE id = %s", (first.id,),
                )

        second = engine.get_or_create_conversation(owner_id=owner_id, contact_id=contact_id)

        assert second.id != first.id
        assert second.status == "INITIATED"

    def test_evenimentul_conversation_created_e_scris_in_events(self):
        owner_id = _create_user("conv-engine-event")
        contact_id = self._create_contact(owner_id)
        engine = ConversationEngine()

        conversation = engine.get_or_create_conversation(owner_id=owner_id, contact_id=contact_id)

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT event_name, target_object FROM events WHERE target_object_id = %s",
                    (conversation.id,),
                )
                row = cur.fetchone()
        assert row == ("ConversationCreated", "conversation")
