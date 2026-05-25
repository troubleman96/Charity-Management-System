# Communications App

The `communications` application provides an internal messaging system and a unified logging interface for external communications (emails).

## Key Components

### Models
- **`Message`**: Internal staff-to-staff messaging. Contains `sender`, `recipient`, `subject`, `body`, and an `is_read` boolean flag.
- **`Notification`**: System-generated alerts (e.g., "New Assistance Request Created").
- **`EmailLog`**: Since CharityOS relies on email for receipts and updates, every external email sent by the system (via Celery or otherwise) should be logged here. It tracks `to_email`, `subject`, `status` (sent/failed), and an `error_message` if applicable.

### Views (`views.py`)
- **`InboxView`**: Displays a paginated list of `Message` objects where the current user is the `recipient`.
- **`ComposeMessageView`**: Allows staff to search for other users and send an internal message.

## Usage Rule
Do not use this app to send public marketing blasts. It is designed for transactional logging and internal operational communication.
