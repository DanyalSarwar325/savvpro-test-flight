## Task: Generate models.py and database.py

**Tool:** GitHub Copilot (VS Code)

**What it got right:**
- Correct SQLAlchemy 2.x DeclarativeBase style
- Proper Mapped[] type annotations
- Both total_seats and seats_available as separate columns
- booking_reference UNIQUE constraint
- relationship() with back_populates on both sides
- get_db() using yield correctly

**What it got wrong:**
1. Used deprecated datetime.utcnow — fixed to datetime.now(timezone.utc)
2. Placed autocommit=False in SessionLocal() call instead of sessionmaker()
3. Added future=True flag which is a SQLAlchemy 1.x migration flag,
   unnecessary in 2.x
4. cascade="all, delete-orphan" would delete booking history if a 
   flight is deleted — conflicts with our soft-cancellation design

**How I corrected it:**
Manually edited all four issues above before proceeding.
