"""Tests for API endpoints."""

from unittest.mock import MagicMock

from fastapi import status
from fastapi.testclient import TestClient
from hid_recorder import EventItem, Session
from ulid import ULID

from input_capture_api.api import create_app
from input_capture_api.session_manager import SessionManager

EXPECTED_EVENT_COUNT = 2
EXPECTED_SESSION_COUNT = 2


def test_start_session() -> None:
    """Test POST /sessions endpoint."""
    mock_session_manager = MagicMock(spec=SessionManager)
    session_ulid = ULID()
    mock_session = MagicMock(spec=Session)
    mock_session.id = session_ulid
    mock_session.name = "test-session"
    mock_session_manager.start_session.return_value = mock_session

    app = create_app(session_manager=mock_session_manager)
    client = TestClient(app)

    response = client.post(
        "/sessions", json={"name": "test-session", "metadata": {"key": "value"}}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(session_ulid)
    assert data["name"] == "test-session"
    mock_session_manager.start_session.assert_called_once()


def test_end_session() -> None:
    """Test PATCH /sessions/{session_id} endpoint."""
    mock_session_manager = MagicMock(spec=SessionManager)
    app = create_app(session_manager=mock_session_manager)
    client = TestClient(app)

    session_id = str(ULID())
    response = client.patch(f"/sessions/{session_id}", json={"status": "ended"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ended"}
    mock_session_manager.end_session.assert_called_once_with(session_id)


def test_end_session_invalid_status() -> None:
    """Test PATCH /sessions/{session_id} endpoint with invalid status."""
    mock_session_manager = MagicMock(spec=SessionManager)
    app = create_app(session_manager=mock_session_manager)
    client = TestClient(app)

    session_id = str(ULID())
    response = client.patch(f"/sessions/{session_id}", json={"status": "invalid"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    mock_session_manager.end_session.assert_not_called()


def test_get_events() -> None:
    """Test GET /sessions/{session_id}/events endpoint."""
    mock_session_manager = MagicMock(spec=SessionManager)
    mock_events = [
        MagicMock(
            spec=EventItem,
        ),
        MagicMock(
            spec=EventItem,
        ),
    ]
    mock_session_manager.get_events.return_value = mock_events

    app = create_app(session_manager=mock_session_manager)
    client = TestClient(app)

    session_id = str(ULID())
    response = client.get(f"/sessions/{session_id}/events")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["events"]) == EXPECTED_EVENT_COUNT
    mock_session_manager.get_events.assert_called_once_with(session_id)


def test_list_sessions() -> None:
    """Test GET /sessions endpoint."""
    mock_session_manager = MagicMock(spec=SessionManager)
    session_1 = MagicMock(spec=Session)
    session_1.id = ULID()
    session_1.name = "session-1"
    session_2 = MagicMock(spec=Session)
    session_2.id = ULID()
    session_2.name = "session-2"
    mock_sessions = [session_1, session_2]
    mock_session_manager.list_sessions.return_value = mock_sessions

    app = create_app(session_manager=mock_session_manager)
    client = TestClient(app)

    response = client.get("/sessions")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["sessions"]) == EXPECTED_SESSION_COUNT
    mock_session_manager.list_sessions.assert_called_once()


def test_get_session() -> None:
    """Test GET /sessions/{session_id} endpoint."""
    mock_session_manager = MagicMock(spec=SessionManager)
    session_ulid = ULID()
    mock_session = MagicMock(spec=Session)
    mock_session.id = session_ulid
    mock_session.name = "test-session"
    mock_session_manager.get_session.return_value = mock_session

    app = create_app(session_manager=mock_session_manager)
    client = TestClient(app)

    session_id = str(session_ulid)
    response = client.get(f"/sessions/{session_id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == session_id
    assert data["name"] == "test-session"
    mock_session_manager.get_session.assert_called_once_with(session_id)


def test_get_session_not_found() -> None:
    """Test GET /sessions/{session_id} endpoint when session not found."""
    mock_session_manager = MagicMock(spec=SessionManager)
    mock_session_manager.get_session.return_value = None

    app = create_app(session_manager=mock_session_manager)
    client = TestClient(app)

    session_id = str(ULID())
    response = client.get(f"/sessions/{session_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_session_manager.get_session.assert_called_once_with(session_id)


def test_session_manager_not_configured() -> None:
    """Test that endpoints return 500 when SessionManager is not configured."""
    app = create_app(session_manager=None)
    client = TestClient(app)

    # Test POST /sessions
    response = client.post("/sessions", json={"name": "test"})
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "SessionManager not configured" in response.json()["detail"]
