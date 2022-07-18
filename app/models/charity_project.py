from sqlalchemy import Column, String, Text

from app.models.base import ProjectDonationBaseClass


class CharityProject(ProjectDonationBaseClass):

    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)

    def __repr__(self) -> str:
        return (f'Charity Project: {self.name}; '
                f'description: {self.description}; '
                f'create date: {self.create_date}.')
