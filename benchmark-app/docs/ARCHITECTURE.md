# Benchmark Upload App Architecture

## System Purpose
This system is a benchmark-grade, intentionally small full-stack file upload application used to validate and measure AI story-to-code workflows.

It solves a concrete workflow: a user selects a local file in a browser UI, uploads it through an HTTP API, and receives a receipt proving the upload was stored.

Domain-specific behavior:
- Document/file type: arbitrary binary or text files (no domain-specific schema enforced by code).
- Primary users: developers, QA engineers, and AI-agent pipelines that need a deterministic end-to-end upload target.
- Operational context: local/dev benchmark runs where predictable infrastructure (PostgreSQL + Azurite) is required.
- Outcome: file bytes are persisted in blob storage; file metadata is persisted in PostgreSQL.

## Architecture Overview
High-level style:
- Distributed 4-service development topology: web client + API + PostgreSQL + Azurite.
- API is a small layered monolith (presentation/controller + persistence/integration in one process).
- Request/response synchronous architecture (no asynchronous messaging, no background workers).

Major structural boundaries:
- Presentation boundary (browser React SPA) in `web/`.
- HTTP/API boundary (ASP.NET Core) in `api/`.
- Relational metadata persistence boundary (PostgreSQL).
- Blob content persistence boundary (Azurite emulating Azure Blob Storage).

Runtime topology:
- `web` runs in browser via Vite dev server or static build.
- `api` runs as ASP.NET Core process.
- `postgres` and `azurite` run as Docker services from `compose.yaml`.

## Components

### 1) Web SPA (`web/`)
Name:
- React Upload Client

Responsibility:
- Renders upload UI.
- Captures file input and performs upload request.
- Displays error state or success receipt returned by API.

Depends on:
- Browser Fetch API.
- API endpoint at `/api/uploads` during local Vite development, proxied to `VITE_API_URL` or `http://localhost:5192` by default.
- React runtime.

Depended on by:
- Human user interaction only (no internal callers).

Key classes/entry points:
- `web/src/main.tsx` (React bootstrap).
- `web/src/App.tsx` (`App` component containing upload logic).

### 2) API Host (`api/Program.cs`)
Name:
- ASP.NET Core API Composition Root

Responsibility:
- Reads configuration and connection strings.
- Registers DI services (DbContext, BlobServiceClient, controllers, CORS).
- Initializes database schema via `EnsureCreatedAsync()` at startup.
- Maps controller routes and starts HTTP server.

Depends on:
- ASP.NET Core hosting.
- Entity Framework Core + Npgsql provider.
- Azure Blob SDK client.
- Configuration files/environment.

Depended on by:
- All API request handlers (controller layer).

Key classes/entry points:
- `api/Program.cs` top-level statements (`WebApplication.CreateBuilder`, `app.Run()`).

### 3) Uploads HTTP Controller (`api/Controllers/UploadsController.cs`)
Name:
- UploadsController

Responsibility:
- Implements upload endpoint and receipt retrieval endpoint.
- Validates file existence and file size.
- Writes file content to blob storage.
- Writes metadata to PostgreSQL.
- Performs compensating cleanup (delete blob) if DB save fails.

Depends on:
- `UploadDbContext`.
- `BlobServiceClient`.
- `IConfiguration` (container name).
- `ILogger<UploadsController>`.

Depended on by:
- ASP.NET Core routing middleware.
- Browser client invoking `/api/uploads` endpoints.

Key classes/entry points:
- `Upload()` (`POST /api/uploads`).
- `GetById()` (`GET /api/uploads/{id}`).

### 4) Persistence Model + DbContext (`api/Data`, `api/Models`)
Name:
- Upload Metadata Persistence Layer

Responsibility:
- Defines uploaded file entity shape and DB mapping.
- Exposes EF Core `DbSet<UploadedFile>`.
- Enforces relational constraints (required fields, max lengths, table mapping).

Depends on:
- EF Core runtime.
- Npgsql EF provider.

Depended on by:
- `UploadsController` for create/read metadata operations.

