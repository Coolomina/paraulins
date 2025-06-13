# Image Search Setup

The image search feature uses the Pixabay API to find free images. To enable this feature, you need to get a free API key from Pixabay.

## Getting a Pixabay API Key (Free)

1. Go to [Pixabay.com](https://pixabay.com/)
2. Create a free account or log in if you already have one
3. Go to [Pixabay API Documentation](https://pixabay.com/api/docs/)
4. Click "Get Started" and follow the instructions to get your API key
5. The free tier allows 5,000 requests per hour, which is more than enough for personal use

## Setting Up the API Key

1. Create a `.env` file in the root directory of this project (if it doesn't exist)
2. Add your API key to the `.env` file:
   ```
   PIXABAY_API_KEY=your-api-key-here
   ```
3. Restart the application
4. The image search feature will now work!

## Without API Key

If you don't set up an API key, the image search feature will show a helpful message and users can still upload their own images using the "Upload File" tab.
