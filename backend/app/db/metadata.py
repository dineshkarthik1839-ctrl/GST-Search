from app.db.base_class import Base

# Import all models here so Alembic can discover them
from app.modules.users.models import *
from app.modules.academic.models import *
from app.modules.content.models import *
from app.modules.assessment.models import *
from app.modules.engagement.models import *
from app.modules.audit.models import *
from app.modules.auth.models import *
