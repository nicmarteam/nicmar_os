"""
Teste unitare pentru ContactAgent — cu mock, fara DB reala.

Sursa: 20-contact-agent-contract.md, sectiunile 3.1 (corectura de
granularitate PDI/PIP, CONFIRMATA 17 august 2026), 5 (regula de
sortare, CONFIRMATA de owner 17 august 2026) si 9 (criterii de
acceptare).

RED intentionat initial: src/agents/contact/contact_agent.py NU exista
inca la prima rulare a acestui fisier. Dupa GREEN, fisierul a fost
extins (RED->GREEN a doua oara) cand a fost descoperit bug-ul de
granularitate PDI/PIP (agregat pe owner_id in loc de per Partener
individual) — v. test_pdi_pip_per_partener_individual_nu_agregat_pe_owner.

Forma datelor asumata pentru get_connection (decizie de implementare,
nu de business logic - nu necesita reconfirmare separata):
    Query principal intoarce randuri:
        (contact_id, full_name, status, last_followup_at,
         last_followup_status, converted_to, updated_at, partner_id)
    Query secundar (doar pentru contactele converted_to == "partner")
    intoarce scoruri PDI/PIP PER PARTENER:
        (partner_id, metric_code, score_value)
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from src.agents.contact.contact_agent import ContactAgent, ContactSummary


NOW = datetime.now(timezone.utc)
PAST = NOW - timedelta(days=1)
FUTURE = NOW + timedelta(days=3)


def _make_cursor(fetchall_return):
    """Cursor mock reutilizabil, acelasi tipar ca test_partner_agent.py."""
    mock_cur = MagicMock()
    mock_cur.fetchall.return_value = fetchall_return
    mock_cur.__enter__.return_value = mock_cur
    mock_cur.__exit__.return_value = False
    return mock_cur


def _make_conn(mock_cur):
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = False
    return mock_conn


@pytest.fixture
def agent():
    return ContactAgent()


# ----------------------------------------------------------------------
# Izolare owner_id (criteriu 1, sectiunea 9)
# ----------------------------------------------------------------------


def test_list_prioritized_contacts_filtreaza_prin_owner_id(agent):
    """Interogarea principala trebuie sa filtreze strict pe owner_id."""
    target_owner_id = uuid4()

    with patch("src.agents.contact.contact_agent.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(fetchall_return=[])
        mock_get_conn.return_value = _make_conn(mock_cur)

        agent.list_prioritized_contacts(target_owner_id)

        executed_sql = mock_cur.execute.call_args_list[0][0][0]
        executed_params = mock_cur.execute.call_args_list[0][0][1]

    assert "SELECT" in executed_sql
    assert "INSERT" not in executed_sql
    assert "UPDATE" not in executed_sql
    assert "DELETE" not in executed_sql
    assert target_owner_id in executed_params


# ----------------------------------------------------------------------
# Fara nicio scriere (criteriu 9, sectiunea 9 - agent strict read-only)
# ----------------------------------------------------------------------


def test_list_prioritized_contacts_nu_scrie_niciodata(agent):
    """Niciun apel SQL nu contine INSERT/UPDATE/DELETE, in nicio interogare."""
    with patch("src.agents.contact.contact_agent.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(fetchall_return=[])
        mock_get_conn.return_value = _make_conn(mock_cur)

        agent.list_prioritized_contacts(uuid4())

        for call in mock_cur.execute.call_args_list:
            sql = call[0][0]
            assert "INSERT" not in sql
            assert "UPDATE" not in sql
            assert "DELETE" not in sql


# ----------------------------------------------------------------------
# owner_id fara contacte -> lista goala (criteriu 8, sectiunea 9)
# ----------------------------------------------------------------------


def test_list_prioritized_contacts_lista_goala_daca_nu_exista_contacte(agent):
    with patch("src.agents.contact.contact_agent.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(fetchall_return=[])
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = agent.list_prioritized_contacts(uuid4())

    assert result == []


# ----------------------------------------------------------------------
# ARCHIVED exclus explicit (contract, sectiunea 5)
# ----------------------------------------------------------------------


def test_list_prioritized_contacts_exclude_archived(agent):
    """
    ARCHIVED nu trebuie sa apara niciodata in output, indiferent daca
    filtrarea se face in SQL (WHERE status != 'ARCHIVED') sau in Python -
    testul verifica doar rezultatul final, nu implementarea interna.
    """
    contact_id_active = uuid4()
    contact_id_archived = uuid4()
    owner_id = uuid4()

    rows = [
        (contact_id_active, "Ana Pop", "ACTIVE", None, None, None, NOW, None, None, None, None, None, None),
        (contact_id_archived, "Ion Vechi", "ARCHIVED", None, None, None, NOW, None, None, None, None, None, None),
    ]

    with patch("src.agents.contact.contact_agent.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(fetchall_return=rows)
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = agent.list_prioritized_contacts(owner_id)

    result_ids = [c.contact_id for c in result]
    assert contact_id_archived not in result_ids


# ----------------------------------------------------------------------
# Regula de sortare CONFIRMATA (contract, sectiunea 5, 17 august 2026)
# ----------------------------------------------------------------------


def test_sortare_followup_scadent_inaintea_celor_fara_followup(agent):
    """
    Grup 1 (FollowUp PENDING scadent) trebuie sa apara inaintea
    Grupului 2 (fara niciun FollowUp).
    """
    owner_id = uuid4()
    contact_scadent = uuid4()
    contact_fara_followup = uuid4()

    rows = [
        # Contact fara followup listat primul in randurile brute,
        # dar trebuie sa apara AL DOILEA in rezultat (dupa sortare).
        (contact_fara_followup, "Maria Ionescu", "ACTIVE", None, None, None, NOW, None, None, None, None, None, None),
        (contact_scadent, "Vasile Pop", "ACTIVE", PAST, "PENDING", None, NOW, None, None, None, None, None, None),
    ]

    with patch("src.agents.contact.contact_agent.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(fetchall_return=rows)
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = agent.list_prioritized_contacts(owner_id)

    result_ids = [c.contact_id for c in result]
    assert result_ids.index(contact_scadent) < result_ids.index(contact_fara_followup)


def test_sortare_fara_followup_inaintea_restului(agent):
    """
    Grup 2 (fara niciun FollowUp) trebuie sa apara inaintea
    Grupului 3 (are FollowUp, dar nu PENDING-scadent: COMPLETED, sau
    PENDING viitor).
    """
    owner_id = uuid4()
    contact_fara_followup = uuid4()
    contact_followup_completat = uuid4()

    rows = [
        (contact_followup_completat, "Radu Stan", "ACTIVE", PAST, "COMPLETED", None, NOW, None, None, None, None, None, None),
        (contact_fara_followup, "Elena Marin", "ACTIVE", None, None, None, NOW, None, None, None, None, None, None),
    ]

    with patch("src.agents.contact.contact_agent.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(fetchall_return=rows)
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = agent.list_prioritized_contacts(owner_id)

    result_ids = [c.contact_id for c in result]
    assert result_ids.index(contact_fara_followup) < result_ids.index(contact_followup_completat)


def test_sortare_followup_viitor_nu_e_scadent(agent):
    """
    Un FollowUp PENDING dar programat in viitor NU se califica drept
    'scadent' - trebuie tratat ca Grupul 3, nu Grupul 1.
    """
    owner_id = uuid4()
    contact_scadent = uuid4()
    contact_viitor = uuid4()

    rows = [
        (contact_viitor, "Dan Ilie", "ACTIVE", FUTURE, "PENDING", None, NOW, None, None, None, None, None, None),
        (contact_scadent, "Ioana Rusu", "ACTIVE", PAST, "PENDING", None, NOW, None, None, None, None, None, None),
    ]

    with patch("src.agents.contact.contact_agent.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(fetchall_return=rows)
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = agent.list_prioritized_contacts(owner_id)

    result_ids = [c.contact_id for c in result]
    assert result_ids.index(contact_scadent) < result_ids.index(contact_viitor)


def test_sortare_restul_dupa_updated_at_desc(agent):
    """In Grupul 3, cel mai recent updated_at trebuie sa apara primul."""
    owner_id = uuid4()
    contact_vechi = uuid4()
    contact_recent = uuid4()

    rows = [
        (contact_vechi, "Costin Voicu", "ACTIVE", PAST, "COMPLETED", None, PAST, None, None, None, None, None, None),
        (contact_recent, "Bianca Toma", "ACTIVE", PAST, "COMPLETED", None, NOW, None, None, None, None, None, None),
    ]

    with patch("src.agents.contact.contact_agent.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(fetchall_return=rows)
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = agent.list_prioritized_contacts(owner_id)

    result_ids = [c.contact_id for c in result]
    assert result_ids.index(contact_recent) < result_ids.index(contact_vechi)


# ----------------------------------------------------------------------
# CONVERTED - fara scor KPI artificial (contract, sectiunea 5 si 2.4)
# ----------------------------------------------------------------------


def test_converted_client_nu_are_pdi_pip(agent):
    """Contact convertit in Client nu are niciodata pdi/pip populate."""
    owner_id = uuid4()
    contact_id = uuid4()

    rows = [
        (contact_id, "Client Nou", "CONVERTED", None, None, "client", NOW, None, None, None, None, None, None),
    ]

    with patch("src.agents.contact.contact_agent.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(fetchall_return=rows)
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = agent.list_prioritized_contacts(owner_id)

    summary = next(c for c in result if c.contact_id == contact_id)
    assert summary.converted_to == "client"
    assert summary.pdi is None
    assert summary.pip is None


def test_converted_partner_fara_scor_persistat_ramane_none(agent):
    """
    Contact convertit in Partner, dar FARA scor PDI/PIP scris inca in
    scores - trebuie sa ramana None, niciodata aproximat sau calculat
    de agent (regula explicita, sectiunea 2.4/5 din contract).
    """
    owner_id = uuid4()
    contact_id = uuid4()
    partner_id = uuid4()

    rows = [
        (contact_id, "Partener Nou", "CONVERTED", None, None, "partner", NOW, partner_id, None, None, None, None, None),
    ]

    with patch("src.agents.contact.contact_agent.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(fetchall_return=None)
        # A doua interogare (scoruri PDI/PIP per Partener) - fara randuri.
        mock_cur.fetchall.side_effect = [rows, []]
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = agent.list_prioritized_contacts(owner_id)

    summary = next(c for c in result if c.contact_id == contact_id)
    assert summary.converted_to == "partner"
    assert summary.pdi is None
    assert summary.pip is None


def test_converted_partner_cu_scor_persistat_populeaza_pdi_pip(agent):
    """Contact Partner CU scor real in scores -> pdi/pip populate corect."""
    owner_id = uuid4()
    contact_id = uuid4()
    partner_id = uuid4()

    contact_rows = [
        (contact_id, "Partener Activ", "CONVERTED", None, None, "partner", NOW, partner_id, None, None, None, None, None),
    ]
    score_rows = [(partner_id, "PDI", 1.0), (partner_id, "PIP", 1.0)]

    with patch("src.agents.contact.contact_agent.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(fetchall_return=None)
        mock_cur.fetchall.side_effect = [contact_rows, score_rows]
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = agent.list_prioritized_contacts(owner_id)

    summary = next(c for c in result if c.contact_id == contact_id)
    assert summary.pdi == 1.0
    assert summary.pip == 1.0


# ----------------------------------------------------------------------
# CORECTURA DE GRANULARITATE (contract, sectiunea 3.1, CONFIRMATA
# 17 august 2026) - testul critic: doi Parteneri ai aceluiasi owner
# trebuie sa primeasca FIECARE scorul propriu, nu cel mai recent
# scor agregat al owner-ului.
# ----------------------------------------------------------------------


def test_pdi_pip_per_partener_individual_nu_agregat_pe_owner(agent):
    """
    Bug corectat: doi Parteneri ai aceluiasi owner, cu scoruri PDI
    diferite - fiecare Contact trebuie sa primeasca scorul PROPRIULUI
    Partener, nu cel mai recent scor din toti Partenerii owner-ului.

    Scenariu exact confirmat:
        Partner A -> PDI 10
        Partner B -> PDI 90
        Contact A (convertit in Partner A) -> trebuie sa primeasca 10
        Contact B (convertit in Partner B) -> trebuie sa primeasca 90
    """
    owner_id = uuid4()
    contact_a = uuid4()
    contact_b = uuid4()
    partner_a = uuid4()
    partner_b = uuid4()

    contact_rows = [
        (contact_a, "Contact A", "CONVERTED", None, None, "partner", NOW, partner_a, None, None, None, None, None),
        (contact_b, "Contact B", "CONVERTED", None, None, "partner", NOW, partner_b, None, None, None, None, None),
    ]
    # Ordinea intentionat "inversata" fata de contacte, ca sa dovedim ca
    # maparea se face explicit prin partner_id, nu prin ordinea randurilor.
    score_rows = [
        (partner_b, "PDI", 90.0),
        (partner_a, "PDI", 10.0),
    ]

    with patch("src.agents.contact.contact_agent.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(fetchall_return=None)
        mock_cur.fetchall.side_effect = [contact_rows, score_rows]
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = agent.list_prioritized_contacts(owner_id)

    summary_a = next(c for c in result if c.contact_id == contact_a)
    summary_b = next(c for c in result if c.contact_id == contact_b)

    assert summary_a.pdi == 10.0
    assert summary_b.pdi == 90.0


# ----------------------------------------------------------------------
# CRH nu este citit niciodata (contract, sectiunea 3.1 si audit)
# ----------------------------------------------------------------------


def test_nicio_interogare_nu_citeste_crh(agent):
    """
    CRH nu are niciun producator in scores (verificat in audit) - agentul
    nu trebuie sa interogheze niciodata acest metric_code.
    """
    with patch("src.agents.contact.contact_agent.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(fetchall_return=[])
        mock_get_conn.return_value = _make_conn(mock_cur)

        agent.list_prioritized_contacts(uuid4())

        for call in mock_cur.execute.call_args_list:
            sql = call[0][0]
            params = call[0][1] if len(call[0]) > 1 else ()
            assert "CRH" not in sql
            assert "CRH" not in params


# ----------------------------------------------------------------------
# `reason` — motiv textual per Contact (contract sectiunea 5.1,
# CONFIRMAT de owner 17 august 2026). Nu recalculeaza PriorityKey,
# doar explica textual grupul deja calculat.
# ----------------------------------------------------------------------


def test_reason_followup_scadent(agent):
    owner_id = uuid4()
    contact_id = uuid4()

    rows = [
        (contact_id, "Contact Scadent", "ACTIVE", PAST, "PENDING", None, NOW, None, None, None, None, None, None),
    ]

    with patch("src.agents.contact.contact_agent.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(fetchall_return=rows)
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = agent.list_prioritized_contacts(owner_id)

    summary = next(c for c in result if c.contact_id == contact_id)
    assert summary.reason == "Follow-up scadent"


def test_reason_fara_niciun_followup(agent):
    owner_id = uuid4()
    contact_id = uuid4()

    rows = [
        (contact_id, "Contact Fara FollowUp", "ACTIVE", None, None, None, NOW, None, None, None, None, None, None),
    ]

    with patch("src.agents.contact.contact_agent.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(fetchall_return=rows)
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = agent.list_prioritized_contacts(owner_id)

    summary = next(c for c in result if c.contact_id == contact_id)
    assert summary.reason == "Fără follow-up programat"


def test_reason_followup_viitor(agent):
    """FollowUp PENDING dar programat in viitor -> reason distinct de 'fara niciun followup'."""
    owner_id = uuid4()
    contact_id = uuid4()

    rows = [
        (contact_id, "Contact Viitor", "ACTIVE", FUTURE, "PENDING", None, NOW, None, None, None, None, None, None),
    ]

    with patch("src.agents.contact.contact_agent.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(fetchall_return=rows)
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = agent.list_prioritized_contacts(owner_id)

    summary = next(c for c in result if c.contact_id == contact_id)
    assert summary.reason == "Fără follow-up scadent"


def test_reason_followup_completat(agent):
    """FollowUp COMPLETED (nu scadent, nu viitor) -> 'Prioritate dupa actualizare'."""
    owner_id = uuid4()
    contact_id = uuid4()

    rows = [
        (contact_id, "Contact Completat", "ACTIVE", PAST, "COMPLETED", None, NOW, None, None, None, None, None, None),
    ]

    with patch("src.agents.contact.contact_agent.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(fetchall_return=rows)
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = agent.list_prioritized_contacts(owner_id)

    summary = next(c for c in result if c.contact_id == contact_id)
    assert summary.reason == "Prioritate după actualizare"


def test_reason_nu_afecteaza_ordinea_sortarii(agent):
    """
    reason e strict text explicativ - PriorityKey/sortarea ramane
    neschimbata, indiferent de reason (regresie explicita ceruta de owner).
    """
    owner_id = uuid4()
    contact_scadent = uuid4()
    contact_viitor = uuid4()

    rows = [
        (contact_viitor, "Contact Viitor", "ACTIVE", FUTURE, "PENDING", None, NOW, None, None, None, None, None, None),
        (contact_scadent, "Contact Scadent", "ACTIVE", PAST, "PENDING", None, NOW, None, None, None, None, None, None),
    ]

    with patch("src.agents.contact.contact_agent.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(fetchall_return=rows)
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = agent.list_prioritized_contacts(owner_id)

    result_ids = [c.contact_id for c in result]
    assert result_ids.index(contact_scadent) < result_ids.index(contact_viitor)


# ----------------------------------------------------------------------
# CONVERTED fara rand nici in clients, nici in partners (date
# inconsistente) - contract sectiunea 9, caz explicit dar netestat
# pana acum (gasit la auditul din 17 august 2026).
# ----------------------------------------------------------------------


def test_converted_fara_client_fara_partner_nu_produce_crash(agent):
    """
    Contact CONVERTED dar fara rand corespondent nici in clients, nici
    in partners (date inconsistente in DB) - trebuie tratat explicit:
    converted_to=None, pdi/pip=None, FARA exceptie ridicata.
    """
    owner_id = uuid4()
    contact_id = uuid4()

    rows = [
        (contact_id, "Contact Inconsistent", "CONVERTED", None, None, None, NOW, None, None, None, None, None, None),
    ]

    with patch("src.agents.contact.contact_agent.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(fetchall_return=rows)
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = agent.list_prioritized_contacts(owner_id)

    summary = next(c for c in result if c.contact_id == contact_id)
    assert summary.converted_to is None
    assert summary.pdi is None
    assert summary.pip is None


# ----------------------------------------------------------------------
# DECIZIA 37A (RED, 19 august 2026) — expunere partner_id in
# ContactSummary. Sursa: 37A-expose-partner-id-contract.md, sectiunea 5.
# partner_id era deja citit intern (pozitia 7 din _ContactRow), dar
# niciodata expus in ContactSummary pana acum.
# ----------------------------------------------------------------------


def test_partner_id_expus_pentru_contact_convertit(agent):
    """
    Criteriul 1 (contract 37A): contact convertit in Partener ->
    partner_id trebuie sa fie EXACT UUID-ul partenerului asociat,
    nu doar "nenul". Testul foloseste doi Parteneri distincti ai
    aceluiasi owner ca sa exclu orice posibilitate ca implementarea
    sa returneze primul/orice partner_id gasit, in loc de cel corect
    pentru fiecare contact in parte.
    """
    owner_id = uuid4()
    contact_a = uuid4()
    contact_b = uuid4()
    partner_a = uuid4()
    partner_b = uuid4()

    rows = [
        (contact_a, "Contact A", "CONVERTED", None, None, "partner", NOW, partner_a, None, None, None, None, None),
        (contact_b, "Contact B", "CONVERTED", None, None, "partner", NOW, partner_b, None, None, None, None, None),
    ]

    with patch("src.agents.contact.contact_agent.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(fetchall_return=None)
        mock_cur.fetchall.side_effect = [rows, []]
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = agent.list_prioritized_contacts(owner_id)

    summary_a = next(c for c in result if c.contact_id == contact_a)
    summary_b = next(c for c in result if c.contact_id == contact_b)

    assert summary_a.partner_id == partner_a
    assert summary_b.partner_id == partner_b
    assert summary_a.partner_id != summary_b.partner_id


def test_partner_id_none_pentru_contact_neconvertit(agent):
    """Criteriul 2 (contract 37A): contact neconvertit -> partner_id is None."""
    owner_id = uuid4()
    contact_id = uuid4()

    rows = [
        (contact_id, "Contact Neconvertit", "ACTIVE", None, None, None, NOW, None, None, None, None, None, None),
    ]

    with patch("src.agents.contact.contact_agent.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(fetchall_return=rows)
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = agent.list_prioritized_contacts(owner_id)

    summary = next(c for c in result if c.contact_id == contact_id)
    assert summary.partner_id is None


def test_partner_id_izolat_pe_owner(agent):
    """
    Criteriul 3 (contract 37A): rezultatul pentru owner_id-ul B nu
    trebuie sa contina niciodata partner_id-ul unui contact/partener
    al owner_id-ului A. Verificat la nivel de rezultat produs de
    agent, nu doar prin prezenta owner_id in parametrii SQL — cursorul
    mock intoarce EXCLUSIV randurile lui B (asa cum ar face un WHERE
    owner_id = %s real), deci orice partner_id al lui A care ar aparea
    in rezultat ar demonstra o scurgere reala intre useri.
    """
    owner_id_b = uuid4()
    contact_b = uuid4()
    partner_b = uuid4()
    partner_id_a_strain = uuid4()  # nu trebuie sa apara niciodata

    rows_doar_ale_lui_b = [
        (contact_b, "Contact B", "CONVERTED", None, None, "partner", NOW, partner_b, None, None, None, None, None),
    ]

    with patch("src.agents.contact.contact_agent.get_connection") as mock_get_conn:
        mock_cur = _make_cursor(fetchall_return=None)
        mock_cur.fetchall.side_effect = [rows_doar_ale_lui_b, []]
        mock_get_conn.return_value = _make_conn(mock_cur)

        result = agent.list_prioritized_contacts(owner_id_b)

    partner_ids_in_rezultat = [c.partner_id for c in result]
    assert partner_id_a_strain not in partner_ids_in_rezultat
    assert partner_ids_in_rezultat == [partner_b]
