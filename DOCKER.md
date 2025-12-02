# Docker Setup for Potluck Organizer

This guide will help you run the Potluck Organizer using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed (usually comes with Docker Desktop)

## Quick Start

1. **Create environment file**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file** and set your admin password and secret key:
   ```bash
   nano .env  # or use your preferred text editor
   ```

   Generate a secure secret key with:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **Build and start the container**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

## Managing the Container

### View logs
```bash
docker-compose logs -f potluck
```

### Stop the container
```bash
docker-compose down
```

### Restart the container
```bash
docker-compose restart
```

### Rebuild the container (after code changes)
```bash
docker-compose up -d --build
```

## Database Persistence

The SQLite database file (`potluck.db`) is stored in the same directory as your `docker-compose.yml` file. This means:

- Your data persists even if you stop or remove the container
- You can back up your data by copying the `potluck.db` file
- The database is shared between the host and container

## Volume Mounts

The following directories are mounted as volumes:

1. **Database**: `./potluck.db:/app/potluck.db`
   - Persists all your potluck data

2. **Static Files**: `./app/static:/app/app/static`
   - Allows you to modify CSS/JS without rebuilding the container

## Environment Variables

You can customize the application using these environment variables in your `.env` file:

- `ADMIN_PASSWORD`: Password for admin access (required)
- `SECRET_KEY`: Secret key for session encryption (required)
- `DATABASE_URL`: Database connection string (default: `sqlite:///./potluck.db`)
- `DEBUG`: Enable debug mode (default: `false`)

## Port Configuration

By default, the application runs on port 8000. To change this, edit the `docker-compose.yml` file:

```yaml
ports:
  - "3000:8000"  # Change 3000 to your preferred port
```

## Troubleshooting

### Container won't start
Check the logs:
```bash
docker-compose logs potluck
```

### Permission issues with database
Ensure the `potluck.db` file has proper permissions:
```bash
chmod 644 potluck.db
```

### Reset the database
Stop the container, delete `potluck.db`, and restart:
```bash
docker-compose down
rm potluck.db
docker-compose up -d
```

## Production Considerations

For production deployment:

1. **Use a strong admin password** and secret key
2. **Set `DEBUG=False`** in your `.env` file
3. **Use a reverse proxy** (like Nginx or Traefik) for HTTPS
4. **Regular backups** of the `potluck.db` file
5. **Consider using PostgreSQL** instead of SQLite for better concurrency

## Image Details

- **Base Image**: `debian:trixie-slim`
- **Image Size**: ~200MB (small and efficient)
- **Python Version**: Python 3.x (from Debian repositories)
- **Web Server**: Uvicorn (ASGI server)

## Health Check

The container includes a health check that runs every 30 seconds. You can check the container health with:

```bash
docker ps
```

Look for the status in the "STATUS" column.
