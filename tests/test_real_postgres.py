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
