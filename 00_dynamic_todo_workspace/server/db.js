import { DatabaseSync } from 'node:sqlite'

export function createDatabase(path = 'tasks.sqlite') {
  const db = new DatabaseSync(path)
  db.exec(`CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    priority TEXT NOT NULL CHECK(priority IN ('low','medium','high')),
    due_date TEXT,
    completed INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  )`)
  return db
}
