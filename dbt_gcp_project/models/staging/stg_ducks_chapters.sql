SELECT *
FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY chapter_id ORDER BY chapter_id) as rn
    FROM {{ source('du_raw', 'ducks_chapters') }}
)
WHERE rn = 1
