from model.attachment import Comment
from model.ideation import Ideation
from model.invest import Investment
from model.user import User


class TestModels:
    def test_create_user(self, db_session):
        user = User(
            name="Test User",
            email="test@example.com",
            _password="hashed_password",
        )
        db_session.add(user)
        db_session.commit()

        fetched_user = (
            db_session.query(User).filter_by(name="Test User").first()
        )
        assert fetched_user is not None
        assert fetched_user.email == "test@example.com"

    def test_create_ideation(self, db_session):
        user = User(
            name="Test User",
            email="test@example.com",
            _password="hashed_password",
        )
        db_session.add(user)
        db_session.commit()

        ideation = Ideation(
            title="Test Idea", content="This is a test idea.", user_id=user.id
        )
        db_session.add(ideation)
        db_session.commit()

        fetched_ideation = (
            db_session.query(Ideation).filter_by(title="Test Idea").first()
        )
        assert fetched_ideation is not None
        assert fetched_ideation.content == "This is a test idea."
        assert fetched_ideation.user_id == user.id

    def test_create_comment(self, db_session):
        user = User(
            name="Test User",
            email="test@example.com",
            _password="hashed_password",
        )
        db_session.add(user)
        db_session.commit()

        ideation = Ideation(
            title="Another Test Idea",
            content="Another test idea.",
            user_id=user.id,
        )
        db_session.add(ideation)
        db_session.commit()

        comment = Comment(
            content="Great idea!", rating=5, related_id=ideation.id, user=user
        )
        db_session.add(comment)
        db_session.commit()

        fetched_comment = (
            db_session.query(Comment).filter_by(content="Great idea!").first()
        )
        assert fetched_comment is not None
        assert fetched_comment.rating == 5
        assert fetched_comment.related_id == ideation.id

    def test_create_invest(self, db_session):
        user = User(
            name="Test Investor",
            email="investor@example.com",
            _password="hashed_password",
        )
        db_session.add(user)
        db_session.commit()

        ideation = Ideation(
            title="Test Idea for Investment",
            content="This is a test idea.",
            user_id=user.id,
        )
        db_session.add(ideation)
        db_session.commit()

        invest = Investment(
            ideation_id=ideation.id,
            investor_id=user.id,
            amount=500000,
            approval_status=True,
        )
        db_session.add(invest)
        db_session.commit()

        fetched_invest = (
            db_session.query(Investment).filter_by(id=invest.id).first()
        )
        assert fetched_invest is not None
        assert fetched_invest.amount == 500000
        assert fetched_invest.approval_status is True
        assert fetched_invest.ideation_id == ideation.id
        assert fetched_invest.investor_id == user.id
