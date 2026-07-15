namespace BenchmarkUpload.Api.Models;

public sealed record UploadResponse(
    Guid Id,
    string FileName,
    string ContentType,
    long SizeBytes,
    DateTimeOffset UploadedAtUtc);