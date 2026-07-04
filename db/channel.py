class Channel(Base):
    __tablename__ = "channels"

    id = mapped_column(primary_key=True)
    telegram_id = mapped_column(BigInteger, unique=True)
    title = mapped_column(String)
    username = mapped_column(String, nullable=True)
