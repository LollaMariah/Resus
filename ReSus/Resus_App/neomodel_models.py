from neomodel import StructuredNode, StringProperty, BooleanProperty, UniqueIdProperty, DateTimeProperty

class NeoUser(StructuredNode):
    uid = UniqueIdProperty()
    email = StringProperty(unique=True, required=True)
    is_active = BooleanProperty(default=True)
    is_superuser = BooleanProperty(default=False)

    def __str__(self):
        return self.email

class Topic(StructuredNode):
    name = StringProperty(unique_index=True)

class Course(StructuredNode):
    courseId = StringProperty(unique_index=True)
    title = StringProperty()
    url = StringProperty()
    image = StringProperty()
    price = StringProperty()
    platform = StringProperty()
    is_about = RelationshipTo('Topic', 'IS_ABOUT')

class User(StructuredNode):
    userId = StringProperty(unique_index=True)
    name = StringProperty()
    has_accessed = RelationshipTo(Course, 'HAS_ACCESSED')