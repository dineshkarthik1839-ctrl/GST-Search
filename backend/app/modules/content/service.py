"""
Content Workflow Service.
Enforces the publishing state machine.
Rule: PUBLISHED content can never be directly edited - a new DRAFT must be spawned.
"""
import uuid
import copy
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from app.modules.content.models import (
    ContentItem, ContentStatus, ContentRevision, ContentAuditLog
)
from app.modules.content.repository import ContentRepository, ContentRevisionRepository
from app.core.logger import logger
from app.core.exceptions import AppException


# Valid workflow transitions
ALLOWED_TRANSITIONS = {
    ContentStatus.DRAFT: [ContentStatus.SUBMITTED, ContentStatus.ARCHIVED],
    ContentStatus.SUBMITTED: [ContentStatus.REVIEW, ContentStatus.DRAFT],
    ContentStatus.REVIEW: [
        ContentStatus.APPROVED,
        ContentStatus.CHANGES_REQUESTED,
        ContentStatus.DRAFT,
    ],
    ContentStatus.CHANGES_REQUESTED: [ContentStatus.SUBMITTED],
    ContentStatus.APPROVED: [ContentStatus.SCHEDULED, ContentStatus.PUBLISHED],
    ContentStatus.SCHEDULED: [ContentStatus.PUBLISHED, ContentStatus.DRAFT],
    ContentStatus.PUBLISHED: [ContentStatus.ARCHIVED],
    ContentStatus.ARCHIVED: [],
}

# Roles that can perform each transition
TRANSITION_ROLES = {
    (ContentStatus.SUBMITTED, ContentStatus.REVIEW): ["Reviewer", "Admin", "Super Admin"],
    (ContentStatus.REVIEW, ContentStatus.APPROVED): ["Reviewer", "Admin", "Super Admin"],
    (ContentStatus.REVIEW, ContentStatus.CHANGES_REQUESTED): ["Reviewer", "Admin", "Super Admin"],
    (ContentStatus.APPROVED, ContentStatus.PUBLISHED): ["Admin", "Super Admin"],
    (ContentStatus.APPROVED, ContentStatus.SCHEDULED): ["Admin", "Super Admin"],
    (ContentStatus.PUBLISHED, ContentStatus.ARCHIVED): ["Admin", "Super Admin"],
}


class ContentWorkflowService:
    def __init__(self, db: Session):
        self.db = db
        self.content_repo = ContentRepository(db)
        self.revision_repo = ContentRevisionRepository(db)

    def _snapshot(self, item: ContentItem) -> Dict[str, Any]:
        """Capture a JSON-serializable snapshot of a ContentItem for revision history."""
        return {
            "id": str(item.id),
            "title": item.title,
            "slug": item.slug,
            "description": item.description,
            "content_type": item.content_type.value,
            "status": item.status.value,
            "version": item.version,
            "language": item.language,
            "thumbnail_url": item.thumbnail_url,
            "publish_date": item.publish_date.isoformat() if item.publish_date else None,
            "expiry_date": item.expiry_date.isoformat() if item.expiry_date else None,
            "metadata_json": item.metadata_json,
            "snapshotted_at": datetime.now(timezone.utc).isoformat(),
        }

    def _audit(
        self,
        item: ContentItem,
        action: str,
        old_status: Optional[ContentStatus],
        new_status: Optional[ContentStatus],
        performed_by_id: Optional[uuid.UUID],
        notes: Optional[str] = None,
    ):
        log = ContentAuditLog(
            content_item_id=item.id,
            action=action,
            old_status=old_status.value if old_status else None,
            new_status=new_status.value if new_status else None,
            performed_by_id=performed_by_id,
            notes=notes,
        )
        self.db.add(log)

    def _create_revision(
        self,
        item: ContentItem,
        performed_by_id: Optional[uuid.UUID],
        change_summary: Optional[str] = None,
    ):
        next_version = self.revision_repo.get_latest_version_number(item.id) + 1
        revision = ContentRevision(
            content_item_id=item.id,
            version_number=next_version,
            snapshot=self._snapshot(item),
            created_by_id=performed_by_id,
            change_summary=change_summary or f"Status changed to {item.status.value}",
        )
        self.db.add(revision)

    def transition(
        self,
        content_id: uuid.UUID,
        new_status: ContentStatus,
        performed_by_id: Optional[uuid.UUID] = None,
        notes: Optional[str] = None,
        publish_date: Optional[datetime] = None,
    ) -> ContentItem:
        item = self.content_repo.get_by_id(content_id)
        if not item:
            raise AppException(message="ContentItem not found", status_code=404)

        old_status = item.status
        allowed = ALLOWED_TRANSITIONS.get(old_status, [])
        if new_status not in allowed:
            raise AppException(
                message=f"Invalid transition: {old_status.value} → {new_status.value}. "
                        f"Allowed: {[s.value for s in allowed]}",
                status_code=422,
            )

        # Save revision snapshot BEFORE mutating
        self._create_revision(item, performed_by_id, notes)

        # Apply transition
        item.status = new_status
        item.updated_at = datetime.now(timezone.utc)

        if new_status == ContentStatus.SCHEDULED and publish_date:
            item.publish_date = publish_date
        if new_status == ContentStatus.PUBLISHED and not item.publish_date:
            item.publish_date = datetime.now(timezone.utc)

        self._audit(item, "STATUS_CHANGED", old_status, new_status, performed_by_id, notes)
        self.db.commit()
        self.db.refresh(item)
        logger.info(f"ContentItem {item.id} transitioned {old_status.value} → {new_status.value}")
        return item

    def spawn_draft_from_published(
        self,
        content_id: uuid.UUID,
        performed_by_id: Optional[uuid.UUID] = None,
    ) -> ContentItem:
        """
        Clone a PUBLISHED ContentItem as a new DRAFT.
        The original remains PUBLISHED and immutable.
        """
        original = self.content_repo.get_by_id(content_id)
        if not original:
            raise AppException(message="ContentItem not found", status_code=404)
        if original.status != ContentStatus.PUBLISHED:
            raise AppException(
                message="Only PUBLISHED content can spawn a new Draft. Use transition() for other statuses.",
                status_code=422,
            )

        new_version_num = original.version + 1
        draft = ContentItem(
            title=original.title,
            slug=f"{original.slug}-v{original.version + 1}",
            description=original.description,
            content_type=original.content_type,
            status=ContentStatus.DRAFT,
            author_id=performed_by_id or original.author_id,
            language=original.language,
            thumbnail_url=original.thumbnail_url,
            metadata_json=copy.deepcopy(original.metadata_json) if original.metadata_json else None,
        )
        self.db.add(draft)
        self.db.commit()
        self.db.refresh(draft)

        # Audit both sides
        self._audit(
            draft, "DRAFT_SPAWNED_FROM_PUBLISHED",
            None, ContentStatus.DRAFT, performed_by_id,
            f"Spawned from published content {original.id}",
        )
        self._create_revision(draft, performed_by_id, f"Initial draft cloned from {original.id}")
        self.db.commit()

        logger.info(f"Spawned new draft {draft.id} from published {original.id}")
        return draft

    def process_scheduled_publishes(self) -> int:
        """
        Called by a scheduler to auto-publish SCHEDULED items whose publish_date has passed.
        Returns count of items published.
        """
        due_items = self.content_repo.get_due_for_publish()
        count = 0
        for item in due_items:
            try:
                self.transition(item.id, ContentStatus.PUBLISHED, notes="Auto-published by scheduler")
                count += 1
            except Exception as e:
                logger.error(f"Failed to auto-publish {item.id}: {e}")
        return count
