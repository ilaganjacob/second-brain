import { useEffect, useState } from 'react'

type Status = 'checking' | 'ok' | 'down'

function App() {
  const [status, setStatus] = useState<Status>('checking')

  useEffect(() => {
    fetch('/api/health')
      .then((res) => (res.ok ? res.json() : Promise.reject(res)))
      .then((body: { ok: boolean }) => setStatus(body.ok ? 'ok' : 'down'))
      .catch(() => setStatus('down'))
  }, [])

  return (
    <main>
      <h1>Second Brain</h1>
      <p>{status === 'checking' ? 'Checking API…' : status === 'ok' ? 'API ok' : 'API down'}</p>
    </main>
  )
}

export default App
