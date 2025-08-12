"""test data

Revision ID: cc0f57d28700
Revises: 5b61b82cba28
Create Date: 2025-07-27 19:30:08.500854

"""
from typing import Sequence, Union
from passlib.hash import bcrypt
from alembic import op
from datetime import datetime, timedelta
from sqlalchemy.sql import table, column
from sqlalchemy import Integer, String, Float, DateTime, Boolean

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

user_table = table('users',
                   column('id', Integer),
                   column('username', String),
                   column('password', String),
                   column('register_time', DateTime),
                   column('city_id', Integer),
                   column('telegram_id', Integer),
                   column('newsletter', Boolean))


def upgrade() -> None:
    test_data_cities = [{'id': 1, 'city_name': 'City1', 'latitude': 45, 'longitude': 50, 'timezone': 3},
                        {'id': 2, 'city_name': 'City2', 'latitude': 45, 'longitude': 34, 'timezone': 5},
                        {'id': 3, 'city_name': 'City3', 'latitude': 45, 'longitude': 53, 'timezone': 7}]
    time = datetime(2025, 7, 20, 15, 56, 40)
    # user1234, user13254, user45345
    test_data_users = [{'id': 1, 'username': 'user1', 'password': "$2b$12$m8kmdT8Dr8emzfq/G.eLRO4Q13iYc/9nvn5amLNsKh8cFpzQdLOCC", 'register_time': time, 'city_id': 1,
                        'telegram_id': 591989105, 'newsletter': True},
                       {'id': 2, 'username': 'user2', 'password': '$2b$12$DnzNGM52Bfjb6I2TGI7RgOAGlHuikjjvRdhIsYdZVyzUVv3oATPRu', 'register_time': time + timedelta(hours=1),
                        'city_id': 2, 'telegram_id': 5919891051, 'newsletter': False},
                       {'id': 3, 'username': 'user3', 'password': '$2b$12$2H8CcXgq0k/3ye6tcIZtfOGR8umtHmclPNRnk4Utm12Qwpq9Uoeym', 'register_time': time + timedelta(hours=2),
                        'city_id': 3, 'telegram_id': 5919891021, 'newsletter': True}]
    op.bulk_insert(city_table, test_data_cities)
    op.bulk_insert(user_table, test_data_users)

def downgrade() -> None:
    op.execute('DELETE FROM cities;')
    op.execute('DELETE FROM users;')
