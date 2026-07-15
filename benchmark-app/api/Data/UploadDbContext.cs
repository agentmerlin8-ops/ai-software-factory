using BenchmarkUpload.Api.Models;
using Microsoft.EntityFrameworkCore;

namespace BenchmarkUpload.Api.Data;

public sealed class UploadDbContext(DbContextOptions<UploadDbContext> options) : DbContext(options)
{
    public DbSet<UploadedFile> UploadedFiles => Set<UploadedFile>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<UploadedFile>(entity =>
        {
            entity.ToTable("uploaded_files");
            entity.HasKey(file => file.Id);
            entity.Property(file => file.OriginalFileName).HasMaxLength(512).IsRequired();
            entity.Property(file => file.ContentType).HasMaxLength(255).IsRequired();
            entity.Property(file => file.BlobName).HasMaxLength(1024).IsRequired();
            entity.Property(file => file.UploadedAtUtc).IsRequired();
        });
    }
}