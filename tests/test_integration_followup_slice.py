"""
Test de integrare — Contact->FollowUp Vertical Slice, cap-coada, ca teste
pytest reale. Acelasi tipar ca test_integration_mission_slice.py.
"""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from src.engines.rule.rule_engine import RuleEngine
from src.engines.followup.followup_engine import FollowUpEngine, FollowUpDuplicateError
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
            self._last_result = (f["status"],) if f and f["owner_id"] == owner_id else None

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
            relevant = [
                s for s in self.scores
                if self.follow_ups.get(s[2], {}).get("owner_id") == owner_id
            ]
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


class TestFollowUpVerticalSlice:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.fake_db = FakeDB()
        self.owner_id = uuid4()
        self.contact_id = uuid4()
        self.conversation_id = uuid4()

        self.patchers = [
            patch("src.engines.rule.rule_engine.get_connection"),
            patch("src.engines.followup.followup_engine.get_connection"),
            patch("src.agents.followup.followup_agent.get_connection"),
        ]
        mocks = [p.start() for p in self.patchers]
        for m in mocks:
            m.return_value = make_fake_connection(self.fake_db)

        self.rule_engine = RuleEngine()
        self.followup_engine = FollowUpEngine(rule_engine=self.rule_engine)
        self.agent = FollowUpAgent(followup_engine=self.followup_engine)

        yield

        for p in self.patchers:
            p.stop()

    def _create(self):
        self.followup = self.followup_engine.create_from_trigger(
            self.owner_id, self.contact_id, self.conversation_id
        )

    def test_01_rule_engine_ready_fara_duplicate(self):
        """RuleEngine — nicio conversatie cu follow-up PENDING -> FOLLOWUP_READY."""
        result = self.rule_engine.evaluate_followup(self.conversation_id)
        assert result.decision_outcome == "FOLLOWUP_READY"

    def test_02_creare_persista_dis_imediat(self):
        """FollowUpEngine creeaza follow-up-ul si persista DIS imediat (nu la finalizare)."""
        self._create()
        assert self.followup.status == "PENDING"
        assert len(self.fake_db.scores) == 1

    def test_03_rule_engine_reevaluat_duplicate(self):
        """Dupa creare, RuleEngine reevaluat -> FOLLOWUP_DUPLICATE."""
        self._create()
        result = self.rule_engine.evaluate_followup(self.conversation_id)
        assert result.decision_outcome == "FOLLOWUP_DUPLICATE"

    def test_04_al_doilea_followup_refuzat(self):
        """Al doilea follow-up pe aceeasi conversatie e refuzat."""
        self._create()
        with pytest.raises(FollowUpDuplicateError):
            self.followup_engine.create_from_trigger(
                self.owner_id, self.contact_id, self.conversation_id
            )

    def test_05_agent_prezinta_lista(self):
        """FollowUpAgent prezinta lista, cu contact_id inclus in text."""
        self._create()
        text = self.agent.present_followup_list([self.followup])
        assert str(self.contact_id) in text

    def test_06_fara_confirmare_refuz_garantat(self):
        """Fara confirmed=True, Agentul refuza finalizarea."""
        self._create()
        with pytest.raises(Exception):
            self.agent.confirm_completion(self.followup.id, self.owner_id, confirmed=False)

    def test_07_confirmare_finalizeaza(self):
        """Liderul confirma finalizarea — via Agent, delegat corect."""
        self._create()
        followup = self.agent.confirm_completion(self.followup.id, self.owner_id, confirmed=True)
        assert followup.status == "COMPLETED"
        assert self.fake_db.follow_ups[followup.id]["status"] == "COMPLETED"

    def test_08_agent_citeste_dis_readonly(self):
        """Agentul poate citi DIS-ul (READ-ONLY), valoare corecta."""
        self._create()
        self.agent.confirm_completion(self.followup.id, self.owner_id, confirmed=True)
        dis = self.agent.get_recent_dis_score(self.owner_id)
        assert dis == 1.0

    def test_09_state_history_si_events_complete(self):
        """state_history (1 tranzitie) si events (2, creare + completare) corecte."""
        self._create()
        self.agent.confirm_completion(self.followup.id, self.owner_id, confirmed=True)
        assert len(self.fake_db.state_history) == 1
        assert len(self.fake_db.events) == 2
