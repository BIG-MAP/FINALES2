from FINALES2.schemas import User, generalMetaData


class tenant:
    def __init__(
        self,
        generalMeta: generalMetaData,
        location: str,
        operator: User,
        tenantType: str,
        quantity: str,
    ):
        self.generalMeta: generalMetaData = generalMeta
        self.location: str = location
        self.operator: User = operator
        self.type: str = tenantType
        self.quantity: str

    def to_dict(self):
        pass

    def from_dict(self):
        pass

    def getRequests(self):
        pass

    def postResults(self):
        pass
