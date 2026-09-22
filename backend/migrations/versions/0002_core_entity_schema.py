"""Create core entity tables, foreign keys, and spatial indices.

Revision ID: 0002_core_entity_schema
Revises: 0001_initial_extensions
Create Date: 2026-09-20 22:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision: str = "0002_core_entity_schema"
down_revision: Union[str, None] = "0001_initial_extensions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Sources table
    op.create_table(
        "sources",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("domain", sa.String(255), nullable=False),
        sa.Column("source_type", sa.String(50), server_default="rss", nullable=False),
        sa.Column("rss_url", sa.Text(), nullable=True),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("priority", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_sources_domain", "sources", ["domain"])

    # 2. Articles table
    op.create_table(
        "articles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("source_id", UUID(as_uuid=True), sa.ForeignKey("sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("canonical_url", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("summary_raw", sa.Text(), nullable=True),
        sa.Column("content_excerpt", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("language", sa.String(10), server_default="vi", nullable=False),
        sa.Column("raw_metadata", JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
    )
    op.create_index("idx_articles_canonical_url", "articles", ["canonical_url"], unique=True)
    op.create_index("idx_articles_content_hash", "articles", ["content_hash"])
    op.create_index("idx_articles_published_at", "articles", ["published_at"])
    op.create_index("idx_articles_source_published", "articles", ["source_id", "published_at"])

    # 3. Locations table (with PostGIS Point)
    op.create_table(
        "locations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("normalized_text", sa.Text(), nullable=False),
        sa.Column("province", sa.String(100), nullable=True),
        sa.Column("district", sa.String(100), nullable=True),
        sa.Column("ward", sa.String(100), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("provider", sa.String(50), server_default="internal", nullable=False),
        sa.Column("confidence", sa.Float(), server_default=sa.text("1.0"), nullable=False),
        sa.Column("geom", Geometry(geometry_type="POINT", srid=4326, spatial_index=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_locations_province", "locations", ["province"])

    # 4. Events table (with PostGIS Point)
    op.create_table(
        "events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("normalized_title", sa.Text(), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("location_label", sa.String(255), nullable=True),
        sa.Column("location_confidence", sa.Float(), server_default=sa.text("1.0"), nullable=False),
        sa.Column("geom", Geometry(geometry_type="POINT", srid=4326, spatial_index=True), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("first_reported_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("status", sa.String(30), server_default="active", nullable=False),
        sa.Column("confidence_score", sa.Float(), server_default=sa.text("0.5"), nullable=False),
        sa.Column("article_count", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("source_count", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_events_category", "events", ["category"])
    op.create_index("idx_events_status", "events", ["status"])
    op.create_index("idx_events_occurred_at", "events", ["occurred_at"])
    op.create_index("idx_events_last_updated_at", "events", ["last_updated_at"])

    # 5. EventArticles (Associative table)
    op.create_table(
        "event_articles",
        sa.Column("event_id", UUID(as_uuid=True), sa.ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("article_id", UUID(as_uuid=True), sa.ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("match_score", sa.Float(), server_default=sa.text("1.0"), nullable=False),
        sa.Column("match_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_event_articles_event", "event_articles", ["event_id"])
    op.create_index("idx_event_articles_article", "event_articles", ["article_id"])

    # 6. EventFacts
    op.create_table(
        "event_facts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("event_id", UUID(as_uuid=True), sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("fact_key", sa.String(100), nullable=False),
        sa.Column("fact_value", sa.Text(), nullable=False),
        sa.Column("fact_confidence", sa.Float(), server_default=sa.text("1.0"), nullable=False),
        sa.Column("supporting_article_count", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_event_facts_event", "event_facts", ["event_id"])

    # 7. EventTimeline
    op.create_table(
        "event_timeline",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("event_id", UUID(as_uuid=True), sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("timeline_type", sa.String(50), server_default="reported", nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("source_article_id", UUID(as_uuid=True), sa.ForeignKey("articles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_event_timeline_event", "event_timeline", ["event_id"])

    # 8. HistoricalSnapshots
    op.create_table(
        "historical_snapshots",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("event_id", UUID(as_uuid=True), sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("article_count", sa.Integer(), nullable=False),
        sa.Column("source_count", sa.Integer(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("idx_snapshots_event_captured", "historical_snapshots", ["event_id", "captured_at"])

    # 9. ProcessingJobs
    op.create_table(
        "processing_jobs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("job_type", sa.String(50), nullable=False),
        sa.Column("entity_id", UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(30), server_default="pending", nullable=False),
        sa.Column("attempt", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("max_attempts", sa.Integer(), server_default=sa.text("3"), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_processing_jobs_type_status_sched", "processing_jobs", ["job_type", "status", "scheduled_at"])


def downgrade() -> None:
    op.drop_table("processing_jobs")
    op.drop_table("historical_snapshots")
    op.drop_table("event_timeline")
    op.drop_table("event_facts")
    op.drop_table("event_articles")
    op.drop_table("events")
    op.drop_table("locations")
    op.drop_table("articles")
    op.drop_table("sources")
