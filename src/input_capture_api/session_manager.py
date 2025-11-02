"""Session manager for HID recording sessions."""

import asyncio
from typing import TYPE_CHECKING, Any

from hid_interceptor import HIDInterceptor
from hid_recorder import EventItem, Recorder, Session
from ulid import ULID

if TYPE_CHECKING:
    from contextlib import AbstractAsyncContextManager


class SessionManager:
    """Manages HID recording sessions using hid-recorder with HIDInterceptor."""

    def __init__(self, recorder: Recorder) -> None:
        """Initialize the session manager.

        Args:
            recorder: hid-recorder Recorder instance
        """
        self.recorder = recorder
        # Maps session_id -> (context_manager, task, stop_event)
        self._sessions: dict[
            str,
            tuple[AbstractAsyncContextManager[Any], asyncio.Task[None], asyncio.Event],
        ] = {}

    async def start_session(
        self, name: str, metadata: dict[str, Any] | None = None
    ) -> Session:
        """Start a new recording session with HIDInterceptor.

        Args:
            name: Name of the session
            metadata: Optional metadata for the session

        Returns:
            Session object
        """
        # Manually manage the async context manager
        ctx = self.recorder.session(name=name, metadata=metadata)
        handle = await ctx.__aenter__()

        # Start HIDInterceptor in background
        stop_event = asyncio.Event()
        interceptor = HIDInterceptor(hooks=[handle.hook])
        task = asyncio.create_task(interceptor.run(stop_event))

        # Store session info
        session_id = str(handle.session.id)
        self._sessions[session_id] = (ctx, task, stop_event)

        return handle.session

    async def end_session(self, session_id: str) -> None:
        """End a recording session and stop HIDInterceptor.

        Args:
            session_id: ID of the session to end
        """
        ulid_id = ULID.from_str(session_id)
        session_id_str = str(ulid_id)

        # Get session info
        ctx, task, stop_event = self._sessions.pop(session_id_str)

        # Stop HIDInterceptor
        stop_event.set()
        await task

        # Exit context manager
        await ctx.__aexit__(None, None, None)

    def get_events(self, session_id: str) -> list[EventItem]:
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
