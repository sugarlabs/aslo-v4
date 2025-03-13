# Fix for Issue #77: Frequent duplicates on default page

## Description
This PR fixes the issue of duplicate activities appearing on the default page of the Sugar Labs Activities Store (ASLO-v4).

## Related Issue
Fixes #77

## Approach
The fix consists of two parts:

1. **Frontend Fix (search.js)**:
   - Added duplicate checking in the `loadAllActivities()` function
   - Created a Set to track bundle_ids that have already been added to the page
   - Only add an activity card if its bundle_id hasn't been seen before

2. **Backend Fix (generator.py)**:
   - Modified the index generation to check for existing bundle_ids
   - Update existing entries instead of adding duplicates
   - Only add new entries for activities that don't already exist in the index

## Testing Done
- Generated the activities store with test activities
- Verified no duplicate activities appear on the default page
- Tested search functionality to ensure no duplicates in search results

## Screenshots (if applicable)
[Add screenshots here if available]

## Additional Notes
This fix maintains all the existing functionality while ensuring each activity appears only once on the page. The changes are minimal and focused on solving the specific issue without introducing new problems. 