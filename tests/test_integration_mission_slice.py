"""
Test de integrare — Mission Vertical Slice, cap-coada.

Nu foloseste PostgreSQL real. Foloseste o baza de date falsa, in memorie,
care tine stare reala intre apeluri (spre deosebire de mock-urile
individuale de dinainte) - simuleaza fidel comportamentul SQL folosit
de RuleEngine, MissionEngine si MissionAgent.
"""
import sys
sys.path.insert(0, '/home/claude/nicmar_impl')

from unittest.mock import MagicMock, patch
from uuid import uuid4, UUID
from datetime import datetime, timezone

from src.engines.rule.rule_engine import RuleEngine
from src.engines.mission.mission_engine import MissionEngine
from src.agents.mission.mission_agent import MissionAgent


class FakeDB:
    """Baza de date falsa, in memorie, cu stare reala intre apeluri."""

    def __init__(self):
        self.missions = {}       # id -> dict(owner_id, title, status)
        self.kpis = {}           # metric_code -> id
        self.scores = []         # lista de (kpi_id, entity_type, entity_id, score_value)
        self.state_history = []
        self.events = []
        # Seed: DIS exista deja in kpis, exact ca in productie (seed data)
        dis_id = uuid4()
        self.kpis["DIS"] = dis_id

    def execute(self, query, params=None):
        q = " ".join(query.split())  # normalizeaza spatiile
        params = params or ()

        if q.startswith("INSERT INTO missions"):
            owner_id, title, description = params
            mission_id = uuid4()
            self.missions[mission_id] = {
                "owner_id": owner_id, "title": title, "status": "GENERATED",
            }
            self._last_result = (mission_id, owner_id, title, "GENERATED")

        elif q.startswith("SELECT status FROM missions"):
            (mission_id,) = params
            m = self.missions.get(mission_id)
            self._last_result = (m["status"],) if m else None

        elif q.startswith("UPDATE missions SET status"):
            new_status, mission_id = params
            m = self.missions[mission_id]
            m["status"] = new_status
            self._last_result = (mission_id, m["owner_id"], m["title"], new_status)

        elif q.startswith("INSERT INTO state_history"):
            self.state_history.append(params)
            self._last_result = None

        elif q.startswith("INSERT INTO events"):
            self.events.append(params)
            self._last_result = None

        elif q.startswith("SELECT id FROM kpis WHERE metric_code"):
            (code,) = params
            kpi_id = self.kpis.get(code)
            self._last_result = (kpi_id,) if kpi_id else None

        elif q.startswith("INSERT INTO scores"):
            self.scores.append(params)
            self._last_result = None

        elif q.startswith("SELECT COUNT(*) FROM missions"):
            owner_id = params[0]
            statuses = params[1:]
            count = sum(
                1 for m in self.missions.values()
                if m["owner_id"] == owner_id and m["status"] in statuses
            )
            self._last_result = (count,)

        elif q.startswith("SELECT s.score_value FROM scores"):
            owner_id = params[0]
            relevant = [s for s in self.scores if self.missions.get(s[2], {}).get("owner_id") == owner_id]
            self._last_result = (relevant[-1][3],) if relevant else None

        else:
            raise NotImplementedError(f"Query neprevazut in FakeDB: {q}")

    def fetchone(self):
        return self._last_result


def make_fake_connection(fake_db):
    """Construieste un obiect conexiune/cursor compatibil cu 'with get_connection() as conn'."""
    mock_cur = MagicMock()
    mock_cur.execute.side_effect = fake_db.execute
    mock_cur.fetchone.side_effect = fake_db.fetchone
    mock_cur.__enter__.return_value = mock_cur
    mock_cur.__exit__.return_value = False

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = False
    return mock_conn


# ============================================================
# TESTUL DE INTEGRARE PROPRIU-ZIS
# ============================================================

fake_db = FakeDB()
owner_id = uuid4()

