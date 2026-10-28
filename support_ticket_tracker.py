"""Support ticket tracker module.

Provides functionality to create, assign, update, search, and persist
customer support tickets.
"""

import json
import logging
import os

TICKETS = {}


# pylint: disable=too-many-arguments,too-many-positional-arguments
def create_ticket(
    title,
    description,
    reporter,
    priority="medium",
    category="general",
    audit_log=None,
):
    """Create a new support ticket and record an audit log entry."""
    if not title:
        return None
    if audit_log is None:
        audit_log = []
    ticket_id = str(len(TICKETS) + 1)
    ticket = {
        "id": ticket_id,
        "title": title,
        "description": description,
        "priority": priority,
        "category": category,
        "status": "open",
        "reporter": reporter,
        "assignee": None,
    }
    TICKETS[ticket_id] = ticket
    audit_log.append(f"Created ticket {ticket_id} for {reporter}")
    return ticket


def assign_ticket(ticket_id, agent, notify=False):
    """Assign a ticket to an agent and optionally send notification."""
    try:
        TICKETS[ticket_id]["assignee"] = agent
        if notify:
            logging.info(
                "Notification sent for ticket %s assigned to %s",
                ticket_id,
                agent,
            )
        return True
    except KeyError:
        logging.warning("Ticket %s not found for assignment", ticket_id)
        return False


def update_status(ticket_id, status):
    """Update the status of a specific ticket."""
    TICKETS[ticket_id]["status"] = status
    return TICKETS[ticket_id]


def search_tickets(status=None, priority=None):
    """Search tickets by status and/or priority."""
    r = []
    for t in TICKETS.values():
        if status is not None and t["status"] != status:
            continue
        if priority and t["priority"] != priority:
            continue
        r.append(t)
    return r


def save_tickets(path="tickets.json"):
    """Save all tickets to a JSON file."""
    with open(path, "w", encoding="utf-8") as file:
        file.write(json.dumps(TICKETS))


def load_tickets(path="tickets.json"):
    """Load tickets from a JSON file into memory."""
    with open(path, "r", encoding="utf-8") as file:
        data = json.loads(file.read())
    TICKETS.clear()
    TICKETS.update(data)


def print_ticket_report():
    """Display a summary report of all registered tickets."""
    print("Support Tickets")
    if not TICKETS:
        print("No tickets yet")
    for ticket_id, ticket in TICKETS.items():
        print(
            ticket_id,
            ticket["title"],
            ticket["status"],
        )


def close_ticket(ticket_id):
    """Close an existing ticket by setting its status to closed."""
    TICKETS[ticket_id]["status"] = "closed"


# Backwards compatibility alias
closeTicket = close_ticket  # pylint: disable=invalid-name


def is_open(ticket_id):
    """Check whether a ticket is currently open or in progress."""
    return TICKETS[ticket_id]["status"] in ("open", "in_progress")


def main():
    """Execute sample workflow demonstrating ticket management."""
    logging.basicConfig(level=logging.INFO)
    create_ticket(
        "Cannot sign in", "Password reset link fails", "alex@example.com"
    )
    create_ticket(
        "Billing question", "Charged twice", "lee@example.com", "high"
    )
    assign_ticket("1", "agent-01")
    update_status("1", "in_progress")
    print_ticket_report()
    logging.info("Tickets created: %d", len(TICKETS))
    print("Ticket 1 open?", is_open("1"))
    ticket_id = input("Ticket id to close (Enter to skip): ")
    if ticket_id:
        close_ticket(ticket_id)
    save_tickets()
    if os.environ.get("RUN_UNSAFE_DEMO") == "1":
        print("unsafe demo")


if __name__ == "__main__":
    main()
