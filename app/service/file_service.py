import mimetypes
import re

from app import hashfs
from app.enums import FileCategory
from app.repository import file_repository
from app.exceptions import ResourceNotFoundException


FILENAME_REGEX = re.compile(r'(.+)\.([^\s.]+)')


def add_file(category, data, filename):
    m = FILENAME_REGEX.match(filename)
    if not m:
        extension = ""
    else:
        extension = m.group(2)

    if category == FileCategory.UPLOADS:
        orig_display_name = m.group(1)

        display_name = orig_display_name
        filename_unique = False
        i = 0

        # Create a unique full display name
        while not filename_unique:
            i += 1
            duplicate = file_repository.find_file_by_display_name(
                display_name, extension)
            if duplicate is not None:
                display_name = "{}_{}".format(orig_display_name, i)
            else:
                filename_unique = True

    address = hashfs.put(data)

    f = file_repository.create_file()
    f.display_name = display_name
    f.hash = address.id
    f.extension = extension
    f.category = category

    file_repository.save(f)

    return f


def delete_file(_file):
    _hash = _file.hash
    file_repository.delete(_file)
    if len(file_repository.find_all_files_by_hash(_hash)) == 0:
        hashfs.delete(_hash)


def get_file_by_id(file_id):
    f = file_repository.find_file_by_id(file_id)
    if not f:
        raise ResourceNotFoundException("file", file_id)
    return f


def get_file_content(_file):
    with hashfs.open(_file.hash) as f:
        content = f.read()

    return content


def get_file_mimetype(_file):
    try:
        return mimetypes.types_map['.' + _file.extension]
    except KeyError:
        return None


def get_all_files_in_category(category, page_nr=None, per_page=None):
    return file_repository.find_all_files_by_category(category,
                                                      page_nr, per_page)


def get_all_files(page_nr=None, per_page=None):
    return file_repository.find_all_files(page_nr, per_page)
