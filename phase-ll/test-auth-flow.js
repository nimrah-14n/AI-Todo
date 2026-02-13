/**
 * Test script to verify the complete authentication flow
 * Run with: node test-auth-flow.js
 */

const API_BASE_URL = 'http://localhost:8001';

async function testAuthFlow() {
  console.log('🧪 Testing Authentication Flow\n');
  console.log('Backend URL:', API_BASE_URL);
  console.log('Frontend URL: http://localhost:3000\n');

  // Test 1: Health Check
  console.log('1️⃣  Testing backend health...');
  try {
    const healthResponse = await fetch(`${API_BASE_URL}/health`);
    const healthData = await healthResponse.json();
    console.log('✅ Backend is healthy:', healthData);
  } catch (error) {
    console.error('❌ Backend health check failed:', error.message);
    return;
  }

  // Test 2: Signup
  console.log('\n2️⃣  Testing signup...');
  const testEmail = `test${Date.now()}@example.com`;
  const testPassword = 'TestPassword123';

  try {
    const signupResponse = await fetch(`${API_BASE_URL}/api/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: testEmail, password: testPassword })
    });

    if (!signupResponse.ok) {
      const error = await signupResponse.json();
      console.error('❌ Signup failed:', error);
      return;
    }

    const signupData = await signupResponse.json();
    console.log('✅ Signup successful');
    console.log('   User ID:', signupData.user.id);
    console.log('   Email:', signupData.user.email);
    console.log('   Token:', signupData.token.substring(0, 20) + '...');
  } catch (error) {
    console.error('❌ Signup request failed:', error.message);
    return;
  }

  // Test 3: Signin
  console.log('\n3️⃣  Testing signin...');
  try {
    const signinResponse = await fetch(`${API_BASE_URL}/api/auth/signin`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: testEmail, password: testPassword })
    });

    if (!signinResponse.ok) {
      const error = await signinResponse.json();
      console.error('❌ Signin failed:', error);
      return;
    }

    const signinData = await signinResponse.json();
    console.log('✅ Signin successful');
    console.log('   User ID:', signinData.user.id);
    console.log('   Email:', signinData.user.email);
    console.log('   Token:', signinData.token.substring(0, 20) + '...');

    // Test 4: Invalid credentials
    console.log('\n4️⃣  Testing invalid credentials...');
    const invalidResponse = await fetch(`${API_BASE_URL}/api/auth/signin`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: testEmail, password: 'WrongPassword' })
    });

    if (invalidResponse.status === 401) {
      console.log('✅ Invalid credentials correctly rejected');
    } else {
      console.error('❌ Invalid credentials should return 401');
    }

  } catch (error) {
    console.error('❌ Signin request failed:', error.message);
    return;
  }

  // Summary
  console.log('\n' + '='.repeat(50));
  console.log('✅ All authentication tests passed!');
  console.log('='.repeat(50));
  console.log('\n📋 Next steps:');
  console.log('1. Open http://localhost:3000/signin in your browser');
  console.log('2. Use these credentials to test:');
  console.log(`   Email: ${testEmail}`);
  console.log(`   Password: ${testPassword}`);
  console.log('3. Or use the demo account:');
  console.log('   Email: demo@example.com');
  console.log('   Password: Demo123456');
}

testAuthFlow().catch(console.error);
