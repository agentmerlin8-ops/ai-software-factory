# API Reference

## Exposed APIs

### Upload a file
- **Method and path**: `POST /api/uploads`
- **Purpose**: Accepts a single uploaded file, stores the file bytes in blob storage, records metadata in PostgreSQL, and returns an upload receipt.
- **Authentication**: None. No authentication middleware or authorization checks are configured.
- **Request**:
  - **Headers**:
    - `Content-Type: multipart/form-data`
  - **Body**: a multipart form with a single field named `file`.
    - `file`: `IFormFile` (binary upload)
  - **Additional constraints**:
    - File must be present and non-empty.
    - File size must be less than or equal to 25 MB.
- **Response**:
  - **Success**: `201 Created`
  - **Body**: `UploadResponse`
    - `id`: `Guid`
    - `fileName`: `string`
    - `contentType`: `string`
    - `sizeBytes`: `long`
    - `uploadedAtUtc`: `DateTimeOffset`
  - **Location header**: points to `GET /api/uploads/{id}`
- **Error cases**:
  - `400 Bad Request` when the file is missing or empty.
  - `413 Payload Too Large` when the file exceeds the 25 MB limit.
  - Unexpected persistence or storage failures propagate as server errors.
- **Side effects**:
  - Creates or reuses the configured blob container.
  - Uploads bytes to blob storage.
  - Inserts a row into the `uploaded_files` table in PostgreSQL.
  - On database save failure, attempts to delete the uploaded blob.

### Retrieve an upload receipt
- **Method and path**: `GET /api/uploads/{id}`
- **Purpose**: Fetches the metadata for a previously uploaded file by its GUID identifier.
- **Authentication**: None.
- **Request**:
  - **Path parameter**:
    - `id`: `Guid`
- **Response**:
  - **Success**: `200 OK`
  - **Body**: `UploadResponse`
    - `id`: `Guid`
    - `fileName`: `string`
    - `contentType`: `string`
    - `sizeBytes`: `long`
    - `uploadedAtUtc`: `DateTimeOffset`
  - **Not found**: `404 Not Found` when no record exists for the given GUID.
- **Error cases**:
  - `404 Not Found` if the upload ID does not exist.
- **Side effects**:
  - None. This is a read-only operation.

## External APIs Consumed

### Azure Blob Storage / Azurite
- **Purpose**: Stores the uploaded file bytes.
- **Integration pattern**: SDK-based blob storage integration using `Azure.Storage.Blobs`.
- **Authentication**: Uses the configured connection string for the storage account. In local development this is the Azurite account connection string from configuration.
- **Key operations used**:
  - `CreateIfNotExistsAsync()` to ensure the target container exists.
  - `UploadAsync()` to write the uploaded bytes to a blob.
  - `DeleteIfExistsAsync()` as a cleanup mechanism if the database write fails.
- **Error handling**: Exceptions from storage operations are not wrapped in custom handling. They bubble up to ASP.NET Core error handling.
- **Where in the code**: [api/Controllers/UploadsController.cs](api/Controllers/UploadsController.cs)

### PostgreSQL
- **Purpose**: Persists upload metadata rows.
- **Integration pattern**: Direct relational database access via Entity Framework Core and Npgsql.
- **Authentication**: Uses the `ConnectionStrings:Uploads` connection string configured in [api/appsettings.json](api/appsettings.json).
- **Key operations used**:
  - `database.UploadedFiles.Add(upload)` to stage a new row.
  - `database.SaveChangesAsync()` to persist the change.
  - `database.UploadedFiles.AsNoTracking().SingleOrDefaultAsync(...)` to read an upload by ID.
- **Error handling**: The controller catches database-save failures to run blob cleanup, then rethrows the exception.
- **Where in the code**: [api/Data/UploadDbContext.cs](api/Data/UploadDbContext.cs) and [api/Controllers/UploadsController.cs](api/Controllers/UploadsController.cs)

## Events and Messages
No event-driven or message-based contracts are implemented in the current codebase.

There are no:
- message queues
- event publishers/subscribers
- background consumers
- webhook callbacks

## Auth and Security Model
- **How are API callers authenticated?**
  - There is no authentication mechanism in the current implementation.
  - Any caller that can reach the API endpoint can upload files and query upload metadata.
- **How is authorization enforced?**
  - No authorization rules are implemented.
  - The API exposes its endpoints to any client without role-based or policy-based checks.
- **What roles or permissions exist?**
  - None defined in the codebase.
- **Where are permission checks performed?**
  - No permission checks are performed; the controller actions are open.

## Notes for Integrators
- The frontend client calls the API using the browser `fetch` API and sends multipart form data to the upload endpoint.
- The API currently assumes a trusted localhost development origin for CORS; the default allowed origin is `http://localhost:5173`.
- The API contract is intentionally minimal and does not include versioning, pagination, filtering, or authentication.
