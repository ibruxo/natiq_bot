class SocialLink(Base):
    __tablename__ = "social_links"

    id = mapped_column(primary_key=True)
    platform = mapped_column(String)   # instagram, telegram, etc
    url = mapped_column(String)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
