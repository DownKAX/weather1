"""test data

Revision ID: cc0f57d28700
Revises: 5b61b82cba28
Create Date: 2025-07-27 19:30:08.500854

"""
from typing import Sequence, Union
from alembic import op
from sqlalchemy.sql import table, column
from sqlalchemy import Integer, String, Float

# revision identifiers, used by Alembic.
revision: str = 'cc0f57d28700'
down_revision: Union[str, None] = '5b61b82cba28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

city_table = table('cities',
                   column('id', Integer),
                   column('city_name', String),
                   column('latitude', Float),
                   column('longitude', Float),
                   column('timezone', Integer))

def upgrade() -> None:
    test_data_cities = [{'city_name': 'City1', 'latitude': 45, 'longitude': 50, 'timezone': 3},
                        {'city_name': 'City2', 'latitude': 45, 'longitude': 34, 'timezone': 5},
                        {'city_name': 'City3', 'latitude': 45, 'longitude': 53, 'timezone': 7}]
    op.bulk_insert(city_table, test_data_cities)


def downgrade() -> None:
    op.execute('TRUNCATE TABLE cities RESTART IDENTITY CASCADE;')
