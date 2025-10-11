-- Delete Test Churches and All Related Data
-- Churches to delete: jack@rbc.org, john@gracecc.com
-- Date: October 8, 2025

-- ==============================================
-- STEP 1: View what will be deleted (SAFE - just viewing)
-- ==============================================

SELECT 
    '=== CHURCHES TO DELETE ===' as section,
    c.id as church_id, 
    c.name, 
    c.primary_email,
    (SELECT COUNT(*) FROM properties WHERE church_id = c.id) as properties_count,
    (SELECT COUNT(*) FROM submissions WHERE church_id = c.id) as submissions_count,
    (SELECT COUNT(*) FROM assessments WHERE property_id IN (SELECT id FROM properties WHERE church_id = c.id)) as assessments_count
FROM churches c
WHERE c.primary_email IN ('jack@rbc.org', 'john@gracecc.com');

-- ==============================================
-- STEP 2: Delete all related data (DESTRUCTIVE - uncomment to execute)
-- ==============================================

-- Delete assessments first (furthest down the dependency chain)
DELETE FROM assessments 
WHERE property_id IN (
    SELECT id FROM properties 
    WHERE church_id IN (
        SELECT id FROM churches 
        WHERE primary_email IN ('jack@rbc.org', 'john@gracecc.com')
    )
);

-- Delete submissions
DELETE FROM submissions 
WHERE church_id IN (
    SELECT id FROM churches 
    WHERE primary_email IN ('jack@rbc.org', 'john@gracecc.com')
);

-- Delete properties
DELETE FROM properties 
WHERE church_id IN (
    SELECT id FROM churches 
    WHERE primary_email IN ('jack@rbc.org', 'john@gracecc.com')
);

-- Finally, delete the churches
DELETE FROM churches 
WHERE primary_email IN ('jack@rbc.org', 'john@gracecc.com');

-- ==============================================
-- STEP 3: Verify deletion
-- ==============================================

SELECT 
    '=== VERIFICATION - Should be empty ===' as section,
    COUNT(*) as remaining_count
FROM churches 
WHERE primary_email IN ('jack@rbc.org', 'john@gracecc.com');
