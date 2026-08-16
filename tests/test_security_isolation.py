"""
Security Isolation Audit — teste negative reale, cu 2 lideri, ca teste
pytest, pentru Mission si FollowUp. Demonstreaza ca Agent A NU poate
actiona asupra datelor Liderului B.
"""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

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


class TestMissionSecurityIsolation:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.fake_db = FakeMissionDB()
        self.lider_a = uuid4()
        self.lider_b = uuid4()

        self.patchers = [
            patch("src.engines.rule.rule_engine.get_connection"),
            patch("src.engines.mission.mission_engine.get_connection"),
            patch("src.agents.mission.mission_agent.get_connection"),
        ]
        mocks = [p.start() for p in self.patchers]
        for m in mocks:
            m.return_value = make_conn(self.fake_db)

        self.rule_engine = RuleEngine()
        self.mission_engine = MissionEngine(rule_engine=self.rule_engine)
        self.agent_a = MissionAgent(mission_engine=self.mission_engine)

        self.mission_b = self.mission_engine.generate_mission(
            self.lider_b, title="Misiune confidentiala Lider B"
        )

        yield

        for p in self.patchers:
            p.stop()

    def test_lider_a_nu_poate_modifica_misiunea_lui_b_direct(self):
        """Prin Engine direct, Lider A nu poate schimba starea misiunii lui B."""
        with pytest.raises(MissionAccessDeniedError):
            self.mission_engine.assign_mission(self.mission_b.id, self.lider_a)

    def test_lider_a_nu_poate_porni_misiunea_lui_b_prin_agent(self):
        """Nici prin Agent — nu doar Engine direct — Lider A nu acceseaza misiunea lui B."""
        with pytest.raises(MissionAccessDeniedError):
            self.agent_a.confirm_and_start(self.mission_b.id, self.lider_a, confirmed=True)

    def test_lider_b_isi_poate_modifica_propria_misiune(self):
        """Verificare pozitiva: Lider B ISI poate modifica propria misiune, fara probleme."""
        mission = self.mission_engine.assign_mission(self.mission_b.id, self.lider_b)
        assert mission.status == "ASSIGNED"


class TestFollowUpSecurityIsolation:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.fake_db = FakeFollowUpDB()
        self.lider_a = uuid4()
        self.lider_b = uuid4()

        self.patchers = [
            patch("src.engines.rule.rule_engine.get_connection"),
            patch("src.engines.followup.followup_engine.get_connection"),
            patch("src.agents.followup.followup_agent.get_connection"),
        ]
        mocks = [p.start() for p in self.patchers]
        for m in mocks:
            m.return_value = make_conn(self.fake_db)

        self.rule_engine = RuleEngine()
        self.followup_engine = FollowUpEngine(rule_engine=self.rule_engine)
        self.agent_a = FollowUpAgent(followup_engine=self.followup_engine)

        self.fu_a = self.followup_engine.create_from_trigger(self.lider_a, uuid4(), uuid4())

        yield

        for p in self.patchers:
            p.stop()

    def test_lider_b_nu_poate_finaliza_followup_lui_a_direct(self):
        """Prin Engine direct, Lider B nu poate finaliza follow-up-ul lui A."""
        with pytest.raises(FollowUpAccessDeniedError):
            self.followup_engine.complete_followup(self.fu_a.id, self.lider_b, confirmed=True)

    def test_lider_b_nu_poate_amana_followup_lui_a_prin_agent(self):
        """Nici prin Agent — Lider B nu acceseaza follow-up-ul lui A."""
        with pytest.raises(FollowUpAccessDeniedError):
            self.agent_a.request_postpone(self.fu_a.id, self.lider_b)

    def test_lider_a_isi_poate_finaliza_propriul_followup(self):
        """Verificare pozitiva: Lider A ISI poate finaliza propriul follow-up."""
        followup = self.followup_engine.complete_followup(self.fu_a.id, self.lider_a, confirmed=True)
        assert followup.status == "COMPLETED"
