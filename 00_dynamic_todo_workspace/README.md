# Dynamic Todo Workspace

A focused task-management MVP with a React/TypeScript interface, Express API, and local SQLite persistence. It supports creating, editing, completing, deleting, searching, and filtering tasks, plus priorities and due dates. No account or external service is required.

## Requirements

- Node.js 24 or newer (the backend uses the built-in `node:sqlite` module)
- npm 11 or newer

## Install

From this directory:

```bash
npm install
```

## Start for development

```bash
npm run dev
```

Open <http://localhost:5173>. Vite proxies `/api` requests to the API at <http://localhost:3001>. Tasks are stored in `tasks.sqlite` in this directory; that local database is gitignored.

## Test

Run all backend and frontend tests:

```bash
npm test
```

Or run the suites separately:

```bash
npm run test:backend
npm run test:frontend
```

## Build

```bash
npm run build
```

The generated `dist/` directory is intentionally ignored.

## Start the built application

```bash
npm run build
npm start
```

Open <http://localhost:3001>. Express serves both the built frontend and the API. Override the port with, for example, `PORT=4000 npm start`.

## Training or analysis

This application is not a machine-learning or data-science project, so it has no training or analysis step and no training command.

## API summary

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/tasks?status=all&search=` | List/filter/search tasks |
| `POST` | `/api/tasks` | Create a task |
| `PUT` | `/api/tasks/:id` | Edit fields or completion state |
| `DELETE` | `/api/tasks/:id` | Delete a task |

Task titles are required and limited to 120 characters. Priorities are `low`, `medium`, or `high`; due dates use `YYYY-MM-DD`.
