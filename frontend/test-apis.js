#!/usr/bin/env node

/**
 * Test script to verify all API integrations
 */

const fetch = require('node-fetch');

const GRAPHHOPPER_API_KEY = '38c87f28-1cc5-48a3-977f-39e49d3c78de';

async function testGraphHopperGeocoding() {
  console.log('\n🔍 Testing GraphHopper Geocoding API...');
  const url = `https://graphhopper.com/api/1/geocode?q=San Francisco&key=${GRAPHHOPPER_API_KEY}`;
  
  try {
    const response = await fetch(url);
    const data = await response.json();
    
    if (data.message && data.message.includes('Wrong credentials')) {
      console.log('❌ GraphHopper API key is invalid!');
      console.log('   Please get a valid key at: https://www.graphhopper.com/developers/');
      return false;
    }
    
    if (data.hits && data.hits.length > 0) {
      console.log('✅ GraphHopper Geocoding API is working!');
      console.log(`   Found: ${data.hits[0].name}`);
      return true;
    }
  } catch (error) {
    console.log('❌ GraphHopper API error:', error.message);
    return false;
  }
}

async function test311API() {
  console.log('\n🔍 Testing SF 311 API...');
  const dateFilter = new Date();
  dateFilter.setDate(dateFilter.getDate() - 30);
  const dateString = dateFilter.toISOString().split('T')[0];
  
  const url = `https://data.sfgov.org/resource/vw6y-z8j6.json?$limit=5&$where=requested_datetime >= '${dateString}'`;
  
  try {
    const response = await fetch(url);
    const data = await response.json();
    
    if (Array.isArray(data) && data.length > 0) {
      console.log('✅ SF 311 API is working!');
      console.log(`   Found ${data.length} recent incidents`);
      return true;
    } else {
      console.log('⚠️  SF 311 API returned no data');
      return false;
    }
  } catch (error) {
    console.log('❌ SF 311 API error:', error.message);
    return false;
  }
}

async function testDispatchAPI() {
  console.log('\n🔍 Testing SFPD Dispatch API...');
  const url = `https://data.sfgov.org/resource/nwbb-fxkq.json?$limit=5`;
  
  try {
    const response = await fetch(url);
    const data = await response.json();
    
    if (Array.isArray(data) && data.length > 0) {
      console.log('✅ SFPD Dispatch API is working!');
      console.log(`   Found ${data.length} recent reports`);
      return true;
    } else {
      console.log('⚠️  SFPD Dispatch API returned no data');
      return false;
    }
  } catch (error) {
    console.log('❌ SFPD Dispatch API error:', error.message);
    return false;
  }
}

async function runAllTests() {
  console.log('=================================');
  console.log('SafePath SF API Integration Tests');
  console.log('=================================');
  
  const results = {
    graphhopper: await testGraphHopperGeocoding(),
    sf311: await test311API(),
    dispatch: await testDispatchAPI()
  };
  
  console.log('\n=================================');
  console.log('Test Summary:');
  console.log('=================================');
  console.log(`GraphHopper: ${results.graphhopper ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`SF 311 API: ${results.sf311 ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`SFPD Dispatch: ${results.dispatch ? '✅ PASS' : '❌ FAIL'}`);
  
  if (!results.graphhopper) {
    console.log('\n⚠️  IMPORTANT: The GraphHopper API key is invalid!');
    console.log('The app will still work but routing functionality will be limited.');
    console.log('To get a free API key:');
    console.log('1. Go to https://www.graphhopper.com/developers/');
    console.log('2. Sign up for a free account');
    console.log('3. Replace the key in .env file');
  }
}

runAllTests();