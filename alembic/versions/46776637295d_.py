"""empty message

Revision ID: 46776637295d
Revises: cc0f57d28700
Create Date: 2025-09-01 13:51:15.979076

"""
from datetime import datetime
from typing import Sequence, Union

from datetime import timedelta
from alembic import op
from sqlalchemy import column, table, Integer, String, DateTime, Boolean, BigInteger

# revision identifiers, used by Alembic.
revision: str = '46776637295d'
down_revision: Union[str, None] = 'cc0f57d28700'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

user_table = table('users',
                   column('id', Integer),
                   column('username', String),
                   column('password', String),
                   column('register_time', DateTime),
                   column('city_id', Integer),
                   column('telegram_id', BigInteger),
                   column('newsletter', Boolean))

def upgrade() -> None:
    time = datetime(2025, 7, 20, 15, 56, 40)
    # user1234, user13254, user45345
    test_data_users = [{'username': 'user1', 'password': "$2b$12$m8kmdT8Dr8emzfq/G.eLRO4Q13iYc/9nvn5amLNsKh8cFpzQdLOCC", 'register_time': time, 'city_id': 1,
                        'telegram_id': 591989105, 'newsletter': True},
                       {'username': 'user2', 'password': '$2b$12$DnzNGM52Bfjb6I2TGI7RgOAGlHuikjjvRdhIsYdZVyzUVv3oATPRu', 'register_time': time + timedelta(hours=1),
                        'city_id': 2, 'telegram_id': 5919891051, 'newsletter': False},
                       {'username': 'user3', 'password': '$2b$12$2H8CcXgq0k/3ye6tcIZtfOGR8umtHmclPNRnk4Utm12Qwpq9Uoeym', 'register_time': time + timedelta(hours=2),
                        'city_id': 3, 'telegram_id': 5919891021, 'newsletter': True}]
    op.bulk_insert(user_table, test_data_users)

def downgrade() -> None:
    op.execute('TRUNCATE TABLE users RESTART IDENTITY CASCADE;')