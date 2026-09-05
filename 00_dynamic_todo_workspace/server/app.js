import express from 'express'
import { createDatabase } from './db.js'

const priorities = new Set(['low', 'medium', 'high'])

function validate(body) {
  const title = typeof body.title === 'string' ? body.title.trim() : ''
  if (!title || title.length > 120) return 'Title must be between 1 and 120 characters.'
  if (!priorities.has(body.priority)) return 'Priority must be low, medium, or high.'
  if (body.dueDate && !/^\d{4}-\d{2}-\d{2}$/.test(body.dueDate)) return 'Due date must use YYYY-MM-DD.'
  return null
}

export function createApp(db = createDatabase(), { staticDir } = {}) {
  const app = express()
  app.use(express.json())

  app.get('/api/health', (_req, res) => res.json({ status: 'ok' }))
  app.get('/api/tasks', (req, res) => {
    const status = ['active', 'completed'].includes(req.query.status) ? req.query.status : 'all'
    const search = typeof req.query.search === 'string' ? req.query.search.trim() : ''
    const clauses = []; const params = []
    if (status !== 'all') { clauses.push('completed = ?'); params.push(status === 'completed' ? 1 : 0) }
    if (search) { clauses.push('title LIKE ?'); params.push(`%${search}%`) }
    const where = clauses.length ? `WHERE ${clauses.join(' AND ')}` : ''
    const tasks = db.prepare(`SELECT id,title,priority,due_date AS dueDate,completed,created_at AS createdAt FROM tasks ${where} ORDER BY completed, created_at DESC`).all(...params)
    res.json(tasks.map(task => ({ ...task, completed: Boolean(task.completed) })))
  })
  app.post('/api/tasks', (req, res) => {
    const error = validate(req.body)
    if (error) return res.status(400).json({ error })
    const { title, priority, dueDate = null } = req.body
    const result = db.prepare('INSERT INTO tasks (title,priority,due_date) VALUES (?,?,?)').run(title.trim(), priority, dueDate || null)
    const task = db.prepare('SELECT id,title,priority,due_date AS dueDate,completed,created_at AS createdAt FROM tasks WHERE id=?').get(result.lastInsertRowid)
    res.status(201).json({ ...task, completed: false })
  })
  app.put('/api/tasks/:id', (req, res) => {
    const current = db.prepare('SELECT * FROM tasks WHERE id=?').get(req.params.id)
    if (!current) return res.status(404).json({ error: 'Task not found.' })
    const next = {
      title: req.body.title ?? current.title,
      priority: req.body.priority ?? current.priority,
      dueDate: req.body.dueDate === undefined ? current.due_date : req.body.dueDate,
      completed: req.body.completed === undefined ? Boolean(current.completed) : req.body.completed,
    }
    const error = validate(next)
    if (error || typeof next.completed !== 'boolean') return res.status(400).json({ error: error || 'Completed must be a boolean.' })
    db.prepare('UPDATE tasks SET title=?,priority=?,due_date=?,completed=? WHERE id=?').run(next.title.trim(), next.priority, next.dueDate || null, next.completed ? 1 : 0, req.params.id)
    res.json({ id: Number(req.params.id), ...next, title: next.title.trim(), dueDate: next.dueDate || null })
  })
  app.delete('/api/tasks/:id', (req, res) => {
    const result = db.prepare('DELETE FROM tasks WHERE id=?').run(req.params.id)
    if (!result.changes) return res.status(404).json({ error: 'Task not found.' })
    res.status(204).end()
  })
  if (staticDir) app.use(express.static(staticDir))
  app.use((error, _req, res, _next) => {
    if (error instanceof SyntaxError && 'body' in error) return res.status(400).json({ error: 'Request body must be valid JSON.' })
    console.error(error)
    res.status(500).json({ error: 'Something went wrong.' })
  })
  return app
}
