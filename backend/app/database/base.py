# Import all the models, so that Base has them before being
# imported by Alembic or used elsewhere.
from app.database.session import Base  # noqa
from app.models.user import User  # noqa
from app.models.document import Document  # noqa
from app.models.chat_session import ChatSession  # noqa
from app.models.ai_audit_log import AiAuditLog  # noqa
from app.models.vendor import Vendor  # noqa
from app.models.invoice import Invoice  # noqa
from app.models.invoice_item import InvoiceItem  # noqa
from app.models.payment import Payment  # noqa
