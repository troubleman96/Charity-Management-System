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

## URLs

```
/communications/inbox/                  → Inbox (InboxView)
/communications/compose/                → Compose new message
/communications/message/<pk>/           → Read a message (marks as read)
/communications/notifications/          → Notification list
/communications/notifications/<pk>/read/→ Mark notification as read
/communications/notifications/read-all/ → Mark all read (HTMX endpoint)
```

## Templates

| Template | Status | Description |
|----------|--------|-------------|
| `communications/inbox.html` | ✅ Complete | Two-panel inbox with sent messages sidebar |
| `communications/message_detail.html` | ✅ Complete | Full message view |
| `communications/compose.html` | ✅ Complete | Compose form (staff/admin recipients only) |
| `communications/notifications.html` | ✅ Complete | Notification list with mark-as-read |

## Implementation Status

| Component | Status |
|-----------|--------|
| Message model | ✅ Complete |
| Notification model | ✅ Complete |
| EmailLog model | ✅ Complete |
| Inbox / message views | ✅ Complete |
| Notification views | ✅ Complete |
| HTMX mark-all-read | ✅ Complete |
| All templates | ✅ Complete |
| Django admin | ✅ Complete |

## Usage Rule
Do not use this app to send public marketing blasts. It is designed for transactional logging and internal operational communication.