Key classes/entry points:
- `api/Data/UploadDbContext.cs`.
- `api/Models/UploadedFile.cs`.
- `api/Models/UploadResponse.cs` (HTTP response DTO contract).

### 5) PostgreSQL Service (`compose.yaml`)
Name:
- Metadata Database

Responsibility:
- Stores rows in `uploaded_files` table with upload metadata.

Depends on:
- Docker runtime.

Depended on by:
- API DbContext via connection string `ConnectionStrings:Uploads`.

Key classes/entry points:
- Docker service `postgres` in `compose.yaml`.

### 6) Azurite Service (`compose.yaml`)
Name:
- Blob Storage Emulator

Responsibility:
- Stores uploaded file payload bytes under container/blob paths.

Depends on:
- Docker runtime.

Depended on by:
- API Blob client via `ConnectionStrings:BlobStorage`.

Key classes/entry points:
- Docker service `azurite` in `compose.yaml`.

## Data Flow

### Primary Flow: File Upload
1. User selects a file in `web/src/App.tsx`.
2. `App.uploadFile()` builds `FormData` with `file` field.
3. Browser sends `POST {apiUrl}/api/uploads` multipart/form-data.
4. ASP.NET Core routes to `UploadsController.Upload()`.
5. Controller validates:
   - file exists and non-empty.
   - file <= 25 MB (`MaxFileSizeBytes`).
6. Controller resolves blob container name from config (`BlobStorage:ContainerName`, default `uploads`).
7. Controller ensures blob container exists (`CreateIfNotExistsAsync`).
8. Controller generates GUID upload id and blob name `"{uploadIdN}/{originalFileName}"`.
9. Controller streams file content to blob storage (`blob.UploadAsync`).
10. Controller creates `UploadedFile` entity with metadata.
11. Controller persists metadata to PostgreSQL (`SaveChangesAsync`).
12. On DB failure, controller attempts compensating delete of uploaded blob (`DeleteIfExistsAsync`) then rethrows.
13. On success, controller returns `201 Created` with `UploadResponse` receipt and `Location` header targeting `GetById` route.
14. Web client renders success details (name, size, receipt ID).

### Secondary Flow: Upload Receipt Retrieval
1. Client (or any HTTP caller) requests `GET /api/uploads/{id}`.
2. Controller queries `UploadedFiles` with `AsNoTracking().SingleOrDefaultAsync`.
3. If found, returns `200 OK` with `UploadResponse`.
4. If missing, returns `404 Not Found`.

### Error Flow
- Client-side precondition failure: no file selected -> UI error without API call.
- API validation failure: returns `400` or `413` with `ProblemDetails`.
- Unexpected server/storage/DB error: exception bubbles to ASP.NET Core default error handling (no custom global exception middleware configured).

## External Dependencies

### 1) PostgreSQL
- System name: PostgreSQL (Docker image `postgres:17-alpine`).
- How used: persistent metadata store for uploaded file records.
- Integration pattern: direct DB access via EF Core provider (Npgsql).
- Owning component: API Persistence Layer (`UploadDbContext`) and `UploadsController`.

### 2) Blob Storage (Azurite / Azure Blob API)
- System name: Azurite Blob service (Azure Blob Storage emulator).
- How used: stores raw uploaded file content.
- Integration pattern: Azure Storage Blob SDK (`Azure.Storage.Blobs`) over HTTP.
- Owning component: `UploadsController` via `BlobServiceClient`.

### 3) Browser Runtime
- System name: Web browser Fetch + FormData APIs.
- How used: sends multipart upload requests and receives JSON responses.
- Integration pattern: REST over HTTP.
- Owning component: Web SPA (`App.tsx`).

## Technology Stack

Backend:
- Runtime/language: .NET 10 (`net10.0`), C#.
- Framework: ASP.NET Core Web API.
- Data access: Entity Framework Core with `Npgsql.EntityFrameworkCore.PostgreSQL` `10.0.0`.
- Blob SDK: `Azure.Storage.Blobs` `12.27.0`.
- Logging: `Microsoft.Extensions.Logging` abstractions (ASP.NET default providers).

