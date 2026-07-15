namespace BenchmarkUpload.Api.Models;

public sealed class UploadedFile
{
    public Guid Id { get; init; }

    public required string OriginalFileName { get; init; }

    public required string ContentType { get; init; }

    public long SizeBytes { get; init; }

    public required string BlobName { get; init; }

    public DateTimeOffset UploadedAtUtc { get; init; }
}