from enum import Enum, unique


@unique
class Roles(Enum):
    """
    Roles used to secure the application

    Note: When updating the list of roles, also insert them in the roles
    table.
    """
    ACTIVITY_READ = 'ACTIVITY_READ'
    ACTIVITY_WRITE = 'ACTIVITY_WRITE'
    ALV_READ = 'ALV_READ'
    ALV_WRITE = 'ALV_WRITE'
    CHALLENGE_READ = 'CHALLENGE_READ'
    CHALLENGE_WRITE = 'CHALLENGE_WRITE'
    COMMITTEE_WRITE = 'COMMITTEE_WRITE'
    CONTACT_READ = 'CONTACT_READ'
    CONTACT_WRITE = 'CONTACT_WRITE'
    DOMJUDGE_WRITE = 'DOMJUDGE_WRITE'
    ELECTIONS_READ = 'ELECTIONS_READ'
    ELECTIONS_WRITE = 'ELECTIONS_WRITE'
    EXAMINATION_READ = 'EXAMINATION_READ'
    EXAMINATION_WRITE = 'EXAMINATION_WRITE'
    FILE_READ = 'FILE_READ'
    FILE_WRITE = 'FILE_WRITE'
    GROUP_READ = 'GROUP_READ'
    GROUP_WRITE = 'GROUP_WRITE'
    LOCATION_READ = 'LOCATION_READ'
    LOCATION_WRITE = 'LOCATION_WRITE'
    MOLLIE_READ = 'MOLLIE_READ'
    NAVIGATION_WRITE = 'NAVIGATION_WRITE'
    NEWSLETTER_READ = 'NEWSLETTER_READ'
    NEWSLETTER_WRITE = 'NEWSLETTER_WRITE'
    NEWS_WRITE = 'NEWS_WRITE'
    PAGE_READ = 'PAGE_READ'
    PAGE_WRITE = 'PAGE_WRITE'
    PIMPY_READ = 'PIMPY_READ'
    PIMPY_WRITE = 'PIMPY_WRITE'
    SEO_WRITE = 'SEO_WRITE'
    USER_READ = 'USER_READ'
    USER_WRITE = 'USER_WRITE'
    VACANCY_READ = 'VACANCY_READ'
    VACANCY_WRITE = 'VACANCY_WRITE'
