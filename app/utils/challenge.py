import datetime

from sqlalchemy import and_

from app import db
from app.models.challenge import Challenge, Submission, Competitor
from app.models.page import Page, PageRevision
from app.models.user import User
from app.service import page_service

ALLOWED_EXTENSIONS = set(['png', 'gif', 'jpg', 'jpeg'])
UPLOAD_DIR = 'app/static/files/users/'


class ChallengeAPI:
    @staticmethod
    def create_challenge(name, description, hint, start_date, end_date,
                         parent_id, weight, type, answer):
        """Create a new challenge."""
        new_challenge = Challenge(name, description, hint, start_date,
                                  end_date, parent_id, weight, type, answer)
        db.session.add(new_challenge)
        db.session.commit()

        return "Succes, challenge with name '" + new_challenge.name +\
            "' created!"

    @staticmethod
    def edit_challenge(id, name, description, hint, start_date, end_date,
                       parent_id, weight, type, answer):
        """Create a new challenge."""
        challenge = ChallengeAPI.fetch_challenge(id)
        challenge.name = name
        challenge.description = description
        challenge.hint = hint
        challenge.start_date = start_date
        challenge.end_date = end_date
        challenge.parent_id = parent_id
        challenge.weight = weight
        challenge.type = type
        challenge.answer = answer
        db.session.add(challenge)
        db.session.commit()

        return "Success, challenge with name '" + challenge.name + \
            "' edited!"

    @staticmethod
    def fetch_challenge(id):
        """Fetch a challenge by id."""
        challenge = Challenge.query.filter_by(id=id).first()
        return challenge

    @staticmethod
    def challenge_exists(name):
        """
        Update a challenge.

        Only give the id and new values that have to
        change.
        """
        challenge = Challenge.query.filter_by(name=name).first()

        if challenge is None:
            return False
        else:
            return True

    @staticmethod
    def update_challenge(challenge):
        """Give the altered challenge object."""
        db.session.add(challenge)
        db.session.commit()

    @staticmethod
    def create_submission(challenge_id=None, user_id=None, submission=None,
                          image_path=None):
        """Create a submission for a challenge and user."""
        if ChallengeAPI.is_approved(challenge_id, user_id) or \
                not ChallengeAPI.is_open_challenge(challenge_id):
            return False

        challenge = ChallengeAPI.fetch_challenge(challenge_id)
        user = User.query.filter_by(id=user_id).first()
        # convert the name.
        new_submission = Submission(challenge_id, challenge, user_id, user,
                                    submission, image_path, approved=False)
        db.session.add(new_submission)
        db.session.commit()

        return new_submission

    @staticmethod
    def can_auto_validate(challenge):
        """Check if a challenge can be auto validated."""
        if challenge.type == 'Text':
            return True
        else:
            return False

    @staticmethod
    def validate_question(submission, challenge):
        """
        Check if a question is valid.

        Submission: String to be validated
        Challenge: Challenge object
        """
        if not ChallengeAPI.can_auto_validate(challenge):
            return 'Not validated'

        if submission.answer.lower() == challenge.answer.lower():
            submission.approved = True
            ChallengeAPI.assign_points_to_user(challenge.weight,
                                               submission.user_id)
            db.session.add(submission)
            db.session.commit()
            return 'Approved'
        else:
            return 'Bad answer'

    @staticmethod
    def fetch_unvalided_submissions(challenge_id):
        return Submission.query.filter_by(challenge_id=challenge_id).all()

    @staticmethod
    def fetch_all_challenges():
        """Fetch all challenges, no filters applied."""
        return Challenge.query.all()

    @staticmethod
    def fetch_all_challenges_user(user_id):
        """

        """
        ids = db.session.query(Challenge.id).join(Submission)\
            .filter(and_(Submission.user_id == user_id,
                         Submission.approved == True)).all()  # noqa
        ids = map(lambda x: x[0], ids)
        return Challenge.query\
            .filter(~Challenge.id.in_(ids),
                    Challenge.start_date <= datetime.date.today(),
                    Challenge.end_date >= datetime.date.today()).all()

    @staticmethod
    def fetch_all_approved_challenges_user(user_id):
        return Challenge.query.join(Submission)\
            .filter(Submission.user_id == user_id, Submission.approved == True)  # noqa

    @staticmethod
    def is_open_challenge(challenge_id):
        challenge = Challenge.query\
            .filter(and_(Challenge.start_date <= datetime.date.today(),
                         Challenge.end_date >= datetime.date.today())).first()
        if challenge is None:
            return False
        else:
            return True

    @staticmethod
    def is_approved(challenge_id, user_id):
        submission = Submission.query\
            .filter(and_(Submission.user_id == user_id,
                         Submission.challenge_id == challenge_id,
                         Submission.approved == True)).first()  # noqa

        if submission is None:
            return False
        else:
            return True

    @staticmethod
    def get_points(user_id):
        competitor = Competitor.query\
            .filter(Competitor.user_id == user_id).first()

        if competitor is None:
            return None
        else:
            return competitor.points

    @staticmethod
    def assign_points_to_user(points, user_id):
        competitor = Competitor.query\
            .filter(Competitor.user_id == user_id).first()

        if competitor is None:
            competitor = Competitor(user_id)
            competitor.points = points
            db.session.add(competitor)
            db.session.commit()
        else:
            competitor.points = competitor.points + points
            db.session.add(competitor)
            db.session.commit()

    @staticmethod
    def get_ranking():
        competitors = Competitor.query.order_by(Competitor.points.desc()).all()
        return competitors

    @staticmethod
    def get_challenge_description():
        """ Get the description page for challenges """
        page = page_service.get_page_by_path(
            Page.strip_path("challenge_description"))

        if not page:
            revision = PageRevision(None, None, None, None, None)
            revision.title = 'Not found!'
            revision.content = 'Description not found'
        else:
            revision = page.get_latest_revision()

        return revision
