"""
User Operations Module

This module provides comprehensive user management operations for the dhanworks-bot,
including user creation, updates, queries, and statistics generation.

Features:
- User creation and registration
- User profile updates
- Query operations for retrieving user data
- Statistical analysis of user base
- Data validation and error handling
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import logging
from enum import Enum


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserStatus(Enum):
    """Enumeration for user status states."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"


class UserRole(Enum):
    """Enumeration for user role types."""
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"


@dataclass
class User:
    """Represents a user in the system."""
    user_id: str
    username: str
    email: str
    created_at: datetime
    updated_at: datetime
    status: UserStatus = UserStatus.ACTIVE
    role: UserRole = UserRole.USER
    profile: Optional[Dict[str, Any]] = None
    last_login: Optional[datetime] = None
    activity_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary format."""
        user_dict = asdict(self)
        user_dict['status'] = self.status.value
        user_dict['role'] = self.role.value
        user_dict['created_at'] = self.created_at.isoformat()
        user_dict['updated_at'] = self.updated_at.isoformat()
        if self.last_login:
            user_dict['last_login'] = self.last_login.isoformat()
        return user_dict

    def __repr__(self) -> str:
        return f"User(user_id={self.user_id}, username={self.username}, status={self.status.value})"


class UserManager:
    """Manages user operations for the dhanworks-bot."""

    def __init__(self):
        """Initialize the UserManager with an empty user storage."""
        self.users: Dict[str, User] = {}
        self.user_index: Dict[str, str] = {}  # username -> user_id mapping
        logger.info("UserManager initialized")

    def create_user(
        self,
        user_id: str,
        username: str,
        email: str,
        role: UserRole = UserRole.USER,
        profile: Optional[Dict[str, Any]] = None
    ) -> User:
        """
        Create a new user in the system.

        Args:
            user_id: Unique identifier for the user
            username: Username for the user
            email: Email address of the user
            role: Role assigned to the user (default: USER)
            profile: Optional user profile information

        Returns:
            User: The created user object

        Raises:
            ValueError: If user_id or username already exists
            TypeError: If required parameters are invalid types
        """
        # Validation
        if not isinstance(user_id, str) or not user_id.strip():
            raise TypeError("user_id must be a non-empty string")
        if not isinstance(username, str) or not username.strip():
            raise TypeError("username must be a non-empty string")
        if not isinstance(email, str) or not email.strip():
            raise TypeError("email must be a non-empty string")

        if user_id in self.users:
            raise ValueError(f"User with ID '{user_id}' already exists")
        if username.lower() in self.user_index:
            raise ValueError(f"Username '{username}' is already taken")

        # Create user
        now = datetime.utcnow()
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            created_at=now,
            updated_at=now,
            role=role,
            profile=profile or {}
        )

        # Store user
        self.users[user_id] = user
        self.user_index[username.lower()] = user_id

        logger.info(f"User created: {user}")
        return user

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Retrieve a user by their user ID.

        Args:
            user_id: The unique identifier of the user

        Returns:
            User: The user object if found, None otherwise
        """
        return self.users.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Retrieve a user by their username.

        Args:
            username: The username to search for

        Returns:
            User: The user object if found, None otherwise
        """
        user_id = self.user_index.get(username.lower())
        if user_id:
            return self.users.get(user_id)
        return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by their email address.

        Args:
            email: The email address to search for

        Returns:
            User: The user object if found, None otherwise
        """
        for user in self.users.values():
            if user.email.lower() == email.lower():
                return user
        return None

    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """
        Update user information.

        Args:
            user_id: The user ID to update
            **kwargs: Key-value pairs of fields to update

        Returns:
            User: The updated user object, None if user not found

        Raises:
            ValueError: If attempting to update immutable fields
        """
        user = self.users.get(user_id)
        if not user:
            logger.warning(f"Update attempted on non-existent user: {user_id}")
            return None

        immutable_fields = {'user_id', 'created_at'}
        for key in kwargs:
            if key in immutable_fields:
                raise ValueError(f"Cannot update immutable field: {key}")

        # Handle field updates
        for key, value in kwargs.items():
            if key == 'status' and isinstance(value, str):
                user.status = UserStatus(value)
            elif key == 'role' and isinstance(value, str):
                user.role = UserRole(value)
            elif key == 'username':
                old_username = user.username.lower()
                if old_username in self.user_index:
                    del self.user_index[old_username]
                self.user_index[value.lower()] = user_id
                user.username = value
            elif hasattr(user, key):
                setattr(user, key, value)

        user.updated_at = datetime.utcnow()
        logger.info(f"User updated: {user_id}")
        return user

    def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Optional[User]:
        """
        Update user profile information.

        Args:
            user_id: The user ID to update
            profile_data: Dictionary containing profile information

        Returns:
            User: The updated user object, None if user not found
        """
        user = self.users.get(user_id)
        if not user:
            return None

        if user.profile is None:
            user.profile = {}

        user.profile.update(profile_data)
        user.updated_at = datetime.utcnow()
        logger.info(f"Profile updated for user: {user_id}")
        return user

    def set_user_status(self, user_id: str, status: UserStatus) -> Optional[User]:
        """
        Set the status of a user.

        Args:
            user_id: The user ID to update
            status: The new status

        Returns:
            User: The updated user object, None if user not found
        """
        return self.update_user(user_id, status=status)

    def set_user_role(self, user_id: str, role: UserRole) -> Optional[User]:
        """
        Set the role of a user.

        Args:
            user_id: The user ID to update
            role: The new role

        Returns:
            User: The updated user object, None if user not found
        """
        return self.update_user(user_id, role=role)

    def record_user_login(self, user_id: str) -> Optional[User]:
        """
        Record a user login event.

        Args:
            user_id: The user ID logging in

        Returns:
            User: The updated user object, None if user not found
        """
        user = self.users.get(user_id)
        if not user:
            return None

        user.last_login = datetime.utcnow()
        user.activity_count += 1
        user.updated_at = datetime.utcnow()
        logger.info(f"Login recorded for user: {user_id}")
        return user

    def record_user_activity(self, user_id: str) -> Optional[User]:
        """
        Record a user activity.

        Args:
            user_id: The user ID with activity

        Returns:
            User: The updated user object, None if user not found
        """
        user = self.users.get(user_id)
        if not user:
            return None

        user.activity_count += 1
        user.updated_at = datetime.utcnow()
        return user

    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user from the system.

        Args:
            user_id: The user ID to delete

        Returns:
            bool: True if successful, False if user not found
        """
        user = self.users.get(user_id)
        if not user:
            return False

        username = user.username.lower()
        if username in self.user_index:
            del self.user_index[username]

        del self.users[user_id]
        logger.info(f"User deleted: {user_id}")
        return True

    def list_users(
        self,
        status: Optional[UserStatus] = None,
        role: Optional[UserRole] = None,
        limit: Optional[int] = None
    ) -> List[User]:
        """
        List users with optional filtering.

        Args:
            status: Filter by user status
            role: Filter by user role
            limit: Maximum number of users to return

        Returns:
            List[User]: List of users matching the criteria
        """
        filtered_users = self.users.values()

        if status:
            filtered_users = [u for u in filtered_users if u.status == status]

        if role:
            filtered_users = [u for u in filtered_users if u.role == role]

        users_list = list(filtered_users)

        if limit:
            users_list = users_list[:limit]

        return users_list

    def get_statistics(self) -> Dict[str, Any]:
        """
        Generate comprehensive statistics about the user base.

        Returns:
            Dict[str, Any]: Dictionary containing user statistics
        """
        if not self.users:
            return {
                "total_users": 0,
                "total_active_users": 0,
                "total_inactive_users": 0,
                "total_suspended_users": 0,
                "total_banned_users": 0,
                "admin_count": 0,
                "moderator_count": 0,
                "user_count": 0,
                "guest_count": 0,
                "average_activity_count": 0,
                "average_days_active": 0,
                "most_active_users": [],
                "recently_active_users": [],
                "recently_created_users": []
            }

        total_users = len(self.users)
        status_counts = {status: 0 for status in UserStatus}
        role_counts = {role: 0 for role in UserRole}

        now = datetime.utcnow()
        total_activity = 0

        for user in self.users.values():
            status_counts[user.status] += 1
            role_counts[user.role] += 1
            total_activity += user.activity_count

        average_activity = total_activity / total_users if total_users > 0 else 0

        # Get most active users
        most_active = sorted(
            self.users.values(),
            key=lambda u: u.activity_count,
            reverse=True
        )[:5]

        # Get recently active users
        recently_active = sorted(
            [u for u in self.users.values() if u.last_login],
            key=lambda u: u.last_login,
            reverse=True
        )[:5]

        # Get recently created users
        recently_created = sorted(
            self.users.values(),
            key=lambda u: u.created_at,
            reverse=True
        )[:5]

        # Calculate average days active
        total_days = sum(
            (now - user.created_at).days for user in self.users.values()
        )
        average_days = total_days / total_users if total_users > 0 else 0

        return {
            "total_users": total_users,
            "total_active_users": status_counts[UserStatus.ACTIVE],
            "total_inactive_users": status_counts[UserStatus.INACTIVE],
            "total_suspended_users": status_counts[UserStatus.SUSPENDED],
            "total_banned_users": status_counts[UserStatus.BANNED],
            "admin_count": role_counts[UserRole.ADMIN],
            "moderator_count": role_counts[UserRole.MODERATOR],
            "user_count": role_counts[UserRole.USER],
            "guest_count": role_counts[UserRole.GUEST],
            "average_activity_count": round(average_activity, 2),
            "average_days_active": round(average_days, 2),
            "most_active_users": [
                {"user_id": u.user_id, "username": u.username, "activity_count": u.activity_count}
                for u in most_active
            ],
            "recently_active_users": [
                {"user_id": u.user_id, "username": u.username, "last_login": u.last_login.isoformat()}
                for u in recently_active
            ],
            "recently_created_users": [
                {"user_id": u.user_id, "username": u.username, "created_at": u.created_at.isoformat()}
                for u in recently_created
            ]
        }

    def export_users(self, format: str = "json") -> str:
        """
        Export all users in the specified format.

        Args:
            format: Export format ('json' or 'csv')

        Returns:
            str: Exported user data as string

        Raises:
            ValueError: If format is not supported
        """
        if format == "json":
            return json.dumps(
                [user.to_dict() for user in self.users.values()],
                indent=2,
                default=str
            )
        elif format == "csv":
            if not self.users:
                return "user_id,username,email,status,role,created_at,activity_count"

            users_list = list(self.users.values())
            headers = ["user_id", "username", "email", "status", "role", "created_at", "activity_count"]
            csv_data = ",".join(headers) + "\n"

            for user in users_list:
                row = [
                    user.user_id,
                    user.username,
                    user.email,
                    user.status.value,
                    user.role.value,
                    user.created_at.isoformat(),
                    str(user.activity_count)
                ]
                csv_data += ",".join(row) + "\n"

            return csv_data
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def get_user_activity_report(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate an activity report for a specific user.

        Args:
            user_id: The user ID to generate report for

        Returns:
            Dict[str, Any]: Activity report for the user, None if user not found
        """
        user = self.users.get(user_id)
        if not user:
            return None

        now = datetime.utcnow()
        days_active = (now - user.created_at).days

        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "status": user.status.value,
            "role": user.role.value,
            "created_at": user.created_at.isoformat(),
            "days_since_creation": days_active,
            "total_activity_count": user.activity_count,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "average_daily_activity": round(user.activity_count / (days_active + 1), 2)
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize manager
    manager = UserManager()

    # Create sample users
    user1 = manager.create_user(
        user_id="user_001",
        username="john_doe",
        email="john@example.com",
        role=UserRole.ADMIN,
        profile={"full_name": "John Doe", "location": "USA"}
    )

    user2 = manager.create_user(
        user_id="user_002",
        username="jane_smith",
        email="jane@example.com",
        role=UserRole.USER,
        profile={"full_name": "Jane Smith", "location": "UK"}
    )

    user3 = manager.create_user(
        user_id="user_003",
        username="bob_wilson",
        email="bob@example.com"
    )

    # Update user
    manager.update_user("user_001", email="john.doe@example.com")
    manager.update_user_profile("user_002", {"bio": "Software developer"})

    # Record activities
    manager.record_user_login("user_001")
    manager.record_user_activity("user_001")
    manager.record_user_activity("user_001")
    manager.record_user_login("user_002")

    # Query users
    print("\n=== User Queries ===")
    print(f"Get user by ID: {manager.get_user_by_id('user_001')}")
    print(f"Get user by username: {manager.get_user_by_username('jane_smith')}")
    print(f"List all active users: {manager.list_users(status=UserStatus.ACTIVE)}")

    # Get statistics
    print("\n=== User Statistics ===")
    stats = manager.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")

    # Activity report
    print("\n=== Activity Report ===")
    report = manager.get_user_activity_report("user_001")
    print(json.dumps(report, indent=2))
