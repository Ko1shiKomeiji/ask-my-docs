from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, Computed, ForeignKey, Identity, Index, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ask_my_docs_api.db.base import Base, CreatedAtMixin, UpdatedAtMixin


class User(CreatedAtMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True)
    name: Mapped[str | None]

    api_keys: Mapped[list["ApiKey"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="raise",
    )
    documents: Mapped[list["Document"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="raise",
    )


class ApiKey(CreatedAtMixin, Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    key_hash: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    revoked_at: Mapped[datetime | None]

    owner: Mapped["User"] = relationship(back_populates="api_keys", lazy="raise")


class Document(CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "documents"
    __table_args__ = (UniqueConstraint("user_id", "sha256"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str]
    filename: Mapped[str]
    content_type: Mapped[str]
    size_bytes: Mapped[int]
    sha256: Mapped[str]
    storage_key: Mapped[str]
    chunks_count: Mapped[int] = mapped_column(server_default="0")

    owner: Mapped["User"] = relationship(back_populates="documents", lazy="raise")
    chunks: Mapped[list["Chunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="raise",
    )


class Chunk(Base):
    __tablename__ = "chunks"

    __table_args__ = (
        Index(None, "tsv", postgresql_using="gin"),
        UniqueConstraint("document_id", "ord"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    document_id: Mapped[UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    ord: Mapped[int]
    heading: Mapped[str | None]
    heading_path: Mapped[list[str]] = mapped_column(ARRAY(Text))
    content: Mapped[str]
    char_count: Mapped[int]
    tsv: Mapped[str] = mapped_column(
        TSVECTOR,
        Computed(
            "setweight(to_tsvector('russian', coalesce(heading, '')), 'A') || "
            "setweight(to_tsvector('russian', content), 'B')",
            persisted=True,
        ),
        deferred=True,
    )

    document: Mapped["Document"] = relationship(back_populates="chunks", lazy="raise")
