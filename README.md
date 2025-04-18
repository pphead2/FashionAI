# Fashion AI

A modern web application that helps users identify and purchase clothing items and accessories from outfit images using AI-powered image recognition and product search.

## Features

- Image Upload and Analysis
  - Upload outfit images
  - AI-powered item detection
  - Automatic identification of clothing, accessories, and styles
  - Smart cropping and item isolation

- Product Search and Recommendations
  - Similar item matching
  - Price comparison
  - Multiple retailer options
  - Smart filtering capabilities

- User Account System
  - Secure authentication with email and Google OAuth
  - Personal profile management
  - Saved favorites
  - Search history

- Advanced Caching
  - Optimized performance
  - Reduced API calls
  - Fast search results

## Tech Stack

- **Frontend**: Next.js 14, React, Chakra UI
- **Backend**: Supabase
- **Authentication**: Supabase Auth, Google OAuth
- **AI Services**: Google Vision AI
- **Database**: PostgreSQL (via Supabase)
- **Caching**: Redis
- **Infrastructure**: Vercel, Supabase Cloud

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/pphead2/FashionAI.git
   cd FashionAI
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env.local`
   - Fill in your Supabase and Google OAuth credentials

4. Run the development server:
   ```bash
   npm run dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.
