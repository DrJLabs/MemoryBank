#!/usr/bin/env python3
"""
Custom GPT Application Management Script

This script provides CLI commands to manage Custom GPT applications in the adapter service.
"""

import os
import sys
import secrets
import string
import argparse
from datetime import datetime
from typing import Optional, List, Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tabulate import tabulate

from app.models.custom_gpt import CustomGPTApplication, CustomGPTSession, CustomGPTAuditLog
from app.core.config import settings
from app.core.security import get_password_hash


def get_db_session():
    """Create a database session"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def generate_client_secret(length: int = 32) -> str:
    """Generate a secure client secret"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def create_application(name: str, permissions: List[str], rate_limit: str = "100/minute") -> Dict[str, Any]:
    """Create a new Custom GPT application"""
    db = get_db_session()

    try:
        # Generate credentials
        client_id = f"cgpt_{secrets.token_urlsafe(16)}"
        client_secret = generate_client_secret()

        # Create application
        app = CustomGPTApplication(
            name=name,
            client_id=client_id,
            client_secret=get_password_hash(client_secret),  # Store hashed
            permissions=permissions,
            rate_limit=rate_limit,
            rate_limits={
                "search": rate_limit,
                "create": rate_limit
            },
            created_at=datetime.utcnow()
        )

        db.add(app)
        db.commit()
        db.refresh(app)

        return {
            "id": str(app.id),
            "name": app.name,
            "client_id": app.client_id,
            "client_secret": client_secret,  # Return plain text (only shown once)
            "permissions": app.permissions,
            "rate_limit": app.rate_limit
        }

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def list_applications() -> List[Dict[str, Any]]:
    """List all Custom GPT applications"""
    db = get_db_session()

    try:
        apps = db.query(CustomGPTApplication).all()

        return [{
            "id": str(app.id),
            "name": app.name,
            "client_id": app.client_id,
            "permissions": ", ".join(app.permissions),
            "rate_limit": app.rate_limit,
            "created_at": app.created_at.isoformat() if app.created_at else None,
            "last_used": app.last_used.isoformat() if app.last_used else "Never"
        } for app in apps]

    finally:
        db.close()