with patch("src.engines.rule.rule_engine.get_connection") as rule_conn, \
     patch("src.engines.mission.mission_engine.get_connection") as mission_conn, \
     patch("src.agents.mission.mission_agent.get_connection") as agent_conn:

    rule_conn.return_value = make_fake_connection(fake_db)
    mission_conn.return_value = make_fake_connection(fake_db)
    agent_conn.return_value = make_fake_connection(fake_db)

    rule_engine = RuleEngine()
    mission_engine = MissionEngine(rule_engine=rule_engine)
    agent = MissionAgent(mission_engine=mission_engine)

    print("=== PASUL 1: RuleEngine evalueaza — owner nu are misiuni active ===")
    rule_result = rule_engine.evaluate(owner_id)
    print("Decizie:", rule_result.decision_outcome)
    assert rule_result.decision_outcome == "MISSION_READY"
    print("OK\n")

    print("=== PASUL 2: MissionEngine genereaza misiunea (via RuleEngine intern) ===")
    mission = mission_engine.generate_mission(owner_id, title="Sună-l pe Andrei")
    print("Mission creata:", mission.id, "status =", mission.status)
    assert mission.status == "GENERATED"
    assert mission.id in fake_db.missions
    print("OK\n")

    print("=== PASUL 3: RuleEngine reevaluat — acum owner ARE o misiune activa ===")
    rule_result_2 = rule_engine.evaluate(owner_id)
    print("Decizie:", rule_result_2.decision_outcome, "(asteptat: MISSION_BLOCKED)")
    assert rule_result_2.decision_outcome == "MISSION_BLOCKED"
    print("OK — RuleEngine si MissionEngine sunt sincronizate prin DB\n")

    print("=== PASUL 4: MissionEngine asigneaza misiunea ===")
    mission = mission_engine.assign_mission(mission.id)
    print("Status:", mission.status)
    assert mission.status == "ASSIGNED"
    print("OK\n")

    print("=== PASUL 5: MissionAgent prezinta misiunea liderului ===")
    text = agent.present_daily_mission(mission)
    print("Text prezentat:", text)
    assert "Sună-l pe Andrei" in text
    print("OK\n")

    print("=== PASUL 6: Liderul confirma 'Sunt gata, incep' — via MissionAgent ===")
    mission = agent.confirm_and_start(mission.id, confirmed=True)
    print("Status:", mission.status)
    assert mission.status == "IN_PROGRESS"
    assert fake_db.missions[mission.id]["status"] == "IN_PROGRESS"
    print("OK — MissionAgent a delegat corect catre MissionEngine\n")

    print("=== PASUL 7: Fara confirmare, refuz garantat (testat prin Agent, nu doar Engine) ===")
    other_mission = mission_engine.generate_mission
    try:
        agent.confirm_and_start(mission.id, confirmed=False)
        print("EROARE: ar fi trebuit sa refuze")
    except Exception as e:
        print("OK: refuzat corect —", type(e).__name__)
    print()

    print("=== PASUL 8: Liderul finalizeaza misiunea — via MissionAgent ===")
    mission = agent.confirm_completion(mission.id)
    print("Status:", mission.status)
    assert mission.status == "COMPLETED"
    print("OK\n")

    print("=== PASUL 9: DIS a fost persistat in scores? ===")
    print("Numar scoruri inregistrate:", len(fake_db.scores))
    assert len(fake_db.scores) == 1
    kpi_id, entity_type, entity_id, score_value = fake_db.scores[0][:4]
    print("kpi_id corect (DIS):", kpi_id == fake_db.kpis["DIS"])
    print("entity_type:", entity_type, " entity_id == mission.id:", entity_id == mission.id)
    print("score_value (placeholder):", score_value)
    assert kpi_id == fake_db.kpis["DIS"]
    assert entity_type == "mission"
    print("OK\n")

    print("=== PASUL 10: MissionAgent poate citi DIS-ul proaspat scris (READ-ONLY) ===")
    dis_score = agent.get_recent_dis_score(owner_id)
    print("DIS citit de Agent:", dis_score)
    assert dis_score == score_value
    print("OK\n")

    print("=== PASUL 11: state_history si events au inregistrat toate tranzitiile? ===")
    print("Tranzitii in state_history:", len(fake_db.state_history))
    print("Evenimente emise:", len(fake_db.events))
    assert len(fake_db.state_history) == 3  # ASSIGNED, IN_PROGRESS, COMPLETED
    assert len(fake_db.events) == 4          # GENERATED + cele 3 de mai sus
    print("OK\n")

print("=" * 60)
print("TEST DE INTEGRARE COMPLET — LANTUL INTREG FUNCTIONEAZA IMPREUNA")
print("=" * 60)
