# Fix for Issue #77: Frequent duplicates on default page

This fix addresses the issue of duplicate activities appearing on the default page of the Sugar Labs Activities Store (ASLO-v4).

## Problem

Activities were appearing multiple times on the default page of the activities store. This was happening due to two main reasons:

1. The `index.json` file could potentially contain duplicate entries for the same activities
2. The frontend JavaScript code didn't check for duplicates when displaying activities

## Solution

The fix consists of two parts:

### 1. Frontend Fix (search.js)

Added duplicate checking in the `loadAllActivities()` function in `search.js`:
- Created a Set to track bundle_ids that have already been added to the page
- Only add an activity card if its bundle_id hasn't been seen before

This ensures that even if the `index.json` file contains duplicates, they won't be displayed on the page.

### 2. Backend Fix (generator.py)

Modified the index generation in `generator.py`:
- Before adding a new activity to the index, check if an activity with the same bundle_id already exists
- If it exists, update the existing entry instead of adding a duplicate
- Only add new entries for activities that don't already exist in the index

This prevents duplicates from being added to the `index.json` file in the first place.

## Testing

To test this fix:
1. Generate the activities store with `python -m aslo4 -i ./activities -b -g -p ./aslo4-static`
2. Open the generated site and verify that no duplicate activities appear on the default page
3. Search for activities and verify that search results don't contain duplicates

## Additional Notes

This fix maintains all the existing functionality while ensuring each activity appears only once on the page. The changes are minimal and focused on solving the specific issue without introducing new problems. 