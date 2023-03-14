from FINALES2.schemas import User, generalMetaData


class tenant:
    def __init__(
        self,
        generalMeta: generalMetaData,
        location: str,
        operator: User,
        type: str,
        quantity: str,
    ):
        self.generalMeta: generalMetaData = generalMeta
        self.location: str
        self.operator: User
        self.type: str
        self.quantity: str
