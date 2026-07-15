using Azure.Storage.Blobs;
using BenchmarkUpload.Api.Data;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

var databaseConnection = builder.Configuration.GetConnectionString("Uploads")
	?? throw new InvalidOperationException("Connection string 'Uploads' is required.");
var blobConnection = builder.Configuration.GetConnectionString("BlobStorage")
	?? throw new InvalidOperationException("Connection string 'BlobStorage' is required.");

builder.Services.AddDbContext<UploadDbContext>(options => options.UseNpgsql(databaseConnection));
builder.Services.AddSingleton(new BlobServiceClient(blobConnection));
builder.Services.AddCors(options => options.AddDefaultPolicy(policy => policy
	.WithOrigins("http://localhost:5173")
	.AllowAnyHeader()
	.AllowAnyMethod()));
builder.Services.AddControllers();

var app = builder.Build();

await using (var scope = app.Services.CreateAsyncScope())
{
	var database = scope.ServiceProvider.GetRequiredService<UploadDbContext>();
	await database.Database.EnsureCreatedAsync();
}

app.UseCors();
app.MapControllers();

app.Run();
