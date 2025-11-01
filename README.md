# input-capture-api

Web API for controlling HID recording sessions using the hid-recorder library.

## Overview

This application provides a REST API to remotely control HID (Human Interface Device) recording sessions. You can start and stop recording sessions, and retrieve recorded events from any device on your network.

When a recording session starts, the application launches HIDInterceptor in the background to continuously capture all input events (keyboard, mouse, etc.) from `/dev/input/event*` devices until the session ends.

## Features

- Start recording sessions with custom names and metadata
- End recording sessions by session ID
- Retrieve recorded events for a specific session
- List all recording sessions
- Get details of a specific session
- Continuous background event capture using HIDInterceptor

## System Requirements

- **Platform**: Linux with evdev support
- **Python**: 3.10 or later
- **Permissions**: Access to `/dev/input/event*` devices (see Permissions section below)

## Installation

1. Install dependencies using `uv`:

```bash
uv sync
```

2. Run the application:

```bash
uv run python -m input_capture_api.main
```

The API will be available at `http://127.0.0.1:8000`.

If you want to change the host or port, you can set the `API_HOST` and `API_PORT` environment variables:

```bash
export API_HOST=<host>
export API_PORT=<port>
uv run python -m input_capture_api.main
```

## Configuration

You can configure the database path using the `HID_RECORDER_DB_PATH` environment variable:

```bash
export HID_RECORDER_DB_PATH=/path/to/database.db
uv run python -m input_capture_api.main
```

## Permissions

The application requires read access to `/dev/input/event*` devices. You have two options:

### Option 1: Run with root privileges (not recommended for production)

```bash
sudo uv run python -m input_capture_api.main
```

### Option 2: Add user to input group (recommended)

Most Linux distributions have `/dev/input/event*` devices owned by the `input` group. Simply add your user to this group:

```bash
sudo usermod -a -G input $USER
```

Then log out and log back in for the group change to take effect. After that, you can run the application without root privileges.

## How It Works

1. **Session Start**: When you create a session via `POST /sessions`, the application:
   - Creates a session record in the database
   - Starts HIDInterceptor in a background async task
   - Begins capturing all input events from HID devices

2. **Event Capture**: HIDInterceptor continuously monitors `/dev/input/event*` and records:
   - Keyboard events (key presses/releases)
   - Mouse events (movements, clicks, scrolls)
   - Other HID device events

3. **Session End**: When you end a session via `PATCH /sessions/{id}`, the application:
   - Stops the HIDInterceptor background task
   - Closes the recording session
   - All captured events remain in the database

**Important**: During active recording sessions, the application captures ALL input from monitored devices. On some systems, this may interfere with standard Ctrl+C termination. Use SSH or send SIGTERM externally if needed.

## API Endpoints

### Start a recording session

```bash
POST /sessions
Content-Type: application/json

{
  "name": "my-session",
  "metadata": {
    "description": "Test session",
    "user": "alice"
  }
}
```

Response:

```json
{
  "id": "session-123",
  "name": "my-session"
}
```

### End a recording session

```bash
PATCH /sessions/{session_id}
Content-Type: application/json

{
  "status": "ended"
}
```

Response:

```json
{
  "status": "ended"
}
```

### Get events for a session

```bash
GET /sessions/{session_id}/events
```

Response:

```json
{
  "events": [
    {
      "device": "/dev/input/event0",
      "code": 30,
      "value": 1,
      "timestamp": 1234567890.123
    }
  ]
}
```

### List all sessions

```bash
GET /sessions
```

Response:

```json
{
  "sessions": [
    {
      "id": "session-1",
      "name": "session-1"
    }
  ]
}
```

### Get a specific session

```bash
GET /sessions/{session_id}
```

Response:

```json
{
  "id": "session-123",
  "name": "my-session"
}
```

## Development

### Running tests

```bash
uv run pytest
```

### Code quality checks

```bash
uv run ruff check src/ tests/
uv run mypy src/
```

## License

See LICENSE file for details.