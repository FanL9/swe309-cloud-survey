"""Server-side validation of survey submissions.

The rating rule matches the C3 pipeline exactly: only "Good", "OK" and
"Poor" are valid, with no trimming or case folding, so "good" or " Good"
are rejected rather than silently corrected.
"""

RATINGS = ("Good", "OK", "Poor")
COMMENT_MAX_LENGTH = 500


class ValidationError(ValueError):
    def __init__(self, reason, message, value=None):
        super().__init__(message)
        self.reason = reason  # short machine-readable code, used in logs
        self.message = message  # human-readable, shown to the respondent
        self.value = value


def validate_submission(data):
    """Return (rating, comment) or raise ValidationError."""
    rating = data.get("rating")
    if rating is None or rating == "":
        raise ValidationError("missing_rating", "Please choose a rating: Good, OK or Poor.")
    if not isinstance(rating, str) or rating not in RATINGS:
        raise ValidationError(
            "invalid_rating",
            "Rating must be exactly one of: Good, OK, Poor.",
            value=rating,
        )

    comment = data.get("comment")
    if comment is not None and not isinstance(comment, str):
        raise ValidationError("invalid_comment", "Comment must be text.")
    comment = (comment or "").strip() or None
    if comment is not None and len(comment) > COMMENT_MAX_LENGTH:
        raise ValidationError(
            "comment_too_long",
            f"Comment must be at most {COMMENT_MAX_LENGTH} characters.",
        )
    return rating, comment
