from getpass import getpass

from pydantic import ValidationError
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.users import AccountType, User
from app.schemas.users import UserCreate


def main():
    email = input("Email: ")
    display_name = input("Display name: ")
    password = getpass("Password: ")
    if getpass("Repeat password: ") != password:
        print("Passwords do not match.")
        return

    try:
        details = UserCreate(
            email=email, display_name=display_name, password=password, account_type="coach"
        )
    except ValidationError as error:
        for problem in error.errors():
            print(f"{problem['loc'][0]}: {problem['msg']}")
        return

    with SessionLocal() as db:
        if db.scalar(select(User).where(User.email == details.email)) is not None:
            print("An account with that email already exists.")
            return
        db.add(User(
            email=details.email,
            display_name=details.display_name,
            password_hash=hash_password(details.password),
            account_type=AccountType.SUPER_ADMIN,
        ))
        db.commit()

    print(f"Super admin {details.email} created.")


if __name__ == "__main__":
    main()
