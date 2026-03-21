"""Add PostGIS extension and geo_point column to locations

Revision ID: b5c8f2a9d1e4
Revises: d29b9e75c0e5
Create Date: 2026-03-21 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geography

# revision identifiers, used by Alembic.
revision: str = "b5c8f2a9d1e4"
down_revision: Union[str, None] = "d29b9e75c0e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.add_column(
        "locations",
        sa.Column(
            "geo_point",
            Geography(geometry_type="POINT", srid=4326),
            nullable=True,
        ),
        schema="geo_app",
    )

    # Populate geo_point from existing lat/lon data
    op.execute(
        """
        UPDATE geo_app.locations
        SET geo_point = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)::geography
        WHERE longitude IS NOT NULL AND latitude IS NOT NULL
        """
    )

    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_locations_geo_point "
        "ON geo_app.locations USING gist (geo_point)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS geo_app.idx_locations_geo_point")
    op.drop_column("locations", "geo_point", schema="geo_app")
