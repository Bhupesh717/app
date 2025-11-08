// Manual trigger endpoint - allows you to test notifications via URL
// Access: https://your-site.netlify.app/.netlify/functions/manual-trigger

const sendNotification = require('./send-notification');

exports.handler = async (event, context) => {
  console.log('📱 Manual trigger called');
  
  // Call the main notification handler
  return await sendNotification.handler(event, context);
};