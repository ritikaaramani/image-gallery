// scripts/start-dev.js
// Usage: node scripts/start-dev.js
// This script: docker-compose up -d --build
// waits for backend to be reachable, runs create_db inside backend container,
// restarts worker, then starts `next dev` in the foreground.

const { spawn } = require('child_process')
const http = require('http')

const BACKEND_URL = process.env.BACKEND_CHECK_URL || 'http://127.0.0.1:8000'
const BACKEND_WAIT_PATH = process.env.BACKEND_WAIT_PATH || '/docs' // fallback to / or /docs
const DOCKER_COMPOSE = process.env.DOCKER_COMPOSE_CMD || 'docker-compose'

function runCmd(cmd, args, opts = {}) {
  return new Promise((resolve, reject) => {
    const p = spawn(cmd, args, { stdio: 'inherit', shell: false, ...opts })
    p.on('error', reject)
    p.on('exit', code => (code === 0 ? resolve() : reject(new Error(`${cmd} ${args.join(' ')} exited ${code}`))))
  })
}

function httpCheck(url, timeout = 2000) {
  return new Promise((resolve) => {
    const req = http.get(url, res => {
      res.resume()
      resolve(res.statusCode >= 200 && res.statusCode < 500)
    })
    req.on('error', () => resolve(false))
    req.setTimeout(timeout, () => { req.destroy(); resolve(false) })
  })
}

async function waitForBackend(url, maxSeconds = 60) {
  const deadline = Date.now() + maxSeconds * 1000
  console.log(`Waiting for backend at ${url} (timeout ${maxSeconds}s)...`)
  while (Date.now() < deadline) {
    try {
      const ok = await httpCheck(url)
      if (ok) {
        console.log('Backend responded.')
        return
      }
    } catch (e) {
      // ignore
    }
    await new Promise(r => setTimeout(r, 1500))
  }
  throw new Error(`Timeout waiting for backend at ${url}`)
}

;(async () => {
  try {
    console.log('1) Starting docker-compose (build & detached)...')
    await runCmd(DOCKER_COMPOSE, ['up', '-d', '--build'])

    // Wait for backend to be reachable (try /docs then /)
    const checkUrls = [
      BACKEND_URL + BACKEND_WAIT_PATH,
      BACKEND_URL + '/'
    ]
    let ok = false
    for (const u of checkUrls) {
      try {
        await waitForBackend(u, 60)
        ok = true
        break
      } catch (e) {
        // try next
      }
    }
    if (!ok) {
      throw new Error('Backend did not become available in time')
    }

    console.log('2) Creating DB tables inside backend container...')
    // Run create_db inside backend container (safe idempotent)
    await runCmd(DOCKER_COMPOSE, ['exec', '-T', 'backend', 'python', '-m', 'backend.create_db'])

    console.log('3) Restarting worker to pick up DB and env changes...')
    await runCmd(DOCKER_COMPOSE, ['restart', 'worker'])

    console.log('4) Starting Next dev server (foreground). Press Ctrl-C to stop.')
    // Spawn next dev and pipe output. We keep the parent process running while next runs.
    const next = spawn('npm', ['run', 'dev'], { stdio: 'inherit', shell: true })

    next.on('exit', code => {
      console.log(`next dev exited with code ${code}. Shutting down docker-compose...`)
      spawn(DOCKER_COMPOSE, ['down'], { stdio: 'inherit', shell: false }).on('exit', () => {
        process.exit(code)
      })
    })

    next.on('error', err => {
      console.error('Failed to start next dev:', err)
      process.exit(1)
    })
  } catch (err) {
    console.error('Error in start-dev script:', err)
    process.exit(1)
  }
})()
