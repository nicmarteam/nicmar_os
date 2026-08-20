"""
Dependency injection pentru API — construiește Engine/Agent la fiecare
request, exact ca în teste, nicio logică nouă adăugată aici.
"""

from fastapi import Depends

from src.engines.rule.rule_engine import RuleEngine
from src.engines.mission.mission_engine import MissionEngine
from src.agents.mission.mission_agent import MissionAgent
from src.engines.followup.followup_engine import FollowUpEngine
from src.agents.followup.followup_agent import FollowUpAgent
from src.engines.partner.partner_engine import PartnerEngine
from src.agents.partner.partner_agent import PartnerAgent
from src.engines.objection.objection_engine import ObjectionEngine
from src.agents.conversation.conversation_agent import ConversationAgent
from src.engines.contact.contact_engine import ContactEngine
from src.agents.contact.contact_agent import ContactAgent
from src.engines.conversation.conversation_engine import ConversationEngine
from src.engines.priority.priority_engine import PriorityEngine
from src.engines.outreach.outreach_engine import OutreachEngine


def get_mission_agent() -> MissionAgent:
    rule_engine = RuleEngine()
    mission_engine = MissionEngine(rule_engine=rule_engine)
    return MissionAgent(mission_engine=mission_engine)


def get_mission_engine() -> MissionEngine:
    rule_engine = RuleEngine()
    return MissionEngine(rule_engine=rule_engine)


def get_followup_agent() -> FollowUpAgent:
    rule_engine = RuleEngine()
    followup_engine = FollowUpEngine(rule_engine=rule_engine)
    return FollowUpAgent(followup_engine=followup_engine)


def get_followup_engine() -> FollowUpEngine:
    rule_engine = RuleEngine()
    return FollowUpEngine(rule_engine=rule_engine)


def get_partner_agent() -> PartnerAgent:
    rule_engine = RuleEngine()
    partner_engine = PartnerEngine(rule_engine=rule_engine)
    return PartnerAgent(partner_engine=partner_engine)


def get_objection_engine() -> ObjectionEngine:
    """Decizia 7, `24-dependency-wiring-contract.md` — fără dependințe proprii."""
    return ObjectionEngine()


def get_conversation_engine() -> ConversationEngine:
    """Decizia 33, `33-conversation-objection-linkage-contract.md` — fără dependințe proprii."""
    return ConversationEngine()


def get_conversation_agent(
    objection_engine: ObjectionEngine = Depends(get_objection_engine),
    conversation_engine: ConversationEngine = Depends(get_conversation_engine),
) -> ConversationAgent:
    """
    Decizia 7 — chaining real, spre deosebire de wiring-ul independent de
    mai sus (Mission/FollowUp/Partner). `Depends(get_objection_engine)`
    garantează, în cadrul aceluiași request, aceeași instanță de
    `ObjectionEngine` pentru orice alt endpoint care ar cere-o separat.

    Decizia 33: a doua dependință, `ConversationEngine`, chaining identic —
    folosită pentru verificarea de ownership a `conversation_id`.
    """
    return ConversationAgent(objection_engine=objection_engine, conversation_engine=conversation_engine)


def get_contact_engine() -> ContactEngine:
    """Decizia 31, `31-contact-create-contract.md` — fără dependințe proprii."""
    return ContactEngine()


def get_contact_agent() -> ContactAgent:
    """Decizia 33, `33-conversation-objection-linkage-contract.md` — expune ContactAgent, deja existent."""
    return ContactAgent()


def get_priority_engine() -> PriorityEngine:
    """Decizia 39, `39-priority-api-contract.md` — PriorityEngine nu are dependințe proprii."""
    return PriorityEngine()


def get_outreach_engine(
    conversation_engine: ConversationEngine = Depends(get_conversation_engine),
) -> OutreachEngine:
    """
    Decizia 46, `46-prospectare-relationala-contract.md` — chaining real
    cu ConversationEngine (necesar pentru handoff-ul automat la
    record_outcome), identic tipar cu get_conversation_agent (Decizia 33).
    """
    return OutreachEngine(conversation_engine=conversation_engine)
