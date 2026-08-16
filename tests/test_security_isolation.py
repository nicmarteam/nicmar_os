"""
Security Isolation Audit — teste negative cu 2 lideri, pentru Mission
si FollowUp. Demonstreaza ca Agent A NU poate actiona asupra datelor
Liderului B, dupa corectarea gaurii gasite in _set_status.
"""
import sys
sys.path.insert(0, '/home/claude/nicmar_impl')

from unittest.mock import MagicMock, patch
from uuid import uuid4

from src.engines.rule.rule_engine import RuleEngine
from src.engines.mission.mission_engine import MissionEngine, MissionAccessDeniedError
from src.agents.mission.mission_agent import MissionAgent
from src.engines.followup.followup_engine import FollowUpEngine, FollowUpAccessDeniedError
from src.agents.followup.followup_agent import FollowUpAgent


class FakeMissionDB:
    def __init__(self):
        self.missions = {}

    def execute(self, query, params=None):
        q = " ".join(query.split())
        params = params or ()
        if q.startswith("INSERT INTO missions"):
            owner_id, title, description = params
            mid = uuid4()
            self.missions[mid] = {"owner_id": owner_id, "title": title, "status": "GENERATED"}
            self._last_result = (mid, owner_id, title, "GENERATED")
        elif q.startswith("SELECT status FROM missions"):
            mid, owner_id = params
            m = self.missions.get(mid)
            self._last_result = (m["status"],) if m and m["owner_id"] == owner_id else None
        elif q.startswith("UPDATE missions SET status"):
            new_status, mid, owner_id = params
            m = self.missions.get(mid)
            if m and m["owner_id"] == owner_id:
                m["status"] = new_status
                self._last_result = (mid, m["owner_id"], m["title"], new_status)
            else:
                self._last_result = None
        elif q.startswith("INSERT INTO state_history") or q.startswith("INSERT INTO events"):
            self._last_result = None
        elif q.startswith("SELECT COUNT(*) FROM missions"):
            owner_id = params[0]
            statuses = params[1:]
            count = sum(1 for m in self.missions.values()
                        if m["owner_id"] == owner_id and m["status"] in statuses)
            self._last_result = (count,)
        else:
            raise NotImplementedError(q)

    def fetchone(self):
        return self._last_result


class FakeFollowUpDB:
    def __init__(self):
        self.follow_ups = {}
        self.kpis = {"DIS": uuid4()}
        self.scores = []

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
            self._last_result = (f["status"],) if f and f["owner_id"] == owner_id else None
        elif q.startswith("UPDATE follow_ups SET status"):
            new_status, fid, owner_id = params
            f = self.follow_ups.get(fid)
            if f and f["owner_id"] == owner_id:
                f["status"] = new_status
                self._last_result = (fid, f["owner_id"], f["contact_id"], f["conversation_id"], new_status)
            else:
                self._last_result = None
        elif q.startswith("INSERT INTO state_history") or q.startswith("INSERT INTO events"):
            self._last_result = None
        elif q.startswith("SELECT COUNT(*) FROM follow_ups"):
            (conv_id,) = params
            count = sum(1 for f in self.follow_ups.values()
                        if f["conversation_id"] == conv_id and f["status"] == "PENDING")
            self._last_result = (count,)
        elif q.startswith("SELECT id FROM kpis WHERE metric_code"):
            (code,) = params
            self._last_result = (self.kpis.get(code),) if code in self.kpis else None
        elif q.startswith("INSERT INTO scores"):
            self.scores.append(params)
            self._last_result = None
        else:
            raise NotImplementedError(q)

    def fetchone(self):
        return self._last_result


def make_conn(fake_db):
    cur = MagicMock()
    cur.execute.side_effect = fake_db.execute
    cur.fetchone.side_effect = fake_db.fetchone
    cur.__enter__.return_value = cur
    cur.__exit__.return_value = False
    conn = MagicMock()
    conn.cursor.return_value = cur
    conn.__enter__.return_value = conn
    conn.__exit__.return_value = False
    return conn


print("=" * 70)
print("SECURITY ISOLATION AUDIT — MISSION")
print("=" * 70)

fake_db = FakeMissionDB()
lider_A = uuid4()
lider_B = uuid4()

