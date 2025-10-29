"""Main entry point for the Input Capture API application."""

import os

import uvicorn
from hid_recorder import Recorder

from input_capture_api.api import create_app
from input_capture_api.session_manager import SessionManager


def main() -> None:
    """Run the FastAPI application with uvicorn."""
    # Get database path from environment or use default
    db_path = os.getenv("HID_RECORDER_DB_PATH", "./hid_recorder.db")

    # Get host and port from environment or use defaults
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))

    # Initialize the recorder and session manager
    recorder = Recorder(db_path=db_path)
    session_manager = SessionManager(recorder=recorder)

    # Create the FastAPI app
    app = create_app(session_manager=session_manager)

    # Run the server
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
