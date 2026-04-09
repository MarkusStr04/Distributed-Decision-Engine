from database import engine
from models import Decision

Decision.metadata.create_all(bind=engine)
print("Tabelele au fost create!")