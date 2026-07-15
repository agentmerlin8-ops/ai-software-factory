using BenchmarkUpload.Api.Data;
using BenchmarkUpload.Api.Models;
using Azure.Storage.Blobs;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace BenchmarkUpload.Api.Controllers;

[ApiController]
[Route("api/uploads")]
public sealed class UploadsController(
    UploadDbContext database,
    BlobServiceClient blobServiceClient,
    IConfiguration configuration,
    ILogger<UploadsController> logger) : ControllerBase
{
    private const long MaxFileSizeBytes = 25 * 1024 * 1024;

    [HttpPost]
    [RequestSizeLimit(MaxFileSizeBytes)]
    [ProducesResponseType<UploadResponse>(StatusCodes.Status201Created)]
    [ProducesResponseType<ProblemDetails>(StatusCodes.Status400BadRequest)]
    [ProducesResponseType<ProblemDetails>(StatusCodes.Status413PayloadTooLarge)]
    public async Task<ActionResult<UploadResponse>> Upload(
        [FromForm] IFormFile? file,
        CancellationToken cancellationToken)
    {
        if (file is null || file.Length == 0)
        {
            return BadRequest(new ProblemDetails
            {
                Title = "A non-empty file is required.",
                Status = StatusCodes.Status400BadRequest
            });
        }

        if (file.Length > MaxFileSizeBytes)
        {
            return StatusCode(StatusCodes.Status413PayloadTooLarge, new ProblemDetails
            {
                Title = "The selected file exceeds the 25 MB limit.",
                Status = StatusCodes.Status413PayloadTooLarge
            });
        }

        var containerName = configuration["BlobStorage:ContainerName"] ?? "uploads";
        var container = blobServiceClient.GetBlobContainerClient(containerName);
        await container.CreateIfNotExistsAsync(cancellationToken: cancellationToken);

        var uploadId = Guid.NewGuid();
        var blobName = $"{uploadId:N}/{Path.GetFileName(file.FileName)}";
        var blob = container.GetBlobClient(blobName);

        await using var content = file.OpenReadStream();
        await blob.UploadAsync(content, overwrite: false, cancellationToken: cancellationToken);

        var upload = new UploadedFile
        {
            Id = uploadId,
            OriginalFileName = Path.GetFileName(file.FileName),
            ContentType = string.IsNullOrWhiteSpace(file.ContentType)
                ? "application/octet-stream"
                : file.ContentType,
            SizeBytes = file.Length,
            BlobName = blobName,
            UploadedAtUtc = DateTimeOffset.UtcNow
        };

        database.UploadedFiles.Add(upload);

        try
        {
            await database.SaveChangesAsync(cancellationToken);
        }
        catch
        {
            await blob.DeleteIfExistsAsync(cancellationToken: cancellationToken);
            throw;
        }

        logger.LogInformation("Stored upload {UploadId} as blob {BlobName}", upload.Id, upload.BlobName);

        var response = new UploadResponse(
            upload.Id,
            upload.OriginalFileName,
            upload.ContentType,
            upload.SizeBytes,
            upload.UploadedAtUtc);

        return CreatedAtAction(nameof(GetById), new { id = upload.Id }, response);
    }

    [HttpGet("{id:guid}")]
    [ProducesResponseType<UploadResponse>(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<ActionResult<UploadResponse>> GetById(Guid id, CancellationToken cancellationToken)
    {
        var upload = await database.UploadedFiles
            .AsNoTracking()
            .SingleOrDefaultAsync(item => item.Id == id, cancellationToken);

        return upload is null
            ? NotFound()
            : Ok(new UploadResponse(
                upload.Id,
                upload.OriginalFileName,
                upload.ContentType,
                upload.SizeBytes,
                upload.UploadedAtUtc));
    }
}