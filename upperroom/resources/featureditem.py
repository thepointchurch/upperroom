SQL_DROP = "DROP VIEW IF EXISTS resources_featureditem;"
SQL_CREATE = [
    "DROP VIEW IF EXISTS resources_featureditem;",
    """CREATE VIEW resources_featureditem AS
                 SELECT title,
                        slug,
                        description,
                        priority,
                        is_private,
                        'R' AS type
                   FROM resources_resource WHERE priority IS NOT NULL AND is_published
                   UNION
                   SELECT name AS title,
                          slug,
                          description,
                          priority,
                          is_private,
                          'T' AS type
                     FROM resources_tag WHERE priority IS NOT NULL;""",
]
