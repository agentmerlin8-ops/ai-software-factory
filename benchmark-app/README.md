# Benchmark Upload App

A deliberately small, full-stack benchmark target for the AI Story-to-Code pipeline.

## Architecture

- `web/`: React and Vite single-page client with one file upload action.
- `api/`: .NET 10 ASP.NET Core API. It accepts multipart uploads, writes metadata to PostgreSQL, and writes the file body to Blob Storage.
- PostgreSQL: metadata store, started through Docker Compose.
- Azurite: local Azure Blob Storage emulator, started through Docker Compose.

## Run Locally

Start backing services:

```bash
cd benchmark-app
docker compose up -d
```

Start the API in one terminal:

```bash
cd benchmark-app/api
dotnet run --urls http://localhost:5185
```

Start the React application in another terminal:

```bash
cd benchmark-app/web
npm run dev
```

Open `http://localhost:5173`. Choose a file and select **Upload file**. The page returns a receipt after the API stores the binary in Azurite and metadata in PostgreSQL.

## Verification

```bash
cd benchmark-app/api
dotnet build

cd ../web
npm run build
```

The API has a 25 MB upload limit. The local Postgres and Azurite connection strings live in `api/appsettings.json` for reproducible benchmark runs; production deployments should use secret-managed configuration.