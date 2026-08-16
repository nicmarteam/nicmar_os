"""
Test de integrare — Mission Vertical Slice, cap-coada, ca teste pytest reale.

Foloseste o clasa (TestMissionVerticalSlice) cu stare partajata intre
pasi (self.mission, self.fake_db etc.) — pytest ruleaza metodele unei
clase in ordinea definirii lor, ceea ce pastreaza exact fluxul original
(fiecare pas depinde de rezultatul celui anterior), dar fiecare pas
apare acum separat, cu nume, in raportul pytest.

Nu foloseste PostgreSQL real — FakeDB in memorie, cu stare reala intre
apeluri (simuleaza fidel comportamentul SQL).
"""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from src.engines.rule.rule_engine import RuleEngine
from src.engines.mission.mission_engine import MissionEngine
from src.agents.mission.mission_agent import MissionAgent


class FakeDB:
    """Baza de date falsa, in memorie, cu stare reala intre apeluri."""

    def __init__(self):
        self.missions = {}
        self.kpis = {}
        self.scores = []
        self.state_history = []
        self.events = []
        self.kpis["DIS"] = uuid4()

    def execute(self, query, params=None):
        q = " ".join(query.split())
        params = params or ()

        if q.startswith("INSERT INTO missions"):
            owner_id, title, description = params
            mission_id = uuid4()
            self.missions[mission_id] = {
                "owner_id": owner_id, "title": title, "status": "GENERATED",
            }
            self._last_result = (mission_id, owner_id, title, "GENERATED")

        elif q.startswith("SELECT status FROM missions"):
            mission_id, owner_id = params
            m = self.missions.get(mission_id)
            self._last_result = (m["status"],) if m and m["owner_id"] == owner_id else None

        elif q.startswith("UPDATE missions SET status"):
            new_status, mission_id, owner_id = params
            m = self.missions.get(mission_id)
            if m and m["owner_id"] == owner_id:
                m["status"] = new_status
                self._last_result = (mission_id, m["owner_id"], m["title"], new_status)
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

        elif q.startswith("SELECT COUNT(*) FROM missions"):
            owner_id = params[0]
            statuses = params[1:]
            count = sum(
                1 for m in self.missions.values()
                if m["owner_id"] == owner_id and m["status"] in statuses
            )
            self._last_result = (count,)

        else:
            raise NotImplementedError(f"Query neprevazut in FakeDB: {q}")

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


class TestMissionVerticalSlice:
    """
    Fiecare metoda e un pas din lantul original, in ordine. Starea
    (fake_db, mission, owner_id) se pastreaza pe instanta (self),
    la fel cum variabilele se pastrau in scriptul original.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        self.fake_db = FakeDB()
        self.owner_id = uuid4()

        self.patchers = [
            patch("src.engines.rule.rule_engine.get_connection"),
            patch("src.engines.mission.mission_engine.get_connection"),
            patch("src.agents.mission.mission_agent.get_connection"),
        ]
        mocks = [p.start() for p in self.patchers]
        for m in mocks:
            m.return_value = make_fake_connection(self.fake_db)

        self.rule_engine = RuleEngine()
        self.mission_engine = MissionEngine(rule_engine=self.rule_engine)
        self.agent = MissionAgent(mission_engine=self.mission_engine)

        yield

        for p in self.patchers:
            p.stop()

    def test_01_rule_engine_evalueaza_ready(self):
        """RuleEngine evalueaza — owner nu are misiuni active -> MISSION_READY."""
        result = self.rule_engine.evaluate(self.owner_id)
        assert result.decision_outcome == "MISSION_READY"

    def test_02_mission_engine_genereaza_misiunea(self):
        """MissionEngine genereaza misiunea (via RuleEngine intern)."""
        self.mission = self.mission_engine.generate_mission(
            self.owner_id, title="Sună-l pe Andrei"
        )
        assert self.mission.status == "GENERATED"
        assert self.mission.id in self.fake_db.missions

    def test_03_rule_engine_reevaluat_blocat(self):
        """Dupa generare, RuleEngine reevaluat -> MISSION_BLOCKED."""
        self.test_02_mission_engine_genereaza_misiunea()
        result = self.rule_engine.evaluate(self.owner_id)
        assert result.decision_outcome == "MISSION_BLOCKED"

    def test_04_asigneaza_misiunea(self):
        """MissionEngine asigneaza misiunea: GENERATED -> ASSIGNED."""
        self.test_02_mission_engine_genereaza_misiunea()
        mission = self.mission_engine.assign_mission(self.mission.id, self.owner_id)
        assert mission.status == "ASSIGNED"

    def test_05_agent_prezinta_misiunea(self):
        """MissionAgent prezinta misiunea liderului, cu titlul inclus."""
        self.test_02_mission_engine_genereaza_misiunea()
        text = self.agent.present_daily_mission(self.mission)
        assert "Sună-l pe Andrei" in text

    def test_06_confirmare_umana_porneste_misiunea(self):
        """Confirmarea 'Sunt gata, incep' -> IN_PROGRESS, delegat corect prin Agent."""
        self.test_02_mission_engine_genereaza_misiunea()
        self.mission_engine.assign_mission(self.mission.id, self.owner_id)
        mission = self.agent.confirm_and_start(self.mission.id, self.owner_id, confirmed=True)
        assert mission.status == "IN_PROGRESS"
        assert self.fake_db.missions[mission.id]["status"] == "IN_PROGRESS"

    def test_07_fara_confirmare_refuz_garantat(self):
        """Fara confirmed=True, Agentul refuza, chiar daca misiunea exista si e ASSIGNED."""
        self.test_02_mission_engine_genereaza_misiunea()
        self.mission_engine.assign_mission(self.mission.id, self.owner_id)
        from src.engines.mission.mission_engine import HumanConfirmationRequiredError
        with pytest.raises(HumanConfirmationRequiredError):
            self.agent.confirm_and_start(self.mission.id, self.owner_id, confirmed=False)

    def test_08_finalizare_prin_agent(self):
        """Liderul finalizeaza misiunea — via MissionAgent."""
        self.test_02_mission_engine_genereaza_misiunea()
        self.mission_engine.assign_mission(self.mission.id, self.owner_id)
        self.agent.confirm_and_start(self.mission.id, self.owner_id, confirmed=True)
        mission = self.agent.confirm_completion(self.mission.id, self.owner_id)
        assert mission.status == "COMPLETED"

    def test_09_dis_persistat_in_scores(self):
        """Dupa finalizare, DIS a fost persistat corect in scores."""
        self.test_02_mission_engine_genereaza_misiunea()
        self.mission_engine.assign_mission(self.mission.id, self.owner_id)
        self.agent.confirm_and_start(self.mission.id, self.owner_id, confirmed=True)
        self.agent.confirm_completion(self.mission.id, self.owner_id)

        assert len(self.fake_db.scores) == 1
        kpi_id, entity_type, entity_id, score_value = self.fake_db.scores[0][:4]
        assert kpi_id == self.fake_db.kpis["DIS"]
        assert entity_type == "mission"

    def test_10_state_history_si_events_complete(self):
        """state_history (3 tranzitii) si events (4, inclusiv generarea) inregistrate corect."""
        self.test_02_mission_engine_genereaza_misiunea()
        self.mission_engine.assign_mission(self.mission.id, self.owner_id)
        self.agent.confirm_and_start(self.mission.id, self.owner_id, confirmed=True)
        self.agent.confirm_completion(self.mission.id, self.owner_id)

        assert len(self.fake_db.state_history) == 3
        assert len(self.fake_db.events) == 4