def update_application(client_id: str, name: Optional[str] = None,
                      permissions: Optional[List[str]] = None,
                      rate_limit: Optional[str] = None) -> Dict[str, Any]:
    """Update an existing Custom GPT application"""
    db = get_db_session()

    try:
        app = db.query(CustomGPTApplication).filter_by(client_id=client_id).first()

        if not app:
            raise ValueError(f"Application with client_id '{client_id}' not found")

        if name:
            app.name = name
        if permissions is not None:
            app.permissions = permissions
        if rate_limit:
            app.rate_limit = rate_limit
            app.rate_limits = {
                "search": rate_limit,
                "create": rate_limit
            }

        db.commit()
        db.refresh(app)

        return {
            "id": str(app.id),
            "name": app.name,
            "client_id": app.client_id,
            "permissions": app.permissions,
            "rate_limit": app.rate_limit
        }

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def delete_application(client_id: str) -> bool:
    """Delete a Custom GPT application"""
    db = get_db_session()

    try:
        app = db.query(CustomGPTApplication).filter_by(client_id=client_id).first()

        if not app:
            raise ValueError(f"Application with client_id '{client_id}' not found")

        # Delete related sessions and audit logs
        db.query(CustomGPTSession).filter_by(application_id=app.id).delete()
        db.query(CustomGPTAuditLog).filter_by(application_id=app.id).delete()

        # Delete application
        db.delete(app)
        db.commit()

        return True

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def reset_client_secret(client_id: str) -> str:
    """Reset the client secret for an application"""
    db = get_db_session()

    try:
        app = db.query(CustomGPTApplication).filter_by(client_id=client_id).first()

        if not app:
            raise ValueError(f"Application with client_id '{client_id}' not found")

        # Generate new secret
        new_secret = generate_client_secret()
        app.client_secret = get_password_hash(new_secret)

        # Invalidate existing sessions
        db.query(CustomGPTSession).filter_by(application_id=app.id).delete()

        db.commit()

        return new_secret

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def show_application_stats(client_id: str) -> Dict[str, Any]:
    """Show statistics for a Custom GPT application"""
    db = get_db_session()

    try:
        app = db.query(CustomGPTApplication).filter_by(client_id=client_id).first()

        if not app:
            raise ValueError(f"Application with client_id '{client_id}' not found")

        # Count audit logs
        total_requests = db.query(CustomGPTAuditLog).filter_by(application_id=app.id).count()
        successful_requests = db.query(CustomGPTAuditLog).filter_by(
            application_id=app.id,
            response_status=200
        ).count()

        # Get operation breakdown
        from sqlalchemy import func
        operation_stats = db.query(
            CustomGPTAuditLog.operation_type,
            func.count(CustomGPTAuditLog.id).label('count')
        ).filter_by(application_id=app.id).group_by(CustomGPTAuditLog.operation_type).all()

        # Active sessions
        active_sessions = db.query(CustomGPTSession).filter_by(
            application_id=app.id
        ).filter(CustomGPTSession.expires_at > datetime.utcnow()).count()

        return {
            "application": {
                "name": app.name,
                "client_id": app.client_id,
                "created_at": app.created_at.isoformat() if app.created_at else None,
                "last_used": app.last_used.isoformat() if app.last_used else "Never"
            },
            "statistics": {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "success_rate": f"{(successful_requests/total_requests*100):.1f}%" if total_requests > 0 else "N/A",
                "active_sessions": active_sessions
            },
            "operations": {op.value: count for op, count in operation_stats}
        }

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Manage Custom GPT Applications")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create application
    create_parser = subparsers.add_parser("create", help="Create a new application")
    create_parser.add_argument("name", help="Application name")
    create_parser.add_argument("--permissions", nargs="+", default=["read", "write"],
                             help="Permissions (default: read write)")
    create_parser.add_argument("--rate-limit", default="100/minute",
                             help="Rate limit (default: 100/minute)")

    # List applications
    subparsers.add_parser("list", help="List all applications")

    # Update application
    update_parser = subparsers.add_parser("update", help="Update an application")
    update_parser.add_argument("client_id", help="Client ID")
    update_parser.add_argument("--name", help="New name")
    update_parser.add_argument("--permissions", nargs="+", help="New permissions")
    update_parser.add_argument("--rate-limit", help="New rate limit")

    # Delete application
    delete_parser = subparsers.add_parser("delete", help="Delete an application")
    delete_parser.add_argument("client_id", help="Client ID")

    # Reset secret
    reset_parser = subparsers.add_parser("reset-secret", help="Reset client secret")
    reset_parser.add_argument("client_id", help="Client ID")

    # Show stats
    stats_parser = subparsers.add_parser("stats", help="Show application statistics")
    stats_parser.add_argument("client_id", help="Client ID")

    args = parser.parse_args()

    try:
        if args.command == "create":
            result = create_application(args.name, args.permissions, args.rate_limit)
            print("\nApplication created successfully!")
            print("\nIMPORTANT: Save these credentials securely. The client secret will not be shown again.\n")
            print(f"Name: {result['name']}")
            print(f"Client ID: {result['client_id']}")
            print(f"Client Secret: {result['client_secret']}")
            print(f"Permissions: {', '.join(result['permissions'])}")
            print(f"Rate Limit: {result['rate_limit']}")

        elif args.command == "list":
            apps = list_applications()
            if apps:
                headers = ["Name", "Client ID", "Permissions", "Rate Limit", "Created", "Last Used"]
                rows = [[app["name"], app["client_id"], app["permissions"],
                        app["rate_limit"], app["created_at"][:10] if app["created_at"] else "N/A",
                        app["last_used"][:10] if app["last_used"] != "Never" else "Never"]
                       for app in apps]
                print(tabulate(rows, headers=headers, tablefmt="grid"))
            else:
                print("No applications found.")

        elif args.command == "update":
            result = update_application(args.client_id, args.name, args.permissions, args.rate_limit)
            print("\nApplication updated successfully!")
            print(f"Name: {result['name']}")
            print(f"Client ID: {result['client_id']}")
            print(f"Permissions: {', '.join(result['permissions'])}")
            print(f"Rate Limit: {result['rate_limit']}")

        elif args.command == "delete":
            if delete_application(args.client_id):
                print(f"\nApplication '{args.client_id}' deleted successfully!")

        elif args.command == "reset-secret":
            new_secret = reset_client_secret(args.client_id)
            print("\nClient secret reset successfully!")
            print("\nIMPORTANT: Save this secret securely. It will not be shown again.\n")
            print(f"New Client Secret: {new_secret}")

        elif args.command == "stats":
            stats = show_application_stats(args.client_id)
            print(f"\nApplication: {stats['application']['name']}")
            print(f"Client ID: {stats['application']['client_id']}")
            print(f"Created: {stats['application']['created_at']}")
            print(f"Last Used: {stats['application']['last_used']}")
            print("\nStatistics:")
            print(f"  Total Requests: {stats['statistics']['total_requests']}")
            print(f"  Successful: {stats['statistics']['successful_requests']}")
            print(f"  Success Rate: {stats['statistics']['success_rate']}")
            print(f"  Active Sessions: {stats['statistics']['active_sessions']}")

            if stats['operations']:
                print("\nOperations:")
                for op, count in stats['operations'].items():
                    print(f"  {op}: {count}")

        else:
            parser.print_help()

    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()