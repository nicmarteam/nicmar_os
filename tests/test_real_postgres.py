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
