from __future__ import annotations

from database.db import connect_db, initialize_db
from database.repository import Repository


def test_repository_stores_statement_path_and_filters_accounts_by_owner(tmp_path) -> None:
    connection = connect_db(tmp_path / "ownership.db")
    initialize_db(connection)
    repository = Repository(connection)
    user_one = repository.create_user("One", "one@example.com")
    user_two = repository.create_user("Two", "two@example.com")

    owned_account = repository.save_account(
        user_id=user_one.id,
        account_ref="24601985",
        broker="MT4",
        currency="USD",
        statement_path="data/imports/mt4_statement.htm",
    )
    repository.save_account(
        user_id=user_two.id,
        account_ref="99887766",
        broker="MT4",
        currency="USD",
        statement_path="data/imports/mt4_statement.htm",
    )

    stored = repository.get_account_for_user(user_one.id, "24601985")
    user_one_accounts = repository.list_accounts(user_one.id)

    assert owned_account.statement_path == "data/imports/mt4_statement.htm"
    assert stored.user_id == user_one.id
    assert len(user_one_accounts) == 1
    assert user_one_accounts[0].account_ref == "24601985"
