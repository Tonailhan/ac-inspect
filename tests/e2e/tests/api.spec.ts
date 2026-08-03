import { test, expect } from '@playwright/test';

test.describe('Anode Cover Inspector API End-to-End Tests', () => {
  test('should load and display the main page', async ({ page }) => {
    await page.goto('/');
    
    // Check if the page loads successfully
    await expect(page).toHaveTitle(/Anode Cover Inspector/);
    
    // Check for main elements
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('text=AI-powered')).toBeVisible();
  });

  test('should have working navigation', async ({ page }) => {
    await page.goto('/');
    
    // Test navigation links
    const navLinks = page.locator('nav a');
    const count = await navLinks.count();
    
    if (count > 0) {
      // Click first navigation link and check it works
      await navLinks.first().click();
      await page.waitForLoadState('networkidle');
    }
  });

  test('should handle API health check', async ({ page }) => {
    // Make direct API call to health endpoint
    const response = await page.request.get('http://localhost:5001/api/health');
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data).toHaveProperty('status', 'healthy');
    expect(data).toHaveProperty('model_loaded');
    expect(data).toHaveProperty('timestamp');
    expect(data).toHaveProperty('version', '1.0.0');
    expect(data).toHaveProperty('uptime_seconds');
    expect(data).toHaveProperty('memory_usage_mb');
    expect(data).toHaveProperty('cpu_percent');
  });

  test('should handle API metrics endpoint', async ({ page }) => {
    const response = await page.request.get('http://localhost:5001/api/metrics');
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data).toHaveProperty('status', 'success');
    expect(data).toHaveProperty('system');
    expect(data).toHaveProperty('application');
    
    expect(data.system).toHaveProperty('uptime_seconds');
    expect(data.system).toHaveProperty('memory_usage_mb');
    expect(data.system).toHaveProperty('cpu_percent');
    
    expect(data.application).toHaveProperty('model_loaded');
    expect(data.application).toHaveProperty('cache_size');
    expect(data.application).toHaveProperty('version');
  });

  test('should handle API info endpoint', async ({ page }) => {
    const response = await page.request.get('http://localhost:5001/api/info');
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data).toHaveProperty('model_name', 'standard_inspection_model');
    expect(data).toHaveProperty('classes');
    expect(data).toHaveProperty('cache_enabled', true);
    expect(data).toHaveProperty('lazy_loading', false);
  });

  test('should handle image upload prediction', async ({ page }) => {
    // Create a small test image (1x1 pixel PNG)
    const testImageBase64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
    
    const response = await page.request.post('http://localhost:5001/api/predict', {
      data: {
        image: `data:image/png;base64,${testImageBase64}`
      }
    });
    
    // Should either succeed (if model is loaded) or fail gracefully
    if (response.status() === 200) {
      const data = await response.json();
      expect(data).toHaveProperty('status');
      expect(data).toHaveProperty('confidence');
      expect(data).toHaveProperty('timestamp');
      expect(data).toHaveProperty('processing_time_ms');
      
      expect(['OK', 'NG']).toContain(data.status);
      expect(typeof data.confidence).toBe('number');
      expect(data.confidence).toBeGreaterThanOrEqual(0);
      expect(data.confidence).toBeLessThanOrEqual(1);
    } else {
      // Model might not be loaded in CI environment
      expect([503, 400]).toContain(response.status());
    }
  });

  test('should validate image upload with invalid data', async ({ page }) => {
    // Test with no image data
    let response = await page.request.post('http://localhost:5001/api/predict', {
      data: {}
    });
    expect(response.status()).toBe(422);
    
    // Test with invalid base64
    response = await page.request.post('http://localhost:5001/api/predict', {
      data: {
        image: 'invalid_base64_data'
      }
    });
    expect([400, 422]).toContain(response.status());
  });

  test('should have proper security headers', async ({ page }) => {
    const response = await page.request.get('http://localhost:5001/api/health');
    
    expect(response.status()).toBe(200);
    
    const headers = response.headers();
    
    // Check security headers
    expect(headers['x-content-type-options']).toBe('nosniff');
    expect(headers['x-frame-options']).toBe('DENY');
    expect(headers['x-xss-protection']).toBe('1; mode=block');
    expect(headers['referrer-policy']).toContain('strict-origin-when-cross-origin');
    expect(headers['content-security-policy']).toContain('default-src');
  });

  test('should handle concurrent requests', async ({ page }) => {
    // Make multiple concurrent requests
    const promises = Array(5).fill(null).map(() => 
      page.request.get('http://localhost:5001/api/health')
    );
    
    const responses = await Promise.all(promises);
    
    // All requests should succeed
    responses.forEach(response => {
      expect(response.status()).toBe(200);
    });
  });

  test('should handle 404 for non-existent endpoints', async ({ page }) => {
    const response = await page.request.get('http://localhost:5001/api/nonexistent');
    expect(response.status()).toBe(404);
  });

  test('should handle invalid HTTP methods', async ({ page }) => {
    const response = await page.request.delete('http://localhost:5001/api/health');
    expect(response.status()).toBe(405);
  });

  test('should test caching functionality', async ({ page }) => {
    const testImageBase64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
    
    // Make first request
    const start1 = Date.now();
    const response1 = await page.request.post('http://localhost:5001/api/predict', {
      data: {
        image: `data:image/png;base64,${testImageBase64}`
      }
    });
    const time1 = Date.now() - start1;
    
    // Make second request
    const start2 = Date.now();
    const response2 = await page.request.post('http://localhost:5001/api/predict', {
      data: {
        image: `data:image/png;base64,${testImageBase64}`
      }
    });
    const time2 = Date.now() - start2;
    
    if (response1.status() === 200 && response2.status() === 200) {
      const data1 = await response1.json();
      const data2 = await response2.json();
      
      // Results should be identical
      expect(data1.status).toBe(data2.status);
      expect(data1.confidence).toBe(data2.confidence);
      
      console.log(`First request: ${time1}ms, Second request: ${time2}ms`);
    }
  });
});
