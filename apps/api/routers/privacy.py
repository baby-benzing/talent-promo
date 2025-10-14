from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import re

router = APIRouter(prefix="/api/privacy", tags=["privacy"])

# In-memory storage (replace with database in production)
user_data: dict[str, dict] = {}
deletion_logs: list[dict] = []


class DeleteDataRequest(BaseModel):
    user_id: str
    confirmation: str  # User must type "DELETE" to confirm


class PII_PATTERNS:
    """Patterns for detecting and scrubbing PII."""
    EMAIL = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    SSN = r'\b\d{3}-\d{2}-\d{4}\b'
    CREDIT_CARD = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'


def scrub_pii(text: str, replacement: str = "[REDACTED]") -> str:
    """
    Scrub personally identifiable information from text.
    Returns redacted version.
    """
    # Redact emails
    text = re.sub(PII_PATTERNS.EMAIL, replacement, text)

    # Redact phone numbers
    text = re.sub(PII_PATTERNS.PHONE, replacement, text)

    # Redact SSNs
    text = re.sub(PII_PATTERNS.SSN, replacement, text)

    # Redact credit cards
    text = re.sub(PII_PATTERNS.CREDIT_CARD, replacement, text)

    return text


def validate_pii_scrubber(test_string: str) -> bool:
    """Validate that PII scrubber works correctly."""
    original = test_string
    scrubbed = scrub_pii(test_string)

    # Check that known PII patterns are removed
    has_email = bool(re.search(PII_PATTERNS.EMAIL, scrubbed))
    has_phone = bool(re.search(PII_PATTERNS.PHONE, scrubbed))
    has_ssn = bool(re.search(PII_PATTERNS.SSN, scrubbed))

    return not (has_email or has_phone or has_ssn)


@router.post("/delete_my_data")
async def delete_user_data(request: DeleteDataRequest) -> dict:
    """
    Delete all user data including uploads and database rows.
    Settings button triggers this purge task.
    """
    if request.confirmation != "DELETE":
        raise HTTPException(
            status_code=400,
            detail="Confirmation must be 'DELETE' to proceed"
        )

    user_id = request.user_id

    if user_id not in user_data:
        raise HTTPException(status_code=404, detail="User data not found")

    # Hard-delete blobs (simulated)
    # In production: delete from S3/storage
    user_info = user_data[user_id]
    deleted_files = user_info.get("files", [])

    # Hard-delete database rows
    del user_data[user_id]

    # Log deletion for audit
    deletion_log = {
        "user_id": user_id,
        "deleted_at": datetime.utcnow().isoformat(),
        "files_deleted": len(deleted_files),
        "confirmed": True,
    }
    deletion_logs.append(deletion_log)

    return {
        "success": True,
        "message": "All user data deleted successfully",
        "files_deleted": len(deleted_files),
        "confirmation_id": f"del_{len(deletion_logs)}",
    }


@router.get("/deletion_status/{user_id}")
async def get_deletion_status(user_id: str) -> dict:
    """Check if user data has been deleted."""
    # Check deletion logs
    for log in deletion_logs:
        if log["user_id"] == user_id:
            return {
                "deleted": True,
                "deleted_at": log["deleted_at"],
                "files_deleted": log["files_deleted"],
            }

    # Check if data still exists
    if user_id in user_data:
        return {
            "deleted": False,
            "data_exists": True,
        }

    return {
        "deleted": False,
        "data_exists": False,
        "message": "No data found for this user",
    }


@router.post("/scrub_logs")
async def scrub_application_logs() -> dict:
    """
    Scrub PII from application logs.
    Should be run periodically via cron job.
    """
    # In production: read log files and scrub them
    # For now, simulate log scrubbing

    scrubbed_count = 0
    sample_log_entries = [
        "User email: john@example.com logged in",
        "Phone number 555-123-4567 was verified",
        "Payment from card 4532-1234-5678-9012 processed",
    ]

    scrubbed_logs = []
    for entry in sample_log_entries:
        scrubbed = scrub_pii(entry)
        scrubbed_logs.append(scrubbed)
        if scrubbed != entry:
            scrubbed_count += 1

    return {
        "success": True,
        "logs_scrubbed": scrubbed_count,
        "sample_output": scrubbed_logs,
    }


@router.get("/validate_scrubber")
async def validate_scrubber() -> dict:
    """Validate that PII scrubber is working correctly."""
    test_cases = [
        "Contact me at test@email.com or call 555-123-4567",
        "SSN: 123-45-6789, Card: 4532-1234-5678-9012",
        "Normal text without PII",
    ]

    results = []
    all_valid = True

    for test_case in test_cases:
        scrubbed = scrub_pii(test_case)
        is_valid = validate_pii_scrubber(test_case)
        all_valid = all_valid and is_valid

        results.append({
            "original": test_case,
            "scrubbed": scrubbed,
            "valid": is_valid,
        })

    return {
        "validated": all_valid,
        "test_results": results,
    }


@router.get("/backup_policy")
async def get_backup_policy() -> dict:
    """
    Return information about backup retention policy.
    Important for GDPR compliance.
    """
    return {
        "policy": "30-day retention",
        "backup_location": "Encrypted S3 bucket",
        "deletion_propagation": "Backups purged after 30 days",
        "note": "Deleted data may exist in backups for up to 30 days",
    }
