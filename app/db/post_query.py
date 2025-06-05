from sqlalchemy import text

POST_MAIN_CATEGORY = text(
    """
    insert into category (title, user_id, updated_at)
    values (:title, :user_id, now())
    returning id
    """
)

GET_CATEGORIY_BY_ID = text(
    """
    select c1.id as id, c1.title as title, 
           coalesce(
               json_agg(
                   json_build_object('id', c2.id, 'title', c2.title)
               ) filter (where c2.id is not null), 
               '[]'
           ) as sub_categories
    from category c1
    left join category c2 on c1.id = c2.parents_id
    where c1.id = :id
    group by c1.id, c1.title
    """
)

POST_SUB_CATEGORY = text(
    """
    insert into category (title, parents_id, user_id, updated_at)
    values (:title, :parents_id, :user_id, now())
    """
)

GET_CATEGORIES = text(
    """
    select c1.id as id, c1.title as title, 
           coalesce(
               json_agg(
                   json_build_object('id', c2.id, 'title', c2.title)
                   order by c2.updated_at desc
               ) filter (where c2.id is not null), 
               '[]'
           ) as sub_categories
    from category c1
    left join category c2 on c1.id = c2.parents_id
    where c1.user_id = :user_id and c1.parents_id is null
    group by c1.id, c1.title, c1.updated_at
    order by c1.updated_at desc
    """
)


UPDATE_CATEGORY = text(
    """
    update category
    set title = :title, updated_at = now()
    where id = :id and user_id = :user_id
    """
)

DELETE_CATEGORY = text(
    """
    delete from category
    where id = :id and user_id = :user_id
    """
)
