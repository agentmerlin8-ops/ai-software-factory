# API Module README

## Purpose
This module is the backend API for the benchmark upload application. It owns the HTTP contract for file uploads, the persistence of upload metadata, and the integration with blob storage.

This module is responsible for:
- accepting multipart file uploads from the client,
- validating the incoming request,
- writing file bytes to blob storage,
- recording upload metadata in PostgreSQL,
- returning a simple upload receipt for later lookup.

This module does not own:
- the frontend UI,
- browser-side state management,
- business workflows beyond the single upload flow,
- authentication or authorization,
- background job processing,
- multi-service orchestration.

The module is intentionally small and centralized. If a feature requires richer domain logic, more services, or more complex workflows, that logic should likely be introduced in a new module or service layer rather than expanded here.

## Key Classes / Files

### [Program.cs](Program.cs)
- **Responsibility**: application composition root.
- **Key public/entry logic**:
  - top-level startup code initializes the ASP.NET Core host,
  - reads connection strings,
  - registers EF Core and the blob client,
  - enables CORS,
  - maps controllers,
  - ensures the database schema exists at startup.
- **Dependencies**:
  - depends on EF Core and Azure Blob SDK configuration,
  - wires [Controllers/UploadsController.cs](Controllers/UploadsController.cs) and [Data/UploadDbContext.cs](Data/UploadDbContext.cs).
- **Dependencies on other modules**:
  - none directly; it configures the API module itself.

### [Controllers/UploadsController.cs](Controllers/UploadsController.cs)
- **Responsibility**: the HTTP API surface for uploads.
- **Key public methods**:
  - `public async Task<ActionResult<UploadResponse>> Upload([FromForm] IFormFile? file, CancellationToken cancellationToken)`
    - validates the incoming file,
    - uploads the file body into blob storage,
    - creates a metadata entity,
    - saves it to PostgreSQL,
    - returns a `201 Created` response.
  - `public async Task<ActionResult<UploadResponse>> GetById(Guid id, CancellationToken cancellationToken)`
    - loads metadata by ID from PostgreSQL,
    - returns either `200 OK` or `404 Not Found`.
- **Dependencies on other classes within this module**:
  - depends on [Data/UploadDbContext.cs](Data/UploadDbContext.cs)
  - depends on [Models/UploadedFile.cs](Models/UploadedFile.cs)
  - depends on [Models/UploadResponse.cs](Models/UploadResponse.cs)
- **Dependencies on other modules**:
  - depends on the Azure Blob Storage client configured by [Program.cs](Program.cs)
  - depends on the PostgreSQL connection configured by [Program.cs](Program.cs)

### [Data/UploadDbContext.cs](Data/UploadDbContext.cs)
- **Responsibility**: EF Core persistence context for upload metadata.
- **Key public members**:
  - `public DbSet<UploadedFile> UploadedFiles => Set<UploadedFile>();`
    - exposes the upload entity as a table-backed set.
- **Key methods**:
  - `protected override void OnModelCreating(ModelBuilder modelBuilder)`
    - maps the entity to the `uploaded_files` table,
    - defines required fields and length constraints.
- **Dependencies**:
  - uses [Models/UploadedFile.cs](Models/UploadedFile.cs).
- **Dependencies on other modules**:
  - none directly.

### [Models/UploadedFile.cs](Models/UploadedFile.cs)
- **Responsibility**: the persisted upload entity.
- **Key public members**:
  - `public Guid Id { get; init; }`
  - `public required string OriginalFileName { get; init; }`
  - `public required string ContentType { get; init; }`
  - `public long SizeBytes { get; init; }`
  - `public required string BlobName { get; init; }`
  - `public DateTimeOffset UploadedAtUtc { get; init; }`
- **Dependencies**:
  - none within the module beyond the EF context and controller.
- **Dependencies on other modules**:
  - none.

### [Models/UploadResponse.cs](Models/UploadResponse.cs)
- **Responsibility**: API response contract for upload receipts.
- **Key public members**:
  - immutable record fields: `Id`, `FileName`, `ContentType`, `SizeBytes`, `UploadedAtUtc`.
- **Dependencies**:
  - none.
- **Dependencies on other modules**:
  - none.

## How It Works
The most important operation in this module is the upload flow.

Sequence:
1. The client sends a `POST /api/uploads` request with multipart form data.
2. [Controllers/UploadsController.cs](Controllers/UploadsController.cs) receives the request in `Upload(...)`.
3. The method validates the upload:
   - file must exist and not be empty,
   - file size must be at most 25 MB.
4. The controller resolves the blob container name from configuration and gets a `BlobServiceClient` from [Program.cs](Program.cs).
5. The controller creates a blob path using a generated `Guid` and the original file name.
6. The file bytes are uploaded to blob storage.
7. A new [Models/UploadedFile.cs](Models/UploadedFile.cs) instance is created with metadata.
8. The entity is added to [Data/UploadDbContext.cs](Data/UploadDbContext.cs) and saved to PostgreSQL.
9. If the database save fails, the controller attempts to delete the blob as cleanup.
10. On success, the controller returns a `UploadResponse` payload and a `Location` header pointing to `GET /api/uploads/{id}`.

The retrieval flow is simpler:
1. [Controllers/UploadsController.cs](Controllers/UploadsController.cs) `GetById(...)` receives the request.
2. It queries the database through `UploadDbContext`.
3. If a matching record exists, it returns a `UploadResponse`; otherwise it returns `404 Not Found`.

## Extension Points
This module is intentionally minimal, so extension points are limited and should remain simple.

### Existing extension hooks
- **New endpoint**: add a new action method to [Controllers/UploadsController.cs](Controllers/UploadsController.cs).
- **New configuration**: add new keys to [appsettings.json](appsettings.json) or [appsettings.Development.json](appsettings.Development.json) and read them through `IConfiguration`.
- **New persistence mapping**: extend [Data/UploadDbContext.cs](Data/UploadDbContext.cs) with additional entity mappings.
- **New response shape**: add or change DTOs under [Models](Models/).

### Patterns to follow when adding behavior
- Keep controller methods thin and focused on HTTP concerns.
- Preserve the current input validation style: explicit checks at the start of the action.
- Keep persistence mapping in [Data/UploadDbContext.cs](Data/UploadDbContext.cs).
- Keep transport DTOs in [Models](Models/).
- If new business logic becomes significant, introduce a separate service layer rather than stuffing it into the controller.

## What Belongs Here
Code that belongs in this module includes:
- new upload-related API endpoints,
- request validation for this API surface,
- EF Core entity mapping for upload-related data,
- request/response DTO definitions,
- integration logic for blob storage and PostgreSQL as they relate to upload handling,
- startup/configuration wiring for the API module.

## What Does NOT Belong Here
Code that should not be added here includes:
- frontend React components or UI state logic,
- browser-specific logic,
- unrelated domain services that are not part of the upload API,
- background workers or event-driven processing unless this module is explicitly expanded to own them,
- authentication/authorization systems unless this module is intentionally being upgraded to own security concerns,
- generic cross-cutting infrastructure that should live in a shared application layer.

If a new feature needs these concerns, place it in a different module or introduce a new abstraction rather than overloading this module.
