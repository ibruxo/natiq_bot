class Chat(Base):
    __tablename__ = "chats"

    id = mapped_column(primary_key=True)
    telegram_id = mapped_column(BigInteger, unique=True)
    type = mapped_column(String)  # private/group/channel
    title = mapped_column(String, nullable=True)
