from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
	__abstract__ = True

	@property
	def to_dict(self):
		return {
            column.name: getattr(self, column.name)
            for column in self.__table__.c
        }