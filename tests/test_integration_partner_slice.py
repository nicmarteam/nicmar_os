"""
Test de integrare — Partner Vertical Slice, cap-coada.

FakeDB in memorie. Diferit de Mission/FollowUp: aici nu exista tabel
de stare tranzitionala (partners.status neatins) - se urmareste doar
`events` (PartnerDiagnosticGenerated) si `scores` (PDI/PIP).
"""
import sys
sys.path.insert(0, '/home/claude/nicmar_impl')

from unittest.mock import MagicMock, patch
from uuid import uuid4

from src.engines.rule.rule_engine import RuleEngine
from src.engines.partner.partner_engine import PartnerEngine, PartnerDiagnosticAlreadyGeneratedError
from src.agents.partner.partner_agent import PartnerAgent


class FakeDB:
    def __init__(self):
        self.kpis = {"PDI": uuid4(), "PIP": uuid4()}
        self.scores = []
        self.events = []
        self.partners = {}  # partner_id -> owner_id, pentru simularea JOIN-ului

    def execute(self, query, params=None):
        q = " ".join(query.split())
        params = params or ()

        if q.startswith("SELECT COUNT(*) FROM events"):
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
        # folosit doar de PartnerAgent.get_recent_scores, dupa JOIN pe partners.owner_id
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


fake_db = FakeDB()
partner_id = uuid4()
owner_id = uuid4()
fake_db.partners[partner_id] = owner_id  # simuleaza randul din tabelul real `partners`

with patch("src.engines.rule.rule_engine.get_connection") as rule_conn, \
     patch("src.engines.partner.partner_engine.get_connection") as pe_conn, \
     patch("src.agents.partner.partner_agent.get_connection") as agent_conn:

    rule_conn.return_value = make_fake_connection(fake_db)
    pe_conn.return_value = make_fake_connection(fake_db)
    agent_conn.return_value = make_fake_connection(fake_db)

    rule_engine = RuleEngine()
    partner_engine = PartnerEngine(rule_engine=rule_engine)
    agent = PartnerAgent(partner_engine=partner_engine)

    print("=== PASUL 1: RuleEngine — partenerul nu a primit diagnostic azi ===")
    r1 = rule_engine.evaluate_partner_diagnostic(partner_id)
    print("Decizie:", r1.decision_outcome)
    assert r1.decision_outcome == "PARTNER_READY"
    print("OK\n")

    print("=== PASUL 2: PartnerAgent solicita diagnostic (deleaga la Engine) ===")
    diagnostic = agent.request_diagnostic(partner_id, owner_id, "NEXT_STEP")
    print("Diagnostic tip:", diagnostic.diagnostic_type)
    assert diagnostic.diagnostic_type == "NEXT_STEP"
    assert len(fake_db.events) == 1
    print("OK — eveniment PartnerDiagnosticGenerated emis\n")

    print("=== PASUL 3: RuleEngine reevaluat — acum e deja diagnosticat azi ===")
    r2 = rule_engine.evaluate_partner_diagnostic(partner_id)
    print("Decizie:", r2.decision_outcome, "(asteptat: PARTNER_ALREADY_DIAGNOSED)")
    assert r2.decision_outcome == "PARTNER_ALREADY_DIAGNOSED"
    print("OK — RuleEngine si PartnerEngine sincronizate prin events\n")

    print("=== PASUL 4: al doilea diagnostic in aceeasi zi -> refuzat ===")
    try:
        agent.request_diagnostic(partner_id, owner_id, "CLARITY")
        print("EROARE: ar fi trebuit sa refuze")
    except PartnerDiagnosticAlreadyGeneratedError:
        print("OK: refuzat corect — nu se genereaza 2 diagnostice/zi\n")

    print("=== PASUL 5: PartnerAgent prezinta diagnosticul (mesaj STUB) ===")
    text = agent.present_diagnostic(diagnostic)
    print(text)
    assert "[STUB]" in text
    print("OK\n")

    print("=== PASUL 6: fara confirmare, refuz garantat ===")
    try:
        agent.confirm_and_send(partner_id, owner_id, confirmed=False)
        print("EROARE: ar fi trebuit sa refuze")
    except Exception as e:
        print("OK: refuzat —", type(e).__name__)
    print()

    print("=== PASUL 7: liderul confirma — PDI + PIP persistate ===")
    agent.confirm_and_send(partner_id, owner_id, confirmed=True)
    print("Numar scoruri:", len(fake_db.scores))
    assert len(fake_db.scores) == 2
    print("OK — PDI si PIP persistate, nu doar unul\n")

    print("=== PASUL 8: Agentul citeste scorurile — DOAR pentru owner-ul corect ===")
    # Adaugam un al doilea partener, al ALTUI lider, cu scoruri proprii —
    # ca sa dovedim ca filtrarea prin owner_id chiar functioneaza,
    # nu doar ca nu mai crapa (bug-ul gasit mai devreme).
    other_owner_id = uuid4()
    other_partner_id = uuid4()
    fake_db.partners[other_partner_id] = other_owner_id
    other_pdi_id = fake_db.kpis["PDI"]
    fake_db.scores.append((other_pdi_id, "partner", other_partner_id, 99.0, "ENG-PRE-001"))

    scores = agent.get_recent_scores(owner_id)
    print("Scoruri citite pentru owner_id corect:", scores)
    assert scores.get("PDI") == 1.0, "Nu trebuie sa vada scorul (99.0) al altui lider!"
    assert scores.get("PIP") == 1.0
    print("OK — scorul (99.0) al altui lider NU a aparut — izolare corecta\n")

    print("=== PASUL 9: events inregistrate corect (diagnostic + completare) ===")
    print("Evenimente:", len(fake_db.events))
    assert len(fake_db.events) == 2  # PartnerDiagnosticGenerated + PartnerInteractionCompleted
    print("OK\n")

print("=" * 60)
print("TEST DE INTEGRARE PARTNER COMPLET — LANTUL FUNCTIONEAZA")
print("=" * 60)
