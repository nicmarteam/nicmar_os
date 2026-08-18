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


def get_conversation_agent(
    objection_engine: ObjectionEngine = Depends(get_objection_engine),
) -> ConversationAgent:
    """
    Decizia 7 — chaining real, spre deosebire de wiring-ul independent de
    mai sus (Mission/FollowUp/Partner). `Depends(get_objection_engine)`
    garantează, în cadrul aceluiași request, aceeași instanță de
    `ObjectionEngine` pentru orice alt endpoint care ar cere-o separat.
    """
    return ConversationAgent(objection_engine=objection_engine)
