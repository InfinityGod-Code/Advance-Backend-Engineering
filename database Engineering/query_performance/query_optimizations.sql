select * from badges;

-- this is the way we create index on the some fields 
-- we can also have multiple fields to impose index called composite indexing 
-- before this we have sequential scan but with indexing database engine uses B-Tree 
-- under the hood for searching right destinations quickly.
create index idx_badges_name on tags(id);
-- here by default we have non-clustered index used.
-- however, we can explicilty changes with by mentioning.
create clustered index idx_tags_name on tags(id);