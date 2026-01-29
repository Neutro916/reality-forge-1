# TDD Command - AI Coding School

You are in **Test-Driven Development Mode** - LAW 1: TEST BEFORE CODE

## Your Task:
Help the user write tests BEFORE writing any implementation code.

## The TDD Cycle (30 seconds):
```
1. RED: Write a failing test
2. GREEN: Write minimum code to pass test
3. REFACTOR: Improve the code
4. REPEAT
```

## Process:
1. Ask user what functionality they want to implement
2. Write the TEST first that proves it works
3. Run the test - IT SHOULD FAIL (feature doesn't exist yet)
4. Write MINIMUM code to make test pass
5. Run test again - IT SHOULD PASS
6. Refactor if needed
7. Repeat for next piece of functionality

## Rules:
- ❌ NEVER write implementation code before the test
- ❌ NEVER skip running tests
- ✅ Write the simplest test that proves the feature works
- ✅ Make sure test FAILS first (proves test is valid)
- ✅ Write minimum code to pass (no over-engineering)
- ✅ Refactor only AFTER tests pass

## Test Levels:
1. **Unit Tests** - Test individual functions
2. **Integration Tests** - Test components working together
3. **End-to-End Tests** - Test complete user workflow

## Example:
```javascript
// 1. RED: Write failing test
test('submitBug should save to database', async () => {
    const result = await submitBug({title: 'Test', description: 'Test'});
    expect(result.success).toBe(true);
    expect(result.recordId).toBeDefined();
});

// Run test - IT FAILS (submitBug doesn't exist)

// 2. GREEN: Write code to pass test
function submitBug(data) {
    // Minimum code that makes test pass
    const recordId = saveToDatabase(data);
    return {success: true, recordId};
}

// Run test - IT PASSES

// 3. REFACTOR: Improve code
// 4. REPEAT for next feature
```

## At the End:
- ✅ All tests written and passing
- ✅ Feature proven to work
- ✅ Ready for deployment
- ✅ Run AI_CODING_ENFORCER.py to verify

Red → Green → Refactor → Repeat! 🎓
