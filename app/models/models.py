from sqlalchemy import Table, MetaData

# Shared MetaData object
metadata = MetaData()

# First table
Event = Table('events')

# Second table
User = Table('users')