import { useRef, useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import './App.css'

type UploadReceipt = {
  id: string
  fileName: string
  contentType: string
  sizeBytes: number
  uploadedAtUtc: string
}

const apiUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:5185'

function App() {
  const fileInput = useRef<HTMLInputElement>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [receipt, setReceipt] = useState<UploadReceipt | null>(null)
  const [error, setError] = useState<string | null>(null)

  function selectFile(event: ChangeEvent<HTMLInputElement>) {
    setSelectedFile(event.target.files?.[0] ?? null)
    setReceipt(null)
    setError(null)
  }

  async function uploadFile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!selectedFile) {
      setError('Choose a file before uploading.')
      return
    }

    setIsUploading(true)
    setError(null)
    setReceipt(null)

    try {
      const data = new FormData()
      data.append('file', selectedFile)
      const response = await fetch(`${apiUrl}/api/uploads`, { method: 'POST', body: data })

      if (!response.ok) {
        const problem = await response.json().catch(() => null)
        throw new Error(problem?.title ?? 'Upload failed. Please try again.')
      }

      setReceipt((await response.json()) as UploadReceipt)
      setSelectedFile(null)
      if (fileInput.current) {
        fileInput.current.value = ''
      }
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : 'Upload failed. Please try again.')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <main className="upload-page">
      <section className="upload-panel" aria-labelledby="page-title">
        <p className="eyebrow">Benchmark upload</p>
        <h1 id="page-title">Store a file</h1>
        <p className="intro">Upload one file. Its metadata is recorded in PostgreSQL and its contents are stored in blob storage.</p>

        <form onSubmit={uploadFile}>
          <label className="file-picker" htmlFor="file">
            <span>Select a file</span>
            <input ref={fileInput} id="file" type="file" onChange={selectFile} />
          </label>
          <p className="file-name" aria-live="polite">{selectedFile?.name ?? 'No file selected'}</p>
          <button type="submit" disabled={isUploading}>
            {isUploading ? 'Uploading...' : 'Upload file'}
          </button>
        </form>

        {error && <p className="message error" role="alert">{error}</p>}
        {receipt && (
          <section className="message success" aria-live="polite">
            <strong>Stored successfully</strong>
            <span>{receipt.fileName}</span>
            <span>{receipt.sizeBytes.toLocaleString()} bytes</span>
            <span>Receipt: {receipt.id}</span>
          </section>
        )}
      </section>
    </main>
  )
}

export default App
