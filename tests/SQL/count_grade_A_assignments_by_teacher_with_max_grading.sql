WITH teacher_grades AS (
    SELECT 
        teacher_id, 
        COUNT(*) AS total_grades
    FROM assignments
    WHERE grade IS NOT NULL  -- Only consider graded assignments
    GROUP BY teacher_id
)
SELECT COUNT(*)
FROM assignments
WHERE grade = 'A'  -- Only count grade 'A' assignments
AND teacher_id = (
    SELECT teacher_id
    FROM teacher_grades
    ORDER BY total_grades DESC
    LIMIT 1  -- Get the teacher with the maximum graded assignments
);
