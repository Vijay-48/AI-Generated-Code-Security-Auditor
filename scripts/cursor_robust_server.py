#!/usr/bin/env python3
"""
Robust FastAPI Server for AI Code Security Auditor - Windows Compatible
Fixed Unicode issues, Redis fallbacks, and improved stability
"""
import os
import sys
import uvicorn
import logging
import asyncio
import signal
from pathlib import Path
from contextlib import asynccontextmanager

# Windows-compatible logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Set UTF-8 encoding for stdout on Windows
if sys.platform.startswith('win'):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    elif hasattr(sys.stdout, 'buffer'):
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables with fallbacks
os.environ.setdefault('OPENROUTER_API_KEY', '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')
os.environ.setdefault('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1/chat/completions')

# Server configuration for better stability
SERVER_CONFIG = {
    "host": "127.0.0.1",  # Use localhost for Windows compatibility
    "port": 8000,
    "log_level": "info",
    "access_log": True,
    "reload": False,  # Disable reload for stability
    "workers": 1,
    "timeout_keep_alive": 120,
    "timeout_graceful_shutdown": 30,
    "limit_concurrency": 10,
    "limit_max_requests": 1000,
}

class RobustServer:
    """Robust server manager with proper startup/shutdown handling"""
    
    def __init__(self):
        self.server = None
        self.should_exit = False
        
    async def startup(self):
        """Server startup with health checks"""
        try:
            logger.info("STARTING AI Code Security Auditor FastAPI Server...")
            logger.info("CURSOR AI Development Mode - Robust Configuration")
            
            # Import the app
            from app.main import app
            
            # Configure the server
            config = uvicorn.Config(
                app,
                **SERVER_CONFIG
            )
            
            self.server = uvicorn.Server(config)
            
            # Print connection info (Windows-compatible)
            print("=" * 60)
            print("AI Code Security Auditor - READY")
            print("=" * 60)
            print(f"API Documentation: http://localhost:8000/docs")
            print(f"Health Check: http://localhost:8000/health")  
            print(f"Models Endpoint: http://localhost:8000/models")
            print(f"Interactive API: http://localhost:8000/redoc")
            print("=" * 60)
            print("Server is stable and ready for CLI commands!")
            print("Press Ctrl+C to stop the server")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup server: {e}")
            print(f"Server setup failed: {e}")
            return False
    
    async def run(self):
        """Run the server with proper error handling"""
        if not await self.startup():
            return False
            
        try:
            await self.server.serve()
        except KeyboardInterrupt:
            logger.info("Server shutdown requested by user")
            print("\nShutting down server...")
        except Exception as e:
            logger.error(f"Server error: {e}")
            print(f"Server error: {e}")
        
        return True
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.should_exit = True
        if self.server:
            self.server.should_exit = True

def main():
    """Main server startup function"""
    server_manager = RobustServer()
    
    # Setup signal handlers for graceful shutdown (Windows compatible)
    if hasattr(signal, 'SIGINT'):
        signal.signal(signal.SIGINT, server_manager.signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, server_manager.signal_handler)
    
    try:
        # Run the server
        asyncio.run(server_manager.run())
        print("Server stopped successfully")
        return 0
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        print(f"Failed to start server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())