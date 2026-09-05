import { createApp } from './app.js'
import { fileURLToPath } from 'node:url'

const port = process.env.PORT || 3001
const staticDir = fileURLToPath(new URL('../dist', import.meta.url))
createApp(undefined, { staticDir }).listen(port, () => console.log(`Application listening on http://localhost:${port}`))
