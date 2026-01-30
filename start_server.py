#!/usr/bin/env python3
"""
Lancer le serveur WebSocket pour le jeu Loup-Garou.
Usage: python start_server.py [--host HOST] [--port PORT] [--no-reload]
"""

import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Lancer le serveur WebSocket")
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Adresse d'écoute (défaut: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port d'écoute (défaut: 8000)"
    )
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Désactiver l'auto-reload (mode production)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎮 Serveur WebSocket Loup-Garou Multi-Agents")
    print("=" * 60)
    print(f"📡 Host: {args.host}")
    print(f"🔌 Port: {args.port}")
    print(f"🔄 Auto-reload: {'Non' if args.no_reload else 'Oui'}")
    print("=" * 60)
    print()
    print("Endpoints:")
    print(f"  • WebSocket: ws://{args.host}:{args.port}/ws/{{client_id}}")
    print(f"  • Health:    http://{args.host}:{args.port}/health")
    print(f"  • Stats:     http://{args.host}:{args.port}/stats")
    print()
    print("Appuyez sur Ctrl+C pour arrêter le serveur")
    print("=" * 60)
    print()
    
    try:
        from server.websocket_server import run_server
        run_server(host=args.host, port=args.port, reload=not args.no_reload)
    except KeyboardInterrupt:
        print("\n\n👋 Serveur arrêté")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
