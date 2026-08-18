"""
Teste RED pentru dependency wiring — get_objection_engine() / get_conversation_agent().

Sursa: 24-dependency-wiring-contract.md, Decizia 7.

Fara TestClient, fara DATABASE_URL, fara router — teste unitare pure,
functiile din dependencies.py doar construiesc obiecte Python, nu ating DB.

IMPORTANT (descoperit in ciclul RED->GREEN): Depends(...) din FastAPI e doar
un marcaj (fastapi.params.Depends) — NU se rezolva automat daca functia e
apelata direct din Python, in afara ciclului de request FastAPI/TestClient.
Deci get_conversation_agent() apelat FARA argumente NU produce un agent cu
.objection_engine rezolvat — primeste literal obiectul Depends(...) ca
valoare. De aceea:
  - verificarea ca agentul functioneaza corect cu un ObjectionEngine real
    foloseste apel EXPLICIT (simuland ce ar face FastAPI dupa rezolvare);
  - verificarea ca wiring-ul e declarat corect (chaining structural)
    inspecteaza signature-ul functiei, nu o apeleaza fara argumente.
"""

import inspect

from fastapi import Depends

from src.api.dependencies import get_conversation_agent, get_objection_engine
from src.agents.conversation.conversation_agent import ConversationAgent
from src.engines.objection.objection_engine import ObjectionEngine


def test_get_objection_engine_returneaza_instanta_objection_engine():
    """get_objection_engine() returneaza o instanta ObjectionEngine."""
    engine = get_objection_engine()
    assert isinstance(engine, ObjectionEngine)


def test_get_conversation_agent_cu_engine_explicit_returneaza_conversation_agent():
    """
    get_conversation_agent(), apelat cu un ObjectionEngine explicit (asa
    cum ar face FastAPI dupa ce rezolva Depends(get_objection_engine) real),
    returneaza o instanta ConversationAgent functionala.
    """
    engine = get_objection_engine()
    agent = get_conversation_agent(objection_engine=engine)
    assert isinstance(agent, ConversationAgent)


def test_get_conversation_agent_cu_engine_explicit_are_objection_engine_atasat():
    """ConversationAgent returnat are .objection_engine de tip ObjectionEngine."""
    engine = get_objection_engine()
    agent = get_conversation_agent(objection_engine=engine)
    assert isinstance(agent.objection_engine, ObjectionEngine)


def test_get_conversation_agent_pastreaza_exact_instanta_injectata():
    """
    Chaining structural (comportament): daca i se transmite explicit o
    instanta ObjectionEngine (simuland ce ar face FastAPI prin Depends),
    agentul trebuie sa pastreze EXACT acea instanta (verificare `is`, nu
    doar tip) — nu construieste silentios propriul ObjectionEngine,
    ignorand dependency injection-ul.
    """
    explicit_engine = ObjectionEngine()
    agent = get_conversation_agent(objection_engine=explicit_engine)
    assert agent.objection_engine is explicit_engine


def test_get_conversation_agent_declara_depends_pe_get_objection_engine():
    """
    Chaining structural (declaratie): parametrul objection_engine al lui
    get_conversation_agent() trebuie sa aiba drept default EXACT
    Depends(get_objection_engine) — nu Depends(altceva), nu o valoare
    hardcodata (ex. ObjectionEngine() direct). Aceasta e verificarea care
    garanteaza ca FastAPI, in productie, va rezolva corect lantul in
    cadrul aceluiasi request — fara sa fie nevoie de TestClient aici.
    """
    sig = inspect.signature(get_conversation_agent)
    default = sig.parameters["objection_engine"].default

    assert isinstance(default, type(Depends()))
    assert default.dependency is get_objection_engine
