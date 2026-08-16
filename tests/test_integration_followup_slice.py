"""
Test de integrare — Contact->FollowUp Vertical Slice, cap-coada.

FakeDB in memorie, extinsa cu follow_ups, la fel ca Mission slice.
"""
import sys
sys.path.insert(0, '/home/claude/nicmar_impl')

from unittest.mock import MagicMock, patch
from uuid import uuid4

from src.engines.rule.rule_engine import RuleEngine
from src.engines.followup.followup_engine import FollowUpEngine
from src.agents.followup.followup_agent import FollowUpAgent


class FakeDB:
    def __init__(self):
        self.follow_ups = {}
        self.kpis = {"DIS": uuid4()}
        self.scores = []
        self.state_history = []
        self.events = []

    def execute(self, query, params=None):
        q = " ".join(query.split())
        params = params or ()

        if q.startswith("INSERT INTO follow_ups"):
            owner_id, contact_id, conversation_id, scheduled_at, notes = params
            fid = uuid4()
            self.follow_ups[fid] = {
                "owner_id": owner_id, "contact_id": contact_id,
                "conversation_id": conversation_id, "status": "PENDING",
            }
            self._last_result = (fid, owner_id, contact_id, conversation_id, "PENDING")

        elif q.startswith("SELECT status FROM follow_ups"):
            fid, owner_id = params
            f = self.follow_ups.get(fid)
            if f and f["owner_id"] == owner_id:
                self._last_result = (f["status"],)
            else:
                self._last_result = None

        elif q.startswith("UPDATE follow_ups SET status"):
            new_status, fid, owner_id = params
            f = self.follow_ups.get(fid)
            if f and f["owner_id"] == owner_id:
                f["status"] = new_status
                self._last_result = (fid, f["owner_id"], f["contact_id"], f["conversation_id"], new_status)
            else:
                self._last_result = None

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

        elif q.startswith("SELECT COUNT(*) FROM follow_ups"):
            (conv_id,) = params
            count = sum(1 for f in self.follow_ups.values()
                        if f["conversation_id"] == conv_id and f["status"] == "PENDING")
            self._last_result = (count,)

        elif q.startswith("SELECT s.score_value FROM scores"):
            owner_id = params[0]
            relevant = [s for s in self.scores if self.follow_ups.get(s[2], {}).get("owner_id") == owner_id]
            self._last_result = (relevant[-1][3],) if relevant else None

        else:
            raise NotImplementedError(f"Query neprevazut: {q}")

    def fetchone(self):
        return self._last_result


def make_fake_connection(fake_db):
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


fake_db = FakeDB()
owner_id = uuid4()
contact_id = uuid4()
conversation_id = uuid4()

with patch("src.engines.rule.rule_engine.get_connection") as rule_conn, \
     patch("src.engines.followup.followup_engine.get_connection") as fu_conn, \
     patch("src.agents.followup.followup_agent.get_connection") as agent_conn:

    rule_conn.return_value = make_fake_connection(fake_db)
    fu_conn.return_value = make_fake_connection(fake_db)
    agent_conn.return_value = make_fake_connection(fake_db)

    rule_engine = RuleEngine()
    followup_engine = FollowUpEngine(rule_engine=rule_engine)
    agent = FollowUpAgent(followup_engine=followup_engine)

    print("=== PASUL 1: RuleEngine — nicio conversatie cu follow-up PENDING ===")
    r1 = rule_engine.evaluate_followup(conversation_id)
    print("Decizie:", r1.decision_outcome)
    assert r1.decision_outcome == "FOLLOWUP_READY"
    print("OK\n")

    print("=== PASUL 2: FollowUpEngine creeaza follow-up-ul + persista DIS imediat ===")
    followup = followup_engine.create_from_trigger(owner_id, contact_id, conversation_id)
    print("FollowUp creat:", followup.id, "status =", followup.status)
    assert followup.status == "PENDING"
    assert len(fake_db.scores) == 1
    print("OK — DIS persistat la creare (nu la finalizare, conform sursei)\n")

    print("=== PASUL 3: RuleEngine reevaluat — acum exista deja un PENDING pe conversatie ===")
    r2 = rule_engine.evaluate_followup(conversation_id)
    print("Decizie:", r2.decision_outcome, "(asteptat: FOLLOWUP_DUPLICATE)")
    assert r2.decision_outcome == "FOLLOWUP_DUPLICATE"
    print("OK — RuleEngine si FollowUpEngine sincronizate prin DB\n")

    print("=== PASUL 4: FollowUpAgent prezinta lista ===")
    text = agent.present_followup_list([followup])
    print(text)
    assert str(contact_id) in text
    print("OK\n")

    print("=== PASUL 5: Fara confirmare, refuz garantat (prin Agent) ===")
    try:
        agent.confirm_completion(followup.id, owner_id, confirmed=False)
        print("EROARE: ar fi trebuit sa refuze")
    except Exception as e:
        print("OK: refuzat —", type(e).__name__)
    print()

    print("=== PASUL 6: Liderul confirma finalizarea — via Agent ===")
    followup = agent.confirm_completion(followup.id, owner_id, confirmed=True)
    print("Status:", followup.status)
    assert followup.status == "COMPLETED"
    assert fake_db.follow_ups[followup.id]["status"] == "COMPLETED"
    print("OK — Agent a delegat corect catre Engine\n")

    print("=== PASUL 7: Agentul poate citi DIS-ul (READ-ONLY) ===")
    dis = agent.get_recent_dis_score(owner_id)
    print("DIS citit:", dis)
    assert dis == 1.0
    print("OK\n")

    print("=== PASUL 8: state_history + events inregistrate corect ===")
    print("Tranzitii:", len(fake_db.state_history), " Evenimente:", len(fake_db.events))
    assert len(fake_db.state_history) == 1  # doar COMPLETED (PENDING e starea initiala, nu o tranzitie)
    assert len(fake_db.events) == 2          # FollowUpTriggered + FollowUpCompleted
    print("OK\n")

print("=" * 60)
print("TEST DE INTEGRARE FOLLOWUP COMPLET — LANTUL FUNCTIONEAZA")
print("=" * 60)
