#!/usr/bin/env python
"""Main entry point for running the IPAM Platform."""
import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('APP_PORT', 5000))
    host = os.environ.get('APP_HOST', '0.0.0.0')
    
    app.run(host=host, port=port, debug=app.config['DEBUG'])
