import random

from sqlalchemy import and_

from datetime import datetime

from app.models.company import Company


class CompanyAPI:
    @staticmethod
    def get_carousel():
        companies = Company.query.filter(and_(Company.contract_start_date <
                                              datetime.utcnow(),
                                              Company.contract_end_date >
                                              datetime.utcnow(),
                                              Company.logo_file_id != None)  # noqa
                                         ).all()
        random.shuffle(companies)
        return companies
