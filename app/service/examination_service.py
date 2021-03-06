import datetime
from flask_sqlalchemy import Pagination

from app.exceptions.base import ResourceNotFoundException, \
    BusinessRuleException, DuplicateResourceException
from app.models.course import Course
from app.repository import examination_repository


def get_examination_by_id(examination_id):
    exam = examination_repository.find_examination_by_id(examination_id)
    if not exam:
        raise ResourceNotFoundException("Examination", examination_id)
    return exam


def get_education_by_id(education_id):
    education = examination_repository.find_education_by_id(education_id)
    if not education:
        raise ResourceNotFoundException("Education", education_id)
    return education


def get_course_by_id(course_id: int) -> Course:
    course = examination_repository.find_course_by_id(course_id)
    if not course:
        raise ResourceNotFoundException("Course", course_id)
    return course


def find_all_courses():
    return examination_repository.find_all_courses()


def paginated_search_courses(search: str, page: int) -> Pagination:
    return examination_repository.paginated_search_all_courses(
        search=search, page=page)


def find_all_educations():
    return examination_repository.find_all_educations()


def paginated_search_educations(search: str, page: int) -> Pagination:
    return examination_repository.paginated_search_all_educations(
        search=search, page=page)


def find_all_examinations_by_course(course_id):
    get_course_by_id(course_id)
    return examination_repository.find_all_examinations_by_course(course_id)


def find_all_examinations_by_education(education_id):
    get_education_by_id(education_id)
    return examination_repository \
        .find_all_examinations_by_education(education_id)


def find_all_examinations(page_nr, per_page):
    return examination_repository.find_all_examinations(page_nr, per_page)


def search_examinations_by_courses(courses, page_nr, per_page):
    return examination_repository \
        .search_examinations_by_courses(courses, page_nr, per_page)


def add_course(name, description):
    existing_course = examination_repository.find_course_by_name(name)
    if existing_course:
        raise DuplicateResourceException(name, existing_course.id)

    course = examination_repository.create_course()
    course.name = name
    course.description = description

    examination_repository.save_course(course)

    return course


def add_education(name):
    existing_education = examination_repository.find_education_by_name(name)
    if existing_education:
        raise DuplicateResourceException(name, existing_education.id)

    education = examination_repository.create_education()
    education.name = name

    examination_repository.save_education(education)

    return education


def add_examination(examination_file, date, comment,
                    course_id, education_id, test_type,
                    answers_file=None):
    exam = examination_repository.create_examination()

    exam.timestamp = datetime.datetime.utcnow()
    exam.examination_file = examination_file
    exam.date = date
    exam.comment = comment
    exam.course_id = course_id
    exam.education_id = education_id
    exam.answers_file = answers_file
    exam.test_type = test_type

    examination_repository.save_examination(exam)

    return exam


def update_examination(exam_id, examination_file, date, comment,
                       course_id, education_id, test_type,
                       answers_file=None):
    exam = examination_repository.find_examination_by_id(exam_id)

    exam.timestamp = datetime.datetime.utcnow()
    exam.examination_file = examination_file
    exam.date = date
    exam.comment = comment
    exam.course_id = course_id
    exam.education_id = education_id
    exam.answers_file = answers_file
    exam.test_type = test_type

    examination_repository.save_education(exam)

    return exam


def update_education(education_id, name):
    education = examination_repository.find_education_by_id(education_id)
    if education.name != name and \
            examination_repository.find_course_by_name(name):
        raise DuplicateResourceException("Education", name)
    education.name = name

    examination_repository.save_education(education)

    return education


def update_course(course_id, name, description):
    course = examination_repository.find_course_by_id(course_id)
    if course.name != name and \
            examination_repository.find_course_by_name(name):
        raise DuplicateResourceException("Course", name)
    course.name = name
    course.description = description

    examination_repository.save_course(course)

    return course


def delete_examination(examination_id):
    examination_repository.delete_examination(examination_id)


def count_examinations_by_course(course: Course):
    exams = examination_repository.find_all_examinations_by_course(course.id)
    return len(exams)


def count_examinations_by_education(education_id):
    exams = examination_repository. \
        find_all_examinations_by_education(education_id)
    return len(exams)


def delete_education(education_id):
    if count_examinations_by_education(education_id) >= 1:
        raise BusinessRuleException("Education has examinations")
    else:
        examination_repository.delete_education(education_id)


def delete_course(course_id: int):
    course = get_course_by_id(course_id)
    if count_examinations_by_course(course) >= 1:
        raise BusinessRuleException("Course has examinations")
    else:
        examination_repository.delete_course(course)