Frontend:
- Runtime/language: TypeScript `~6.0.2`, React `19.2.7`.
- Build/dev framework: Vite `8.1.1` with `@vitejs/plugin-react` `6.0.3`.
- Linting: `oxlint` `1.71.0`.

Infrastructure/runtime support:
- Container orchestration (local dev): Docker Compose (`compose.yaml`).
- Data service images:
  - PostgreSQL `17-alpine`.
  - Azurite `3.35.0`.

Build systems:
- Backend build: `dotnet build`.
- Frontend build: `tsc -b && vite build`.

## Entry Points

HTTP endpoints:
- `POST /api/uploads`
  - Framework: ASP.NET Core MVC controller action.
  - Location: `api/Controllers/UploadsController.cs` (`Upload`).
- `GET /api/uploads/{id:guid}`
  - Framework: ASP.NET Core MVC controller action.
  - Location: `api/Controllers/UploadsController.cs` (`GetById`).

Application bootstraps:
- API process start: `api/Program.cs` (top-level host initialization + route mapping + `app.Run()`).
- Web process start: `web/src/main.tsx` (React root render).
- Browser page shell: `web/index.html` loads `src/main.tsx`.

Background jobs / schedulers:
- None implemented.

Event listeners / message consumers:
- None implemented.

Plugin hooks / extension points:
- No formal plugin system exists.
- Practical extension points are code-level only:
  - Add new ASP.NET controllers/actions.
  - Add middleware/services in `Program.cs`.
  - Extend React components/state in `App.tsx`.

## Known Constraints and Limitations
1. Upload size hard limit is 25 MB, enforced in two places:
   - `[RequestSizeLimit(MaxFileSizeBytes)]`.
   - explicit runtime check `if (file.Length > MaxFileSizeBytes)`.
2. CORS is locked to `http://localhost:5173` by default; non-matching web origins will fail without config/code change.
3. API has no authentication or authorization; any caller with network access can upload and query receipts.
4. API has no virus/malware scanning, MIME validation, or file content inspection.
5. Metadata persistence and blob persistence are not wrapped in a distributed transaction:
   - Blob write happens first.
   - DB write failure triggers compensating blob delete attempt.
   - If compensating delete fails, orphaned blobs may remain.
6. Startup schema management uses `Database.EnsureCreatedAsync()` rather than migrations:
   - suitable for benchmark/dev simplicity.
   - less appropriate for evolving production schemas.
7. Storage naming strategy preserves original filename (after `Path.GetFileName` sanitization), which may still carry user-provided naming quirks.
8. There is no deduplication, resumable upload, chunking, versioning, or lifecycle cleanup logic.
9. Error handling is mostly local to controller; no custom global exception middleware or standardized error envelope beyond default `ProblemDetails` for validation branches.
10. Configuration includes local development connection strings in `appsettings.json`; production-grade secret management is not implemented here.
11. Architecture is intentionally minimal and centralized (single controller, no service/repository layer), so behavior changes are likely to concentrate in `UploadsController` and `Program.cs`.
12. Frontend assumes API response schema fields (`id`, `fileName`, `contentType`, `sizeBytes`, `uploadedAtUtc`) and will break if response contract changes without synchronized updates.

## AI Agent Guidance Summary
For safe modifications, AI agents should follow these practical rules:
- Treat `UploadsController` as the current orchestration layer for upload workflow.
- Keep API response contract (`UploadResponse`) and frontend `UploadReceipt` type aligned.
- Preserve blob-first then metadata-write behavior unless redesigning transactional semantics intentionally.
- Preserve or explicitly revise CORS and file-size limits when changing endpoints.
- Keep `UploadDbContext` as the single source of table mapping truth.
- Prefer additive endpoint changes over implicit behavior changes to existing upload semantics.
- If introducing production concerns (auth, scanning, migrations, observability), document them explicitly because baseline code is benchmark-oriented by design.
