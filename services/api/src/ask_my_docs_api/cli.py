import argparse
import asyncio

from ask_my_docs_api.core.config import get_settings
from ask_my_docs_api.core.security import generate_api_key, hash_api_key
from ask_my_docs_api.db.models import ApiKey, User
from ask_my_docs_api.db.session import build_engine, build_sessionmaker


async def create_user(name: str, key_name: str) -> None:
    engine = build_engine(get_settings())
    sessionmaker = build_sessionmaker(engine)
    key = generate_api_key()
    try:
        async with sessionmaker.begin() as session:
            user = User(name=name)
            session.add(ApiKey(key_hash=hash_api_key(key), name=key_name, owner=user))
            await session.flush()
            user_id = user.id
    finally:
        await engine.dispose()

    print(f"User created: id={user_id}, name={name}")
    print(f"API key: {key}")
    print("Save it now, it will not be shown again.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m ask_my_docs_api.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create-user", help="create a user and print a new API key")
    create.add_argument("--name", required=True)
    create.add_argument("--key-name", default="default")

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    if args.command == "create-user":
        asyncio.run(create_user(args.name, args.key_name))


if __name__ == "__main__":
    main()
