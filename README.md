# Ticketing System

A full-stack customer support ticketing system built with Django REST Framework, Vue.js, and PostgreSQL. Built as part of the Paylik intern onboarding program.

---

## Stack

- **Backend** — Django REST Framework
- **Frontend** — Vue.js + PrimeVue
- **Database** — PostgreSQL
- **Auth** — JWT (access + refresh tokens)
- **Infrastructure** — Docker + Docker Compose

---

## Getting Started

### Prerequisites

- Docker and Docker Compose installed on your machine

### Setup

1. Clone the repository
```bash
   git clone https://github.com/BOUKHAL/ticketing-system.git
   cd ticketing-system
```

2. Create the environment file
```bash
   cp backend/.env.example backend/.env
```

   Then open `backend/.env` and fill in your values:
```
   POSTGRES_DB=ticketing
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=yourpassword
   SECRET_KEY=your-django-secret-key
   DEBUG=True
```

3. Start the project
```bash
   docker compose up --build
```

4. Create an admin account
```bash
   docker exec -it ticketing_backend python manage.py createsuperuser
```

Once everything is running:

- Frontend → http://localhost:5173
- Backend API → http://localhost:8000/api

---

## Test Accounts

The admin account is created via `createsuperuser`. Agent and customer accounts can be created through the Admin Panel inside the app or via the API.

---

## Features

- Role-based access control (customer, agent, admin)
- JWT authentication with automatic token refresh
- Ticket creation, assignment, and status management
- Markdown support for ticket descriptions
- Real-time message polling on ticket detail
- Clean, responsive UI with PrimeVue

---

## Permissions Overview

| Action | Customer | Agent | Admin |
|---|---|---|---|
| Create ticket | ✅ | ❌ | ✅ |
| View own tickets | ✅ | ❌ | ✅ |
| View all open tickets | ❌ | ✅ | ✅ |
| Update ticket status | ❌ | ✅ | ✅ |
| Assign tickets | ❌ | ❌ | ✅ |
| Manage users | ❌ | ❌ | ✅ |
| Delete tickets | ❌ | ❌ | ✅ |

---

## What I'd Improve With More Time

**Performance** — I would implement Redis as a caching layer for JWT
blacklisting and session validation. This would reduce database load by
avoiding a PostgreSQL lookup on every authenticated request, improving API
response times at scale.

**Real-time updates** — The current message system uses polling every 5
seconds. With more time I would replace this with WebSockets using
Django Channels, which would give instant message delivery without the
unnecessary network requests when nothing has changed.

**Agent ticket visibility** — Agents can currently only see `open` tickets.
Once they update a ticket to `in_progress` they lose access to it in their
list. A better approach would be to show agents all tickets assigned to them
regardless of status, so they can track the full lifecycle of tickets they're
handling without losing context.

---