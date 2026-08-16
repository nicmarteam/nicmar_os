"""
Test de integrare — Partner Vertical Slice, cap-coada, ca teste pytest reale.
Include si dovada de izolare intre lideri (owner_id), gasita ca bug real
in testarea originala.
"""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from src.engines.rule.rule_engine import RuleEngine
from src.engines.partner.partner_engine import PartnerEngine, PartnerDiagnosticAlreadyGeneratedError
from src.agents.partner.partner_agent import PartnerAgent


class FakeDB:
    def __init__(self):
        self.kpis = {"PDI": uuid4(), "PIP": uuid4()}
        self.scores = []
        self.events = []
        self.partners = {}  # partner_id -> owner_id

    def execute(self, query, params=None):
        q = " ".join(query.split())
        params = params or ()

        if q.startswith("SELECT 1 FROM partners"):
            pid, oid = params
            self._last_result = (1,) if self.partners.get(pid) == oid else None

        elif q.startswith("SELECT COUNT(*) FROM events"):
            (partner_id,) = params
            count = sum(
                1 for e in self.events
                if e[0] == "PartnerDiagnosticGenerated" and e[2] == partner_id
            )
            self._last_result = (count,)

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

        elif q.startswith("SELECT k.metric_code, s.score_value FROM scores"):
            (query_owner_id,) = params
            self._fetchall_owner_id = query_owner_id
            self._last_result = None

        else:
            raise NotImplementedError(f"Query neprevazut: {q}")

    def fetchone(self):
        return self._last_result

    def fetchall(self):
        owner_id = getattr(self, "_fetchall_owner_id", None)
        result = []
        seen = set()
        for s in reversed(self.scores):
            kpi_id, entity_type, entity_id, score_value = s[:4]
            partner_owner = self.partners.get(entity_id)
            if partner_owner != owner_id:
                continue
            code = next((c for c, kid in self.kpis.items() if kid == kpi_id), None)
            if code and code not in seen:
                result.append((code, score_value))
                seen.add(code)
        return result


def make_fake_connection(fake_db):
    mock_cur = MagicMock()
    mock_cur.execute.side_effect = fake_db.execute
    mock_cur.fetchone.side_effect = fake_db.fetchone
    mock_cur.fetchall.side_effect = fake_db.fetchall
    mock_cur.__enter__.return_value = mock_cur
    mock_cur.__exit__.return_value = False
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = False
    return mock_conn


class TestPartnerVerticalSlice:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.fake_db = FakeDB()
        self.partner_id = uuid4()
        self.owner_id = uuid4()
        self.fake_db.partners[self.partner_id] = self.owner_id

        self.patchers = [
            patch("src.engines.rule.rule_engine.get_connection"),
            patch("src.engines.partner.partner_engine.get_connection"),
            patch("src.agents.partner.partner_agent.get_connection"),
        ]
        mocks = [p.start() for p in self.patchers]
        for m in mocks:
            m.return_value = make_fake_connection(self.fake_db)

        self.rule_engine = RuleEngine()
        self.partner_engine = PartnerEngine(rule_engine=self.rule_engine)
        self.agent = PartnerAgent(partner_engine=self.partner_engine)

        yield

        for p in self.patchers:
            p.stop()

    def _request_diagnostic(self):
        self.diagnostic = self.agent.request_diagnostic(self.partner_id, self.owner_id, "NEXT_STEP")

    def test_01_rule_engine_ready_fara_diagnostic(self):
        """RuleEngine — partenerul nu a primit diagnostic azi -> PARTNER_READY."""
        result = self.rule_engine.evaluate_partner_diagnostic(self.partner_id)
        assert result.decision_outcome == "PARTNER_READY"

    def test_02_agent_solicita_diagnostic(self):
        """PartnerAgent solicita diagnostic (deleaga la Engine), tip corect, event emis."""
        self._request_diagnostic()
        assert self.diagnostic.diagnostic_type == "NEXT_STEP"
        assert len(self.fake_db.events) == 1

    def test_03_rule_engine_reevaluat_deja_diagnosticat(self):
        """Dupa diagnostic, RuleEngine reevaluat -> PARTNER_ALREADY_DIAGNOSED."""
        self._request_diagnostic()
        result = self.rule_engine.evaluate_partner_diagnostic(self.partner_id)
        assert result.decision_outcome == "PARTNER_ALREADY_DIAGNOSED"

    def test_04_al_doilea_diagnostic_refuzat(self):
        """Al doilea diagnostic in aceeasi zi e refuzat — nu se genereaza 2/zi."""
        self._request_diagnostic()
        with pytest.raises(PartnerDiagnosticAlreadyGeneratedError):
            self.agent.request_diagnostic(self.partner_id, self.owner_id, "CLARITY")

    def test_05_agent_prezinta_diagnosticul_stub(self):
        """PartnerAgent prezinta diagnosticul, mesaj STUB inclus."""
        self._request_diagnostic()
        text = self.agent.present_diagnostic(self.diagnostic)
        assert "[STUB]" in text

    def test_06_fara_confirmare_refuz_garantat(self):
        """Fara confirmare, finalizarea e refuzata."""
        self._request_diagnostic()
        with pytest.raises(Exception):
            self.agent.confirm_and_send(self.partner_id, self.owner_id, confirmed=False)

    def test_07_confirmare_persista_pdi_si_pip(self):
        """Liderul confirma — PDI si PIP persistate, nu doar unul."""
        self._request_diagnostic()
        self.agent.confirm_and_send(self.partner_id, self.owner_id, confirmed=True)
        assert len(self.fake_db.scores) == 2

    def test_08_agent_citeste_scorurile_izolat_pe_owner(self):
        """
        Agentul citeste scorurile DOAR pentru owner-ul corect.

        Adauga un al doilea partener, al ALTUI lider, cu scor propriu —
        dovedeste ca filtrarea prin owner_id chiar functioneaza (bug
        real gasit si corectat aici, nu doar ipotetic).
        """
        self._request_diagnostic()
        self.agent.confirm_and_send(self.partner_id, self.owner_id, confirmed=True)

        other_owner_id = uuid4()
        other_partner_id = uuid4()
        self.fake_db.partners[other_partner_id] = other_owner_id
        other_pdi_id = self.fake_db.kpis["PDI"]
        self.fake_db.scores.append((other_pdi_id, "partner", other_partner_id, 99.0, "ENG-PRE-001"))

        scores = self.agent.get_recent_scores(self.owner_id)

        assert scores.get("PDI") == 1.0, "Nu trebuie sa vada scorul (99.0) al altui lider!"
        assert scores.get("PIP") == 1.0
