'use client'

import { useCallback, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import styles from './page.module.css'

type KeyValue = { id: number; key: string; value: string }
type BodyMode = 'json' | 'form-data' | 'x-www-form-urlencoded'
type AuthMode = 'none' | 'apiKey'

const methodOptions = ['POST', 'GET', 'PUT', 'PATCH', 'DELETE'] as const
type KeployAuth = { type: 'none' } | { type: 'apiKey'; key: string; value: string }
type KeployPayload = {
  method: (typeof methodOptions)[number]
  url: string
  params: Record<string, string>
  headers: Record<string, string>
  body: unknown
  bodyType: BodyMode
  auth: KeployAuth
}

type KeyValueListProps = {
  items: KeyValue[]
  onChange: (id: number, field: 'key' | 'value', value: string) => void
  onAdd?: () => void
  addLabel?: string
  placeholders?: { key?: string; value?: string }
}

const KeyValueList = ({ items, onChange, onAdd, addLabel = '+ Add', placeholders }: KeyValueListProps) => (
  <>
    {items.map((item) => (
      <div className={styles.kvRow} key={item.id}>
        <input
          className={styles.input}
          value={item.key}
          onChange={(event) => onChange(item.id, 'key', event.target.value)}
          placeholder={placeholders?.key ?? 'Key'}
        />
        <input
          className={styles.input}
          value={item.value}
          onChange={(event) => onChange(item.id, 'value', event.target.value)}
          placeholder={placeholders?.value ?? 'Value'}
        />
      </div>
    ))}
    {onAdd ? (
      <button type="button" className={styles.addButton} onClick={onAdd}>
        {addLabel}
      </button>
    ) : null}
  </>
)

const buildKeyValueMap = (items: KeyValue[]) =>
  items
    .map(({ key, value }) => ({ key: key.trim(), value: value.trim() }))
    .filter(({ key }) => key.length > 0)
    .reduce<Record<string, string>>((acc, { key, value }) => {
      acc[key] = value
      return acc
    }, {})

export default function Home() {
  const [method, setMethod] = useState<(typeof methodOptions)[number]>('POST')
  const [apiUrl, setApiUrl] = useState('https://api.example.com/v1/loans')
  const [params, setParams] = useState<KeyValue[]>([{ id: 1, key: 'tenantId', value: 'abaco' }])
  const [headers, setHeaders] = useState<KeyValue[]>([{
    id: 1,
    key: 'Content-Type',
    value: 'application/json',
  }])
  const [bodyMode, setBodyMode] = useState<BodyMode>('json')
  const [jsonBody, setJsonBody] = useState(
    JSON.stringify({
      applicant: 'Adriana Navarrete',
      amount: 75000,
      currency: 'USD',
      tenorMonths: 36,
    }, null, 2)
  )
  const [formBody, setFormBody] = useState<KeyValue[]>([{ id: 1, key: 'amount', value: '75000' }])
  const [authMode, setAuthMode] = useState<AuthMode>('none')
  const [apiKeyName, setApiKeyName] = useState('x-api-key')
  const [apiKeyValue, setApiKeyValue] = useState('')
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [result, setResult] = useState<string>('Ready to orchestrate Keploy and accelerate QA coverage.')

  const createKeyValueChangeHandler = useCallback(
    (setList: (next: KeyValue[] | ((prev: KeyValue[]) => KeyValue[])) => void) =>
      (id: number, field: 'key' | 'value', value: string) =>
        setList((prev) => prev.map((item) => (item.id === id ? { ...item, [field]: value } : item))),
    []
  )

  const createAddRowHandler = useCallback(
    (setList: (next: KeyValue[] | ((prev: KeyValue[]) => KeyValue[])) => void) => () =>
      setList((prev) => {
        const nextId = Math.max(0, ...prev.map(({ id }) => id)) + 1
        return [...prev, { id: nextId, key: '', value: '' }]
      }),
    []
  )

  const onParamsChange = useMemo(() => createKeyValueChangeHandler(setParams), [createKeyValueChangeHandler])
  const onHeadersChange = useMemo(() => createKeyValueChangeHandler(setHeaders), [createKeyValueChangeHandler])
  const onFormBodyChange = useMemo(() => createKeyValueChangeHandler(setFormBody), [createKeyValueChangeHandler])

  const addParamRow = useMemo(() => createAddRowHandler(setParams), [createAddRowHandler])
  const addHeaderRow = useMemo(() => createAddRowHandler(setHeaders), [createAddRowHandler])
  const addFormRow = useMemo(() => createAddRowHandler(setFormBody), [createAddRowHandler])

  const cleanKeyValue = useCallback((values: KeyValue[]) => buildKeyValueMap(values), [])

  const parseBody = useCallback(() => {
    if (bodyMode === 'json') {
      if (!jsonBody.trim()) return { body: {}, error: null }
      try {
        return { body: JSON.parse(jsonBody), error: null }
      } catch {
        return { body: null, error: 'Body must be valid JSON to reach Keploy securely.' }
      }
    }

    return { body: cleanKeyValue(formBody), error: null }
  }, [bodyMode, cleanKeyValue, formBody, jsonBody])

  const payloadPreview = useMemo(() => {
    const { body, error } = parseBody()
    if (error) return { payload: null, error }

    const sanitizedHeaders = cleanKeyValue(headers)
    const requestHeaders = {
      ...sanitizedHeaders,
      ...(authMode === 'apiKey' && apiKeyName.trim()
        ? { [apiKeyName.trim()]: apiKeyValue.trim() }
        : {}),
    }

    return {
      payload: {
        method,
        url: apiUrl,
        params: cleanKeyValue(params),
        headers: requestHeaders,
        body,
        bodyType: bodyMode,
        auth: authMode === 'apiKey'
          ? { type: 'apiKey', key: apiKeyName, value: apiKeyValue }
          : { type: 'none' },
      },
      error: null,
    }
  }, [apiKeyName, apiKeyValue, apiUrl, authMode, bodyMode, cleanKeyValue, headers, method, params, parseBody])

  const previewText = payloadPreview.error
    ? payloadPreview.error
    : payloadPreview.payload
      ? JSON.stringify(payloadPreview.payload, null, 2)
      : ''

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setStatus('loading')
    setResult('Connecting to Keploy...')

    const { body: parsedBody, error } = parseBody()

    if (error) {
      setStatus('error')
      setResult(error)
      return
    }

    const sanitizedHeaders = cleanKeyValue(headers)
    const requestHeaders = {
      ...sanitizedHeaders,
      ...(authMode === 'apiKey' && apiKeyName.trim()
        ? { [apiKeyName.trim()]: apiKeyValue.trim() }
        : {}),
    }

    const payload: KeployPayload = {
      method,
      url: apiUrl,
      params: cleanKeyValue(params),
      headers: requestHeaders,
      body: parsedBody,
      bodyType: bodyMode,
      auth: authMode === 'apiKey'
        ? { type: 'apiKey', key: apiKeyName, value: apiKeyValue }
        : { type: 'none' },
    }

    let response: Response
    try {
      response = await fetch('https://app.keploy.io/api-testing/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
    } catch {
      setStatus('error')
      setResult('Unable to reach Keploy. Check connectivity or proxy settings and try again.')
      return
    }

    const contentType = response.headers.get('content-type') || ''
    let text: string

    if (contentType.includes('application/json')) {
      try {
        text = JSON.stringify(await response.json(), null, 2)
      } catch {
        const fallbackText = await response.text()
        setStatus('error')
        setResult(`Keploy returned an unreadable JSON response. Raw response: ${fallbackText || 'Empty body.'}`)
        return
      }
    } else {
      text = await response.text()
    }

    if (!response.ok) {
      setStatus('error')
      setResult(`Keploy responded with ${response.status}: ${text}`)
      return
    }

    setStatus('success')
    setResult(text || 'Keploy returned an empty response. Validate your request details and retry.')
  }

  return (
    <div className={styles.page}>
      <div className={styles.gridOverlay} />
      <main className={styles.main}>
        <section className={styles.hero}>
          <div>
            <p className={styles.badge}>Fintech-grade QA · Keploy x ABACO</p>
            <h1>Generate API Test Scenarios at warp speed.</h1>
            <p className={styles.lead}>
              Plug your endpoint, enrich headers and auth, and let Keploy craft deterministic scenarios for every critical workflow.
              Built for growth teams who need bulletproof reliability and audit-ready evidence.
            </p>
            <div className={styles.pillRow}>
              <span className={styles.pill}>Zero-trust ready</span>
              <span className={styles.pill}>Deterministic mocks</span>
              <span className={styles.pill}>Traceable KPIs</span>
            </div>
          </div>
          <div className={styles.scorecard}>
            <div>
              <p className={styles.scoreLabel}>Coverage velocity</p>
              <p className={styles.scoreValue}>11x</p>
              <p className={styles.scoreHint}>vs. manual test authoring</p>
            </div>
            <div className={styles.divider} />
            <div>
              <p className={styles.scoreLabel}>Rollback risk</p>
              <p className={styles.scoreValue}>↓72%</p>
              <p className={styles.scoreHint}>with auto-generated mocks</p>
            </div>
            <div className={styles.divider} />
            <div>
              <p className={styles.scoreLabel}>Time-to-signal</p>
              <p className={styles.scoreValue}>Minutes</p>
              <p className={styles.scoreHint}>instrument once, reuse everywhere</p>
            </div>
          </div>
        </section>

        <section className={styles.panel}>
          <div className={styles.panelHeader}>
            <div>
              <p className={styles.eyebrow}>Configure API Request</p>
              <h2>Orchestrate Keploy in one secure request.</h2>
              <p className={styles.panelCopy}>
                We parse the endpoint instantly and prepare a replay-ready payload. Toggle method, headers, params, and body type to
                adapt to fintech-grade APIs without losing observability.
              </p>
            </div>
            <a className={styles.link} href="https://keploy.io" target="_blank" rel="noopener noreferrer">
              keploy.io
            </a>
          </div>

          <form className={styles.form} onSubmit={handleSubmit}>
            <div className={styles.row}>
              <label className={styles.field}>Method</label>
              <div className={styles.methods}>
                {methodOptions.map((option) => (
                  <button
                    type="button"
                    key={option}
                    aria-pressed={method === option}
                    className={`${styles.methodButton} ${method === option ? styles.methodActive : ''}`}
                    onClick={() => setMethod(option)}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>

            <div className={styles.row}>
              <label className={styles.field}>API URL</label>
              <input
                type="url"
                className={styles.input}
                required
                value={apiUrl}
                onChange={(event) => setApiUrl(event.target.value)}
                placeholder="https://app.keploy.io/api-testing/generate"
              />
            </div>

            <div className={styles.grid}> 
              <div className={styles.card}>
                <div className={styles.cardHeader}>
                  <p className={styles.eyebrow}>Params</p>
                  <button type="button" className={styles.addButton} onClick={addParamRow}>
                    + Add
                  </button>
                </div>
                <KeyValueList items={params} onChange={onParamsChange} />
              </div>

              <div className={styles.card}>
                <div className={styles.cardHeader}>
                  <p className={styles.eyebrow}>Headers</p>
                  <button type="button" className={styles.addButton} onClick={addHeaderRow}>
                    + Add
                  </button>
                </div>
                <KeyValueList items={headers} onChange={onHeadersChange} />
              </div>
            </div>

            <div className={styles.grid}> 
              <div className={styles.card}>
                <div className={styles.cardHeader}>
                  <p className={styles.eyebrow}>Body</p>
                  <div className={styles.tags}>
                    {(['json', 'form-data', 'x-www-form-urlencoded'] as BodyMode[]).map((mode) => (
                      <button
                        type="button"
                        key={mode}
                        aria-pressed={bodyMode === mode}
                        className={`${styles.tag} ${bodyMode === mode ? styles.tagActive : ''}`}
                        onClick={() => setBodyMode(mode)}
                      >
                        {mode}
                      </button>
                    ))}
                  </div>
                </div>
                {bodyMode === 'json' && (
                  <textarea
                    className={styles.textarea}
                    value={jsonBody}
                    onChange={(event) => setJsonBody(event.target.value)}
                    placeholder='{"amount":75000}'
                    rows={10}
                  />
                )}
                {bodyMode !== 'json' && (
                  <div className={styles.kvCol}>
                    <KeyValueList
                      items={formBody}
                      onChange={onFormBodyChange}
                      onAdd={addFormRow}
                      addLabel="+ Add field"
                      placeholders={{ key: 'Key', value: 'Value' }}
                    />
                  </div>
                )}
              </div>

              <div className={styles.card}>
                <div className={styles.cardHeader}>
                  <p className={styles.eyebrow}>Auth</p>
                  <div className={styles.tags}>
                    {(['none', 'apiKey'] as AuthMode[]).map((mode) => (
                      <button
                        type="button"
                        key={mode}
                        aria-pressed={authMode === mode}
                        className={`${styles.tag} ${authMode === mode ? styles.tagActive : ''}`}
                        onClick={() => setAuthMode(mode)}
                      >
                        {mode === 'none' ? 'None' : 'API Key'}
                      </button>
                    ))}
                  </div>
                </div>
                {authMode === 'apiKey' && (
                  <div className={styles.kvCol}>
                    <input
                      className={styles.input}
                      value={apiKeyName}
                      onChange={(event) => setApiKeyName(event.target.value)}
                      placeholder="Header name"
                    />
                    <input
                      className={styles.input}
                      value={apiKeyValue}
                      onChange={(event) => setApiKeyValue(event.target.value)}
                      placeholder="Header value"
                    />
                  </div>
                )}
                <p className={styles.helper}>
                  Keploy supports key-based auth for internal and partner APIs. Keys are only used for this request and sent
                  directly to Keploy without being stored.
                </p>
              </div>
            </div>

            <div className={styles.actions}>
              <div>
                <p className={styles.eyebrow}>Preview payload</p>
                <pre className={styles.preview}>{previewText}</pre>
              </div>
              <button className={styles.cta} type="submit" disabled={status === 'loading'}>
                {status === 'loading' ? 'Generating with Keploy...' : 'Generate API Test Scenarios'}
              </button>
            </div>
          </form>
        </section>

        <section className={styles.results}>
          <div>
            <p className={styles.eyebrow}>Response & Observability</p>
            <h3>Trace every scenario with audit-ready context.</h3>
            <p className={styles.panelCopy}>
              Keploy returns deterministic captures you can replay across staging, UAT, or production-simulated environments.
              Export them into CI pipelines, GitHub workflows, or SonarCloud quality gates to protect revenue-critical journeys.
            </p>
          </div>
          <div className={`${styles.card} ${styles.responseCard}`}>
            <p className={styles.responseLabel}>Live status: {status.toUpperCase()}</p>
            <pre className={styles.response}>{result}</pre>
          </div>
        </section>
      </main>
    </div>
  )
}
