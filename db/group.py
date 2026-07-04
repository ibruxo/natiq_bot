class Group(Base):
    __tablename__ = "groups"

    id = mapped_column(primary_key=True)
    telegram_id = mapped_column(BigInteger, unique=True)
    title = mapped_column(String)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
