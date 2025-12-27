"""change_member_skills_to_json

Revision ID: 0ec1aa542677
Revises: 6b6da3eebbcd
Create Date: 2025-12-27 21:07:29.969119

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0ec1aa542677"
down_revision: Union[str, None] = "6b6da3eebbcd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Use raw SQL for type conversion with proper casting
    op.execute("ALTER TABLE members ALTER COLUMN skills TYPE JSON USING to_json(skills)")


def downgrade() -> None:
    """Downgrade database schema."""
    # Convert back to array
    op.execute("""
        ALTER TABLE members
        ALTER COLUMN skills TYPE VARCHAR(100)[]
        USING ARRAY(SELECT jsonb_array_elements_text(skills::jsonb))
    """)
