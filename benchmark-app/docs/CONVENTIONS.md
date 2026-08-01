# Repository Conventions

This document captures the conventions that are already present in this repository. It is intended for AI coding agents so generated code matches the existing style, structure, and intent of the project.

## Naming Conventions

### Classes
- Classes use PascalCase.
- Names are descriptive and usually reflect the domain role they play.
- Representative examples:
  - `UploadsController` in [api/Controllers/UploadsController.cs](api/Controllers/UploadsController.cs)
  - `UploadDbContext` in [api/Data/UploadDbContext.cs](api/Data/UploadDbContext.cs)
  - `UploadedFile` in [api/Models/UploadedFile.cs](api/Models/UploadedFile.cs)
  - `UploadResponse` in [api/Models/UploadResponse.cs](api/Models/UploadResponse.cs)
- Suffixes are used sparingly and only when they add meaning: `Controller`, `Context`, `Response`.

### Methods
- Methods use PascalCase.
- Method names are usually verb-based or verb-phrase-based.
- Representative examples:
  - `Upload` in [api/Controllers/UploadsController.cs](api/Controllers/UploadsController.cs)
  - `GetById` in [api/Controllers/UploadsController.cs](api/Controllers/UploadsController.cs)
- The code favors short, direct names over long abstractions.

### Variables
- Local variables and parameters use camelCase.
- Representative examples:
  - `database`
  - `blobServiceClient`
  - `containerName`
  - `uploadId`
  - `blobName`
  - `content`
- The code uses concise names when the surrounding type or method already makes the meaning clear.

### Constants
- Constants use PascalCase.
- Representative example:
  - `MaxFileSizeBytes` in [api/Controllers/UploadsController.cs](api/Controllers/UploadsController.cs)
- The repository does not use ALL_CAPS constant style.

### Files and namespaces/packages
- C# source files use PascalCase matching the type they contain.
  - Example: [api/Controllers/UploadsController.cs](api/Controllers/UploadsController.cs)
  - Example: [api/Data/UploadDbContext.cs](api/Data/UploadDbContext.cs)
- Frontend files use a mix of PascalCase and lowercase-style names consistent with the Vite/React template:
  - [web/src/App.tsx](web/src/App.tsx)
  - [web/src/main.tsx](web/src/main.tsx)
  - [web/src/index.css](web/src/index.css)
- Namespaces follow the project root and feature area structure:
  - `BenchmarkUpload.Api.Controllers`
  - `BenchmarkUpload.Api.Data`
  - `BenchmarkUpload.Api.Models`

### Database tables and columns
- The only explicitly named database table in the code is `uploaded_files`, which uses snake_case.
- The code does not define explicit column names in the EF model, so column naming is left to EF Core defaults unless a future change introduces explicit mapping.
- The entity property names remain PascalCase in C# and are mapped via EF Core conventions.

### API endpoints
- API routes use lowercase, resource-oriented path segments.
- The current routes are:
  - `POST /api/uploads`
  - `GET /api/uploads/{id}`
- Route naming is simple and explicit; the code does not use versioned paths, nested resource namespaces, or overly abstract URL patterns.

## Code Patterns

### Dependency injection via constructor injection
- Pattern: services are registered in [api/Program.cs](api/Program.cs) and consumed as constructor parameters.
- When used: for web controller dependencies, EF Core context, and Azure Blob client.
- Representative example: `UploadsController` accepts `UploadDbContext`, `BlobServiceClient`, `IConfiguration`, and `ILogger<UploadsController>` in its constructor.

### Explicit validation at the request boundary
- Pattern: validation is performed directly inside the controller action before the main workflow starts.
- When used: for file presence, file size, and request shape.
- Representative example: [api/Controllers/UploadsController.cs](api/Controllers/UploadsController.cs)
- The app uses both framework-level attributes such as `[RequestSizeLimit]` and inline checks.

### Return typed action results instead of exceptions for expected failures
- Pattern: controller methods return `ActionResult<T>` and use explicit status codes such as `BadRequest`, `StatusCode`, and `NotFound`.
- When used: for user-facing validation and lookup failures.
- Representative example: `Upload` and `GetById` in [api/Controllers/UploadsController.cs](api/Controllers/UploadsController.cs)
- The project does not use a large custom exception hierarchy for normal application flow.

