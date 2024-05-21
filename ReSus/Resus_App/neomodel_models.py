from neomodel import StructuredNode, StringProperty, BooleanProperty, UniqueIdProperty

class NeoUser(StructuredNode):
    uid = UniqueIdProperty()
    email = StringProperty(unique=True, required=True)
    is_active = BooleanProperty(default=True)
    is_superuser = BooleanProperty(default=False)

    def __str__(self):
        return self.email
