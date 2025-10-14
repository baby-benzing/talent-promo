from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import jwt
import secrets

router = APIRouter(prefix="/api/review", tags=["review"])

# Secret key for signing tokens (should be in environment variables)
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"

# In-memory storage (replace with database in production)
review_links: dict[str, dict] = {}
comments: dict[str, list[dict]] = {}


class CreateReviewLinkRequest(BaseModel):
    document_id: str
    reviewer_email: EmailStr
    expiry_hours: int = 72  # 3 days default


class AddCommentRequest(BaseModel):
    target_path: str
    comment_text: str


def create_signed_token(document_id: str, reviewer_email: str, expiry_hours: int) -> str:
    """Create a signed JWT token for reviewer access."""
    expiry = datetime.utcnow() + timedelta(hours=expiry_hours)
    payload = {
        "document_id": document_id,
        "reviewer_email": reviewer_email,
        "exp": expiry,
        "type": "review_access",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """Verify and decode a review token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Review link has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid review link")


@router.post("/create_link")
async def create_review_link(request: CreateReviewLinkRequest) -> dict:
    """
    Create a time-boxed share link for external reviewer.
    Returns signed token URL.
    """
    token = create_signed_token(
        request.document_id,
        request.reviewer_email,
        request.expiry_hours
    )

    # Store link metadata
    link_id = f"link_{secrets.token_hex(8)}"
    review_links[link_id] = {
        "document_id": request.document_id,
        "reviewer_email": request.reviewer_email,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(hours=request.expiry_hours)).isoformat(),
        "token": token,
    }

    review_url = f"http://localhost:3000/review/{token}"

    return {
        "link_id": link_id,
        "review_url": review_url,
        "expires_at": review_links[link_id]["expires_at"],
    }


@router.get("/verify/{token}")
async def verify_review_access(token: str) -> dict:
    """Verify review token and return document access info."""
    payload = verify_token(token)

    return {
        "document_id": payload["document_id"],
        "reviewer_email": payload["reviewer_email"],
        "expires_at": datetime.fromtimestamp(payload["exp"]).isoformat(),
        "valid": True,
    }


@router.post("/comment/{token}")
async def add_comment(token: str, request: AddCommentRequest) -> dict:
    """
    Add a comment to a specific bullet.
    Comments map to REVIEWER_NOTE suggestions.
    """
    payload = verify_token(token)
    document_id = payload["document_id"]

    # Create comment entry
    comment = {
        "id": f"comment_{secrets.token_hex(8)}",
        "document_id": document_id,
        "target_path": request.target_path,
        "comment_text": request.comment_text,
        "reviewer_email": payload["reviewer_email"],
        "created_at": datetime.utcnow().isoformat(),
        "resolved": False,
    }

    # Store comment
    if document_id not in comments:
        comments[document_id] = []
    comments[document_id].append(comment)

    return {
        "success": True,
        "comment_id": comment["id"],
        "message": "Comment added successfully",
    }


@router.get("/comments/{document_id}")
async def get_comments(document_id: str) -> dict:
    """Get all comments for a document (for owner)."""
    doc_comments = comments.get(document_id, [])

    return {
        "document_id": document_id,
        "comments": doc_comments,
        "count": len(doc_comments),
    }


@router.post("/resolve/{comment_id}")
async def resolve_comment(comment_id: str) -> dict:
    """Mark a comment as resolved."""
    # Find and mark comment as resolved
    for doc_id, doc_comments in comments.items():
        for comment in doc_comments:
            if comment["id"] == comment_id:
                comment["resolved"] = True
                return {
                    "success": True,
                    "comment_id": comment_id,
                    "message": "Comment resolved",
                }

    raise HTTPException(status_code=404, detail="Comment not found")
