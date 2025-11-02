"""FastAPI application for HID recording control."""

from typing import Any

from fastapi import FastAPI, HTTPException
from hid_recorder import EventItem, Session
from pydantic import BaseModel

from input_capture_api.session_manager import SessionManager

_SESSION_MANAGER_NOT_CONFIGURED = "SessionManager not configured"


class SessionCreateRequest(BaseModel):
    """Request model for creating a session."""

    name: str
    metadata: dict[str, Any] | None = None


SessionResponse = Session


class SessionStatusUpdate(BaseModel):
    """Request model for updating session status."""

    status: str


class SessionEndResponse(BaseModel):
    """Response model for ending a session."""

    status: str


class EventsResponse(BaseModel):
    """Response model for events list."""

    events: list[EventItem]


class SessionsResponse(BaseModel):
    """Response model for sessions list."""

    sessions: list[SessionResponse]


def _check_session_manager(manager: SessionManager | None) -> SessionManager:
    """Check if session manager is configured.

    Args:
        manager: SessionManager instance or None

    Returns:
        SessionManager instance

    Raises:
        HTTPException: If session manager is not configured
    """
    if manager is None:
        msg = _SESSION_MANAGER_NOT_CONFIGURED
        raise HTTPException(status_code=500, detail=msg)
    return manager


def create_app(session_manager: SessionManager | None = None) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        session_manager: Optional SessionManager instance for dependency injection

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(title="Input Capture API", version="0.1.0")

    @app.post("/sessions")
    async def start_session(request: SessionCreateRequest) -> SessionResponse:
        """Start a new recording session.

        Args:
            request: Session creation request

        Returns:
            Session information
        """
        manager = _check_session_manager(session_manager)
        return await manager.start_session(request.name, request.metadata)

    @app.patch("/sessions/{session_id}")
    async def update_session_status(
        session_id: str, status_update: SessionStatusUpdate
    ) -> SessionEndResponse:
        """Update a recording session status.

        Args:
            session_id: ID of the session to update
            status_update: Status update request

        Returns:
            Status response

        Raises:
            HTTPException: If status is invalid
        """
        if status_update.status != "ended":
            msg = f"Invalid status: {status_update.status}. Only 'ended' is supported."
            raise HTTPException(status_code=400, detail=msg)
        manager = _check_session_manager(session_manager)
        await manager.end_session(session_id)
        return SessionEndResponse(status="ended")

    @app.get("/sessions/{session_id}/events")
    def get_events(session_id: str) -> EventsResponse:
        """Get events for a session.

        Args:
            session_id: ID of the session

        Returns:
            List of events
        """
        manager = _check_session_manager(session_manager)
        events = manager.get_events(session_id)
        return EventsResponse(events=events)

    @app.get("/sessions")
    def list_sessions() -> SessionsResponse:
        """List all sessions.

        Returns:
            List of sessions
        """
        manager = _check_session_manager(session_manager)
        sessions = manager.list_sessions()
        return SessionsResponse(sessions=sessions)

    @app.get("/sessions/{session_id}")
    def get_session(session_id: str) -> SessionResponse:
        """Get a specific session.

        Args:
            session_id: ID of the session

        Returns:
            Session information

        Raises:
            HTTPException: If session not found
        """
        manager = _check_session_manager(session_manager)
        session = manager.get_session(session_id)
        if session is None:
            msg = f"Session {session_id} not found"
            raise HTTPException(status_code=404, detail=msg)
        return session

    return app
