from sqlalchemy import Column, ForeignKey, Integer, Text

from app.models.base import ProjectDonationBaseClass


class Donation(ProjectDonationBaseClass):

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    comment = Column(Text)

    def __repr__(self) -> str:
        return (f'Donation from user_id: {self.user_id}; '
                f'comment: {self.comment}; '
                f'full_amount: {self.full_amount}; '
                f'create date: {self.create_date}.')
