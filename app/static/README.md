# Frontend UI

This directory contains the frontend chat interface for the AI Life Insurance Sales Agent.

## Access

The frontend is automatically served at:
- **Main UI**: http://localhost:8000/
- **API Docs**: http://localhost:8000/docs

## Features

- **Chat Interface**: Start conversations and chat with the AI agent
- **Real-time Updates**: See conversation stage and interest level updates
- **Conversation Info**: View session ID, conversation ID, and current stage
- **Admin Panel**: Quick access to analytics (requires authentication)
- **History View**: View full conversation history

## Usage

1. Open http://localhost:8000/ in your browser
2. Click "Start Conversation" to begin
3. Type messages and interact with the AI agent
4. Use the sidebar to view conversation info and analytics

## API Endpoints Used

- `POST /api/conversation/start` - Start a new conversation
- `POST /api/conversation/message` - Send a message
- `POST /api/conversation/end` - End a conversation
- `GET /api/conversation/{session_id}` - Get conversation history
- `GET /api/analytics/conversations` - Get analytics (admin)

