import pytest

from app.core.domain.models.game import Game


class TestGameService:
    @pytest.mark.asyncio
    async def test_get_rawg_id_by_name_returns_rawg_id(self, mocks_for_game_service):
        game_service, _game_repository_mock, rawg_client_mock = mocks_for_game_service

        rawg_client_mock.search_games.return_value = {
            "results": [
                {
                    "id": 3328,
                    "name": "The Witcher 3",
                }
            ]
        }

        rawg_id = await game_service._get_rawg_id_by_name("Witcher 3")

        rawg_client_mock.search_games.assert_awaited_once_with("Witcher 3")
        assert rawg_id == 3328

    def test_build_game_from_rawg_data_returns_valid_game(self, mocks_for_game_service):
        game_service, _game_repository_mock, _rawg_client_mock = mocks_for_game_service

        game_data = {
            "id": 3328,
            "name": "The Witcher 3",
            "description_raw": "Open world RPG.",
            "genres": [
                {"name": "RPG"},
                {"name": "Adventure"},
            ],
        }

        game = game_service._build_game_from_rawg_data(game_data)

        assert game.rawg_id == 3328
        assert game.name == "The Witcher 3"
        assert game.description == "Open world RPG."
        assert game.genres == ["RPG", "Adventure"]

    @pytest.mark.asyncio
    async def test_get_or_create_game_by_name_creates_game_in_db(
        self,
        mocks_for_game_service,
        rawg_client_get_game_filled_response,
    ):
        game_service, game_repository_mock, rawg_client_mock = mocks_for_game_service

        rawg_client_mock.search_games.return_value = {
            "results": [
                {
                    "id": 3328,
                    "name": "The Witcher 3",
                }
            ]
        }

        game_repository_mock.get_game_by_rawg_id.return_value = None
        rawg_client_mock.get_game.return_value = rawg_client_get_game_filled_response
        game_repository_mock.create_game.side_effect = lambda game: game

        created_game = await game_service.get_or_create_game_by_name("Witcher 3")

        assert created_game.rawg_id == 3328
        assert created_game.name == "The Witcher 3"
        assert created_game.description == "Open world RPG."
        assert created_game.genres == ["RPG", "Adventure"]

        rawg_client_mock.search_games.assert_awaited_once_with("Witcher 3")
        game_repository_mock.get_game_by_rawg_id.assert_called_once_with(3328)
        rawg_client_mock.get_game.assert_awaited_once_with(3328)
        game_repository_mock.create_game.assert_called_once_with(created_game)

    @pytest.mark.asyncio
    async def test_get_or_create_game_by_name_returns_game_from_db(
        self,
        mocks_for_game_service,
    ):
        game_service, game_repository_mock, rawg_client_mock = mocks_for_game_service

        existing_game = Game(
            rawg_id=3328,
            name="The Witcher 3",
            description="Open world RPG.",
            genres=["RPG", "Adventure"],
        )

        rawg_client_mock.search_games.return_value = {
            "results": [
                {
                    "id": 3328,
                    "name": "The Witcher 3",
                }
            ]
        }

        game_repository_mock.get_game_by_rawg_id.return_value = existing_game

        searched_game = await game_service.get_or_create_game_by_name("Witcher 3")

        assert searched_game is existing_game
        assert searched_game.rawg_id == 3328
        assert searched_game.name == "The Witcher 3"

        rawg_client_mock.search_games.assert_awaited_once_with("Witcher 3")
        game_repository_mock.get_game_by_rawg_id.assert_called_once_with(3328)

        rawg_client_mock.get_game.assert_not_awaited()
        game_repository_mock.create_game.assert_not_called()
