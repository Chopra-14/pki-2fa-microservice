# pki-2fa-microservice-23A91A6127
PKI + TOTP Authentication Microservice
A secure, containerized microservice that combines RSA-4096 encryption, TOTP-based 2FA, cron automation, and persistent Docker volumes. This project demonstrates enterprise-grade security practices and modern microservice deployment patterns.

This microservice provides a complete authentication workflow using:
-> RSA 4096-bit key pair for decrypting an encrypted seed.
-> TOTP (SHA-1, 6 digits, 30s) for 2FA code generation.
-> REST API endpoints for decryption, code generation, and verification.
-> Docker multi-stage build for efficient containerization.
-> Cron job that logs TOTP codes every minute.
-> Persistent storage using Docker volumes (/data, /cron).
-> The decrypted seed is stored securely inside the container volume and used to generate and verify 2FA codes that match standard authenticator apps.

Features
🔐 Cryptographic Operations:
RSA 4096-bit key generation (public exponent 65537)
RSA/OAEP (SHA-256, MGF1) seed decryption
RSA/PSS (SHA-256, max salt) commit signing
Base32 conversion from hex seed for TOTP
Strong input validation and error handling

🌐 REST API Endpoints
Endpoint	   Method	     Description
/decrypt-seed	POST	Decrypts seed using RSA private key and stores it persistently
/generate-2fa	GET	    Generates current 6-digit TOTP code and expiration time
/verify-2fa	    POST	Verifies TOTP code with ±1 time window

Persistent Storage:
Two Docker volumes ensure data survives container restarts:
-> /data/seed.txt → stores decrypted seed
-> /cron/last_code.txt → stores cron-generated logs

Docker Setup

This project uses a multi-stage Dockerfile:
Builder Stage: installs dependencies
Runtime Stage: minimal image with:
    cron daemon
    UTC timezone
    application code
    cron configuration
    exposed API port (8080)
    mounted volumes (/data and /cron)
A docker-compose.yml is included for easy development and testing.

How to Run the Project
1. Build and start the container
docker-compose build
docker-compose up -d

2. Test the endpoints

Decrypt seed:
curl -X POST http://localhost:8080/decrypt-seed \
  -H "Content-Type: application/json" \
  -d "{\"encrypted_seed\": \"$(cat encrypted_seed.txt)\"}"

Generate TOTP code:
curl http://localhost:8080/generate-2fa

Verify a code:
curl -X POST http://localhost:8080/verify-2fa \
  -H "Content-Type: application/json" \
  -d '{"code": "123456"}'

3. Check cron output
docker exec <container-name> cat /cron/last_code.txt

Implementation Decisions:
RSA-4096 chosen for strong encryption guarantees
OAEP + SHA-256 ensures safe seed transmission
TOTP standard (RFC 6238) for full authenticator compatibility
UTC timezone prevents mismatched TOTP windows
Volumes ensure decrypted seed persists across restarts
Cron + API separation mirrors real production setups
Implemented strict error handling and clear status codes
Designed container for deterministic, reproducible builds

Requirements Achieved:
All cryptographic algorithms and parameters implemented exactly
All three API endpoints functional
Seed decryption fully working
TOTP generation and verification correct
Cron job runs reliably every minute
Docker container passes persistence and restart tests
Commit proof signing and encryption supported
Clean repository with required files committed