with patch("src.engines.rule.rule_engine.get_connection") as rc, \
     patch("src.engines.mission.mission_engine.get_connection") as mc, \
     patch("src.agents.mission.mission_agent.get_connection") as ac:
    rc.return_value = make_conn(fake_db)
    mc.return_value = make_conn(fake_db)
    ac.return_value = make_conn(fake_db)

    rule_engine = RuleEngine()
    mission_engine = MissionEngine(rule_engine=rule_engine)
    agent_A = MissionAgent(mission_engine=mission_engine)

    print("\n--- Lider A creeaza o misiune ---")
    mission_B = mission_engine.generate_mission(lider_B, title="Misiunea confidentiala a lui B")
    print("Misiune creata pentru Lider B:", mission_B.id)

    print("\n--- TEST NEGATIV: Lider A incearca sa modifice misiunea lui B ---")
    try:
        mission_engine.assign_mission(mission_B.id, lider_A)
        print("!!! EROARE GRAVA: Lider A a putut modifica misiunea lui B !!!")
        sys.exit(1)
    except MissionAccessDeniedError:
        print("OK: MissionAccessDeniedError — Lider A NU a putut accesa misiunea lui B")

    print("\n--- TEST NEGATIV: Lider A incearca sa porneasca misiunea lui B (prin Agent) ---")
    try:
        agent_A.confirm_and_start(mission_B.id, lider_A, confirmed=True)
        print("!!! EROARE GRAVA: Agent A a putut porni misiunea lui B !!!")
        sys.exit(1)
    except MissionAccessDeniedError:
        print("OK: refuzat corect, chiar si prin Agent, nu doar Engine direct")

    print("\n--- Verificare pozitiva: Lider B ISI poate modifica propria misiune ---")
    mission_B = mission_engine.assign_mission(mission_B.id, lider_B)
    print("OK: Lider B a reusit, status =", mission_B.status)


print()
print("=" * 70)
print("SECURITY ISOLATION AUDIT — FOLLOWUP")
print("=" * 70)

fake_db_2 = FakeFollowUpDB()

with patch("src.engines.rule.rule_engine.get_connection") as rc, \
     patch("src.engines.followup.followup_engine.get_connection") as fc, \
     patch("src.agents.followup.followup_agent.get_connection") as ac:
    rc.return_value = make_conn(fake_db_2)
    fc.return_value = make_conn(fake_db_2)
    ac.return_value = make_conn(fake_db_2)

    rule_engine_2 = RuleEngine()
    followup_engine = FollowUpEngine(rule_engine=rule_engine_2)
    agent_A2 = FollowUpAgent(followup_engine=followup_engine)

    print("\n--- Lider A creeaza un follow-up (pentru propriul contact) ---")
    fu_A = followup_engine.create_from_trigger(lider_A, uuid4(), uuid4())
    print("Follow-up creat pentru Lider A:", fu_A.id)

    print("\n--- TEST NEGATIV: Lider B incearca sa finalizeze follow-up-ul lui A ---")
    try:
        followup_engine.complete_followup(fu_A.id, lider_B, confirmed=True)
        print("!!! EROARE GRAVA: Lider B a putut finaliza follow-up-ul lui A !!!")
        sys.exit(1)
    except FollowUpAccessDeniedError:
        print("OK: FollowUpAccessDeniedError — Lider B NU a putut accesa follow-up-ul lui A")

    print("\n--- TEST NEGATIV: Lider B incearca sa amane follow-up-ul lui A (prin Agent) ---")
    try:
        agent_A2.request_postpone(fu_A.id, lider_B)
        print("!!! EROARE GRAVA: Agent B a putut amana follow-up-ul lui A !!!")
        sys.exit(1)
    except FollowUpAccessDeniedError:
        print("OK: refuzat corect, chiar si prin Agent")

    print("\n--- Verificare pozitiva: Lider A ISI poate finaliza propriul follow-up ---")
    fu_A = followup_engine.complete_followup(fu_A.id, lider_A, confirmed=True)
    print("OK: Lider A a reusit, status =", fu_A.status)


print()
print("=" * 70)
print("SECURITY ISOLATION AUDIT — TOATE TESTELE NEGATIVE AU TRECUT")
print("Niciun lider nu poate actiona asupra datelor altui lider.")
print("=" * 70)
