"""
PriorityEngine — motorul de prioritizare pentru NicMar OS.

Contract: docs/architecture/19-priority-engine-contract.md.
Specificație: docs/architecture/18-priority-engine-spec-v1.md.

Motor strict READ-ONLY: citește Mission + FollowUp active, derivă
Impact, Urgență și Vechime, construiește PriorityKey și returnează
activitățile în ordine lexicografică. Nu scrie în DB.
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional, Tuple
from uuid import UUID

from src.data.db import get_connection


ACTIVE_MISSION_STATUSES = ("GENERATED", "ASSIGNED", "IN_PROGRESS")
ACTIVE_FOLLOWUP_STATUS = "PENDING"

IMPACT_MISSION = 1.0
IMPACT_FOLLOWUP_BASE = 1.0
IMPACT_FOLLOWUP_BONUS = {
    "ARCHIVED": 0.0,
    "NEW": 0.5,
    "ACTIVE": 1.0,
    "CONVERTED": 0.0,
}

URGENCY_MISSION = 1.0
URGENCY_FOLLOWUP_FAR = 1.00
URGENCY_FOLLOWUP_NEAR = 1.33
URGENCY_FOLLOWUP_TODAY = 1.67
URGENCY_FOLLOWUP_OVERDUE = 2.00


@dataclass(frozen=True)
class PrioritizedActivity:
    """Activitate eligibilă pentru prioritizare."""

    entity_type: str
    entity_id: UUID
    title: str
    impact: float
    urgency: float
    vechime_seconds: float
    priority_key: Tuple[float, float, float]


class PriorityEngine:
    """
    Motor read-only pentru ordonarea activităților zilei.

    Nu primește motoare secundare și nu modifică starea niciunei entități.
    Izolarea se face în SQL prin owner_id, conform contractului 19.
    """

    def build_priority_list(self, owner_id: UUID) -> List[PrioritizedActivity]:
        """
        Construiește lista completă, ordonată, a activităților active ale owner-ului.

        Filtrul Planului Zilei este separat: apply_workload_filter().
        """
        now = self._read_now()
        activities: List[PrioritizedActivity] = []
        activities.extend(self._load_missions(owner_id, now))
        activities.extend(self._load_followups(owner_id, now))
        return sorted(activities, key=lambda activity: activity.priority_key, reverse=True)

    @staticmethod
    def apply_workload_filter(
        sorted_activities: List[PrioritizedActivity],
    ) -> List[PrioritizedActivity]:
        """Aplică plafonul Planului Zilei: cel mult 5, fără minim artificial."""
        return sorted_activities[:5]

    @staticmethod
    def _read_now() -> datetime:
        """Obține un timestamp real din PostgreSQL, păstrând sursa de timp a sistemului."""
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT clock_timestamp()")
                now = cur.fetchone()[0]
        return now

    def _load_missions(self, owner_id: UUID, now: datetime) -> List[PrioritizedActivity]:
        query = """
            SELECT id, title, created_at
            FROM missions
            WHERE owner_id = %s
              AND status IN ('GENERATED', 'ASSIGNED', 'IN_PROGRESS')
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (owner_id,))
                rows = cur.fetchall()

        return [
            self._make_activity(
                entity_type="mission",
                entity_id=row[0],
                title=row[1],
                created_at=row[2],
                impact=IMPACT_MISSION,
                urgency=URGENCY_MISSION,
                now=now,
            )
            for row in rows
        ]

    def _load_followups(self, owner_id: UUID, now: datetime) -> List[PrioritizedActivity]:
        query = """
            SELECT f.id, f.notes, f.created_at, f.scheduled_at, c.status
            FROM follow_ups AS f
            JOIN contacts AS c ON c.id = f.contact_id
            WHERE f.owner_id = %s
              AND f.status = 'PENDING'
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (owner_id,))
                rows = cur.fetchall()

        return [
            self._make_activity(
                entity_type="followup",
                entity_id=row[0],
                title=row[1] or f"FollowUp {row[0]}",
                created_at=row[2],
                impact=self._followup_impact(row[4]),
                urgency=self._followup_urgency(row[3], now),
                now=now,
            )
            for row in rows
        ]

    @staticmethod
    def _followup_impact(contact_status: str) -> float:
        try:
            bonus = IMPACT_FOLLOWUP_BONUS[contact_status]
        except KeyError as exc:
            raise ValueError(f"Status Contact necunoscut: {contact_status}") from exc
        return IMPACT_FOLLOWUP_BASE + bonus

    @staticmethod
    def _followup_urgency(scheduled_at: datetime, now: datetime) -> float:
        if scheduled_at < now:
            return URGENCY_FOLLOWUP_OVERDUE

        scheduled_date = scheduled_at.date()
        today = now.date()

        if scheduled_date == today:
            return URGENCY_FOLLOWUP_TODAY
        if scheduled_date <= today + timedelta(days=2):
            return URGENCY_FOLLOWUP_NEAR
        return URGENCY_FOLLOWUP_FAR

    @staticmethod
    def _make_activity(
        entity_type: str,
        entity_id: UUID,
        title: str,
        created_at: datetime,
        impact: float,
        urgency: float,
        now: datetime,
    ) -> PrioritizedActivity:
        vechime_seconds = max(0.0, (now - created_at).total_seconds())
        priority_key = (impact, urgency, vechime_seconds)
        return PrioritizedActivity(
            entity_type=entity_type,
            entity_id=entity_id,
            title=title,
            impact=impact,
            urgency=urgency,
            vechime_seconds=vechime_seconds,
            priority_key=priority_key,
        )
