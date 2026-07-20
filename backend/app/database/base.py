# Import all the models, so that Base has them before being
# imported by Alembic or used elsewhere.
from app.database.session import Base  # noqa
from app.models.document import Document  # noqa
