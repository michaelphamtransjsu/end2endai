import assert from 'node:assert/strict'
import { after, beforeEach, describe, test } from 'node:test'
import request from 'supertest'
import { createApp } from './app.js'
import { createDatabase } from './db.js'

const db = createDatabase(':memory:')
const app = createApp(db)
beforeEach(() => db.exec('DELETE FROM tasks'))
after(() => db.close())

describe('task API', () => {
  test('creates, lists, updates, filters, searches, and deletes a task', async () => {
    const created = await request(app).post('/api/tasks').send({ title: 'Ship MVP', priority: 'high', dueDate: '2026-09-05' }).expect(201)
    assert.equal(created.body.title, 'Ship MVP')
    await request(app).put(`/api/tasks/${created.body.id}`).send({ completed: true }).expect(200)
    const filtered = await request(app).get('/api/tasks?status=completed&search=Ship').expect(200)
    assert.equal(filtered.body.length, 1)
    assert.equal(filtered.body[0].completed, true)
    await request(app).delete(`/api/tasks/${created.body.id}`).expect(204)
    assert.deepEqual((await request(app).get('/api/tasks')).body, [])
  })
  test('returns useful validation and missing-task errors', async () => {
    const invalid = await request(app).post('/api/tasks').send({ title: '', priority: 'urgent' }).expect(400)
    assert.match(invalid.body.error, /Title/)
    await request(app).put('/api/tasks/404').send({ completed: true }).expect(404)
    const malformed = await request(app).post('/api/tasks').set('Content-Type', 'application/json').send('{').expect(400)
    assert.match(malformed.body.error, /valid JSON/)
  })
})
