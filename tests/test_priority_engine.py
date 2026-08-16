"""Teste unitare pentru PriorityEngine — fara PostgreSQL real."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from src.engines.priority.priority_engine import (
    IMPACT_FOLLOWUP_BASE,
    IMPACT_MISSION,
    URGENCY_FOLLOWUP_FAR,
    URGENCY_FOLLOWUP_NEAR,
    URGENCY_FOLLOWUP_OVERDUE,
    URGENCY_FOLLOWUP_TODAY,
    URGENCY_MISSION,
    PrioritizedActivity,
    PriorityEngine,
)


UTC = timezone.utc


def make_conn(*, fetchone=None, fetchall=None):
    cur = MagicMock()
    cur.fetchone.return_value = fetchone
    cur.fetchall.return_value = [] if fetchall is None else fetchall
    cur.__enter__.return_value = cur
    cur.__exit__.return_value = False

    conn = MagicMock()
    conn.cursor.return_value = cur
    conn.__enter__.return_value = conn
    conn.__exit__.return_value = False
    return conn


def activity(impact, urgency, age):
    return PrioritizedActivity(
        entity_type="mission",
        entity_id=uuid4(),
        title="Test",
        impact=impact,
        urgency=urgency,
        vechime_seconds=age,
        priority_key=(impact, urgency, age),
    )


class TestImpact:
    @pytest.mark.parametrize(
        ("contact_status", "expected"),
        [
            ("ARCHIVED", 1.0),
            ("NEW", 1.5),
            ("ACTIVE", 2.0),
            ("CONVERTED", 1.0),
        ],
    )
    def test_followup_impact(self, contact_status, expected):
        assert PriorityEngine._followup_impact(contact_status) == expected

    def test_mission_impact_is_fixed(self):
        assert IMPACT_MISSION == 1.0
        assert IMPACT_FOLLOWUP_BASE == 1.0

    def test_unknown_contact_status_is_explicit_error(self):
        with pytest.raises(ValueError, match="Status Contact necunoscut"):
            PriorityEngine._followup_impact("UNKNOWN")


class TestUrgency:
    def test_mission_urgency_is_fixed(self):
        assert URGENCY_MISSION == 1.0

    @pytest.mark.parametrize(
        ("delta", "expected"),
        [
            (timedelta(days=-1), URGENCY_FOLLOWUP_OVERDUE),
            (timedelta(hours=2), URGENCY_FOLLOWUP_TODAY),
            (timedelta(days=1, hours=2), URGENCY_FOLLOWUP_NEAR),
            (timedelta(days=2, hours=2), URGENCY_FOLLOWUP_NEAR),
            (timedelta(days=3), URGENCY_FOLLOWUP_FAR),
        ],
    )
    def test_followup_urgency(self, delta, expected):
        now = datetime(2026, 8, 15, 12, 0, tzinfo=UTC)
        scheduled_at = now + delta
        assert PriorityEngine._followup_urgency(scheduled_at, now) == expected


class TestSorting:
    def test_impact_dominates(self):
        low_impact = activity(1.0, 2.0, 999999.0)
        high_impact = activity(2.0, 1.0, 1.0)
        result = sorted([low_impact, high_impact], key=lambda a: a.priority_key, reverse=True)
        assert result[0] is high_impact

    def test_urgency_breaks_equal_impact(self):
        low_urgency = activity(2.0, 1.0, 999999.0)
        high_urgency = activity(2.0, 2.0, 1.0)
        result = sorted([low_urgency, high_urgency], key=lambda a: a.priority_key, reverse=True)
        assert result[0] is high_urgency

    def test_vechime_breaks_equal_impact_and_urgency(self):
        younger = activity(2.0, 2.0, 10.0)
        older = activity(2.0, 2.0, 20.0)
        result = sorted([younger, older], key=lambda a: a.priority_key, reverse=True)
        assert result[0] is older


class TestWorkloadFilter:
    @pytest.mark.parametrize("count", [0, 1, 2, 3, 4, 5, 6, 10])
    def test_maximum_five_without_artificial_minimum(self, count):
        activities = [activity(1.0, 1.0, float(i)) for i in range(count)]
        result = PriorityEngine.apply_workload_filter(activities)
        assert len(result) == min(count, 5)
        assert result == activities[:5]


class TestBuildPriorityList:
    def test_owner_is_passed_to_both_activity_queries_and_terminal_statuses_are_excluded(self):
        owner_id = uuid4()
        now = datetime(2026, 8, 15, 12, 0, tzinfo=UTC)
        mission_id = uuid4()
        followup_id = uuid4()

        now_conn = make_conn(fetchone=(now,))
        mission_conn = make_conn(
            fetchall=[(mission_id, "Mission test", now - timedelta(hours=1))]
        )
        followup_conn = make_conn(
            fetchall=[
                (
                    followup_id,
                    "FollowUp test",
                    now - timedelta(hours=2),
                    now,
                    "ACTIVE",
                )
            ]
        )

        with patch(
            "src.engines.priority.priority_engine.get_connection",
            side_effect=[now_conn, mission_conn, followup_conn],
        ):
            result = PriorityEngine().build_priority_list(owner_id)

        assert {item.entity_id for item in result} == {mission_id, followup_id}

        mission_sql = mission_conn.cursor.return_value.execute.call_args[0][0]
        mission_params = mission_conn.cursor.return_value.execute.call_args[0][1]
        followup_sql = followup_conn.cursor.return_value.execute.call_args[0][0]
        followup_params = followup_conn.cursor.return_value.execute.call_args[0][1]

        assert owner_id in mission_params
        assert owner_id in followup_params
        assert "GENERATED" in mission_sql
        assert "ASSIGNED" in mission_sql
        assert "IN_PROGRESS" in mission_sql
        assert "COMPLETED" not in mission_sql
        assert "status = 'PENDING'" in followup_sql
        assert "COMPLETED" not in followup_sql
        assert "POSTPONED" not in followup_sql
        assert "RESCHEDULED" not in followup_sql

    def test_empty_owner_returns_empty_list(self):
        owner_id = uuid4()
        now_conn = make_conn(fetchone=(datetime.now(UTC),))
        mission_conn = make_conn(fetchall=[])
        followup_conn = make_conn(fetchall=[])

        with patch(
            "src.engines.priority.priority_engine.get_connection",
            side_effect=[now_conn, mission_conn, followup_conn],
        ):
            result = PriorityEngine().build_priority_list(owner_id)

        assert result == []

    def test_followup_notes_have_identifier_fallback(self):
        owner_id = uuid4()
        followup_id = uuid4()
        now = datetime(2026, 8, 15, 12, 0, tzinfo=UTC)

        now_conn = make_conn(fetchone=(now,))
        mission_conn = make_conn(fetchall=[])
        followup_conn = make_conn(
            fetchall=[
                (followup_id, None, now, now, "NEW"),
            ]
        )

        with patch(
            "src.engines.priority.priority_engine.get_connection",
            side_effect=[now_conn, mission_conn, followup_conn],
        ):
            result = PriorityEngine().build_priority_list(owner_id)

        assert result[0].title == f"FollowUp {followup_id}"
        assert result[0].impact == 1.5
