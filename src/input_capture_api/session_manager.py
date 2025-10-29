"""Session manager for HID recording sessions."""

from typing import Any

from hid_recorder import Event, Recorder, Session
from ulid import ULID


class SessionManager:
    """Manages HID recording sessions using hid-recorder."""

    def __init__(self, recorder: Recorder) -> None:
        """Initialize the session manager.

        Args:
            recorder: hid-recorder Recorder instance
        """
        self.recorder = recorder

    def start_session(
        self, name: str, metadata: dict[str, Any] | None = None
    ) -> Session:
        """Start a new recording session.

        Args:
            name: Name of the session
            metadata: Optional metadata for the session

        Returns:
            Session object
        """
        return self.recorder.start_session(name, metadata)

    def end_session(self, session_id: str) -> None:
        """End a recording session.

        Args:
            session_id: ID of the session to end
        """
        ulid_id = ULID.from_str(session_id)
        self.recorder.end_session(ulid_id)

    def get_events(self, session_id: str) -> list[Event]:
        """Get events for a session.

        Args:
            session_id: ID of the session

        Returns:
            List of events
        """
        ulid_id = ULID.from_str(session_id)
        return self.recorder.get_events(ulid_id)

    def list_sessions(self) -> list[Session]:
        """List all sessions.

        Returns:
            List of sessions
        """
        return self.recorder.list_sessions()

    def get_session(self, session_id: str) -> Session | None:
        """Get a specific session.

        Args:
            session_id: ID of the session

        Returns:
            Session object or None if not found
        """
        ulid_id = ULID.from_str(session_id)
        return self.recorder.get_session(ulid_id)
