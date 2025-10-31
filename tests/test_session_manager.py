"""Tests for session manager."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from hid_recorder import Event, Recorder, Session
from ulid import ULID

from input_capture_api.session_manager import SessionManager

EXPECTED_EVENT_COUNT = 2
EXPECTED_SESSION_COUNT = 2


@pytest.mark.asyncio
async def test_start_session() -> None:
    """Test starting a new session."""
    mock_recorder = MagicMock(spec=Recorder)
    mock_session = MagicMock(spec=Session)
    session_ulid = ULID()
    mock_session.session_id = session_ulid
    mock_session.name = "test-session"

    # Mock the session context manager
    mock_handle = MagicMock()
    mock_handle.session = mock_session
    mock_handle.hook = MagicMock()

    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_handle
    mock_recorder.session.return_value = mock_ctx

    session_manager = SessionManager(recorder=mock_recorder)
    session = await session_manager.start_session(
        name="test-session", metadata={"key": "value"}
    )

    mock_recorder.session.assert_called_once_with(
        name="test-session", metadata={"key": "value"}
    )
    assert session.session_id == session_ulid
    assert session.name == "test-session"
    # Verify background task was created
    assert str(session_ulid) in session_manager._sessions  # noqa: SLF001


@pytest.mark.asyncio
async def test_end_session() -> None:
    """Test ending an existing session."""
    mock_recorder = MagicMock(spec=Recorder)
    session_ulid = ULID()
    session_id = str(session_ulid)

    # Mock the session context manager
    mock_session = MagicMock(spec=Session)
    mock_session.session_id = session_ulid
    mock_session.name = "test-session"

    mock_handle = MagicMock()
    mock_handle.session = mock_session
    mock_handle.hook = MagicMock()

    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_handle
    mock_recorder.session.return_value = mock_ctx

    session_manager = SessionManager(recorder=mock_recorder)

    # Start a session first
    await session_manager.start_session(name="test-session", metadata=None)

    # End the session
    await session_manager.end_session(session_id)

    # Verify context manager was exited
    mock_ctx.__aexit__.assert_called_once()
    # Verify session was removed from internal dict
    assert session_id not in session_manager._sessions  # noqa: SLF001


def test_get_events() -> None:
    """Test retrieving events for a session."""
    mock_recorder = MagicMock(spec=Recorder)
    mock_events = [
        MagicMock(spec=Event, device="/dev/input/event0", code=30, value=1),
        MagicMock(spec=Event, device="/dev/input/event0", code=30, value=0),
    ]
    mock_recorder.get_events.return_value = mock_events

    session_manager = SessionManager(recorder=mock_recorder)
    session_id = str(ULID())
    events = session_manager.get_events(session_id)

    mock_recorder.get_events.assert_called_once()
    called_ulid = mock_recorder.get_events.call_args[0][0]
    assert str(called_ulid) == session_id
    assert len(events) == EXPECTED_EVENT_COUNT
    assert events == mock_events


def test_list_sessions() -> None:
    """Test listing all sessions."""
    mock_recorder = MagicMock(spec=Recorder)
    mock_session_1 = MagicMock(spec=Session)
    mock_session_1.session_id = ULID()
    mock_session_1.name = "session-1"
    mock_session_2 = MagicMock(spec=Session)
    mock_session_2.session_id = ULID()
    mock_session_2.name = "session-2"
    mock_sessions = [mock_session_1, mock_session_2]
    mock_recorder.list_sessions.return_value = mock_sessions

    session_manager = SessionManager(recorder=mock_recorder)
    sessions = session_manager.list_sessions()

    mock_recorder.list_sessions.assert_called_once()
    assert len(sessions) == EXPECTED_SESSION_COUNT
    assert sessions == mock_sessions


def test_get_session() -> None:
    """Test getting a specific session."""
    mock_recorder = MagicMock(spec=Recorder)
    session_ulid = ULID()
    mock_session = MagicMock(spec=Session)
    mock_session.session_id = session_ulid
    mock_session.name = "test-session"
    mock_recorder.get_session.return_value = mock_session

    session_manager = SessionManager(recorder=mock_recorder)
    session_id = str(session_ulid)
    session = session_manager.get_session(session_id)

    mock_recorder.get_session.assert_called_once()
    called_ulid = mock_recorder.get_session.call_args[0][0]
    assert str(called_ulid) == session_id
    assert session is not None
    assert session.session_id == session_ulid
    assert session.name == "test-session"
