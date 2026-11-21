"""core resume schema

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-21 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建候选人与简历核心表。"""
    op.create_table(
        "candidate",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("full_name", sa.String(length=80), nullable=False),
        sa.Column("headline", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("phone", sa.String(length=40), nullable=False),
        sa.Column("city", sa.String(length=60), nullable=False),
        sa.Column("github_url", sa.String(length=300), nullable=False),
        sa.Column("blog_url", sa.String(length=300), nullable=False),
        sa.Column("website_url", sa.String(length=300), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "certificates",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("issuer", sa.String(length=120), nullable=False),
        sa.Column("issued_on", sa.Date(), nullable=True),
        sa.Column("expires_on", sa.Date(), nullable=True),
        sa.Column("credential_id", sa.String(length=120), nullable=False),
        sa.Column("url", sa.String(length=300), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidate.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_certificates_candidate_id", "certificates", ["candidate_id"])
    op.create_table(
        "educations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=False),
        sa.Column("school", sa.String(length=120), nullable=False),
        sa.Column("degree_level", sa.String(length=20), nullable=False),
        sa.Column("major", sa.String(length=120), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.Column("gpa", sa.String(length=32), nullable=False),
        sa.Column("courses", sa.JSON(), nullable=False),
        sa.Column("thesis", sa.String(length=300), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidate.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_educations_candidate_id", "educations", ["candidate_id"])
    op.create_index("ix_educations_candidate_order", "educations", ["candidate_id", "sort_order"])
    op.create_table(
        "experiences",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=False),
        sa.Column("company", sa.String(length=120), nullable=False),
        sa.Column("role", sa.String(length=120), nullable=False),
        sa.Column("location", sa.String(length=60), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("highlights", sa.JSON(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidate.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_experiences_candidate_id", "experiences", ["candidate_id"])
    op.create_index("ix_experiences_candidate_order", "experiences", ["candidate_id", "sort_order"])
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("direction", sa.String(length=40), nullable=False),
        sa.Column("role", sa.String(length=120), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("repo_url", sa.String(length=300), nullable=False),
        sa.Column("demo_url", sa.String(length=300), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("architecture", sa.Text(), nullable=False),
        sa.Column("highlights", sa.JSON(), nullable=False),
        sa.Column("challenges", sa.Text(), nullable=False),
        sa.Column("retrospective", sa.Text(), nullable=False),
        sa.Column("ci_status", sa.String(length=40), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidate.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_projects_candidate_id", "projects", ["candidate_id"])
    op.create_index("ix_projects_candidate_order", "projects", ["candidate_id", "sort_order"])
    op.create_table(
        "project_metrics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=60), nullable=False),
        sa.Column("value", sa.String(length=60), nullable=False),
        sa.Column("unit", sa.String(length=20), nullable=False),
        sa.Column("note", sa.String(length=200), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_project_metrics_project_order", "project_metrics", ["project_id", "sort_order"]
    )
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=40), nullable=False),
        sa.Column("dimension", sa.String(length=20), nullable=False),
        sa.Column("color", sa.String(length=16), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_tags_dimension", "tags", ["dimension"])
    op.create_table(
        "project_tags",
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("project_id", "tag_id"),
    )
    op.create_index("ix_project_tags_tag", "project_tags", ["tag_id"])
    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=60), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("years", sa.Float(), nullable=True),
        sa.Column("self_score", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidate.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "candidate_id", "category", "name", name="uq_skills_candidate_name"
        ),
    )
    op.create_index(
        "ix_skills_candidate_order", "skills", ["candidate_id", "category", "sort_order"]
    )
    op.create_table(
        "skill_evidence",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("experience_id", sa.Integer(), nullable=True),
        sa.Column("statement", sa.Text(), nullable=False),
        sa.Column("metric_note", sa.String(length=200), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["experience_id"], ["experiences.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_skill_evidence_skill_id", "skill_evidence", ["skill_id"])
    op.create_index("ix_skill_evidence_project", "skill_evidence", ["project_id"])
    op.create_table(
        "resume_versions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("target_role", sa.String(length=120), nullable=False),
        sa.Column("target_jd", sa.Text(), nullable=False),
        sa.Column("template", sa.String(length=40), nullable=False),
        sa.Column("theme", sa.String(length=40), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidate.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_resume_versions_candidate_id", "resume_versions", ["candidate_id"])
    op.create_table(
        "resume_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column("item_type", sa.String(length=20), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("section", sa.String(length=20), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("override_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["version_id"], ["resume_versions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_resume_items_version_order", "resume_items", ["version_id", "sort_order"])
    op.create_index("ix_resume_items_target", "resume_items", ["item_type", "item_id"])
    op.create_table(
        "snapshots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=80), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["version_id"], ["resume_versions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_snapshots_version_time", "snapshots", ["version_id", "created_at"])
    op.create_table(
        "attachments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("owner_type", sa.String(length=20), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("file_name", sa.String(length=200), nullable=False),
        sa.Column("path", sa.String(length=500), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("mime", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_attachments_owner", "attachments", ["owner_type", "owner_id"])


def downgrade() -> None:
    """按依赖逆序删除核心表。"""
    op.drop_index("ix_attachments_owner", table_name="attachments")
    op.drop_table("attachments")
    op.drop_index("ix_snapshots_version_time", table_name="snapshots")
    op.drop_table("snapshots")
    op.drop_index("ix_resume_items_target", table_name="resume_items")
    op.drop_index("ix_resume_items_version_order", table_name="resume_items")
    op.drop_table("resume_items")
    op.drop_index("ix_resume_versions_candidate_id", table_name="resume_versions")
    op.drop_table("resume_versions")
    op.drop_index("ix_skill_evidence_project", table_name="skill_evidence")
    op.drop_index("ix_skill_evidence_skill_id", table_name="skill_evidence")
    op.drop_table("skill_evidence")
    op.drop_index("ix_skills_candidate_order", table_name="skills")
    op.drop_table("skills")
    op.drop_index("ix_project_tags_tag", table_name="project_tags")
    op.drop_table("project_tags")
    op.drop_index("ix_tags_dimension", table_name="tags")
    op.drop_table("tags")
    op.drop_index("ix_project_metrics_project_order", table_name="project_metrics")
    op.drop_table("project_metrics")
    op.drop_index("ix_projects_candidate_order", table_name="projects")
    op.drop_index("ix_projects_candidate_id", table_name="projects")
    op.drop_table("projects")
    op.drop_index("ix_experiences_candidate_order", table_name="experiences")
    op.drop_index("ix_experiences_candidate_id", table_name="experiences")
    op.drop_table("experiences")
    op.drop_index("ix_educations_candidate_order", table_name="educations")
    op.drop_index("ix_educations_candidate_id", table_name="educations")
    op.drop_table("educations")
    op.drop_index("ix_certificates_candidate_id", table_name="certificates")
    op.drop_table("certificates")
    op.drop_table("candidate")
