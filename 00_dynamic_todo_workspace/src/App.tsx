import { FormEvent, useCallback, useEffect, useState } from 'react'

type Priority = 'low' | 'medium' | 'high'
type Task = { id: number; title: string; priority: Priority; dueDate: string | null; completed: boolean }
type Draft = { title: string; priority: Priority; dueDate: string }
const empty: Draft = { title: '', priority: 'medium', dueDate: '' }

async function api(path: string, options?: RequestInit) {
  const response = await fetch(`/api${path}`, { headers: { 'Content-Type': 'application/json' }, ...options })
  if (!response.ok) { const body = await response.json().catch(() => ({})); throw new Error(body.error || 'Request failed. Please try again.') }
  return response.status === 204 ? null : response.json()
}

export default function App() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [draft, setDraft] = useState<Draft>(empty)
  const [editing, setEditing] = useState<number | null>(null)
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('all')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    try { setLoading(true); setError(''); setTasks(await api(`/tasks?status=${filter}&search=${encodeURIComponent(search)}`)) }
    catch (err) { setError((err as Error).message) }
    finally { setLoading(false) }
  }, [filter, search])
  useEffect(() => { const timer = setTimeout(load, 200); return () => clearTimeout(timer) }, [load])

  async function submit(event: FormEvent) {
    event.preventDefault(); setError('')
    if (!draft.title.trim()) return setError('Enter a task title.')
    try {
      await api(editing ? `/tasks/${editing}` : '/tasks', { method: editing ? 'PUT' : 'POST', body: JSON.stringify(draft) })
      setDraft(empty); setEditing(null); await load()
    } catch (err) { setError((err as Error).message) }
  }
  function beginEdit(task: Task) { setEditing(task.id); setDraft({ title: task.title, priority: task.priority, dueDate: task.dueDate || '' }); window.scrollTo({ top: 0, behavior: 'smooth' }) }
  async function mutate(path: string, options: RequestInit) { try { setError(''); await api(path, options); await load() } catch (err) { setError((err as Error).message) } }

  return <main>
    <header><span className="eyebrow">FOCUS WORKSPACE</span><h1>Make room for what matters.</h1><p>Capture your next move, set its weight, and keep momentum visible.</p></header>
    <section className="panel composer" aria-labelledby="composer-title">
      <h2 id="composer-title">{editing ? 'Edit task' : 'Add a task'}</h2>
      <form onSubmit={submit}>
        <label className="title-field">Task title<input autoFocus maxLength={120} value={draft.title} onChange={e => setDraft({ ...draft, title: e.target.value })} placeholder="What needs doing?" /></label>
        <label>Priority<select value={draft.priority} onChange={e => setDraft({ ...draft, priority: e.target.value as Priority })}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option></select></label>
        <label>Due date<input type="date" value={draft.dueDate} onChange={e => setDraft({ ...draft, dueDate: e.target.value })} /></label>
        <button className="primary" type="submit">{editing ? 'Save changes' : 'Add task'} <span aria-hidden="true">→</span></button>
        {editing && <button type="button" className="cancel" onClick={() => { setEditing(null); setDraft(empty) }}>Cancel</button>}
      </form>
    </section>
    {error && <div className="error" role="alert">{error}</div>}
    <section className="tasks" aria-labelledby="tasks-title">
      <div className="toolbar"><div><span className="eyebrow">YOUR LIST</span><h2 id="tasks-title">Tasks <small>{tasks.length}</small></h2></div><label className="search"><span className="sr-only">Search tasks</span><input type="search" placeholder="Search tasks…" value={search} onChange={e => setSearch(e.target.value)} /></label></div>
      <div className="filters" aria-label="Filter tasks">{['all','active','completed'].map(value => <button key={value} aria-pressed={filter === value} onClick={() => setFilter(value)}>{value}</button>)}</div>
      {loading ? <p className="empty">Loading tasks…</p> : tasks.length === 0 ? <div className="empty"><strong>No tasks here.</strong><span>Add one above or change your filters.</span></div> : <ul>{tasks.map(task => <li key={task.id} className={task.completed ? 'done' : ''}>
        <button className="check" aria-label={`${task.completed ? 'Mark active' : 'Complete'}: ${task.title}`} onClick={() => mutate(`/tasks/${task.id}`, { method: 'PUT', body: JSON.stringify({ completed: !task.completed }) })}>{task.completed ? '✓' : ''}</button>
        <div className="task-copy"><strong>{task.title}</strong><span><i className={task.priority}>{task.priority}</i>{task.dueDate && <>Due <time dateTime={task.dueDate}>{new Date(`${task.dueDate}T00:00:00`).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}</time></>}</span></div>
        <div className="actions"><button onClick={() => beginEdit(task)}>Edit</button><button className="delete" onClick={() => mutate(`/tasks/${task.id}`, { method: 'DELETE' })}>Delete</button></div>
      </li>)}</ul>}
    </section>
  </main>
}
