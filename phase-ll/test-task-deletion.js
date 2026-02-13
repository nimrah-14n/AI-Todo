/**
 * Test script to verify task deletion works correctly
 * Run with: node test-task-deletion.js
 */

const API_BASE_URL = 'http://localhost:8001';

async function testTaskDeletion() {
  console.log('🧪 Testing Task Deletion Flow\n');

  // Step 1: Login to get token
  console.log('1️⃣  Logging in...');
  const loginResponse = await fetch(`${API_BASE_URL}/api/auth/signin`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: 'demo@example.com',
      password: 'Demo123456'
    })
  });

  if (!loginResponse.ok) {
    console.error('❌ Login failed');
    return;
  }

  const { token, user } = await loginResponse.json();
  console.log('✅ Logged in as:', user.email);

  // Step 2: Create a test task
  console.log('\n2️⃣  Creating test task...');
  const createResponse = await fetch(`${API_BASE_URL}/api/${user.id}/tasks`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      title: 'Test Task for Deletion',
      description: 'This task will be deleted'
    })
  });

  if (!createResponse.ok) {
    console.error('❌ Task creation failed');
    return;
  }

  const task = await createResponse.json();
  console.log('✅ Task created:', task.id);

  // Step 3: Delete the task
  console.log('\n3️⃣  Deleting task...');
  const deleteResponse = await fetch(`${API_BASE_URL}/api/${user.id}/tasks/${task.id}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  console.log('   Response status:', deleteResponse.status);
  console.log('   Response status text:', deleteResponse.statusText);
  console.log('   Content-Type:', deleteResponse.headers.get('content-type'));

  if (deleteResponse.status === 204) {
    console.log('✅ Task deleted successfully (204 No Content)');
  } else {
    console.error('❌ Unexpected status code:', deleteResponse.status);
    return;
  }

  // Step 4: Verify task is deleted
  console.log('\n4️⃣  Verifying task is deleted...');
  const verifyResponse = await fetch(`${API_BASE_URL}/api/${user.id}/tasks/${task.id}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (verifyResponse.status === 404) {
    console.log('✅ Task confirmed deleted (404 Not Found)');
  } else {
    console.error('❌ Task still exists');
    return;
  }

  console.log('\n' + '='.repeat(50));
  console.log('✅ Task deletion test passed!');
  console.log('='.repeat(50));
  console.log('\n📋 The fix:');
  console.log('- API client now handles 204 No Content responses');
  console.log('- DELETE operations no longer try to parse empty JSON');
  console.log('- Frontend should now delete tasks without errors');
}

testTaskDeletion().catch(console.error);
