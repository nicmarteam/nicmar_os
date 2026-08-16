"""
Dependency injection pentru API — construiește Engine/Agent la fiecare
request, exact ca în teste, nicio logică nouă adăugată aici.
"""

from src.engines.rule.rule_engine import RuleEngine
from src.engines.mission.mission_engine import MissionEngine
from src.agents.mission.mission_agent import MissionAgent
from src.engines.followup.followup_engine import FollowUpEngine
from src.agents.followup.followup_agent import FollowUpAgent


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