### Logging with structured messages
- Pattern: log important milestones with `ILogger` using structured placeholders.
- When used: when a file upload has been successfully stored.
- Representative example: `logger.LogInformation("Stored upload {UploadId} as blob {BlobName}", upload.Id, upload.BlobName);`
- The code does not use elaborate logging infrastructure, custom log wrappers, or logging in every method.

### Configuration access through `IConfiguration`
- Pattern: configuration values are read directly from `builder.Configuration` or the injected `IConfiguration` instance.
- When used: for database connection strings and blob container settings.
- Representative example: [api/Program.cs](api/Program.cs) and [api/Controllers/UploadsController.cs](api/Controllers/UploadsController.cs)
- The code does not introduce a custom settings wrapper.

### Simple persistence and cleanup flow
- Pattern: the controller writes the blob first, then writes metadata to the database, and uses a cleanup attempt if persistence fails.
- When used: for the upload workflow.
- Representative example: [api/Controllers/UploadsController.cs](api/Controllers/UploadsController.cs)
- There is no explicit distributed transaction or outbox pattern in this codebase.

### Startup schema initialization
- Pattern: the application creates the database schema at startup with `EnsureCreatedAsync()`.
- When used: for local benchmark/dev simplicity.
- Representative example: [api/Program.cs](api/Program.cs)
- The repository does not currently use EF Core migrations for schema management.

## Anti-Patterns to Avoid

The following patterns should not be introduced unless the project intentionally grows beyond its current benchmark scope.

- Do not introduce a complex layered architecture (controllers, services, repositories, managers, unit-of-work abstractions) unless the feature genuinely requires it. The current project is intentionally small and centralized.
- Do not add broad `catch (Exception)` handlers for normal application flow. The existing code uses explicit validation and narrow cleanup logic around persistence failures.
- Do not add a custom exception framework for common validation or not-found cases. The existing style uses `ProblemDetails` and action results.
- Do not introduce a custom configuration abstraction when `IConfiguration` already suffices.
- Do not add background jobs, queues, or event-driven infrastructure unless the task specifically requires it. The current app is synchronous and request-driven.
- Do not use a different C# naming style from the rest of the codebase. Keep types as PascalCase, methods as PascalCase, and local values as camelCase.
- Do not add verbose comments to restate the code. The codebase favors clear naming over commentary.
- Do not switch the project to migrations-based schema management unless the scope is being expanded intentionally; the current code uses `EnsureCreatedAsync()` for simplicity.

## Testing Conventions

### Current state
- There is no test project in the repository.
- There are no existing unit or integration tests under the root, [api](api), or [web](web) folders.
- The project currently relies on build verification (`dotnet build` and `npm run build`) rather than an automated test suite.

### What this means for future tests
- If tests are added later, they should be placed in a dedicated test project rather than mixed into the application folders.
- The repository does not yet establish a framework convention, so no existing xUnit/NUnit/MSTest pattern should be assumed.
- For now, the closest existing quality gate is the documented build verification in [README.md](README.md).

## Module/Package Structure

The repository is intentionally simple and split into two main areas:

- [api](api): the backend ASP.NET Core application
- [web](web): the frontend React/Vite application

### Backend structure
- [api/Controllers](api/Controllers): HTTP endpoints and request handling
- [api/Data](api/Data): EF Core persistence context and database mapping
- [api/Models](api/Models): domain models and API response DTOs
- [api/Properties](api/Properties): launch settings
- [api/appsettings.json](api/appsettings.json) and [api/appsettings.Development.json](api/appsettings.Development.json): configuration

### Frontend structure
- [web/src](web/src): React application code and CSS
- [web/src/App.tsx](web/src/App.tsx): main UI and upload flow
- [web/src/main.tsx](web/src/main.tsx): React bootstrap entry point
- [web/index.html](web/index.html): HTML shell for Vite

### Rules for organization
- Keep HTTP concerns in the controller layer.
- Keep persistence concerns in the Data layer.
- Keep domain/entity types in the Models layer.
- Keep local infrastructure definitions in [compose.yaml](compose.yaml).
- Keep the frontend UI logic in [web/src/App.tsx](web/src/App.tsx) rather than scattering it across many files unless the feature genuinely grows.

## Comments and Documentation

- The codebase does not use Javadoc/JSDoc/XML doc comments for classes or methods.
- The code also does not rely on dense inline comments.
- The preferred style is to use clear names and straightforward structure instead of explanatory comments.
- When comments are added, they should be short and explain intent or non-obvious constraints rather than restating what the code obviously does.
- The repository’s main documentation lives in [README.md](README.md) and this file, not in code comments.
