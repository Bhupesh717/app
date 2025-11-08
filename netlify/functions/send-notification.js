// Netlify Scheduled Function for OneSignal Push Notifications
// Fetches random WordPress post and sends push notification

const https = require('https');
const http = require('http');

// Helper function to make HTTP/HTTPS requests
function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const protocol = urlObj.protocol === 'https:' ? https : http;
    
    const requestOptions = {
      hostname: urlObj.hostname,
      path: urlObj.pathname + urlObj.search,
      method: options.method || 'GET',
      headers: options.headers || {},
      ...options
    };

    const req = protocol.request(requestOptions, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const jsonData = JSON.parse(data);
          resolve({ statusCode: res.statusCode, data: jsonData });
        } catch (e) {
          resolve({ statusCode: res.statusCode, data: data });
        }
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    if (options.body) {
      req.write(options.body);
    }

    req.end();
  });
}

// Fetch random WordPress post
async function fetchRandomWordPressPost() {
  try {
    const wordpressSiteUrl = process.env.WORDPRESS_SITE_URL || 'https://ccodelearner.com';
    const apiUrl = `${wordpressSiteUrl}/wp-json/wp/v2/posts?per_page=100&status=publish&_fields=id,title,excerpt,link`;
    
    console.log('Fetching posts from:', apiUrl);
    
    const response = await makeRequest(apiUrl);
    
    if (response.statusCode !== 200) {
      throw new Error(`Failed to fetch posts. Status: ${response.statusCode}`);
    }
    
    const posts = response.data;
    
    if (!posts || posts.length === 0) {
      throw new Error('No posts found on WordPress site');
    }
    
    // Select random post
    const randomPost = posts[Math.floor(Math.random() * posts.length)];
    
    // Clean HTML from excerpt
    const cleanExcerpt = randomPost.excerpt.rendered
      .replace(/<[^>]*>/g, '')
      .replace(/&nbsp;/g, ' ')
      .replace(/&amp;/g, '&')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&quot;/g, '"')
      .trim()
      .substring(0, 150);
    
    return {
      title: randomPost.title.rendered,
      excerpt: cleanExcerpt,
      url: randomPost.link
    };
  } catch (error) {
    console.error('Error fetching WordPress post:', error);
    throw error;
  }
}

// Send OneSignal push notification
async function sendOneSignalNotification(post) {
  try {
    const appId = process.env.ONESIGNAL_APP_ID;
    const apiKey = process.env.ONESIGNAL_REST_API_KEY;
    
    if (!appId || !apiKey) {
      throw new Error('OneSignal credentials not configured. Please set ONESIGNAL_APP_ID and ONESIGNAL_REST_API_KEY environment variables.');
    }
    
    const payload = JSON.stringify({
      app_id: appId,
      included_segments: ['All'],
      headings: { en: post.title },
      contents: { en: post.excerpt },
      url: post.url
    });
    
    console.log('Sending notification for post:', post.title);
    
    const response = await makeRequest('https://onesignal.com/api/v1/notifications', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Basic ${apiKey}`
      },
      body: payload
    });
    
    if (response.statusCode !== 200) {
      throw new Error(`OneSignal API error. Status: ${response.statusCode}, Response: ${JSON.stringify(response.data)}`);
    }
    
    console.log('✅ Notification sent successfully!');
    console.log('Recipients:', response.data.recipients || 0);
    
    return response.data;
  } catch (error) {
    console.error('Error sending OneSignal notification:', error);
    throw error;
  }
}

// Main handler - called by Netlify scheduler
exports.handler = async (event, context) => {
  console.log('🚀 Starting scheduled notification job...');
  console.log('Triggered at:', new Date().toISOString());
  
  try {
    // Step 1: Fetch random WordPress post
    console.log('Step 1: Fetching random WordPress post...');
    const post = await fetchRandomWordPressPost();
    console.log('✅ Post fetched:', post.title);
    
    // Step 2: Send OneSignal notification
    console.log('Step 2: Sending OneSignal notification...');
    const result = await sendOneSignalNotification(post);
    
    // Success response
    return {
      statusCode: 200,
      body: JSON.stringify({
        success: true,
        message: 'Notification sent successfully',
        post: {
          title: post.title,
          excerpt: post.excerpt.substring(0, 100) + '...',
          url: post.url
        },
        recipients: result.recipients || 0,
        timestamp: new Date().toISOString()
      })
    };
  } catch (error) {
    console.error('❌ Error in scheduled job:', error);
    
    // Error response
    return {
      statusCode: 500,
      body: JSON.stringify({
        success: false,
        error: error.message,
        timestamp: new Date().toISOString()
      })
    };
  }
};