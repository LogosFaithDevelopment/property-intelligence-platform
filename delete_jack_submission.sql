-- Delete church submission for Jack's test email
-- Run this in Adminer (http://localhost:8080) or via psql

-- First, let's see what we're deleting
SELECT 
    c.id as church_id,
    c.name as church_name,
    c.primary_email,
    a.id as assessment_id,
    a.status,
    p.id as property_id,
    p.street_address
FROM churches c
LEFT JOIN assessments a ON a.church_id = c.id
LEFT JOIN properties p ON a.property_id = p.id
WHERE c.primary_email LIKE '%jack%'
   OR c.primary_email LIKE '%test%';

-- Delete in correct order (respecting foreign keys)
-- Step 1: Delete assessments (references church_id and property_id)
DELETE FROM assessments
WHERE church_id IN (
    SELECT id FROM churches 
    WHERE primary_email LIKE '%jack%' OR primary_email LIKE '%test%'
);

-- Step 2: Delete properties (if they exist and are only linked to this church)
DELETE FROM properties
WHERE id IN (
    SELECT DISTINCT a.property_id 
    FROM assessments a
    JOIN churches c ON a.church_id = c.id
    WHERE c.primary_email LIKE '%jack%' OR c.primary_email LIKE '%test%'
);

-- Step 3: Delete the church
DELETE FROM churches
WHERE primary_email LIKE '%jack%' OR primary_email LIKE '%test%';

-- Verify deletion
SELECT COUNT(*) as remaining_test_churches
FROM churches
WHERE primary_email LIKE '%jack%' OR primary_email LIKE '%test%';
