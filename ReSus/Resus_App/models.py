from neomodel import StructuredNode, StringProperty, IntegerProperty, RelationshipFrom, RelationshipTo, UniqueIdProperty, DateTimeProperty, StructuredRel

class AccessRel(StructuredRel):
    date_accessed = DateTimeProperty(default_now=True)

class Topic(StructuredNode):
    topicId = StringProperty(unique_index=True)
    name = StringProperty()
    # Relationship to Course
    is_about = RelationshipFrom('Course', 'IS_ABOUT')

class Platform(StructuredNode):
    platformId = StringProperty(unique_index=True)
    name = StringProperty()
    weight = IntegerProperty()

class Role(StructuredNode):
    role_id = StringProperty(unique_index=True)
    name = StringProperty()
    topics = RelationshipTo(Topic, 'CONSIST_OF')

class User(StructuredNode):
    userId = UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)
    email = StringProperty(unique_index=True, required=True)
    password = StringProperty(required=True)

    # Relationship to Course
    has_accessed = RelationshipTo('Course', 'HAS_ACCESSED', model=AccessRel)

    def __str__(self):
        return self.name

class Course(StructuredNode):
    courseId = StringProperty(unique_index=True)
    title = StringProperty()
    description = StringProperty()
    duration = StringProperty()
    image = StringProperty()
    level = StringProperty()
    price = StringProperty()
    url = StringProperty()
    degree = IntegerProperty()

    # Relationship from User
    accessed_by = RelationshipFrom('User', 'HAS_ACCESSED', model=AccessRel)

    # Relationship to Topic
    is_about = RelationshipTo(Topic, 'IS_ABOUT')

    # Relationship to Platform
    belongs_to = RelationshipTo(Platform, 'BELONGS_TO')

    def get_accessed_degree(self):
        # Count the number of users who have accessed this course
        return len(self.accessed_by.all())
